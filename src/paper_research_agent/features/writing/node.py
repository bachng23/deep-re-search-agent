from __future__ import annotations

from paper_research_agent.core.models import Paper
from paper_research_agent.core.state import Conflict, ResearchGap, ResearchState
from paper_research_agent.features.writing.prompts import (
    WRITER_SYSTEM_PROMPT,
    WRITER_USER_PROMPT,
)
from paper_research_agent.llm import chat_model_for_tier


def write_report(state: ResearchState) -> ResearchState:
    if not state.papers:
        return state

    try:
        body = _write_report_with_llm(state)
        conflicts = _format_conflicts(state.conflicts)
        references = _format_references(state.papers)
        sections = [body, conflicts, references]
        state.report_markdown = "\n\n".join(s for s in sections if s)
    except Exception as e:
        state.errors.append(f"writing failed: {e}")

    return state


def _write_report_with_llm(state: ResearchState) -> str:
    model = chat_model_for_tier("balanced")

    prompt = WRITER_USER_PROMPT.format(
        topic=state.topic,
        user_idea=state.user_idea or "Not provided",
        novelty=_format_novelty(state),
        gaps=_format_gaps(state.gaps),
        papers=_format_papers(state.papers),
    )

    result = model.invoke([("system", WRITER_SYSTEM_PROMPT), ("user", prompt)])

    return str(result.content).strip()


def _format_novelty(state: ResearchState) -> str:
    if state.novelty_score is None:
        return "Not assessed (no user idea provided)."

    overlap = ", ".join(state.overlapping_papers) or "none"

    return (
        f"Score: {state.novelty_score}/100\n"
        f"    Reasoning: {state.novelty_reasoning}\n"
        f"    Overlapping papers: {overlap}"
    )


def _format_gaps(gaps: list[ResearchGap]) -> str:
    if not gaps:
        return "No gaps identified."

    blocks: list[str] = []
    for gap in gaps:
        block = f"- {gap.description} (confidence: {gap.confidence})"
        for quote in gap.evidence_quotes:
            block += f'\n    > "{quote}"'
        blocks.append(block)

    return "\n".join(blocks)


def _format_papers(papers: list[Paper]) -> str:
    blocks: list[str] = []

    for i, paper in enumerate(papers, start=1):
        abstract = (paper.abstract or "No abstract available.").strip()
        blocks.append(f"[{i}] {paper.title} ({paper.year})\n{abstract}")

    return "\n\n".join(blocks)


def _format_references(papers: list[Paper]) -> str:
    lines = ["## References"]

    for i, paper in enumerate(papers, start=1):
        authors = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors += " et al."

        parts = [f"[{i}] {paper.title}"]
        if paper.year:
            parts.append(f"({paper.year})")
        if authors:
            parts.append(f"- {authors}")
        if paper.url:
            parts.append(paper.url)

        lines.append(" ".join(parts))

    return "\n".join(lines)


def _format_conflicts(conflicts: list[Conflict]) -> str:
    if not conflicts:
        return ""

    lines = ["## Conflicting Evidence"]
    for c in conflicts:
        a = ", ".join(c.position_a_papers)
        b = ", ".join(c.position_b_papers)
        lines.append(f"- **{c.topic}**")
        lines.append(f" - {c.position_a} ({a}) - '{c.position_a_quote}'")
        lines.append(f" - {c.position_b} ({b}) - '{c.position_b_quote}'")
    return "\n".join(lines)
