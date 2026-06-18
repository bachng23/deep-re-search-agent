from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from paper_research_agent.core.state import ResearchState
from paper_research_agent.features.contrast.ranking import _keywords  # reuse


class ResultMemory:
    """Episodic memory of past runs: topic -> prior gaps. path=None -> no-op (gated off)."""

    def __init__(self, path: str | None = None) -> None:
        self._conn: sqlite3.Connection | None = None
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(path)
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS runs "
                "(topic TEXT, gaps TEXT, novelty INTEGER, created REAL)"
            )
            self._conn.commit()

    def remember(self, state: ResearchState) -> None:
        if self._conn is None or not state.gaps:
            return
        self._conn.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?)",
            (
                state.topic,
                json.dumps([g.description for g in state.gaps]),
                state.novelty_reasoning,
                time.time(),
            ),
        )
        self._conn.commit()

    def recall(self, topic: str, *, top_k: int = 3) -> list[str]:
        "Gap descriptions from past runs on keyword-related topics."
        if self._conn is None:
            return []
        kw = _keywords(topic)
        scored: list[tuple[int, list[str]]] = []
        for past_topic, gaps_json in self._conn.execute("SELECT topic, gaps FROM runs"):
            if past_topic == topic:
                continue
            overlap = len(kw & _keywords(past_topic))
            if overlap:
                scored.append((overlap, json.loads(gaps_json)))
        scored.sort(key=lambda x: x[0], reverse=True)
        seen, out = set(), []
        for _, gaps in scored[:top_k]:
            for g in gaps:
                if g not in seen:
                    seen.add(g)
                    out.append(g)
        return out
