from paper_research_agent.core.models import Paper
from paper_research_agent.providers.arxiv import ArxivProvider


def search_arxiv(
    query: str,
    *,
    max_results: int | None = None,
) -> list[Paper]:
    return ArxivProvider().search(query, max_results=max_results)
