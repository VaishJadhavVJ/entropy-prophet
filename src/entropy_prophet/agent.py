import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
)

N_SAMPLES = 3  # self-consistency runs per event

def call_glm(event: dict) -> tuple[dict, str]:
    """Single LLM call. Returns (probabilities dict, raw reasoning text)."""
    outcomes = event["outcomes"]
    outcomes_str = json.dumps(outcomes)
    
    prompt = f"""You are an expert forecasting agent. Analyze this prediction market event carefully.

Event: {event['title']}
Description: {event['description']}
Category: {event['category']}
Rules: {event['rules']}
Outcomes: {outcomes_str}

Think through this step by step:
1. What do you know about this topic?
2. What factors influence the outcome?
3. How confident are you at each reasoning step?
4. What is your final probability estimate?

Return ONLY valid JSON in this exact format:
{{
  "reasoning_steps": [
    {{"step": "step description", "confidence": 0.0-1.0}},
    {{"step": "step description", "confidence": 0.0-1.0}}
  ],
  "probabilities": {{
    {", ".join([f'"{o}": 0.0' for o in outcomes])}
  }}
}}

Probabilities must sum to 1.0."""

    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,  # some variance for self-consistency
        max_tokens=1500
    )
    
    raw_text = response.choices[0].message.content
    
    # parse JSON from response
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    parsed = json.loads(raw_text[start:end])
    
    return parsed, raw_text


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


def recalibrate(mean_probs: dict, entropy: dict) -> dict:
    """
    Compress probabilities toward uniform when entropy is high.
    High entropy = model is uncertain = pull toward uniform distribution.
    Low entropy = model is confident = trust its probabilities.
    """
    outcomes = list(mean_probs.keys())
    n = len(outcomes)
    uniform = 1.0 / n
    
    # entropy weight: how much to compress toward uniform
    # combined_entropy of 0 = full trust in LLM
    # combined_entropy of 0.1+ = significant compression
    entropy_weight = min(0.9, mean_probs.get("_entropy_weight", 
                         math.sigmoid_approx(entropy["combined_entropy"] * 8 - 1)))
    
    recalibrated = {}
    for outcome in outcomes:
        raw = mean_probs[outcome]
        recalibrated[outcome] = round(
            (1 - entropy_weight) * raw + entropy_weight * uniform, 4
        )
    
    return recalibrated


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def predict(event: dict) -> dict:
    """Main predict function -- called by Prophet Arena CLI."""
    outcomes = event["outcomes"]
    
    # run N self-consistency samples
    samples = []
    for i in range(N_SAMPLES):
        try:
            parsed, _ = call_glm(event)
            # normalize probabilities
            total = sum(parsed["probabilities"].get(o, 0) for o in outcomes)
            if total > 0:
                for o in outcomes:
                    parsed["probabilities"][o] = parsed["probabilities"].get(o, 0) / total
            samples.append(parsed)
        except Exception as e:
            print(f"  Sample {i+1} failed: {e}")
            continue
    
    if not samples:
        # fallback: uniform distribution
        p = 1.0 / len(outcomes)
        return {"probabilities": [{"market": o, "probability": p} for o in outcomes]}
    
    # average probabilities across samples
    mean_probs = {}
    for outcome in outcomes:
        vals = [s["probabilities"].get(outcome, 0) for s in samples]
        mean_probs[outcome] = sum(vals) / len(vals)
    
    # compute entropy
    entropy = compute_entropy(samples, outcomes)
    
    # recalibrate based on entropy
    recalibrated = {}
    uniform = 1.0 / len(outcomes)
    entropy_weight = min(0.9, sigmoid(entropy["combined_entropy"] * 8 - 1))
    
    for outcome in outcomes:
        raw = mean_probs[outcome]
        recalibrated[outcome] = (1 - entropy_weight) * raw + entropy_weight * uniform
    
    # normalize recalibrated
    total = sum(recalibrated.values())
    for outcome in outcomes:
        recalibrated[outcome] = round(recalibrated[outcome] / total, 4)
    
    # log entropy for inspection
    print(f"  Event: {event['event_ticker']}")
    print(f"  Entropy: {entropy}")
    print(f"  Entropy weight applied: {round(entropy_weight, 3)}")
    print(f"  Raw mean probs: { {o: round(mean_probs[o], 3) for o in outcomes[:3]} }...")
    print(f"  Recalibrated:   { {o: recalibrated[o] for o in outcomes[:3]} }...")
    
    return {
        "probabilities": [
            {"market": o, "probability": recalibrated[o]} 
            for o in outcomes
        ]
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