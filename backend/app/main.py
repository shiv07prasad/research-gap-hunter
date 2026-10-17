"""FastAPI app. Run from the backend folder:  uvicorn app.main:app --reload --port 8000"""
import json
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, config, db, ingest, novelty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        db.setup_schema()  # once at startup, so uploads don't pay for it
    except Exception as exc:  # the app still starts; /api/health reports the problem
        print(f"Schema setup skipped: {exc}")
    yield


app = FastAPI(title="Research Gap Hunter", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class IdeaIn(BaseModel):
    idea: str


class QuestionIn(BaseModel):
    question: str


@app.get("/api/health")
def health():
    try:
        db.run("RETURN 1 AS ok")
        neo4j_ok = True
    except Exception:
        neo4j_ok = False
    return {"neo4j": neo4j_ok, "openai_key": bool(config.OPENAI_API_KEY)}


@app.get("/api/stats")
def stats():
    counts = db.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n")
    top = db.run(
        """
        MATCH (p:Paper)
        RETURN p.id AS id, p.title AS title, p.is_stub AS is_stub,
               round(coalesce(p.pagerank, 0.0), 3) AS pagerank,
               COUNT { (p)<-[:CITES]-() } AS cited_by
        ORDER BY pagerank DESC LIMIT 5
        """
    )
    stubs = db.run("MATCH (p:Paper {is_stub: true}) RETURN count(p) AS n")[0]["n"]
    return {"counts": {r["label"]: r["n"] for r in counts}, "stubs": stubs, "top_papers": top}


@app.get("/api/graph")
def graph():
    nodes = db.run(
        """
        MATCH (n) WHERE n:Paper OR n:Author OR n:Institution OR n:Venue OR n:Method OR n:Dataset OR n:Task
                     OR n:Limitation
        RETURN labels(n)[0] AS label, coalesce(n.id, n.key, n.name) AS key,
               coalesce(n.title, n.name) AS name, n.year AS year, n.is_stub AS is_stub,
               n.pagerank AS pagerank, n.community AS community, n.source AS source
        """
    )
    links = db.run(
        """
        MATCH (a)-[r]->(b)
        RETURN labels(a)[0] AS al, coalesce(a.id, a.key, a.name) AS ak,
               labels(b)[0] AS bl, coalesce(b.id, b.key, b.name) AS bk, type(r) AS type
        """
    )
    return {
        "nodes": [{**n, "id": ingest.node_id(n["label"], n["key"])} for n in nodes],
        "links": [
            {"source": ingest.node_id(l["al"], l["ak"]), "target": ingest.node_id(l["bl"], l["bk"]), "type": l["type"]}
            for l in links
        ],
    }


@app.post("/api/upload")
def upload(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file")
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file.filename)
    path = config.LIVE_UPLOAD_DIR / safe_name
    path.write_bytes(file.file.read())
    return ingest.ingest_upload(path)


SAMPLE_DIR = config.DATA_DIR / "pdf" / "upload"


@app.get("/api/samples")
def samples():
    """The bundled demo PDFs, so judges can add papers with one click."""
    truth = {}
    gt_path = config.DATA_DIR / "upload_ground_truth.json"
    if gt_path.exists():
        truth = {p["pdf_file"]: p for p in json.loads(gt_path.read_text(encoding="utf-8"))}
    papers = ingest.snapshot()["papers"]
    out = []
    for pdf in sorted(SAMPLE_DIR.glob("*.pdf")):
        meta = truth.get(pdf.name, {})
        title = meta.get("title", pdf.stem)
        match = ingest.find_paper_by_title(title, papers)
        out.append({
            "file": pdf.name,
            "title": title,
            "year": meta.get("year"),
            "in_graph": bool(match and not match["is_stub"]),
        })
    return out


@app.post("/api/upload-sample/{name}")
def upload_sample(name: str):
    path = SAMPLE_DIR / name
    if path.suffix.lower() != ".pdf" or path.parent != SAMPLE_DIR or not path.exists():
        raise HTTPException(404, "Unknown sample")
    return ingest.ingest_upload(path)


@app.post("/api/novelty")
def check(body: IdeaIn):
    if not body.idea.strip():
        raise HTTPException(400, "Idea text is empty")
    return novelty.check_novelty(body.idea.strip())


@app.post("/api/ask")
def ask(body: QuestionIn):
    return agent.ask(body.question)


@app.post("/api/reset-demo")
def reset_demo():
    return ingest.reset_demo()


# ---------- built frontend (production) ----------
# In deployment the React app is built into frontend/dist and served by this same
# server, so the whole demo is one service on one URL. In development Vite serves it.
DIST_DIR = config.ROOT_DIR / "frontend" / "dist"

if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith("api/"):
            raise HTTPException(404, "Unknown API route")
        file = (DIST_DIR / path).resolve()
        if path and file.is_file() and DIST_DIR.resolve() in file.parents:
            return FileResponse(file)
        return FileResponse(DIST_DIR / "index.html")
