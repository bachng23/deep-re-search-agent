"""Vertical feature slices, one package per graph node.

Each feature owns its node function plus any prompts, schemas, and
pure helpers it needs. Nodes are wired into the graph via
`agent.registry` — features never import each other; they communicate
only through `core.state.ResearchState`.
"""
