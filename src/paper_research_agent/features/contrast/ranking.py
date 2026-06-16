from __future__ import annotations

import re

from paper_research_agent.core.state import ResearchGap, ResearchState

_CONFIDENCE_WEIGHT = {"high": 2.0, "medium": 1.0, "low": 0.0}


def rank_gaps(state: ResearchState) -> ResearchState:
    """Order gaps by importance so the report leads with what matters."""
    state.gaps = sorted(
        state.gaps,
        key=lambda g: _importance(g, state.user_idea),
        reverse=True,
    )

    return state


def _importance(gap: ResearchGap, user_idea: str | None) -> float:
    confidence = _CONFIDENCE_WEIGHT.get(gap.confidence, 0.0)
    support = min(len(gap.supporting_papers), 3)
    relevance = _idea_overlap(gap.description, user_idea)
    return 2.0 * confidence + 1.5 * relevance + 1.0 * support


def _idea_overlap(description: str, user_idea: str | None) -> int:
    if not user_idea:
        return 0
    idea = _keywords(user_idea)
    return len(idea & _keywords(description)) if idea else 0


def _keywords(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{4,}", text.lower()))
