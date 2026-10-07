import pytest

def test_career_gps_path():
    # Dummy test for career GPS graph path
    path = ["Python", "ML", "Deep Learning"]
    assert len(path) == 3
    assert path[0] == "Python"
    assert path[-1] == "Deep Learning"
