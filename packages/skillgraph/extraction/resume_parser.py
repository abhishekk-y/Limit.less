import re
from typing import Dict, Any, List

class ExtractedProfile:
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "")
        self.email = data.get("email", "")
        self.skills = data.get("skills", [])
        self.projects = data.get("projects", [])
        self.education = data.get("education", [])
        self.experience = data.get("experience", [])

    def evaluate(self, truth: 'ExtractedProfile') -> Dict[str, float]:
        """Precision, recall, F1 for skills extraction."""
        true_skills = set([s.lower() for s in truth.skills])
        pred_skills = set([s.lower() for s in self.skills])
        
        if not pred_skills and not true_skills:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
        if not pred_skills or not true_skills:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
            
        tp = len(true_skills.intersection(pred_skills))
        precision = tp / len(pred_skills)
        recall = tp / len(true_skills)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {"precision": precision, "recall": recall, "f1": f1}

class ResumeParser:
    """Parses PDF/DOCX/text resumes."""
    
    def __init__(self, taxonomy: List[str]):
        self.taxonomy = set([s.lower() for s in taxonomy])
        self.email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        
    def parse(self, text: str) -> ExtractedProfile:
        """Regex + keyword matching."""
        emails = self.email_regex.findall(text)
        email = emails[0] if emails else ""
        
        words = text.lower().replace(",", " ").replace("\n", " ").split()
        skills = list(set([w for w in words if w in self.taxonomy]))
        
        return ExtractedProfile({
            "name": "Extracted Name",
            "email": email,
            "skills": skills,
            "projects": [],
            "education": [],
            "experience": []
        })
