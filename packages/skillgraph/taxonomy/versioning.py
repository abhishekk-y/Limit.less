from typing import Dict, List, Optional
import json
import os

class TaxonomyVersioning:
    """Tracks version changes, maps old IDs to new, ensures score comparability."""
    
    def __init__(self, history_file: str = "taxonomy_history.json"):
        self.history_file = history_file
        self.version_map: Dict[str, Dict[str, str]] = {} # version -> {old_id: new_id}
        self.current_version = "1.0.0"
        
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                data = json.load(f)
                self.version_map = data.get("version_map", {})
                self.current_version = data.get("current_version", "1.0.0")

    def migrate_id(self, skill_id: str, from_version: str, to_version: str) -> str:
        """Migrate a skill ID from an older version to a newer version."""
        current_id = skill_id
        # Simplified migration logic for exact version jumps
        if from_version in self.version_map:
            current_id = self.version_map[from_version].get(skill_id, skill_id)
        return current_id

    def get_comparability_score(self, old_score: float, skill_id: str, from_version: str) -> float:
        """Adjusts score based on taxonomy changes. Deterministic adjustment."""
        # E.g., if a skill was split, maybe confidence drops by 10%
        return old_score * 0.9 if self.migrate_id(skill_id, from_version, self.current_version) != skill_id else old_score
