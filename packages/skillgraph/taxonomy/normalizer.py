from typing import List, Tuple
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
from .loader import SkillTaxonomy

class NormalizationResult(BaseModel):
    skill_id: str
    canonical_name: str
    confidence: float
    is_exact: bool

class NormalizationMetrics(BaseModel):
    top_1_accuracy: float
    top_5_accuracy: float

class SkillNormalizer:
    def __init__(self, taxonomy: SkillTaxonomy, model_name: str = 'all-MiniLM-L6-v2'):
        self.taxonomy = taxonomy
        self.model = SentenceTransformer(model_name)
        self.alias_map = {}
        for skill in self.taxonomy.skills.values():
            self.alias_map[skill.canonical_name.lower()] = skill.id
            for alias in skill.aliases:
                self.alias_map[alias.lower()] = skill.id
                
        self.skill_ids = list(self.taxonomy.skills.keys())
        self.skill_names = [self.taxonomy.skills[sid].canonical_name for sid in self.skill_ids]
        self.embeddings = self.model.encode(self.skill_names)

    def normalize(self, raw_skill: str) -> NormalizationResult:
        res = self.normalize_top_k(raw_skill, k=1)
        return res[0] if res else None

    def normalize_top_k(self, raw_skill: str, k: int = 5) -> List[NormalizationResult]:
        raw_lower = raw_skill.lower()
        if raw_lower in self.alias_map:
            sid = self.alias_map[raw_lower]
            return [NormalizationResult(skill_id=sid, canonical_name=self.taxonomy.skills[sid].canonical_name, confidence=1.0, is_exact=True)]
        
        emb = self.model.encode([raw_skill])[0]
        similarities = np.dot(self.embeddings, emb) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(emb))
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] >= 0.7:
                sid = self.skill_ids[idx]
                results.append(NormalizationResult(skill_id=sid, canonical_name=self.taxonomy.skills[sid].canonical_name, confidence=float(similarities[idx]), is_exact=False))
        return results
        
    def evaluate(self, labeled_set: List[Tuple[str, str]]) -> NormalizationMetrics:
        top_1_correct = 0
        top_5_correct = 0
        for raw, expected_id in labeled_set:
            res = self.normalize_top_k(raw, k=5)
            if not res: continue
            if res[0].skill_id == expected_id: top_1_correct += 1
            if any(r.skill_id == expected_id for r in res): top_5_correct += 1
        n = len(labeled_set) if labeled_set else 1
        return NormalizationMetrics(top_1_accuracy=top_1_correct/n, top_5_accuracy=top_5_correct/n)
