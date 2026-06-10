"""Node registry: the single place where graph nodes are declared.

To add a pipeline step, implement its node in features/<name>/node.py
and append a NodeSpec here — graph.py picks it up automatically.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from paper_research_agent.core.state import ResearchState
from paper_research_agent.features.fetching import fetch_papers
from paper_research_agent.features.planning import plan_queries

NodeFn = Callable[[ResearchState], ResearchState]


@dataclass(frozen=True)
class NodeSpec:
    name: str
    run: NodeFn


def default_nodes() -> list[NodeSpec]:
    return [
        NodeSpec("plan_queries", plan_queries),
        NodeSpec("fetch_papers", fetch_papers),
        # Upcoming, in order: find_gaps (contrast), score_novelty (novelty),
        # write_report (writing).
    ]
