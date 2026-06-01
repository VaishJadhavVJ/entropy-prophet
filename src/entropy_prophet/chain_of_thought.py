# Chain-of-Thought reasoning-step entropy extractor for LLM completions.
import re
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StepAnalysis(BaseModel):
    step_num: int
    text: str
    tokens: Optional[List[str]] = None
    logprobs: Optional[List[float]] = None
    entropy: Optional[float] = None
    confidence_signals: Dict[str, Any] = Field(default_factory=dict)

class CoTAnalysis(BaseModel):
    raw_completion: str
    steps: List[StepAnalysis]
    mean_entropy: float = 0.0
    variance_entropy: float = 0.0
    final_raw_probability: float

def parse_chain_of_thought_steps(completion: str) -> List[str]:
    """
    Parses a completion containing Chain of Thought reasoning into separate steps.
    Common formats:
    - Step 1:, Step 2:
    - 1., 2. at start of line
    - Paragraph splits (\n\n) if explicitly formatted.
    """
    # Try step-based patterns
    pattern = r'(?:^|\n)\s*(?:Step\s+\d+[:\.]*|\d+[\.\)]\s+)'
    splits = re.split(pattern, completion)
    
    # Clean and filter empty steps
    steps = [s.strip() for s in splits if s.strip()]
    if len(steps) <= 1:
        # Fall back to double newlines if no explicit list structure is parsed
        steps = [s.strip() for s in completion.split('\n\n') if s.strip()]
        
    return steps

def calculate_token_entropy(logprobs: List[float]) -> float:
    """
    Calculates Shannon entropy in bits from a list of log probabilities.
    Assumes logprobs are base-e (natural log).
    """
    if not logprobs:
        return 0.0
    
    # Convert logprobs to probabilities
    probs = np.exp(logprobs)
    
    # Normalize if necessary
    total_p = np.sum(probs)
    if total_p > 0:
        probs = probs / total_p
        
    # Calculate -sum(p * log2(p))
    entropy = -np.sum(probs * np.log2(probs + 1e-12))
    return float(entropy)

def analyze_cot_completion(
    completion: str,
    step_logprobs: Optional[List[List[float]]] = None,
    default_prob: float = 0.5
) -> CoTAnalysis:
    """
    Parses steps from a completed CoT output and matches them with their log probabilities
    to compute step-by-step and overall entropy.
    """
    raw_steps = parse_chain_of_thought_steps(completion)
    steps_analysis = []
    entropies = []
    
    for i, step_text in enumerate(raw_steps):
        # Determine signals of hedging/confidence in reasoning
        hedging_words = ['maybe', 'perhaps', 'unlikely', 'likely', 'possibly', 'uncertain', 'volatile', 'depends']
        signals = {
            "length": len(step_text),
            "hedging_count": sum(1 for w in hedging_words if w in step_text.lower())
        }
        
        # Calculate step entropy if logprobs are provided
        step_entropy = 0.0
        if step_logprobs and i < len(step_logprobs):
            step_entropy = calculate_token_entropy(step_logprobs[i])
            entropies.append(step_entropy)
        else:
            # Pseudo-entropy estimation based on hedging/verbal uncertainty when no API logprobs exist
            # Scale from 0.1 to 1.5 based on length & hedging words
            pseudo_entropy = min(1.5, 0.1 + (signals["hedging_count"] * 0.4) + (min(signals["length"], 500) / 1000.0))
            step_entropy = pseudo_entropy
            entropies.append(pseudo_entropy)
            
        steps_analysis.append(StepAnalysis(
            step_num=i + 1,
            text=step_text,
            entropy=step_entropy,
            confidence_signals=signals
        ))
        
    # Extract raw final probability from the text (e.g. "Probability: 75%", "75% chance")
    # Search for percent signs or fractional representations
    prob_match = re.search(r'(?:probability|chance|likelihood|forecast)[\s:]*(\d+)%', completion, re.IGNORECASE)
    if not prob_match:
        prob_match = re.search(r'(\d+)%\s*(?:probability|chance|likelihood|forecast)?', completion, re.IGNORECASE)
        
    final_prob = default_prob
    if prob_match:
        final_prob = float(prob_match.group(1)) / 100.0
        
    mean_ent = float(np.mean(entropies)) if entropies else 0.0
    var_ent = float(np.var(entropies)) if entropies else 0.0
    
    return CoTAnalysis(
        raw_completion=completion,
        steps=steps_analysis,
        mean_entropy=mean_ent,
        variance_entropy=var_ent,
        final_raw_probability=final_prob
    )
