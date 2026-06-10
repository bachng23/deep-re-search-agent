from paper_research_agent.core.models import Paper
from paper_research_agent.providers.openalex import OpenAlexProvider


def search_openalex(
    query: str,
    *,
    max_results: int | None = None,
) -> list[Paper]:
    return OpenAlexProvider().search(query, max_results=max_results)
