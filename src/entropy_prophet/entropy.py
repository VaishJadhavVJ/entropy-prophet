import math
from typing import List
from .models import ReasoningPath, CoTStep

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    """Calculates Shannon entropy for a list of probabilities."""
    if not probabilities:
        return 0.0
    # Normalize probabilities to sum to 1
    total = sum(probabilities)
    if total == 0:
        return 0.0
    normalized = [p / total for p in probabilities]
    return -sum(p * math.log2(p) for p in normalized if p > 0.0)

def calculate_path_entropy(path: ReasoningPath) -> float:
    """
    Calculates the average step entropy for a reasoning path.
    Also returns variance or maximum step entropy to understand transition spikes.
    """
    if not path.steps:
        return 0.0
    entropies = [step.entropy for step in path.steps]
    return sum(entropies) / len(entropies)

def calculate_ensemble_entropy(paths: List[ReasoningPath]) -> float:
    """
    Calculates ensemble/divergence entropy across multiple reasoning paths.
    Measures the standard deviation of final predicted probabilities as an indicator
    of path divergence (inter-path entropy).
    """
    if not paths:
        return 0.0
    probabilities = [p.final_prediction_probability for p in paths]
    mean_p = sum(probabilities) / len(probabilities)
    variance_p = sum((p - mean_p) ** 2 for p in probabilities) / len(probabilities)
    return math.sqrt(variance_p)
