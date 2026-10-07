from typing import Dict, List, Any

class SOECalculator:
    """Skill Opportunity Expectancy (SOE) Calculator."""
    
    def __init__(self):
        pass

    def compute_soe(self, 
                    current_match_score: float, 
                    projected_match_score: float, 
                    learning_hours: float,
                    learning_velocity: float = 1.0) -> Dict[str, Any]:
        """
        SOE = delta_opportunity / (learning_effort / velocity)
        """
        delta_opportunity = projected_match_score - current_match_score
        if delta_opportunity < 0:
            delta_opportunity = 0.0
            
        effective_effort = learning_hours / max(0.1, learning_velocity)
        
        soe = 0.0
        if effective_effort > 0:
            soe = delta_opportunity / effective_effort

        return {
            "soe_score": soe,
            "delta_opportunity": delta_opportunity,
            "effective_effort_hours": effective_effort,
            "lineage": {
                "formula": "delta_opportunity / (learning_hours / learning_velocity)"
            }
        }

    def optimizer_40_hour(self, skill_soes: Dict[str, Dict[str, float]]) -> List[str]:
        """
        Prerequisite-aware knapsack optimizer for a 40-hour learning budget.
        skill_soes: {skill_id: {"soe": float, "hours": float, "prereqs": [str]}}
        """
        # Simplified greedy approach for demo
        budget = 40.0
        selected = []
        
        # Sort by SOE descending
        sorted_skills = sorted(skill_soes.items(), key=lambda x: x[1]["soe"], reverse=True)
        
        for skill, data in sorted_skills:
            if budget >= data["hours"]:
                # Check prereqs
                prereqs_met = all(p in selected for p in data.get("prereqs", []))
                # For simplicity, if prereqs not met in selected, we skip (a real knapsack would handle this better)
                if not data.get("prereqs") or prereqs_met:
                    selected.append(skill)
                    budget -= data["hours"]
                    
        return selected
