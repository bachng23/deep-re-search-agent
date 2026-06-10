"""Model router: maps a capability tier to a concrete chat model.

Nodes never name a model directly — they ask for a tier ("fast",
"balanced", "reasoning") so routing can be tuned in one place.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI

from paper_research_agent.config import ModelTier, get_settings, model_for_tier


@lru_cache
def chat_model_for_tier(tier: ModelTier, temperature: float = 0.0) -> ChatOpenAI:
    settings = get_settings()

    return ChatOpenAI(
        model=model_for_tier(tier),
        api_key=settings.api_key,
        base_url=settings.llm_base_url,
        temperature=temperature,
        timeout=settings.request_timeout_seconds,
    )
