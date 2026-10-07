from app.repositories.base import BaseRepository
from app.models.opportunity import Opportunity

class OpportunityRepository(BaseRepository[Opportunity]):
    def __init__(self):
        super().__init__(Opportunity)

opportunity_repo = OpportunityRepository()
