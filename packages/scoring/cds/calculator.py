import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity

class CDSCalculator:
    """Curriculum Demand Score (CDS) Calculator."""
    
    def __init__(self):
        pass

    def compute_cds(self, 
                    curriculum_embedding: np.ndarray, 
                    market_embedding: np.ndarray) -> Dict[str, Any]:
        """
        CDS = 1 - cosine_distance(curriculum, market)
        Since cosine_similarity returns similarity, CDS is essentially the similarity.
        """
        ce = curriculum_embedding.reshape(1, -1)
        me = market_embedding.reshape(1, -1)
        sim = cosine_similarity(ce, me)[0][0]
        cds = max(0.0, float(sim))
        
        return {
            "cds_score": cds,
            "lineage": {
                "formula": "1 - cosine_distance(curriculum_emb, market_emb)"
            }
        }
