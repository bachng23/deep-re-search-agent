import logging

_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=_FORMAT)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"paper_research_agent.{name}")
