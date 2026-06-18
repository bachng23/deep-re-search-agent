from __future__ import annotations

import re

from paper_research_agent.core.state import ResearchState
from paper_research_agent.eval.golden import GoldenCase


def operational(state: ResearchState) -> dict:
    return {
        "papers": len(state.papers),
        "gaps": len(state.gaps),
        "conflicts": len(state.conflicts),
        "rounds": state.iteration,
        "tool_calls": state.tool_call_count,
        "provider_errors": len(state.errors),
    }


def grounded_in_fulltext(state: ResearchState) -> float:
    "Fraction of quote-bearing gaps whose evidence quote appears in a full-text excerpt."
    excerpts = [p.full_text_excerpt for p in state.papers if p.full_text_excerpt]
    gaps_q = [g for g in state.gaps if g.evidence_quotes]
    if not gaps_q:
        return 0.0
    grounded = sum(
        1
        for g in gaps_q
        if any(q and e and q in e for q in g.evidence_quotes for e in excerpts)
    )
    return grounded / len(gaps_q)


def citation_coverage(state: ResearchState) -> float:
    "Fraction of inline [n] citations in the report that resolve to a reference."
    md = state.report_markdown or ""
    body = md.split("## references")[0]
    cited = {int(n) for n in re.findall(r"\n[(\d+)]", body)}
    if not cited:
        return 1.0  # nothing to resolve
    n_refs = len(state.papers)
    resolved = sum(1 for n in cited if 1 <= n <= n_refs)
    return resolved / len(cited)


def gap_keyword_recall(state: ResearchState, case: GoldenCase) -> float:
    "Fraction of expected key-gap keywords found across gap descriptions."
    if not case.expected_gap_keywords:
        return 1.0
    text = " ".join(g.description.lower() for g in state.gaps)
    hit = sum(1 for kw in case.expected_gap_keywords if kw.lower() in text)
    return hit / len(case.expected_gap_keywords)


def paper_recall(state: ResearchState, case: GoldenCase) -> float:
    "Fraction of expected papers (title substrings) that appeared."
    if not case.expected_papers:
        return 1.0
    titles = " || ".join(p.title.lower() for p in state.papers)
    hit = sum(1 for t in case.expected_papers if t.lower() in titles)
    return hit / len(case.expected_papers)


def score_case(state: ResearchState, case: GoldenCase) -> dict:
    "All metrics for one finished run against its golden case."
    return {
        **operational(state),
        "novelty": state.novelty_score,
        "grounded_in_fulltext": round(grounded_in_fulltext(state), 2),
        "citation_coverage": round(citation_coverage(state), 2),
        "gap_keyword_recall": round(gap_keyword_recall(state, case), 2),
        "paper_recall": round(paper_recall(state, case), 2),
        "meets_min_gaps": len(state.gaps) >= case.min_gaps,
    }
