---
title: Research Gap Hunter
emoji: 🧭
colorFrom: green
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: Graph + AI novelty check for research ideas
---

# Research Gap Hunter

Describe a research idea and find out whether it already exists. A Neo4j knowledge graph of
papers (citations, authors, and the methods, datasets and tasks the LLM extracts) is searched
with vectors and then expanded through the graph. The result is a novelty verdict, a coverage
matrix, the remaining gap and a reading path. New PDFs can be uploaded live, and the answer
changes as the graph grows.

The graph follows the challenge shape **Paper → Author → Concept → Method → Limitation → Related
Paper**. Each paper's own limitations are extracted, and a later paper gets a `RESOLVES` link only
when it overcomes a limitation of a paper it cites (the candidates come from the graph; gpt-4o
makes that one judgment). "Ask the graph" answers questions like *"Which approaches to reducing
hallucination have been explored, what are their limitations, and which papers address them?"*
and highlights the path.

Graph: `(Paper)-[:CITES]->(Paper)`, `WRITTEN_BY`→Author→`AFFILIATED_WITH`→Institution,
`PROPOSES|USES`→Method, `EVALUATES_ON`→Dataset, `ADDRESSES`→Task (concept),
`HAS_LIMITATION`→Limitation←`RESOLVES` (later paper).

## Layout

```
docker-compose.yml   optional local Neo4j 5 + GDS (the demo runs on Neo4j Aura)
.env                 OpenAI key + Neo4j Aura connection (never commit)
data/
  base_papers.json         structure for the 17 base papers (stand-in for a metadata API)
  base_ground_truth.json   expected entities for the base papers (scoring only)
  upload_ground_truth.json expected extraction for the 3 live-upload papers (scoring only)
  pdf/base/                17 PDFs loaded before the demo
  pdf/upload/              P17, P18, P19 for the live upload
  cache/                   cached LLM + embedding results (offline safety net)
backend/             FastAPI (Python)
  app/  config, db, llm, extraction, ingest, novelty, agent, main
  scripts/load_base.py, scripts/score_extraction.py
frontend/            React + Vite (graph view, upload, novelty matrix, Q&A)
docs/                paper prompts + original metadata
```

## Setup (once)

1. Fill in `OPENAI_API_KEY` in `.env`, plus the Aura values from the downloaded credentials file:
   `NEO4J_URI` (`neo4j+s://...`), `NEO4J_USERNAME` and `NEO4J_PASSWORD`.
   Aura Free has no GDS plugin, so PageRank is computed in Python (same formula).
   Aura Free pauses when idle: open https://console.neo4j.io and resume it before a demo.
2. (Optional, offline backup) local Neo4j instead of Aura: `docker compose up -d` and point
   `NEO4J_URI` at `bolt://localhost:7687`.
3. Backend dependencies (already installed in `backend/.venv`):
   ```
   cd backend
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
4. Frontend dependencies (already installed):
   ```
   cd frontend
   npm install
   ```

## Load the base graph

```
cd backend
.venv\Scripts\python -m scripts.load_base --wipe
```

This loads 17 papers. P17 is created as a **stub**: 5 papers cite it, but it has no text yet.

## Run

Use two terminals:

```
cd backend
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

```
cd frontend
npm run dev
```

Open http://localhost:5173

## Rehearse the demo (do this before the event)

1. Run the idea check with the example idea. Expected: **Partially exists** (P16 is closest at 70%),
   the graph reports Knowledge Graph never combined with Small Language Model, Medical QA or MedQA,
   and P17 is listed as "cited but not yet in the graph".
2. Upload `data/pdf/upload/P17.pdf`, `P18.pdf`, `P19.pdf`. P17 fills its stub and 5 existing
   citations light up; CuraGraph and TinyVeri appear as new papers.
3. Run the idea check again. Expected: TinyVeri, P17 and CuraGraph join the matrix (the novelty
   triangle) and the gap narrows to a single pair: **Knowledge Graph + MedQA**.
4. Click **Reset demo** to restore the base graph.

Every LLM extraction and embedding is cached in `data/cache/`, so after one rehearsal the
uploads work offline and give the same result every time.

To get an extraction accuracy score for the demo:
```
cd backend
.venv\Scripts\python -m scripts.score_extraction
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | /api/health | Neo4j + OpenAI key check |
| GET | /api/stats | counts, top PageRank papers |
| GET | /api/graph | nodes + links for the graph view |
| POST | /api/upload | PDF → extraction → merge into graph |
| POST | /api/novelty | `{idea}` → verdict, matrix, gaps, reading path |
| POST | /api/ask | `{question}` → agent answer (read-only Cypher + vector search) |
| POST | /api/reset-demo | remove live uploads, restore stubs |

## Deployment (Hugging Face Spaces)

The repo root is a Docker Space: the `Dockerfile` builds the React app and runs FastAPI on
port 7860, which serves both the UI and `/api`. Neo4j stays on Aura.

1. Create a Space with the **Docker** SDK (blank template).
2. In the Space's **Settings → Variables and secrets**, add secrets:
   `OPENAI_API_KEY`, `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`.
3. Push this repo to the Space (`git push space main`). PDFs go through Git LFS
   (see `.gitattributes`). The build takes a few minutes; logs are in the Space's **Logs** tab.

`data/cache/` is committed on purpose: it holds the rehearsed LLM results, so the deployed
demo gives the same answers and repeat runs cost nothing. The app is public, so keep an
OpenAI budget cap in place.
