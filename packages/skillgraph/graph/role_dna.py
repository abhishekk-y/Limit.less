import numpy as np
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity

class RoleDNA:
    """Compute role vectors, normalize titles, role similarity."""
    
    def __init__(self, skill_embeddings: Dict[str, np.ndarray]):
        self.skill_embeddings = skill_embeddings

    def compute_role_vector(self, required_skills: List[str]) -> np.ndarray:
        """Role DNA is the average of its skill embeddings."""
        vectors = []
        for s in required_skills:
            if s in self.skill_embeddings:
                vectors.append(self.skill_embeddings[s])
                
        if not vectors:
            return np.zeros(384) # Assuming sentence-transformer dimension
            
        return np.mean(vectors, axis=0)

    def role_similarity(self, role_vec1: np.ndarray, role_vec2: np.ndarray) -> float:
        """Cosine similarity between two role DNAs."""
        v1 = role_vec1.reshape(1, -1)
        v2 = role_vec2.reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])
