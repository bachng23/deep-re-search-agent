"""Planner node: expands the topic into multi-angle search queries.

Currently a deterministic fallback (topic as the single query). The
LLM-backed planner (fast tier, see llm.chat_model_for_tier) replaces
the body of plan_queries without changing its signature.
"""

from __future__ import annotations

from paper_research_agent.core.state import ResearchState


def plan_queries(state: ResearchState) -> ResearchState:
    if not state.search_queries:
        state.search_queries = [state.topic]

    return state
