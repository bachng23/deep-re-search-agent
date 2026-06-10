from __future__ import annotations

from paper_research_agent.core.models import Paper


def rank_papers(papers: list[Paper]) -> list[Paper]:
    return sorted(
        papers,
        key=lambda paper: (
            paper.abstract is not None,
            paper.citation_count or 0,
            paper.year or 0,
        ),
        reverse=True,
    )
