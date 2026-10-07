import pytest

def compute_cds(current_skills, target_skills, graph):
    """
    Dummy implementation of Career Distance Score (CDS).
    Calculates distance based on missing skills.
    """
    missing = set(target_skills) - set(current_skills)
    return len(missing) * 10

def test_compute_cds_exact_match():
    assert compute_cds(['Python', 'ML'], ['Python', 'ML'], {}) == 0

def test_compute_cds_missing_skills():
    assert compute_cds(['Python'], ['Python', 'ML', 'SQL'], {}) == 20

def test_compute_cds_extra_skills():
    assert compute_cds(['Python', 'ML', 'Docker'], ['Python', 'ML'], {}) == 0
