import sys
import os
import json
from entropy_prophet import ProphetArenaMock, recalibrate_probability

def main():
    print("=" * 60)
    print("        ENTROPY-PROPHET PROOF OF CONCEPT DEMO")
    print("=" * 60)
    print("Goal: Recalibrate LLM Forecast Probabilities on Prediction")
    print("      Markets using reasoning-step (CoT) entropy & liquidity.")
    print("-" * 60)

    # Initialize mock prophet arena
    arena = ProphetArenaMock()
    events = arena.list_events()

    for event in events:
        print(f"\n--- Event: {event.title} ({event.event_id}) ---")
        print(f"  Market Price (YES): {event.yes_price:.2f}")
        print(f"  Liquidity: ${event.liquidity_usd:,.2f} | Spread: {event.spread:.2%}")
        
        # Simulate CoT paths
        paths = arena.simulate_llm_cot_generation(event.event_id)
        print(f"  Simulated {len(paths)} Chain-of-Thought Paths:")
        for path in paths:
            avg_step_ent = sum(step.entropy for step in path.steps) / len(path.steps)
            print(f"    * Path {path.path_id}: predicted={path.final_prediction_probability:.2%}, avg step entropy={avg_step_ent:.4f}")
        
        # Run calibration
        result = recalibrate_probability(paths, event)
        print("\n  Recalibration Results:")
        print(f"    * LLM Raw Mean:         {result['mean_raw_probability']:.2%}")
        print(f"    * Prophet Arena Price: {result['market_price']:.2%}")
        print(f"    * Recalibrated Prob:    {result['recalibrated_probability']:.2%}")
        print(f"    * Intra-Path Entropy:   {result['intra_path_entropy']:.4f}")
        print(f"    * Inter-Path Entropy:   {result['inter_path_entropy']:.4f}")
        print(f"    * Market Weight Applied:{result['market_weight_applied']:.2%}")
        
        # Interpretation of calibration
        diff = result['recalibrated_probability'] - result['mean_raw_probability']
        if abs(diff) < 0.02:
            interpretation = "LLM predictions are robust, minimal recalibration needed."
        elif diff > 0:
            interpretation = f"Recalibration pulled LLM prediction UPWARDS (+{diff:.2%}) towards market consensus."
        else:
            interpretation = f"Recalibration pulled LLM prediction DOWNWARDS ({diff:.2%}) towards market consensus due to reasoning uncertainty."
        
        print(f"    * Interpretation:       {interpretation}")
        print("-" * 60)

if __name__ == "__main__":
    main()
