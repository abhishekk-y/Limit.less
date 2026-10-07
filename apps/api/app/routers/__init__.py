from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .health import router as health_router
from .skills import router as skills_router
from .opportunities import router as opportunities_router
from .applications import router as applications_router
from .talent_twin import router as talent_twin_router
from .career_gps import router as career_gps_router
from .vault import router as vault_router
from .billing import router as billing_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(health_router, prefix="/system", tags=["System"])
api_router.include_router(skills_router, prefix="/skills", tags=["Skills"])
api_router.include_router(opportunities_router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_router.include_router(talent_twin_router, prefix="/talent-twin", tags=["Talent Twin"])
api_router.include_router(career_gps_router, prefix="/career-gps", tags=["Career GPS"])
api_router.include_router(vault_router, prefix="/vault", tags=["Vault"])
api_router.include_router(billing_router, prefix="/billing", tags=["Billing"])
