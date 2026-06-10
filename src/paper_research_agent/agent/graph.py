from __future__ import annotations

from langgraph.graph import END, StateGraph

from paper_research_agent.agent.registry import NodeSpec, default_nodes
from paper_research_agent.core.state import ResearchState


def build_graph(nodes: list[NodeSpec] | None = None):
    specs = nodes or default_nodes()

    graph = StateGraph(ResearchState)

    for spec in specs:
        graph.add_node(spec.name, spec.run)

    graph.set_entry_point(specs[0].name)
    for current, following in zip(specs, specs[1:]):
        graph.add_edge(current.name, following.name)
    graph.add_edge(specs[-1].name, END)

    return graph.compile()


def run_research(topic: str, user_idea: str | None = None) -> ResearchState:
    app = build_graph()

    initial_state = ResearchState(topic=topic, user_idea=user_idea)

    result = app.invoke(initial_state)
    return ResearchState.model_validate(result)
