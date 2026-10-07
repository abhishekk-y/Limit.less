import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity

class MatchCalculator:
    """Computes Match Score between a candidate and an opportunity."""
    
    def __init__(self):
        pass

    def compute_match(
        self, 
        candidate_skills: Dict[str, float], 
        required_skills: List[str], 
        optional_skills: List[str],
        candidate_embedding: np.ndarray,
        opportunity_embedding: np.ndarray
    ) -> Dict[str, Any]:
        """
        Compute total match score based on STS-weighted coverage and embedding similarity.
        candidate_skills: Dict mapping skill_id to its STS score (0 to 1).
        """
        # 1. Critical Skill Coverage
        crit_score = 0.0
        if required_skills:
            crit_sum = sum(candidate_skills.get(s, 0.0) for s in required_skills)
            crit_score = crit_sum / len(required_skills)
            
        # 2. Optional Skill Coverage
        opt_score = 0.0
        if optional_skills:
            opt_sum = sum(candidate_skills.get(s, 0.0) for s in optional_skills)
            opt_score = opt_sum / len(optional_skills)

        # 3. Embedding Similarity
        sim_score = 0.0
        if candidate_embedding is not None and opportunity_embedding is not None:
            # Reshape for sklearn
            ce = candidate_embedding.reshape(1, -1)
            oe = opportunity_embedding.reshape(1, -1)
            sim = cosine_similarity(ce, oe)[0][0]
            sim_score = max(0.0, float(sim))

        # Weighting
        final_score = (crit_score * 0.6) + (opt_score * 0.2) + (sim_score * 0.2)
        
        return {
            "match_score": min(1.0, final_score),
            "breakdown": {
                "critical_coverage": crit_score,
                "optional_coverage": opt_score,
                "semantic_similarity": sim_score
            },
            "lineage": {
                "formula": "0.6*crit + 0.2*opt + 0.2*sim"
            }
        }

    def evaluate(self, y_true: List[List[str]], y_pred: List[List[str]], k: int = 5) -> Dict[str, float]:
        """Evaluate recommendations using Precision@K, Recall@K, NDCG@K."""
        precisions = []
        recalls = []
        for true_items, pred_items in zip(y_true, y_pred):
            pred_k = pred_items[:k]
            hits = len(set(true_items).intersection(set(pred_k)))
            precisions.append(hits / k)
            recalls.append(hits / len(true_items) if true_items else 0.0)
            
        return {
            "precision_at_k": np.mean(precisions),
            "recall_at_k": np.mean(recalls)
            # NDCG omitted for brevity in demo
        }
