from paper_research_agent.core.state import ResearchGap, ResearchState
from paper_research_agent.features.contrast import rank_gaps


def _gap(description, confidence="medium", supporting=0):
    return ResearchGap(
        description=description,
        confidence=confidence,
        supporting_papers=[f"p{i}" for i in range(supporting)],
    )


def test_idea_relevant_high_confidence_gap_ranks_first():
    state = ResearchState(
        topic="t",
        user_idea="hierarchical chunking summarization retrieval",
    )
    state.gaps = [
        _gap("unrelated study about migratory birds", confidence="low"),
        _gap(
            "hierarchical chunking summarization improves retrieval",
            confidence="high",
            supporting=2,
        ),
    ]

    rank_gaps(state)

    assert state.gaps[0].description.startswith("hierarchical chunking")


def test_ranks_by_confidence_without_user_idea():
    state = ResearchState(topic="t")  # no idea -> relevance is 0 for all
    state.gaps = [
        _gap("gap A", confidence="medium"),
        _gap("gap B", confidence="high"),
    ]

    rank_gaps(state)

    assert [g.confidence for g in state.gaps] == ["high", "medium"]


def test_support_count_breaks_confidence_ties():
    state = ResearchState(topic="t")
    state.gaps = [
        _gap("few supporters", confidence="medium", supporting=1),
        _gap("many supporters", confidence="medium", supporting=3),
    ]

    rank_gaps(state)

    assert state.gaps[0].description == "many supporters"


def test_one_important_gap_outranks_several_minor_ones():
    # The user's concern: 1 important gap should beat many small ones.
    state = ResearchState(topic="t", user_idea="hierarchical chunking retrieval")
    state.gaps = [
        _gap("minor tangential note one", confidence="low"),
        _gap("minor tangential note two", confidence="low"),
        _gap(
            "hierarchical chunking retrieval remains unevaluated",
            confidence="high",
            supporting=3,
        ),
    ]

    rank_gaps(state)

    assert state.gaps[0].description.startswith("hierarchical chunking")
