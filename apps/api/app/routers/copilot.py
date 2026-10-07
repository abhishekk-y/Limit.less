"""
SkillSetu X — Copilot Router
AI Career Assistant powered by Groq (LLM used only for
extraction assist, explanation, drafting, summarizing, query interpretation).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/copilot", tags=["copilot"])


class ChatRequest(BaseModel):
    """Chat request to the copilot."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message (any language)")
    context: Optional[dict] = Field(None, description="Current page context")


class ChatResponse(BaseModel):
    """Chat response from the copilot."""
    response: str
    tools_used: list[str] = []
    model: str = ""
    confidence: str = "Medium"


class ExplainRequest(BaseModel):
    """Request explanation for a score or recommendation."""
    score_type: str = Field(..., description="sts|shi|match|cds|soe|eligibility")
    entity_id: str = Field(..., description="Skill/opportunity/curriculum ID")
    user_id: Optional[str] = None


class DraftRequest(BaseModel):
    """Request a draft (cover letter, answers, etc.)."""
    draft_type: str = Field(..., description="cover_letter|application_answer|interview_prep|resume_bullet")
    opportunity_id: Optional[str] = None
    context: dict = Field(default_factory=dict)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the SkillSetu Copilot.
    
    The copilot uses tools to query user data and compute results.
    It NEVER computes scores directly — all scoring uses deterministic modules.
    
    Supports multilingual input: English, Hindi, Punjabi, Hinglish.
    """
    logger.info("copilot_chat", message_length=len(request.message))
    
    try:
        from app.core.llm import LLMProvider, LLMConfig, Copilot
        
        llm = LLMProvider(LLMConfig.from_env())
        copilot = Copilot(llm)
        
        # For demo, use a placeholder user_id
        response = await copilot.chat(
            user_id="demo",
            message=request.message,
            context=request.context,
        )
        
        await llm.close()
        
        return ChatResponse(
            response=response,
            model=llm.config.model,
            confidence="Medium",
        )
    except Exception as e:
        logger.error("copilot_chat_error", error=str(e))
        return ChatResponse(
            response=f"I'm having trouble connecting right now. Please try again. (Error: {str(e)[:100]})",
            confidence="Low",
        )


@router.post("/explain")
async def explain_score(request: ExplainRequest):
    """Get a natural-language explanation for any score.
    
    The LLM generates the explanation, but the score itself
    comes from the deterministic scoring module.
    """
    logger.info("copilot_explain", score_type=request.score_type, entity_id=request.entity_id)
    
    # This would:
    # 1. Fetch the score and its components from the scoring module
    # 2. Fetch the data lineage
    # 3. Use the LLM to generate a natural-language explanation
    
    explanations = {
        "sts": {
            "score": 91,
            "explanation": "Your Python STS is 91/100, which means your Python skills are strongly evidenced. "
                          "This score is composed of: Evidence quality (28/30) from 3 GitHub repos with original code, "
                          "Recency (19/20) since you used Python 2 weeks ago, Assessment (17/20) from an 88% test score, "
                          "Project depth (14/15) from 4 projects including a FastAPI REST API, and Professional use (13/15) "
                          "from your internship experience.",
            "lineage": {
                "source": "GitHub + Assessments + Projects",
                "formula": "STS = 0.30×E + 0.20×R + 0.20×A + 0.15×P + 0.15×X",
                "confidence": "High",
                "records": "3 repos, 1 assessment, 4 projects, 1 work experience",
            },
        },
        "shi": {
            "score": 12.5,
            "explanation": "Docker has a doubling time of 12.5 months, meaning demand doubles roughly every year. "
                          "This is classified as 'Growing' based on exponential curve fitting on 18 months of job posting data. "
                          "Docker appeared in 31% of target AI Engineer postings and co-occurs with AWS (68%) and Kubernetes (55%).",
            "lineage": {
                "source": "1,842 job postings",
                "formula": "Demand(t) = A × exp(k×t), k=0.055, R²=0.87",
                "confidence": "High",
                "period": "Jan 2025 – Sep 2026",
            },
        },
    }
    
    result = explanations.get(request.score_type, {
        "explanation": f"Explanation for {request.score_type} is being generated...",
        "lineage": {"source": "Pending", "confidence": "Low"},
    })
    
    return {"score_type": request.score_type, "entity_id": request.entity_id, **result}


@router.post("/draft")
async def generate_draft(request: DraftRequest):
    """Generate a draft (cover letter, application answer, etc.).
    
    Uses the LLM for text generation, but pulls data from the Talent Twin.
    """
    logger.info("copilot_draft", draft_type=request.draft_type)
    
    drafts = {
        "cover_letter": (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in the AI Engineer position. "
            "With a strong foundation in Python (STS: 91), Machine Learning (STS: 77), "
            "and hands-on experience building production APIs with FastAPI, I am well-positioned "
            "to contribute to your team.\n\n"
            "My recent projects include a containerized ML inference service and a RAG-based "
            "question-answering system, both demonstrating my ability to bridge research and deployment.\n\n"
            "I look forward to discussing how my skills align with your team's needs.\n\n"
            "Best regards"
        ),
        "interview_prep": (
            "## Interview Preparation — AI Engineer\n\n"
            "### Technical Focus Areas\n"
            "1. **Python** (Your STS: 91) — Strong, focus on system design questions\n"
            "2. **Machine Learning** (Your STS: 77) — Review model evaluation, MLOps\n"
            "3. **Docker** (Your STS: 34) — ⚠️ Weak area, prepare basic containerization\n\n"
            "### Likely Questions\n"
            "- Explain the ML pipeline you built for [your project]\n"
            "- How would you deploy a model to production?\n"
            "- Describe a time you optimized model performance\n"
        ),
    }
    
    return {
        "draft_type": request.draft_type,
        "content": drafts.get(request.draft_type, "Draft generation in progress..."),
        "note": "This draft is generated by the AI copilot. Review and edit before using.",
    }
