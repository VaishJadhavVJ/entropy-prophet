import pytest
import numpy as np
from entropy_prophet.chain_of_thought import (
    calculate_token_entropy,
    parse_chain_of_thought_steps,
    analyze_cot_completion
)
from entropy_prophet.prophet_client import ProphetArenaClient, MarketLiquidity
from entropy_prophet.calibrator import ProphetCalibrator

def test_parse_steps():
    text = "Step 1: First step\nStep 2: Second step\nStep 3: Third step"
    steps = parse_chain_of_thought_steps(text)
    assert len(steps) == 3
    assert steps[0] == "First step"
    assert steps[1] == "Second step"

    # Number list representation
    text_numbered = "1. Point one\n2. Point two"
    steps_num = parse_chain_of_thought_steps(text_numbered)
    assert len(steps_num) == 2
    assert steps_num[0] == "Point one"

def test_calculate_entropy():
    # Equal distribution logprobs (p = 0.5, 0.5)
    logprobs = [np.log(0.5), np.log(0.5)]
    # - (0.5 * log2(0.5) + 0.5 * log2(0.5)) = - (-0.5 - 0.5) = 1.0 bits
    entropy = calculate_token_entropy(logprobs)
    assert abs(entropy - 1.0) < 1e-5

    # Certain distribution (p = 1.0)
    logprobs_certain = [np.log(1.0)]
    entropy_certain = calculate_token_entropy(logprobs_certain)
    assert abs(entropy_certain - 0.0) < 1e-5

def test_analyze_cot_completion():
    completion = """
    Step 1: Analyzing the situation. High level of hedging here. Maybe, perhaps.
    Step 2: Looking at further details. It is unlikely we cut.
    
    Probability: 60% chance
    """
    analysis = analyze_cot_completion(completion)
    assert len(analysis.steps) == 2
    assert analysis.final_raw_probability == 0.60
    assert analysis.mean_entropy > 0.0

def test_market_liquidity_score():
    high_liq = MarketLiquidity(
        volume=100000.0,
        open_interest=50000.0,
        bid_ask_spread=0.01,
        depth_bids=5000.0,
        depth_asks=5000.0
    )
    low_liq = MarketLiquidity(
        volume=100.0,
        open_interest=50.0,
        bid_ask_spread=0.18,
        depth_bids=50.0,
        depth_asks=50.0
    )
    assert high_liq.liquidity_score > low_liq.liquidity_score

def test_calibrator():
    client = ProphetArenaClient()
    market = client.get_market("fed-rate-cut-sep") # yes_price = 0.68, liquidity is high
    
    # Analyze CoT with high explicit uncertainty (hedging) -> high pseudo-entropy
    completion_uncertain = """
    Step 1: Perhaps, maybe, depends on volatile signals.
    Step 2: Unlikely but possibly another factor.
    Probability: 95%
    """
    cot_uncertain = analyze_cot_completion(completion_uncertain)
    
    calibrator = ProphetCalibrator()
    result = calibrator.recalibrate(cot_uncertain, market)
    
    # With high reasoning-entropy and high market liquidity, 
    # the 95% forecast should be heavily pulled down towards the market price (68%)
    assert result.recalibrated_forecast < 0.95
    assert result.recalibrated_forecast > 0.60
