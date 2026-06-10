from __future__ import annotations

from paper_research_agent.core.state import ResearchState
from paper_research_agent.features.fetching.service import (
    default_providers,
    fetch_papers_for_queries,
)


def fetch_papers(state: ResearchState) -> ResearchState:
    queries = state.search_queries or [state.topic]
    providers = default_providers()

    state.papers = fetch_papers_for_queries(queries, providers=providers)
    state.tool_call_count += len(queries) * len(providers)

    return state
