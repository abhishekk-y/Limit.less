import pytest

def test_workforce_analysis():
    workforce = [
        {"role": "Dev", "skills": ["Python"]},
        {"role": "Dev", "skills": ["Java"]}
    ]
    skill_counts = {}
    for w in workforce:
        for s in w["skills"]:
            skill_counts[s] = skill_counts.get(s, 0) + 1
            
    assert skill_counts["Python"] == 1
    assert skill_counts["Java"] == 1
