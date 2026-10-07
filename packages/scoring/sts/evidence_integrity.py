from typing import List, Dict

class EvidenceIntegrityChecker:
    """Detect forks, non-authored commits, duplicated project text."""
    
    def __init__(self):
        pass

    def check_github_repo(self, repo_data: Dict) -> Dict[str, bool]:
        """Basic check if a repo is a pure fork without original contributions."""
        is_fork = repo_data.get("is_fork", False)
        commits_by_user = repo_data.get("commits_by_user", 0)
        
        if is_fork and commits_by_user == 0:
            return {"valid": False, "reason": "Unmodified fork"}
        return {"valid": True, "reason": "Valid contributions"}

    def check_text_duplication(self, text1: str, text2: str) -> float:
        """Simple jaccard similarity for duplication detection."""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        if not set1 or not set2:
            return 0.0
        return len(set1.intersection(set2)) / len(set1.union(set2))
