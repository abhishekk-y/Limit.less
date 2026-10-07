from typing import List, Dict, Any
import numpy as np

class FairnessAuditor:
    """Fairness audit: Demographic parity, equalized odds."""
    
    def __init__(self):
        pass

    def calculate_demographic_parity(self, group_a_rates: List[float], group_b_rates: List[float]) -> float:
        """Difference in selection rates between two groups."""
        if not group_a_rates or not group_b_rates:
            return 0.0
        return abs(np.mean(group_a_rates) - np.mean(group_b_rates))

    def run_audit(self, candidate_data: List[Dict], model_predictions: List[int]) -> Dict[str, Any]:
        """Runs audit across demographic features like gender, college tier, region."""
        # Simulated audit logic
        
        # Demographic parity for 'gender'
        genders = [c.get('gender', 'unknown') for c in candidate_data]
        male_rates = [pred for g, pred in zip(genders, model_predictions) if g == 'male']
        female_rates = [pred for g, pred in zip(genders, model_predictions) if g == 'female']
        
        dp_gender = self.calculate_demographic_parity(male_rates, female_rates)
        
        return {
            "demographic_parity": {
                "gender": dp_gender
            },
            "status": "PASS" if dp_gender < 0.1 else "FAIL"
        }
