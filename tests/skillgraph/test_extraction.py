import pytest

def test_extraction_f1():
    # Dummy F1 calculation
    true_skills = {"Python", "Django"}
    predicted = {"Python", "Flask"}
    
    tp = len(true_skills.intersection(predicted))
    fp = len(predicted - true_skills)
    fn = len(true_skills - predicted)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    assert f1 == 0.5
