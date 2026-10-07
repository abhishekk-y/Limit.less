import os
import json

base_dir = "d:/Skill Setu"

directories = [
    "packages/skillgraph/taxonomy",
    "packages/skillgraph/extraction",
    "packages/skillgraph/graph",
    "packages/scoring/sts",
    "packages/scoring/shi",
    "packages/scoring/matching",
    "packages/scoring/soe",
    "packages/scoring/cds",
    "packages/scoring/career_gps",
    "packages/scoring/salary",
    "packages/scoring/forecasting",
    "packages/scoring/eligibility",
    "packages/scoring/workforce",
    "packages/scoring/fairness",
    "data/seed",
    "tests/scoring",
    "tests/skillgraph",
]

for d in directories:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

def write_file(path, content):
    with open(os.path.join(base_dir, path), "w", encoding="utf-8") as f:
        f.write(content)

# SkillGraph pyproject.toml
write_file("packages/skillgraph/pyproject.toml", """[project]
name = "skillgraph"
version = "0.1.0"
dependencies = [
    "networkx",
    "sentence-transformers",
    "spacy",
    "pandas",
    "numpy",
    "pydantic>=2.0"
]
""")

# Scoring pyproject.toml
write_file("packages/scoring/pyproject.toml", """[project]
name = "scoring"
version = "0.1.0"
dependencies = [
    "numpy",
    "scipy",
    "scikit-learn",
    "xgboost",
    "pandas",
    "pydantic>=2.0",
    "shap"
]
""")

# packages/skillgraph/taxonomy/loader.py
write_file("packages/skillgraph/taxonomy/loader.py", """from typing import Optional, List, Dict
from pydantic import BaseModel
import json

class SkillNode(BaseModel):
    id: str
    canonical_name: str
    esco_id: Optional[str]
    onet_id: Optional[str]
    nco_code: Optional[str]
    nsqf_level: Optional[int]
    category: str
    aliases: List[str]
    version: int

class SkillTaxonomy:
    def __init__(self):
        self.skills: Dict[str, SkillNode] = {}

    def load_from_json(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            skill = SkillNode(**item)
            self.skills[skill.id] = skill
""")

# packages/skillgraph/taxonomy/normalizer.py
write_file("packages/skillgraph/taxonomy/normalizer.py", """from typing import List, Tuple
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np

class NormalizationResult(BaseModel):
    skill_id: str
    canonical_name: str
    confidence: float
    is_exact: bool

class NormalizationMetrics(BaseModel):
    top_1_accuracy: float
    top_5_accuracy: float

class SkillNormalizer:
    def __init__(self, taxonomy, model_name: str = 'all-MiniLM-L6-v2'):
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
        n = len(labeled_set)
        return NormalizationMetrics(top_1_accuracy=top_1_correct/n, top_5_accuracy=top_5_correct/n)
""")

# packages/skillgraph/graph/skill_graph.py
write_file("packages/skillgraph/graph/skill_graph.py", """import networkx as nx
import numpy as np

class SkillGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_skill(self, skill) -> None:
        self.graph.add_node(skill.id, **skill.dict())

    def add_relation(self, source: str, target: str, rel_type: str, weight: float) -> None:
        self.graph.add_edge(source, target, rel_type=rel_type, weight=weight)

    def get_prerequisites(self, skill_id: str) -> list[str]:
        return [u for u, v, d in self.graph.in_edges(skill_id, data=True) if d.get('rel_type') == 'prerequisite']

    def shortest_path(self, source: str, target: str) -> list[str]:
        try:
            return nx.shortest_path(self.graph, source=source, target=target, weight='weight')
        except nx.NetworkXNoPath:
            return []
""")

# packages/scoring/shi/calculator.py
write_file("packages/scoring/shi/calculator.py", """import numpy as np
from scipy.optimize import curve_fit
from pydantic import BaseModel
from typing import List, Tuple, Dict
from datetime import datetime

class SHIResult(BaseModel):
    k: float
    half_life_or_doubling: float
    r2: float
    confidence_interval: Tuple[float, float]
    trend_class: str

class SHICalculator:
    def __init__(self, min_data_points: int = 6):
        self.min_data_points = min_data_points

    def exponential_model(self, t, A, k):
        return A * np.exp(k * t)

    def compute(self, skill_id: str, monthly_counts: List[Tuple[datetime, int]]) -> SHIResult:
        if len(monthly_counts) < self.min_data_points:
            raise ValueError("Insufficient data points")
        
        times = np.array([(d[0] - monthly_counts[0][0]).days / 30.0 for d in monthly_counts])
        counts = np.array([d[1] for d in monthly_counts])
        
        try:
            popt, pcov = curve_fit(self.exponential_model, times, counts, p0=(counts[0], 0))
            A, k = popt
            err = np.sqrt(np.diag(pcov))
            ci = (k - 1.96*err[1], k + 1.96*err[1])
            
            residuals = counts - self.exponential_model(times, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((counts - np.mean(counts))**2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            half_life_or_doubling = np.log(2) / abs(k) if k != 0 else float('inf')
            trend = self.get_trend_class(k, r2)
            
            return SHIResult(k=k, half_life_or_doubling=half_life_or_doubling, r2=r2, confidence_interval=ci, trend_class=trend)
        except:
            return SHIResult(k=0, half_life_or_doubling=float('inf'), r2=0, confidence_interval=(0,0), trend_class='stable')

    def get_trend_class(self, k: float, r2: float) -> str:
        if r2 < 0.3: return 'stable'
        if k > 0.1: return 'exploding'
        if k > 0.02: return 'emerging'
        if k < -0.1: return 'decaying'
        if k < -0.02: return 'cooling'
        return 'stable'
""")

# Create some basic tests
write_file("tests/scoring/test_shi.py", """import unittest
from datetime import datetime, timedelta
from packages.scoring.shi.calculator import SHICalculator

class TestSHI(unittest.TestCase):
    def test_exponential_growth(self):
        calc = SHICalculator()
        now = datetime.now()
        data = [(now + timedelta(days=30*i), int(100 * (1.1 ** i))) for i in range(10)]
        res = calc.compute("skill_1", data)
        self.assertTrue(res.k > 0)
        self.assertEqual(res.trend_class, "exploding")
""")

# Seed data
write_file("data/seed/skills.json", json.dumps([
    {
        "id": "sk_python",
        "canonical_name": "Python Programming",
        "category": "Programming",
        "aliases": ["python", "python3"],
        "version": 1
    },
    {
        "id": "sk_ml",
        "canonical_name": "Machine Learning",
        "category": "AI/ML",
        "aliases": ["ml"],
        "version": 1
    }
], indent=2))

print("Scaffolding complete.")
