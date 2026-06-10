from fastapi import FastAPI

from paper_research_agent.api.routes import router
from paper_research_agent.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title="paper-research-agent", version="0.1.0")
    app.include_router(router)

    return app


app = create_app()
