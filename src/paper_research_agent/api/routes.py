from fastapi import APIRouter

from paper_research_agent.agent.graph import run_research
from paper_research_agent.api.schemas import ResearchRequest, ResearchResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    state = run_research(topic=request.topic, user_idea=request.user_idea)
    return ResearchResponse.from_state(state)
