from typing import Optional, List, Dict
from pydantic import BaseModel
import json

class SkillNode(BaseModel):
    id: str
    canonical_name: str
    esco_id: Optional[str] = None
    onet_id: Optional[str] = None
    nco_code: Optional[str] = None
    nsqf_level: Optional[int] = None
    category: str
    aliases: List[str] = []
    version: int = 1

class SkillTaxonomy:
    def __init__(self):
        self.skills: Dict[str, SkillNode] = {}

    def load_from_json(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for item in data:
            skill = SkillNode(**item)
            self.skills[skill.id] = skill
