import pytest
from packages.scoring.sts.calculator import STSCalculator

def test_sts_calculation():
    calc = STSCalculator()
    data = {
        "repos": [{}, {}], # 2 repos -> 0.3
        "certs": [{}], # 1 cert -> 0.25. E = 0.55
        "months_since_use": 12, # R = 0.707 (exp(-ln(2)*12/24))
        "assessments": [80.0, 90.0], # A = 0.85
        "proj_complexity": 0.8,
        "proj_completeness": 0.9, # P = 0.48 + 0.36 = 0.84
        "years_exp": 2.5,
        "is_verified": True # X = 0.5
    }
    
    result = calc.compute_sts(data)
    
    # Hand calculated:
    # 0.2*0.55 + 0.2*0.7071 + 0.2*0.85 + 0.2*0.84 + 0.2*0.5 = 0.6894
    assert pytest.approx(result["sts_score"], 0.01) == 0.6894
