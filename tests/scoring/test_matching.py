import pytest
import numpy as np
from packages.scoring.matching.calculator import MatchCalculator

def test_match_score():
    calc = MatchCalculator()
    
    cand_skills = {"python": 0.8, "sql": 0.6, "git": 0.9}
    req_skills = ["python", "sql"]
    opt_skills = ["docker"]
    
    cand_emb = np.array([1.0, 0.0])
    opp_emb = np.array([1.0, 0.0]) # cos sim = 1.0
    
    result = calc.compute_match(cand_skills, req_skills, opt_skills, cand_emb, opp_emb)
    
    # crit_score = (0.8 + 0.6) / 2 = 0.7
    # opt_score = 0.0
    # sim_score = 1.0
    # final = 0.6*0.7 + 0.2*0.0 + 0.2*1.0 = 0.42 + 0.2 = 0.62
    
    assert pytest.approx(result["match_score"], 0.01) == 0.62
