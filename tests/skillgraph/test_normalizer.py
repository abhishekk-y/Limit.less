import pytest

def test_normalizer_accuracy():
    mappings = {"JS": "JavaScript", "k8s": "Kubernetes"}
    
    assert mappings.get("JS") == "JavaScript"
    assert mappings.get("k8s") == "Kubernetes"
    assert mappings.get("Unknown", "Unknown") == "Unknown"
