import random
from typing import List, Dict, Any
from .models import MarketState, ReasoningPath, CoTStep

class ProphetArenaMock:
    """
    Mocking interface for prediction market events from Prophet Arena.
    Simulates retrieval of market events and generation of LLM Chain-of-Thought reasoning.
    """
    
    def __init__(self):
        # Let's seed with some interesting mock prediction market events
        self.events = {
            "event_001": MarketState(
                event_id="event_001",
                title="Will the Federal Reserve cut interest rates in their next meeting?",
                yes_price=0.68,
                liquidity_usd=120000.0,
                spread=0.01,
                volume_24h=15000.0
            ),
            "event_002": MarketState(
                event_id="event_002",
                title="Will SpaceX successfully launch Starship Flight 6 this month?",
                yes_price=0.82,
                liquidity_usd=45000.0,
                spread=0.03,
                volume_24h=8000.0
            ),
            "event_003": MarketState(
                event_id="event_003",
                title="Will a new major open-source LLM top the LMSYS Arena Leaderboard by next Friday?",
                yes_price=0.35,
                liquidity_usd=1500.0, # Low liquidity market
                spread=0.15,          # High spread
                volume_24h=200.0
            )
        }

    def get_market_state(self, event_id: str) -> MarketState:
        if event_id in self.events:
            return self.events[event_id]
        raise ValueError(f"Event ID {event_id} not found.")

    def list_events(self) -> List[MarketState]:
        return list(self.events.values())

    def simulate_llm_cot_generation(self, event_id: str, num_paths: int = 3) -> List[ReasoningPath]:
        """
        Simulates generation of multiple CoT reasoning paths with associated token-entropy values.
        For high-liquidity consensus events, we can simulate highly confident or highly uncertain paths.
        """
        event = self.get_market_state(event_id)
        paths = []
        
        # We'll simulate different behaviors for different events
        if event_id == "event_001": # Fed rate cut (moderate uncertainty)
            # Path 1: Yes, inflation cooling
            paths.append(ReasoningPath(
                path_id="path_001_1",
                steps=[
                    CoTStep(step_number=1, content="Analyze CPI inflation data which came in lower than expected.", entropy=0.15, confidence=0.8),
                    CoTStep(step_number=2, content="Consider unemployment uptick slightly signaling softening labor market.", entropy=0.25, confidence=0.75),
                    CoTStep(step_number=3, content="Conclude that Fed is highly likely to cut rate to maintain soft landing.", entropy=0.12, confidence=0.85)
                ],
                final_prediction_probability=0.85,
                raw_generation="CPI cooling + labor softening = Fed rate cut likely (85%)"
            ))
            # Path 2: No/Maybe, Fed remaining hawkish
            paths.append(ReasoningPath(
                path_id="path_001_2",
                steps=[
                    CoTStep(step_number=1, content="Examine hawkish minutes from the prior Fed meeting emphasizing high terminal rates.", entropy=0.35, confidence=0.6),
                    CoTStep(step_number=2, content="Retail sales and GDP numbers still strong, reducing pressure to cut.", entropy=0.45, confidence=0.55),
                    CoTStep(step_number=3, content="Conclude Fed will wait one more meeting to see stability.", entropy=0.50, confidence=0.40)
                ],
                final_prediction_probability=0.45,
                raw_generation="Fed minutes show hawkishness, economy strong = hold cut (45%)"
            ))
            # Path 3: Moderate Yes
            paths.append(ReasoningPath(
                path_id="path_001_3",
                steps=[
                    CoTStep(step_number=1, content="Look at core PCE data aligning with target.", entropy=0.20, confidence=0.7),
                    CoTStep(step_number=2, content="Global central banks are cutting rates, pressure on Fed.", entropy=0.30, confidence=0.65),
                    CoTStep(step_number=3, content="Conclude probability is favorable for rate cut.", entropy=0.22, confidence=0.70)
                ],
                final_prediction_probability=0.70,
                raw_generation="PCE aligning + global trends = cut probable (70%)"
            ))
            
        elif event_id == "event_002": # Starship (High prediction confidence)
            # All paths agree on high probability, very low intra/inter-entropy
            paths.append(ReasoningPath(
                path_id="path_002_1",
                steps=[
                    CoTStep(step_number=1, content="FAA license issued quickly, booster in position.", entropy=0.05, confidence=0.9),
                    CoTStep(step_number=2, content="Wet dress rehearsal completely successful.", entropy=0.08, confidence=0.92)
                ],
                final_prediction_probability=0.90,
                raw_generation="Booster ready, FAA license done = Launch success likely (90%)"
            ))
            paths.append(ReasoningPath(
                path_id="path_002_2",
                steps=[
                    CoTStep(step_number=1, content="Static fire tests completed with full duration.", entropy=0.06, confidence=0.95),
                    CoTStep(step_number=2, content="SpaceX maintaining aggressive launch schedule.", entropy=0.07, confidence=0.88)
                ],
                final_prediction_probability=0.88,
                raw_generation="Static fire done, rapid schedule = Launch success likely (88%)"
            ))
            
        else: # event_003 (High uncertainty, low liquidity, high divergence)
            # Highly divergent thoughts
            paths.append(ReasoningPath(
                path_id="path_003_1",
                steps=[
                    CoTStep(step_number=1, content="Rumors of GPT-5 or Anthropic Opus 3.5 release.", entropy=0.65, confidence=0.5),
                    CoTStep(step_number=2, content="If released, it will quickly rise to #1 position.", entropy=0.70, confidence=0.8)
                ],
                final_prediction_probability=0.75,
                raw_generation="Rumored release of top model = Yes (75%)"
            ))
            paths.append(ReasoningPath(
                path_id="path_003_2",
                steps=[
                    CoTStep(step_number=1, content="LMSYS ranking updates take time and require thousands of votes.", entropy=0.45, confidence=0.7),
                    CoTStep(step_number=2, content="It's already Friday, impossible to gather enough votes in 7 days.", entropy=0.55, confidence=0.8)
                ],
                final_prediction_probability=0.10,
                raw_generation="LMSYS voting lag prevents leaderboard rank in 7 days = No (10%)"
            ))
            
        return paths
