import argparse
import json

from paper_research_agent.agent.graph import run_research
from paper_research_agent.core.logging import configure_logging


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="paper-research",
        description="Scan academic literature for research gaps.",
    )
    parser.add_argument("topic", help="Research topic to investigate")
    parser.add_argument(
        "--idea", default=None, help="Your idea, to be scored for novelty"
    )
    args = parser.parse_args()

    configure_logging()

    state = run_research(topic=args.topic, user_idea=args.idea)

    print(json.dumps(state.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
