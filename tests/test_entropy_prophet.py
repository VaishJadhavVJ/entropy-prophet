import unittest
from entropy_prophet.models import MarketState, ReasoningPath, CoTStep
from entropy_prophet.entropy import calculate_shannon_entropy, calculate_path_entropy, calculate_ensemble_entropy
from entropy_prophet.recalibration import recalibrate_probability

class TestEntropyProphet(unittest.TestCase):

    def test_shannon_entropy(self):
        # Equal probabilities should have high entropy
        p = [0.5, 0.5]
        self.assertAlmostEqual(calculate_shannon_entropy(p), 1.0)
        
        # Certain outcome should have 0 entropy
        p2 = [1.0, 0.0]
        self.assertAlmostEqual(calculate_shannon_entropy(p2), 0.0)

    def test_recalibration_high_entropy_pulls_to_market(self):
        # LLM predicts 90%, but has highly divergent reasoning steps (high entropy)
        # Market price is 50%, with high liquidity ($1M)
        market = MarketState(
            event_id="test_evt",
            title="Test Event",
            yes_price=0.50,
            liquidity_usd=1000000.0,
            spread=0.01,
            volume_24h=10000.0
        )
        
        paths = [
            ReasoningPath(
                path_id="p1",
                steps=[CoTStep(step_number=1, content="...", entropy=0.8, confidence=0.9)],
                final_prediction_probability=0.90,
                raw_generation="..."
            ),
            ReasoningPath(
                path_id="p2",
                steps=[CoTStep(step_number=1, content="...", entropy=0.9, confidence=0.2)],
                final_prediction_probability=0.20, # high divergence
                raw_generation="..."
            )
        ]
        
        result = recalibrate_probability(paths, market)
        # Recalibrated should be between the LLM raw mean (0.55) and market price (0.50)
        # Since entropy is extremely high and market liquidity is high, it should pull towards 0.50
        self.assertTrue(0.50 <= result["recalibrated_probability"] <= 0.55)
        self.assertTrue(result["market_weight_applied"] > 0.1)

if __name__ == "__main__":
    unittest.main()
