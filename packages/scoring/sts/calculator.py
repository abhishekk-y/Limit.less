import math
import numpy as np
from typing import Dict, Any, List

class STSCalculator:
    """
    Skill Trust Score (STS) Calculator.
    STS = w_e*E + w_r*R + w_a*A + w_p*P + w_x*X
    Computed purely using deterministic algorithms.
    """
    
    def __init__(self, config: Dict[str, float] = None):
        self.weights = config or {
            "w_e": 0.2, # Evidence quality
            "w_r": 0.2, # Recency
            "w_a": 0.2, # Assessment
            "w_p": 0.2, # Project depth
            "w_x": 0.2  # Professional use
        }

    def _evidence_score(self, repos: List[Dict], certs: List[Dict]) -> float:
        score = min(1.0, (len(repos) * 0.15) + (len(certs) * 0.25))
        return score

    def _recency_decay(self, months_since_use: int, half_life_months: int = 24) -> float:
        """Exponential decay based on months since last use."""
        return math.exp(-math.log(2) * months_since_use / half_life_months)

    def _assessment_score(self, scores: List[float]) -> float:
        if not scores: return 0.0
        return np.mean(scores) / 100.0 if max(scores) > 1.0 else np.mean(scores)

    def _project_depth_score(self, complexity: float, completeness: float) -> float:
        return (complexity * 0.6) + (completeness * 0.4)

    def _professional_use_score(self, years_exp: float, verified: bool) -> float:
        base = min(1.0, years_exp / 5.0)
        return base * 1.0 if verified else base * 0.6

    def compute_sts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute total STS score.
        """
        E = self._evidence_score(data.get("repos", []), data.get("certs", []))
        R = self._recency_decay(data.get("months_since_use", 12))
        A = self._assessment_score(data.get("assessments", []))
        P = self._project_depth_score(data.get("proj_complexity", 0.0), data.get("proj_completeness", 0.0))
        X = self._professional_use_score(data.get("years_exp", 0.0), data.get("is_verified", False))
        
        sts_val = (
            self.weights["w_e"] * E +
            self.weights["w_r"] * R +
            self.weights["w_a"] * A +
            self.weights["w_p"] * P +
            self.weights["w_x"] * X
        )
        
        return {
            "sts_score": min(1.0, sts_val),
            "components": {"E": E, "R": R, "A": A, "P": P, "X": X},
            "lineage": {
                "source": "STSCalculator v1",
                "formula": "w_e*E + w_r*R + w_a*A + w_p*P + w_x*X"
            }
        }
