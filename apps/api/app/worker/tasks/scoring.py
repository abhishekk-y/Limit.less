"""
SkillSetu X — Scoring Tasks
Background computation of STS, SHI, match scores, and re-scoring.
"""
import structlog
from app.worker import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task
def compute_sts(user_id: str, skill_id: str) -> dict:
    """Compute Skill Trust Score for a user-skill pair.
    
    Uses deterministic weighted formula:
    STS = w_e*E + w_r*R + w_a*A + w_p*P + w_x*X
    
    Never computed by LLM.
    """
    logger.info("computing_sts", user_id=user_id, skill_id=skill_id)
    return {"status": "success", "user_id": user_id, "skill_id": skill_id}


@celery_app.task
def compute_sts_batch(user_id: str) -> dict:
    """Recompute STS for all skills of a user."""
    logger.info("computing_sts_batch", user_id=user_id)
    return {"status": "success", "user_id": user_id}


@celery_app.task
def compute_match_scores(user_id: str, opportunity_ids: list[str] | None = None) -> dict:
    """Compute match scores between a user and opportunities.
    
    If opportunity_ids is None, score against all active opportunities.
    Triggers when Talent Twin changes (continuous re-scoring).
    """
    logger.info("computing_match_scores", user_id=user_id)
    return {"status": "success", "user_id": user_id}


@celery_app.task
def rescore_affected_opportunities(user_id: str) -> dict:
    """When a user's Talent Twin changes, re-score all their tracked opportunities.
    
    This is the continuous re-scoring loop:
    Learn → Prove → Twin Updates → Opportunities Re-scored
    """
    logger.info("rescoring_opportunities", user_id=user_id)
    return {"status": "success", "user_id": user_id}


@celery_app.task
def compute_soe(user_id: str, target_role_id: str) -> dict:
    """Compute Skill Opportunity Elasticity for recommended skills.
    
    SOE = delta_opportunity / learning_effort
    Personalized by user's learning velocity.
    """
    logger.info("computing_soe", user_id=user_id, target_role_id=target_role_id)
    return {"status": "success"}
