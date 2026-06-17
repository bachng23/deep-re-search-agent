import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

import paper_research_agent.mcp.server as server
from paper_research_agent.core.errors import RateLimitError
from paper_research_agent.core.models import Paper


class _StubProvider:
    name = "stub"

    def __init__(self, papers=None, error=None):
        self._papers = papers or []
        self._error = error

    def search(self, query, max_results=None):
        if self._error is not None:
            raise self._error
        return self._papers


@pytest.mark.asyncio
async def test_lists_both_search_tools():
    async with Client(server.mcp) as client:
        tools = {t.name for t in await client.list_tools()}

    assert {"arxiv_search", "openalex_search"} <= tools


@pytest.mark.asyncio
async def test_arxiv_search_serializes_and_truncates(monkeypatch):
    paper = Paper(
        title="A Paper",
        authors=["A", "B", "C", "D", "E", "F"],  # 6 -> capped to 5
        year=2024,
        abstract="x" * 1000,  # long -> truncated
        url="http://x",
        source="arxiv",
    )
    monkeypatch.setattr(server, "ArxivProvider", lambda: _StubProvider([paper]))

    async with Client(server.mcp) as client:
        result = await client.call_tool("arxiv_search", {"query": "q"})

    [item] = result.data
    assert item["title"] == "A Paper"
    assert item["authors"] == ["A", "B", "C", "D", "E"]  # capped
    assert item["source"] == "arxiv"
    assert item["abstract"].endswith("...[truncated]")
    assert len(item["abstract"]) < 1000


@pytest.mark.asyncio
async def test_rate_limit_becomes_prompt_friendly_tool_error(monkeypatch):
    monkeypatch.setattr(
        server,
        "OpenAlexProvider",
        lambda: _StubProvider(error=RateLimitError("openalex", "Wait or set OPENALEX_API_KEY")),
    )

    async with Client(server.mcp) as client:
        with pytest.raises(ToolError, match="OPENALEX_API_KEY"):
            await client.call_tool("openalex_search", {"query": "q"})
