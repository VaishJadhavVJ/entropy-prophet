# CLI Entrypoint for Entropy Prophet
import os
import argparse
import sys
from dotenv import load_dotenv

from .chain_of_thought import analyze_cot_completion
from .prophet_client import ProphetArenaClient
from .calibrator import ProphetCalibrator

def run_pipeline(market_id: str, sample_completion: str):
    """
    Runs a single calibration pipeline on a prediction market.
    """
    print(f"=== Starting Entropy-Prophet Pipeline for Market: {market_id} ===")
    
    # 1. Fetch market details
    client = ProphetArenaClient()
    market = client.get_market(market_id)
    print(f"Market Question: '{market.question}'")
    print(f"Market YES Price: {market.yes_price} | NO Price: {market.no_price}")
    print(f"Market Liquidity Score: {market.liquidity.liquidity_score:.4f}")
    
    # 2. Analyze Chain-of-Thought completion
    print("\nAnalyzing LLM completion...")
    cot_analysis = analyze_cot_completion(sample_completion)
    print(f"Detected reasoning steps: {len(cot_analysis.steps)}")
    print(f"Raw Forecast parsed: {cot_analysis.final_raw_probability * 100:.1f}%")
    print(f"Mean Step Entropy: {cot_analysis.mean_entropy:.4f}")
    
    # 3. Recalibrate
    calibrator = ProphetCalibrator()
    result = calibrator.recalibrate(cot_analysis, market)
    
    print("\n=== Calibration Results ===")
    print(f"Original Forecast:     {result.original_forecast * 100:.1f}%")
    print(f"Recalibrated Forecast: {result.recalibrated_forecast * 100:.1f}%")
    print(f"Market Price:          {result.market_price * 100:.1f}%")
    print(f"Market Weight Influence: {result.market_influence_weight * 100:.1f}%")
    print(f"Confidence Interval:   ({result.confidence_interval[0]*100:.1f}%, {result.confidence_interval[1]*100:.1f}%)")
    
    return result

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Entropy Prophet: CoT + Liquidity Recalibrator")
    parser.add_argument("--market-id", type=str, default="fed-rate-cut-sep", help="Prophet Arena market ID")
    args = parser.parse_args()
    
    # Mock LLM prediction with visible CoT
    sample_cot = """
    Step 1: Let's look at recent inflation data and jobs report. The PCE index remained moderate, but employment showed slightly slower job growth than projected. This increases the argument for rate reduction.
    Step 2: However, several FOMC members remain hawkish or neutral, voicing hesitation about cutting rates too prematurely before inflation is fully sustained under 2%. There's significant uncertainty here.
    Step 3: But overall economic trend indicates that holding rates high for too long poses a substantial recession risk. Therefore, a rate cut is more probable than not.
    
    Probability: 75% chance of a rate cut of 25bps or more in September.
    """
    
    run_pipeline(args.market_id, sample_cot)

if __name__ == "__main__":
    main()
