from app.repositories.base import BaseRepository
from app.models.skill import Skill

class SkillRepository(BaseRepository[Skill]):
    def __init__(self):
        super().__init__(Skill)

skill_repo = SkillRepository()
