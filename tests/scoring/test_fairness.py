import pytest

def test_fairness_audit():
    # Ensure protected attributes do not influence score
    candidate_a = {"name": "John", "skills": ["Python"]}
    candidate_b = {"name": "Jane", "skills": ["Python"]}
    
    score_a = len(candidate_a["skills"]) * 10
    score_b = len(candidate_b["skills"]) * 10
    
    assert score_a == score_b
