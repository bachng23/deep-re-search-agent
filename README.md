# paper-research-agent

An AI agent that automatically scans academic literature, identifies research gaps, and evaluates the novelty of your ideas — built with LangGraph, FastAPI, and OpenAI.

---

## What it does

Given a research topic or idea, the agent:

1. **Searches** ArXiv and OpenAlex for relevant papers
2. **Contrasts** methodologies, datasets, and findings across papers to surface what's missing
3. **Scores** your idea's novelty against existing literature (0–100)
4. **Reports** identified gaps with citations, and explains why your idea is or isn't novel

---

## Architecture

```
User input (topic or idea)
        │
   ┌────▼─────┐
   │  Router   │  Dispatches model tier per node (fast/balanced/reasoning)
   └────┬─────┘
        │
   ┌────▼─────┐
   │  Planner  │  Generates multi-angle search queries  [Fast lane]
   └────┬─────┘
        │
   ┌────▼─────┐
   │  Fetcher  │  Calls ArXiv + OpenAlex MCP tools  [Fast lane]
   └────┬─────┘  ↺ loops until enough papers (max_steps, timeout, stop_criteria)
        │
   ┌────▼─────┐
   │  Contrast │  Finds gaps between papers (core node)  [Reasoning lane]
   └────┬─────┘
        │
   ┌────▼──────────┐
   │ Novelty checker│  Scores your idea against found gaps  [Reasoning lane]
   └────┬──────────┘
        │
   ┌────▼─────┐
   │  Writer   │  Synthesizes report with citations  [Balanced lane]
   └────┬─────┘
        │
   Research report (JSON + Markdown)
```

The **Contrast node** is what makes this agent different from a simple literature summarizer. It doesn't just describe papers — it reasons about the *space between them* to identify what hasn't been done.

---

## Model routing

Per the AI Engineer course (Lesson 2.5 — *Fast / Balanced / Reasoning lanes*), we don't use one model for every node. Routing trades cost for capability where it matters.

| Node | Model tier | Why |
|---|---|---|
| Planner | **Fast** (`gpt-5.4-nano`) | Query expansion = pattern matching |
| Fetcher (tool arg generation) | **Fast** (`gpt-5.4-nano`) | Just selects tools + arguments |
| **Contrast** | **Reasoning** (`o4-mini`) | Multi-paper reasoning, gap analysis |
| **Novelty** | **Reasoning** (`o4-mini`) | High-stakes scoring with explanation |
| Writer | **Balanced** (`gpt-5.4`) | Synthesis, no deep reasoning needed |

> Model names are illustrative — finalize after measuring on the project's golden set (see `tests/evaluation.py`). Override per node via `MODEL_TIER_OVERRIDE` for A/B testing.

**Why this matters**: routing 60–80% of calls to fast/balanced lanes (planner, fetcher, writer) reserves the reasoning budget for the two nodes where it actually moves the needle (contrast, novelty).

---

## Project structure

```
paper-research-agent/
├── pyproject.toml                        # package config, deps, entry points
├── .env.example                          # required environment variables
├── Makefile                              # make dev, make test, make lint
├── README.md
│
├── src/paper_research_agent/             # core package — pip installable
│   ├── __init__.py                       # exports run_research(), ResearchResult
│   ├── config.py                         # Pydantic Settings, constants
│   ├── llm.py                            # ⭐ model router + OpenAI client factory
│   ├── state.py                          # ResearchState (Pydantic, not TypedDict)
│   │
│   ├── tools/                            # MCP tools — testable independently
│   │   ├── arxiv_tool.py                 # search ArXiv, returns enriched objects
│   │   ├── openalex.py                   # citation graph + metadata
│   │   └── __init__.py
│   │
│   └── agent/                            # LangGraph graph
│       ├── prompts.py                    # markdown sections (not Claude XML)
│       ├── schemas.py                    # ⭐ Pydantic models for structured output
│       ├── nodes.py                      # planner, fetcher, contrast, novelty, writer
│       ├── graph.py                      # StateGraph, edges, compile()
│       └── __init__.py
│
├── api/                                  # FastAPI backend
│   ├── main.py                           # app init, CORS, routers
│   ├── routes.py                         # POST /research, GET /health
│   └── schemas.py                        # Pydantic request/response models
│
├── frontend/                             # Streamlit UI
│   └── app.py                            # calls FastAPI, renders report
│
└── tests/
    ├── test_tools.py                     # unit tests for MCP tools
    └── evaluation.py                     # 5 test cases + failure analysis
```

---

## Tech stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent framework | LangGraph | Stateful multi-node workflow (LLM-agnostic) |
| LLM — Router/Planner/Fetcher | `gpt-5.4-nano` | Fast lane: routing, query expansion, tool dispatch |
| LLM — Writer | `gpt-5.4` | Balanced lane: synthesis & report drafting |
| LLM — Contrast/Novelty | `o4-mini` | Reasoning lane: multi-paper gap analysis & scoring |
| Structured output | OpenAI native JSON Schema mode | Schema enforced by API — eliminates manual validate/retry loops |
| Data — papers | ArXiv API (`arxiv` PyPI) | Full metadata + abstracts, free |
| Data — citations | OpenAlex API | Citation graph, influential papers, open metadata |
| Tool protocol | FastMCP | Custom MCP server wrapping both APIs |
| API | FastAPI | Expose agent as REST endpoint |
| UI | Streamlit | Demo frontend, calls FastAPI |
| Observability | LangSmith | Trace every node execution (works with OpenAI) |

---

## Design principles applied from the course

This project deliberately applies patterns from the AI Engineer course rather than just calling LLMs ad hoc.

| Principle | Where applied | Source |
|---|---|---|
| **Agentic loop** (Plan → Act → Observe → Reflect → Stop) with explicit loop control (`max_steps`, `timeout`, `stop_criteria`) | Fetcher node | Lesson 2.2 |
| **Structured output first** — define Pydantic schemas *before* writing prompts; use OpenAI native JSON Schema mode | `agent/schemas.py` | Lesson 2.1 |
| **Tool = workflow, not API wrapper** — `search_papers(topic, year_range, limit)` returns enriched objects, not raw endpoint dumps | `tools/arxiv_tool.py`, `tools/openalex.py` | Lesson 3.4 |
| **Namespacing** — `arxiv_search`, `s2_search`, `s2_citations` (no generic `search()`) | MCP tool names | Lesson 3.4 |
| **Helpful errors as prompts** — rate-limit errors return `"Wait or set OPENALEX_API_KEY"` instead of HTTP 429 | Tool error handlers | Lesson 3.4 |
| **Context efficiency** — Contrast clears raw abstracts from state after extracting gap summaries (tool-result clearing) | Graph reducer | Lesson 4.6 |
| **Quote-first prompting** — Contrast must cite a specific finding/quote from a paper before naming it as evidence for a gap | `agent/prompts.py` | Lesson 4.3 |
| **Markdown sections, not XML tags** — GPT family responds better to markdown headers + JSON Schema than to Claude-style `<instructions>` tags | `agent/prompts.py` | Lesson 4.3 (inverse) |
| **No "think step by step" for reasoning models** — `o4-mini` over-thinks if pushed; we only specify output shape | Contrast/Novelty prompts | Lesson 4.3 |
| **Stable prefix for KV cache** — no `datetime.now()` in system prompts; JSON serialized with `sort_keys=True` | `agent/prompts.py`, state serialization | Lesson 4.7 |
| **Parallel tool calls** — Fetcher calls ArXiv + OpenAlex concurrently | Fetcher node | Lesson 4.3 |
| **Evaluation-driven** — track `tool_call_count`, `token_usage`, `repeated_searches`, `wrong_tool_usage`, not just final accuracy | `tests/evaluation.py` | Lesson 3.4 |
| **Extraction vs Calculation** — LLM extracts, Python computes (paper counts, year ranges, score normalization) | `nodes.py` helpers | Lesson 2.6 |
| **Audit logging** — every node call logs input, output, model, latency, timestamp to LangSmith | Graph middleware | Lesson 2.6 |

---

## Setup

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- (Optional) A [LangSmith API key](https://smith.langchain.com/) for tracing
- (Optional) A [OpenAlex API key](https://openalex.org/settings/api) — raises the daily credit limit and avoids the lowest quota tier

### Install

```bash
git clone https://github.com/yourusername/paper-research-agent
cd paper-research-agent

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -e ".[dev]"

cp .env.example .env
# Edit .env and fill in your API keys
```

### Environment variables

```bash
# .env.example
OPENAI_API_KEY=sk-...

# Optional — overrides per-node tier defaults. "fast" | "balanced" | "reasoning"
MODEL_TIER_OVERRIDE=

# Optional — enables tracing
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=paper-research-agent

# Optional — OpenAlex API key
OPENALEX_API_KEY=
```

### Run

```bash
# Start API + frontend together
make dev

# Or separately
uvicorn api.main:app --reload --port 8000
streamlit run frontend/app.py
```

### Test

```bash
make test                       # run unit tests
python tests/evaluation.py      # run agent evaluation (calls real APIs)
```

---

## API

### `POST /research`

Run the research agent on a topic or idea.

**Request**
```json
{
  "topic": "retrieval-augmented generation for long documents",
  "user_idea": "using hierarchical chunking to improve RAG recall"
}
```

**Response**
```json
{
  "topic": "retrieval-augmented generation for long documents",
  "papers_found": 18,
  "gaps": [
    {
      "description": "No work combines hierarchical chunking with late interaction retrieval",
      "supporting_papers": ["arxiv.org/abs/2312.xxxxx", "arxiv.org/abs/2401.xxxxx"],
      "confidence": "medium"
    }
  ],
  "novelty_score": 74,
  "novelty_reasoning": "The idea partially overlaps with ..., but the hierarchical angle is underexplored.",
  "overlapping_papers": ["arxiv.org/abs/2401.xxxxx"],
  "report_markdown": "## Research Gap Report\n..."
}
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## Evaluation

The agent is evaluated on 5 test cases designed to cover different scenarios. Following Lesson 3.4 (*evaluation-driven development*), we track operational metrics in addition to output quality:

| # | Topic | Expected | Tests |
|---|---|---|---|
| 1 | Attention mechanism | Known gaps found | Gap quality on well-studied topic |
| 2 | RAG for long documents | Known gaps found | Recent literature coverage |
| 3 | Federated learning privacy | Known gaps found | Multi-paper contrast quality |
| 4 | Obscure niche topic | Graceful degradation | Failure mode handling |
| 5 | Idea that already exists | Low novelty score | Novelty checker accuracy |

**Operational metrics tracked per run**: `tool_call_count`, `token_usage` (per tier), `runtime_seconds`, `repeated_searches`, `wrong_tool_usage`, `schema_pass_rate`.

Run `python tests/evaluation.py` to generate `evaluation_results.md`.

---

## Known limitations

- **Abstract-only**: the agent reads abstracts, not full paper text. Deep methodological gaps may be missed.
- **English only**: ArXiv and OpenAlex coverage is strongest for English-language CS papers.
- **Novelty scoring uses a reasoning model (`o4-mini`)** — scores are explainable (`novelty_reasoning` + `overlapping_papers` always returned) but are reasoned estimates, not ground truth. Use as a signal, not a verdict.
- **Rate limits**: OpenAlex now requires a free API key for full usage. For heavy use, set `OPENALEX_API_KEY`.
- **No XML-tag prompts**: by design — GPT family responds better to markdown + native JSON Schema than to Claude-style `<instructions>` tags. Do not port Claude prompt patterns wholesale.

---

## Roadmap

- [ ] PDF upload — read your own draft, agent finds gaps in your contribution
- [ ] Abstract writer — draft an abstract based on identified gaps
- [ ] Semantic search — replace keyword search with embedding-based retrieval
- [ ] Citation graph visualization — see how papers connect to each other
- [ ] Multi-provider routing — fall back from OpenAI reasoning lane to open-weight reasoning models for cost control

---

## Built for

AIE1 Final Project — Module 1: Building a complete AI Agent
