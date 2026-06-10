from typing import Protocol

from paper_research_agent.core.models import Paper


class PaperProvider(Protocol):
    name: str

    def search(self, query: str, max_results: int | None = None) -> list[Paper]:
        ...
