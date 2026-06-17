import paper_research_agent.features.conflicts.node as conflicts_node
from paper_research_agent.core.models import Paper
from paper_research_agent.core.state import Conflict, ResearchState
from paper_research_agent.features.conflicts import find_conflicts
from paper_research_agent.features.conflicts.schemas import ConflictAnalysis


class _FakeStructured:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def invoke(self, messages):
        if self._error is not None:
            raise self._error
        return self._result


class _FakeModel:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def with_structured_output(self, schema):
        return _FakeStructured(result=self._result, error=self._error)


def _patch_llm(monkeypatch, *, result=None, error=None):
    monkeypatch.setattr(
        conflicts_node,
        "chat_model_for_tier",
        lambda tier, temperature=0.0: _FakeModel(result=result, error=error),
    )


def _paper(title):
    return Paper(title=title, source="arxiv", abstract="a", year=2024)


def _conflict():
    return Conflict(
        topic="does hierarchical chunking help recall",
        position_a="it helps",
        position_a_papers=["Paper A"],
        position_a_quote="hierarchical chunking improves recall.",
        position_b="it does not help",
        position_b_papers=["Paper B"],
        position_b_quote="we observe no recall gain from hierarchy.",
    )


def test_find_conflicts_fills_state(monkeypatch):
    _patch_llm(monkeypatch, result=ConflictAnalysis(conflicts=[_conflict()]))

    state = ResearchState(topic="t", papers=[_paper("Paper A"), _paper("Paper B")])
    find_conflicts(state)

    assert len(state.conflicts) == 1
    assert state.conflicts[0].topic.startswith("does hierarchical")
    assert state.errors == []


def test_empty_conflicts_is_valid(monkeypatch):
    # Papers that don't disagree -> empty list, no error, no retry needed.
    _patch_llm(monkeypatch, result=ConflictAnalysis(conflicts=[]))

    state = ResearchState(topic="t", papers=[_paper("A"), _paper("B")])
    find_conflicts(state)

    assert state.conflicts == []
    assert state.errors == []


def test_skips_when_fewer_than_two_papers(monkeypatch):
    _patch_llm(monkeypatch, error=AssertionError("LLM should not be called"))

    state = ResearchState(topic="t", papers=[_paper("only one")])
    find_conflicts(state)

    assert state.conflicts == []
    assert state.errors == []


def test_records_error_on_failure(monkeypatch):
    _patch_llm(monkeypatch, error=RuntimeError("boom"))

    state = ResearchState(topic="t", papers=[_paper("A"), _paper("B")])
    find_conflicts(state)

    assert state.conflicts == []
    assert len(state.errors) == 1
    assert state.errors[0].startswith("conflicts failed:")
