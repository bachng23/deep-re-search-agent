from __future__ import annotations

from collections.abc import Iterable

from paper_research_agent.core.models import Paper
from paper_research_agent.features.fetching.dedup import deduplicate_papers
from paper_research_agent.features.fetching.ranking import rank_papers
from paper_research_agent.providers import ArxivProvider, OpenAlexProvider, PaperProvider


def default_providers() -> list[PaperProvider]:
    return [ArxivProvider(), OpenAlexProvider()]


def fetch_papers_for_queries(
    queries: Iterable[str],
    *,
    providers: list[PaperProvider] | None = None,
    max_results_per_provider: int | None = None,
    limit: int = 20,
) -> list[Paper]:
    active_providers = providers or default_providers()
    papers: list[Paper] = []

    for query in queries:
        for provider in active_providers:
            papers.extend(provider.search(query, max_results=max_results_per_provider))

    papers = deduplicate_papers(papers)
    papers = rank_papers(papers)

    return papers[:limit]
