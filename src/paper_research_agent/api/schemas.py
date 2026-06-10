from pydantic import BaseModel, Field

from paper_research_agent.core.models import Paper
from paper_research_agent.core.state import ResearchGap, ResearchState


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3)
    user_idea: str | None = None


class ResearchResponse(BaseModel):
    topic: str
    papers_found: int
    papers: list[Paper]
    gaps: list[ResearchGap]
    novelty_score: int | None
    novelty_reasoning: str | None
    overlapping_papers: list[str]
    report_markdown: str | None

    @classmethod
    def from_state(cls, state: ResearchState) -> "ResearchResponse":
        return cls(
            topic=state.topic,
            papers_found=len(state.papers),
            papers=state.papers,
            gaps=state.gaps,
            novelty_score=state.novelty_score,
            novelty_reasoning=state.novelty_reasoning,
            overlapping_papers=state.overlapping_papers,
            report_markdown=state.report_markdown,
        )
