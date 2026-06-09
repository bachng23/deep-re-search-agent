from __future__ import annotations

from collections.abc import Iterable

import requests

from paper_research_agent.config import get_settings
from paper_research_agent.state import Paper

OPENALEX_SEARCH_URL = "https://api.openalex.org/works"


def _reconstruct_abstract(abstract_inverted_index: dict[str, list[int]] | None) -> str | None:
    if not abstract_inverted_index:
        return None

    positions: dict[int, str] = {}
    for word, indexes in abstract_inverted_index.items():
        for index in indexes:
            positions[index] = word

    if not positions:
        return None

    return " ".join(positions[index] for index in sorted(positions)).strip() or None


def _author_names(authorships: Iterable[dict]) -> list[str]:
    authors: list[str] = []
    for authorship in authorships:
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)
    return authors


def _paper_url(item: dict) -> str | None:
    best_location = item.get("best_oa_location") or {}
    primary_location = item.get("primary_location") or {}

    for candidate in (
        best_location.get("landing_page_url"),
        best_location.get("pdf_url"),
        primary_location.get("landing_page_url"),
        primary_location.get("pdf_url"),
        item.get("doi"),
        item.get("id"),
    ):
        if candidate:
            return candidate

    return None


def search_openalex(
    query: str,
    *,
    max_results: int | None = None,
) -> list[Paper]:
    settings = get_settings()
    limit = max_results or settings.openalex_max_results

    params = {
        "search": query,
        "per-page": limit,
        "select": (
            "id,doi,display_name,authorships,publication_year,"
            "abstract_inverted_index,cited_by_count,best_oa_location,primary_location"
        ),
    }

    headers = {}
    if settings.openalex_api_key:
        params["api_key"] = settings.openalex_api_key

    response = requests.get(
        OPENALEX_SEARCH_URL,
        params=params,
        headers=headers,
        timeout=settings.request_timeout_seconds,
    )

    if response.status_code == 429:
        raise RuntimeError(
            "OpenAlex rate limit hit. Wait or set OPENALEX_API_KEY"
        )

    response.raise_for_status()

    payload = response.json()
    papers: list[Paper] = []

    for item in payload.get("results", []):
        papers.append(
            Paper(
                title=(item.get("display_name") or "").strip(),
                authors=_author_names(item.get("authorships") or []),
                year=item.get("publication_year"),
                abstract=_reconstruct_abstract(item.get("abstract_inverted_index")),
                url=_paper_url(item),
                source="openalex",
                citation_count=item.get("cited_by_count"),
            )
        )

    return papers


def search_semantic_scholar(
    query: str,
    *,
    max_results: int | None = None,
) -> list[Paper]:
    return search_openalex(query, max_results=max_results)
