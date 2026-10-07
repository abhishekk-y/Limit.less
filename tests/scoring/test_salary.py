import pytest

def test_salary_prediction():
    # Base 12LPA for AI Engineer in BLR at 2 yrs.
    base_salary = 12.0
    location_multiplier = 1.1 # BLR
    exp_multiplier = 1.0 # 2 yrs
    
    expected = base_salary * location_multiplier * exp_multiplier
    assert expected == pytest.approx(13.2, abs=0.01)
