from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from paper_research_agent.core.errors import RateLimitError
from paper_research_agent.core.models import Paper
from paper_research_agent.providers import ArxivProvider, OpenAlexProvider

mcp = FastMCP("paper-research")

_MAX_ABSTRACT_CHARS = 600


def _serialize(paper: Paper) -> dict:
    abstract = (paper.abstract or "").strip()
    if len(abstract) > _MAX_ABSTRACT_CHARS:
        abstract = abstract[:_MAX_ABSTRACT_CHARS].rstrip() + " ...[truncated]"

    return {
        "title": paper.title,
        "authors": paper.authors[:5],
        "year": paper.year,
        "abstract": abstract,
        "url": paper.url,
        "source": paper.source,
        "citation_count": paper.citation_count,
    }


def _run_search(provider, query: str, max_results: int) -> list[dict]:
    try:
        papers = provider.search(query, max_results=max_results)
    except RateLimitError as e:
        raise ToolError(str(e)) from e
    except Exception as e:
        raise ToolError(f"{provider.name} search failed: {e}") from e

    return [_serialize(p) for p in papers]


@mcp.tool
def arxiv_search(query: str, max_results: int = 8) -> list[dict]:
    """Search arXiv for academic papers. Best for recent preprints in CS, ML,
    physics, and math. Returns title, authors, year, a truncated abstract, and
    URL. Use this for cutting-edge or very recent work."""
    return _run_search(ArxivProvider(), query, max_results)


@mcp.tool
def openalex_search(query: str, max_results: int = 8) -> list[dict]:
    """Search OpenAlex, a catalog covering ALL disciplines and peer-reviewed
    works, with citation counts. Returns title, authors, year, a truncated
    abstract, URL, and citation_count. Use this for established, highly-cited,
    or cross-disciplinary literature."""
    return _run_search(OpenAlexProvider(), query, max_results)


if __name__ == "__main__":
    mcp.run()
