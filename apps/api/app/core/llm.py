"""
SkillSetu X — LLM Provider Interface
Single copilot interface using Groq (OpenAI-compatible API).

The LLM is used ONLY for:
- Extraction assist (resume/JD parsing assistance)
- Explanation generation (Why? views)
- Drafting (cover letters, application answers)
- Summarizing (career insights, reports)
- Query interpretation (natural language to structured queries)

The LLM is NEVER used for:
- SHI, CDS, STS, SOE computation
- Match score calculation
- Eligibility determination
- Career distance / graph algorithms
- Salary estimation
- Any scoring or ranking
"""
import os
import json
import structlog
from typing import AsyncGenerator
from dataclasses import dataclass, field

import httpx

logger = structlog.get_logger(__name__)


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "groq"
    api_key: str = ""
    model: str = "llama-3.3-70b-versatile"
    base_url: str = "https://api.groq.com/openai/v1"
    max_tokens: int = 4096
    temperature: float = 0.1
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "groq"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        )


@dataclass
class LLMResponse:
    """Structured response from the LLM."""
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    finish_reason: str = ""


@dataclass
class Tool:
    """Tool definition for the copilot."""
    name: str
    description: str
    parameters: dict
    handler: callable = None


class LLMProvider:
    """
    LLM provider interface — OpenAI-compatible API.
    Works with Groq, OpenAI, Together, Ollama, etc.
    
    This is the ONLY place in SkillSetu X where an LLM is called.
    All scoring/computation uses deterministic code.
    """
    
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
        self._tools: dict[str, Tool] = {}
        logger.info(
            "llm_provider_initialized",
            provider=self.config.provider,
            model=self.config.model,
            base_url=self.config.base_url,
        )
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool for the copilot to use."""
        self._tools[tool.name] = tool
        logger.info("tool_registered", tool_name=tool.name)
    
    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send a completion request to the LLM.
        
        Args:
            messages: Chat messages [{"role": "user", "content": "..."}]
            system_prompt: Optional system prompt
            tools: Optional tool definitions for function calling
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            LLMResponse with content and metadata
        """
        if not self.config.api_key:
            logger.warning("llm_no_api_key", provider=self.config.provider)
            return LLMResponse(
                content="LLM not configured. Please set LLM_API_KEY.",
                model=self.config.model,
            )
        
        request_messages = []
        if system_prompt:
            request_messages.append({"role": "system", "content": system_prompt})
        request_messages.extend(messages)
        
        payload = {
            "model": self.config.model,
            "messages": request_messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = await self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            
            return LLMResponse(
                content=choice["message"].get("content", ""),
                model=data.get("model", self.config.model),
                usage=data.get("usage", {}),
                finish_reason=choice.get("finish_reason", ""),
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "llm_request_failed",
                status_code=e.response.status_code,
                detail=e.response.text,
            )
            raise
        except Exception as e:
            logger.error("llm_request_error", error=str(e))
            raise
    
    async def complete_stream(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion response."""
        if not self.config.api_key:
            yield "LLM not configured."
            return
        
        request_messages = []
        if system_prompt:
            request_messages.append({"role": "system", "content": system_prompt})
        request_messages.extend(messages)
        
        payload = {
            "model": self.config.model,
            "messages": request_messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True,
        }
        
        try:
            async with self._client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error("llm_stream_error", error=str(e))
            yield f"Error: {str(e)}"
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


# ============================================================
# COPILOT — Single tool-using agent
# ============================================================

COPILOT_SYSTEM_PROMPT = """You are SkillSetu Copilot, an AI career assistant for India's workforce.

You help users with:
- Understanding their Talent Twin and skill scores
- Explaining career paths and recommendations
- Drafting cover letters and application answers
- Interpreting career goals in natural language (Hindi, Hinglish, Punjabi, English)
- Answering questions about opportunities, eligibility, and skills

You have access to tools that query the user's data:
- query_talent_twin: Get the user's skill profile and scores
- run_career_gps: Compute career paths to a target role
- check_eligibility: Check eligibility for an opportunity
- search_opportunities: Search available opportunities
- draft_resume: Generate a role-specific resume
- explain_score: Explain how a score was computed

IMPORTANT RULES:
1. You NEVER compute scores yourself. Always use the appropriate tool.
2. You NEVER invent data. If you don't have information, say so.
3. You always cite the source and confidence level of any metric you mention.
4. You support multilingual input — Hindi, Punjabi, Hinglish are all fine.
5. You are honest about limitations and demo data.
"""


class Copilot:
    """SkillSetu Copilot — single tool-using LLM agent.
    
    No multi-agent system. One copilot with registered tools.
    The copilot handles: chat, explanation, drafting, summarization, query interpretation.
    It NEVER directly computes scores.
    """
    
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self._conversation_history: dict[str, list[dict]] = {}
    
    async def chat(
        self,
        user_id: str,
        message: str,
        context: dict | None = None,
    ) -> str:
        """Process a user message and return a response.
        
        Args:
            user_id: The user's ID for conversation context
            message: The user's message (any language)
            context: Optional context (current page, selected skill, etc.)
            
        Returns:
            The copilot's response
        """
        # Get or create conversation history
        if user_id not in self._conversation_history:
            self._conversation_history[user_id] = []
        
        history = self._conversation_history[user_id]
        
        # Add context if provided
        user_message = message
        if context:
            user_message = f"[Context: {json.dumps(context)}]\n\n{message}"
        
        history.append({"role": "user", "content": user_message})
        
        # Keep last 20 messages to manage context window
        if len(history) > 20:
            history = history[-20:]
            self._conversation_history[user_id] = history
        
        # Get tools as OpenAI format
        tools = self._get_tool_definitions()
        
        response = await self.llm.complete(
            messages=history,
            system_prompt=COPILOT_SYSTEM_PROMPT,
            tools=tools if tools else None,
        )
        
        history.append({"role": "assistant", "content": response.content})
        
        return response.content
    
    def _get_tool_definitions(self) -> list[dict]:
        """Convert registered tools to OpenAI function calling format."""
        tools = []
        for tool in self.llm._tools.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            })
        return tools
    
    def clear_history(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        self._conversation_history.pop(user_id, None)


# ============================================================
# COPILOT TOOLS — Registered at app startup
# ============================================================

COPILOT_TOOLS = [
    Tool(
        name="query_talent_twin",
        description="Get the user's Talent Twin data: skills, STS scores, evidence, freshness, market relevance",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID"},
                "skill_filter": {"type": "string", "description": "Optional skill name to filter"},
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="run_career_gps",
        description="Compute career paths from current profile to a target role",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "target_role": {"type": "string", "description": "Target role name"},
                "route_type": {"type": "string", "enum": ["fastest", "cheapest", "highest_opportunity", "lowest_risk", "best_remote"]},
            },
            "required": ["user_id", "target_role"],
        },
    ),
    Tool(
        name="check_eligibility",
        description="Check if user is eligible for a specific opportunity",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "opportunity_id": {"type": "string"},
            },
            "required": ["user_id", "opportunity_id"],
        },
    ),
    Tool(
        name="search_opportunities",
        description="Search opportunities matching user's profile and preferences",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "type_filter": {"type": "string", "enum": ["private_job", "government_job", "internship", "scholarship", "fellowship", "exam", "scheme"]},
                "min_match_score": {"type": "number"},
                "location": {"type": "string"},
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="explain_score",
        description="Explain how a specific score (STS, SHI, match, CDS, SOE) was computed, showing full lineage",
        parameters={
            "type": "object",
            "properties": {
                "score_type": {"type": "string", "enum": ["sts", "shi", "match", "cds", "soe"]},
                "entity_id": {"type": "string", "description": "Skill ID, opportunity ID, or curriculum ID"},
                "user_id": {"type": "string"},
            },
            "required": ["score_type", "entity_id"],
        },
    ),
]
