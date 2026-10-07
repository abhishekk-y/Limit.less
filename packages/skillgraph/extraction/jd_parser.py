from typing import Dict, Any, List
import re

class JDParser:
    """Parse job descriptions, extract title/skills/education/experience/salary."""
    
    def __init__(self, taxonomy: List[str]):
        self.taxonomy = set([s.lower() for s in taxonomy])

    def parse(self, text: str) -> Dict[str, Any]:
        """Extract elements from JD."""
        words = text.lower().replace(",", " ").replace("\n", " ").split()
        skills = list(set([w for w in words if w in self.taxonomy]))
        
        # Simple heuristics for salary (e.g. $100k, 100,000)
        salary_matches = re.findall(r'\$\d{2,3}[kK]|\$\d{2,3},\d{3}', text)
        
        return {
            "title": "Extracted Title", # Placeholder for actual extraction logic
            "skills": skills,
            "education": [],
            "experience": [],
            "salary_range": salary_matches
        }
