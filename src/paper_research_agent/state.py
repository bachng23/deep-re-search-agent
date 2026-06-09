from typing import Literal

from pydantic import BaseModel, Field

Confidence = Literal["low", "medium", "high"]


class Paper(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    abstract: str | None = None
    url: str | None = None
    source: Literal["arxiv", "openalex"]
    citation_count: int | None = None


class ResearchGap(BaseModel):
    description: str
    supporting_papers: list[str] = Field(default_factory=list)
    confidence: Confidence = "medium"


class ResearchState(BaseModel):
    topic: str
    user_idea: str | None = None

    search_queries: list[str] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)

    gaps: list[ResearchGap] = Field(default_factory=list)

    novelty_score: int | None = Field(default=None, ge=0, le=100)
    novelty_reasoning: str | None = None
    overlapping_papers: list[str] = Field(default_factory=list)

    report_markdown: str | None = None

    errors: list[str] = Field(default_factory=list)
    tool_call_count: int = 0
