import os
import json
import math
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from json_repair import repair_json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
)

N_SAMPLES = 3
KALSHI_FILES = [
    "kalshi_data/kalshi_cpi.json",
    "kalshi_data/kalshi_nba2.json",
    "kalshi_data/kalshi_nba.json",
    "kalshi_data/kalshi_fed.json",
    "kalshi_data/kalshi_tariffs.json"
]

def load_markets():
    markets = []
    for f in KALSHI_FILES:
        try:
            data = json.load(open(f))
            valid = [m for m in data.get("markets", [])
                     if not m["ticker"].startswith("KXMVE")
                     and m.get("result") in ["yes", "no"]
                     and m.get("title")]
            markets.extend(valid)
        except Exception as e:
            print(f"Failed to load {f}: {e}")
    return markets

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def call_glm(title, rules="", temperature=0.7):
    prompt = f"""You are an expert forecasting agent.

Event: {title}
Rules: {rules}

This is a binary YES/NO prediction market. Think step by step and assign a probability.

Return ONLY valid JSON, no markdown:
{{
  "reasoning_steps": [
    {{"step": "your reasoning", "confidence": 0.8}}
  ],
  "p_yes": 0.0
}}

p_yes must be between 0.01 and 0.99."""

    response = client.chat.completions.create(
        model="glm-5.1",
        messages=[
            {"role": "system", "content": "You are a precise forecasting agent. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=800
    )

    raw = response.choices[0].message.content
    if not raw or not raw.strip():
        raise ValueError("Empty response")

    clean = raw.strip()
    for fence in ["```json", "```JSON", "```"]:
        if clean.startswith(fence):
            clean = clean[len(fence):]
            break
    if clean.endswith("```"):
        clean = clean[:-3]

    start = clean.find("{")
    end = clean.rfind("}") + 1
    if start == -1:
        raise ValueError("No JSON found")

    parsed = json.loads(repair_json(clean[start:end]))
    p_yes = float(parsed.get("p_yes", 0.5))
    p_yes = max(0.01, min(0.99, p_yes))
    steps = parsed.get("reasoning_steps", [])
    return p_yes, steps

def compute_entropy(samples_data):
    probs = [s[0] for s in samples_data]
    mean = sum(probs) / len(probs)
    inter_variance = sum((p - mean)**2 for p in probs) / len(probs)

    all_conf = []
    for _, steps in samples_data:
        for step in steps:
            all_conf.append(step.get("confidence", 0.5))

    step_variance = 0
    if all_conf:
        mc = sum(all_conf) / len(all_conf)
        step_variance = sum((c - mc)**2 for c in all_conf) / len(all_conf)

    combined = (inter_variance + step_variance) / 2
    return {
        "inter_variance": round(inter_variance, 4),
        "step_variance": round(step_variance, 4),
        "combined": round(combined, 4),
        "mean_p_yes": round(mean, 4)
    }

def recalibrate(mean_p_yes, entropy):
    uniform = 0.5  # binary event
    weight = min(0.9, sigmoid(entropy["combined"] * 8 - 1))
    calibrated = (1 - weight) * mean_p_yes + weight * uniform
    return round(calibrated, 4), round(weight, 4)

def brier_score(predicted, actual):
    outcome = 1 if actual == "yes" else 0
    return (predicted - outcome) ** 2

def run_backtest(max_events=50):
    markets = load_markets()
    print(f"Loaded {len(markets)} valid markets")
    
    # sample max_events
    import random
    random.seed(42)
    sample = random.sample(markets, min(max_events, len(markets)))
    
    results = []
    
    for i, market in enumerate(sample):
        ticker = market["ticker"]
        title = market["title"]
        actual = market["result"]
        market_price = float(market.get("last_price_dollars", 0.5))
        
        print(f"\n[{i+1}/{len(sample)}] {ticker[:50]}")
        print(f"  Title: {title[:60]}")
        print(f"  Actual: {actual} | Market price: {market_price}")
        
        # run N samples
        samples_data = []
        for j in range(N_SAMPLES):
            try:
                p_yes, steps = call_glm(title, market.get("rules_primary", ""))
                samples_data.append((p_yes, steps))
                print(f"  Sample {j+1}: p_yes={p_yes}")
            except Exception as e:
                print(f"  Sample {j+1} failed: {e}")
            time.sleep(1)
        
        if not samples_data:
            print("  All samples failed, skipping")
            continue
        
        entropy = compute_entropy(samples_data)
        mean_p_yes = entropy["mean_p_yes"]
        calibrated_p_yes, weight = recalibrate(mean_p_yes, entropy)
        
        baseline_brier = brier_score(mean_p_yes, actual)
        calibrated_brier = brier_score(calibrated_p_yes, actual)
        market_brier = brier_score(market_price if market_price > 0 else 0.5, actual)
        
        result = {
            "ticker": ticker,
            "title": title,
            "actual": actual,
            "market_price": market_price,
            "baseline_p_yes": mean_p_yes,
            "calibrated_p_yes": calibrated_p_yes,
            "entropy": entropy["combined"],
            "entropy_weight": weight,
            "baseline_brier": round(baseline_brier, 4),
            "calibrated_brier": round(calibrated_brier, 4),
            "market_brier": round(market_brier, 4),
            "improvement": round(baseline_brier - calibrated_brier, 4)
        }
        results.append(result)
        print(f"  Entropy: {entropy['combined']} | Weight: {weight}")
        print(f"  Baseline Brier: {baseline_brier:.4f} | Calibrated: {calibrated_brier:.4f} | Market: {market_brier:.4f}")
        
        # save incrementally
        json.dump(results, open("backtest_results.json", "w"), indent=2)
    
    # summary
    if results:
        avg_baseline = sum(r["baseline_brier"] for r in results) / len(results)
        avg_calibrated = sum(r["calibrated_brier"] for r in results) / len(results)
        avg_market = sum(r["market_brier"] for r in results) / len(results)
        improved = sum(1 for r in results if r["improvement"] > 0)
        
        summary = {
            "n_events": len(results),
            "avg_baseline_brier": round(avg_baseline, 4),
            "avg_calibrated_brier": round(avg_calibrated, 4),
            "avg_market_brier": round(avg_market, 4),
            "improvement_rate": round(improved / len(results), 3),
            "avg_improvement": round(sum(r["improvement"] for r in results) / len(results), 4)
        }
        
        print("\n" + "="*50)
        print("BACKTEST SUMMARY")
        print("="*50)
        print(f"Events evaluated: {summary['n_events']}")
        print(f"Baseline Brier:   {summary['avg_baseline_brier']}")
        print(f"Calibrated Brier: {summary['avg_calibrated_brier']}")
        print(f"Market Brier:     {summary['avg_market_brier']}")
        print(f"Improved:         {improved}/{len(results)} ({summary['improvement_rate']*100:.1f}%)")
        
        json.dump({"summary": summary, "results": results}, 
                  open("backtest_results.json", "w"), indent=2)
        print("\nResults saved to backtest_results.json")
    
    return results

if __name__ == "__main__":
    run_backtest(max_events=50)