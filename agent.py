import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv
from json_repair import repair_json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
)

N_SAMPLES = 3  # self-consistency runs per event

def call_glm(event: dict) -> tuple[dict, str]:
    """Single LLM call. Returns (probabilities dict, raw reasoning text)."""
    outcomes = event["outcomes"]
    
    # for large outcome lists, only ask about top candidates
    # GLM struggles to output JSON with 15-30 outcomes
    if len(outcomes) > 8:
        outcomes_to_use = outcomes[:8]
        has_truncated = True
    else:
        outcomes_to_use = outcomes
        has_truncated = False
    
    outcomes_str = json.dumps(outcomes_to_use)
    
    prompt = f"""You are an expert forecasting agent.

Event: {event['title']}
Description: {event.get('description', '')}
Category: {event['category']}
Rules: {event.get('rules', '')}

Outcomes to evaluate: {outcomes_str}

Instructions:
1. Think through what you know about this topic
2. For each reasoning step, rate your confidence (0.0 to 1.0)
3. Assign a probability to each outcome
4. Probabilities must sum to exactly 1.0

Return ONLY this JSON, no other text, no markdown:
{{
  "reasoning_steps": [
    {{"step": "your reasoning here", "confidence": 0.8}},
    {{"step": "your reasoning here", "confidence": 0.7}}
  ],
  "probabilities": {{
    {", ".join([f'"{o}": 0.0' for o in outcomes_to_use])}
  }}
}}"""

    try:
        response = client.chat.completions.create(
            model="glm-5.1",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a precise forecasting agent. Always respond with valid JSON only. No markdown, no explanation outside the JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        raw_text = response.choices[0].message.content
        
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty response from GLM")
        
        # clean markdown fences
        clean = raw_text.strip()
        for fence in ["```json", "```JSON", "```"]:
            if clean.startswith(fence):
                clean = clean[len(fence):]
                break
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        
        # extract JSON object
        start = clean.find("{")
        end = clean.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = clean[start:end]
        parsed = json.loads(repair_json(json_str))
        
        # validate probabilities key exists
        if "probabilities" not in parsed:
            raise ValueError("No probabilities key in response")
        
        # if we truncated outcomes, distribute remaining probability uniformly
        if has_truncated:
            remaining_outcomes = outcomes[8:]
            total_assigned = sum(parsed["probabilities"].values())
            remaining_prob = max(0, 1.0 - total_assigned)
            per_remaining = remaining_prob / len(remaining_outcomes) if remaining_outcomes else 0
            for o in remaining_outcomes:
                parsed["probabilities"][o] = per_remaining
        
        return parsed, raw_text
        
    except Exception as e:
        raise ValueError(f"call_glm failed: {e}")


def compute_entropy(samples: list[dict], outcomes: list[str]) -> dict:
    """
    Compute entropy signals from N self-consistency samples.
    
    - step_confidence_entropy: variance in per-step confidence across samples
    - inter_sample_entropy: how much final probabilities diverge across runs
    """
    # inter-sample entropy: variance of predicted probability per outcome
    inter_variances = []
    for outcome in outcomes:
        probs = [s["probabilities"].get(outcome, 0) for s in samples]
        mean = sum(probs) / len(probs)
        variance = sum((p - mean) ** 2 for p in probs) / len(probs)
        inter_variances.append(variance)
    
    inter_entropy = sum(inter_variances) / len(inter_variances) if inter_variances else 0

    # step confidence entropy: how uncertain the model is about its own reasoning
    all_confidences = []
    for sample in samples:
        for step in sample.get("reasoning_steps", []):
            all_confidences.append(step.get("confidence", 0.5))
    
    if all_confidences:
        mean_conf = sum(all_confidences) / len(all_confidences)
        step_variance = sum((c - mean_conf) ** 2 for c in all_confidences) / len(all_confidences)
    else:
        step_variance = 0

    return {
        "inter_sample_entropy": round(inter_entropy, 4),
        "step_confidence_variance": round(step_variance, 4),
        "combined_entropy": round((inter_entropy + step_variance) / 2, 4),
        "n_samples": len(samples)
    }



def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def predict(event: dict) -> dict:
    outcomes = event["outcomes"]
    
    # run N self-consistency samples
    samples = []
    for i in range(N_SAMPLES):
        try:
            parsed, _ = call_glm(event)
            total = sum(parsed["probabilities"].get(o, 0) for o in outcomes)
            if total > 0:
                for o in outcomes:
                    parsed["probabilities"][o] = parsed["probabilities"].get(o, 0) / total
            samples.append(parsed)
        except Exception as e:
            print(f"  Sample {i+1} failed: {e}")
            continue
    
    if not samples:
        return {"p_yes": 0.5, "rationale": "fallback uniform"}
    
    # average probabilities across samples
    mean_probs = {}
    for outcome in outcomes:
        vals = [s["probabilities"].get(outcome, 0) for s in samples]
        mean_probs[outcome] = sum(vals) / len(vals)
    
    # compute entropy
    entropy = compute_entropy(samples, outcomes)
    
    # recalibrate
    uniform = 1.0 / len(outcomes)
    entropy_weight = min(0.9, sigmoid(entropy["combined_entropy"] * 8 - 1))
    
    recalibrated = {}
    for outcome in outcomes:
        raw = mean_probs[outcome]
        recalibrated[outcome] = (1 - entropy_weight) * raw + entropy_weight * uniform
    
    total = sum(recalibrated.values())
    for outcome in outcomes:
        recalibrated[outcome] = round(recalibrated[outcome] / total, 4)
    
    print(f"  Event: {event['event_ticker']}")
    print(f"  Entropy: {entropy}")
    print(f"  Entropy weight: {round(entropy_weight, 3)}")
    
    # for binary events, return p_yes
    # for multi-outcome, return probabilities array
    if len(outcomes) == 2:
        p_yes = recalibrated[outcomes[0]]
        return {"p_yes": p_yes, "rationale": f"entropy={entropy['combined_entropy']}, weight={round(entropy_weight,3)}"}
    else:
        return {
            "p_yes": max(recalibrated.values()),
            "rationale": f"multi-outcome: entropy={entropy['combined_entropy']}"
        }


if __name__ == "__main__":
    # quick test on a single event
    test_event = {
        "event_ticker": "test-001",
        "market_ticker": "test-001", 
        "title": "Will the Federal Reserve cut rates at its next meeting?",
        "description": "Resolves Yes if the Fed cuts the federal funds rate.",
        "category": "Economics",
        "rules": "Resolves based on the official Fed announcement.",
        "close_time": "2026-06-15T00:00:00Z",
        "outcomes": ["Yes", "No"]
    }
    
    print("Running test prediction...")
    result = predict(test_event)
    print(f"\nFinal result: {result}")