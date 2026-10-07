from typing import Dict, Any

class EligibilityEngine:
    """Rule-based eligibility engine for filtering candidates."""
    
    def __init__(self):
        self.relaxations = {
            "SC": 5,
            "ST": 5,
            "OBC": 3,
            "PwD": 10
        }

    def check_eligibility(self, candidate: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Returns PASS, CONDITIONAL, or MISSING."""
        status = "PASS"
        
        # Age check
        max_age = requirements.get("max_age", 99)
        cat = candidate.get("category", "General")
        relaxed_max_age = max_age + self.relaxations.get(cat, 0)
        
        if candidate.get("age", 0) > relaxed_max_age:
            return "MISSING"
            
        # Education check
        req_edu = requirements.get("education_level", 0)
        cand_edu = candidate.get("education_level", 0)
        if cand_edu < req_edu:
            return "MISSING"
            
        # CGPA check
        req_cgpa = requirements.get("min_cgpa", 0.0)
        cand_cgpa = candidate.get("cgpa", 0.0)
        if cand_cgpa < req_cgpa:
            status = "CONDITIONAL"  # E.g., might be conditional on final semester results
            
        return status
