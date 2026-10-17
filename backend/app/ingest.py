"""Loading papers into Neo4j: the base graph, live PDF uploads and demo reset.

Every database call is a network round-trip (~0.2 s on Aura), so writes are
batched with UNWIND and lookups read one snapshot instead of querying per item.
"""
import difflib
import hashlib
import json
import re
from pathlib import Path

from . import config, db, extraction, llm

# extraction key -> (node label, relationship type).
# Datasets and tasks go first so a "method" that is really a dataset/task
# (e.g. a proposed benchmark) links to that existing node instead of duplicating it.
ENTITY_RELS = {
    "datasets": ("Dataset", "EVALUATES_ON"),
    "tasks": ("Task", "ADDRESSES"),
    "proposes": ("Method", "PROPOSES"),
    "uses": ("Method", "USES"),
    # (Paper)-[:HAS_LIMITATION]->(Limitation)<-[:RESOLVES]-(later Paper)
    "limitations": ("Limitation", "HAS_LIMITATION"),
    "resolves": ("Limitation", "RESOLVES"),
}
LIMITATION_MATCH = 0.85  # fuzzy match so near-identical wordings become one Limitation node


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def short_id(prefix: str, text: str) -> str:
    return prefix + hashlib.sha1(norm(text).encode()).hexdigest()[:8]


def node_id(label: str, key: str) -> str:
    """Stable node id shared with the frontend graph view."""
    return f"{label}:{key}"


# ---------- snapshot helpers ----------

def snapshot() -> dict:
    """All papers and all Method/Dataset/Task entities, in one round-trip."""
    row = db.run(
        """
        CALL { MATCH (p:Paper)
               RETURN collect({id: p.id, tn: p.title_norm, is_stub: p.is_stub}) AS papers }
        CALL { MATCH (e) WHERE e:Method OR e:Dataset OR e:Task OR e:Limitation
               RETURN collect({label: labels(e)[0], name: e.name, key: e.key}) AS entities }
        RETURN papers, entities
        """
    )[0]
    return row


def known_entities(snap: dict | None = None) -> dict[str, list[str]]:
    snap = snap or snapshot()
    known: dict[str, list[str]] = {label: [] for label in db.ENTITY_LABELS}
    for e in snap["entities"]:
        known[e["label"]].append(e["name"])
    return known


def find_paper_by_title(title: str, papers: list[dict], threshold: float = 0.88) -> dict | None:
    target = norm(title)
    if not target:
        return None
    best, best_score = None, 0.0
    for p in papers:
        score = difflib.SequenceMatcher(None, target, p["tn"] or "").ratio()
        if score > best_score:
            best, best_score = p, score
    return best if best_score >= threshold else None


def upload_paper_id(title: str, papers: list[dict]) -> str:
    """Readable id for an uploaded paper, e.g. 'CuraGraph' from 'CuraGraph: Knowledge ...'."""
    head = title.split(":")[0].strip()
    taken = {p["id"] for p in papers}
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{1,24}", head) and head not in taken:
        return head
    return short_id("U", title)


def merge_entities(paper_id: str, sem: dict, entities: list[dict] | None = None) -> list[str]:
    """Create Method/Dataset/Task nodes + relationships. Returns ids of NEW entity nodes."""
    if entities is None:
        entities = snapshot()["entities"]
    # keys that already exist as Dataset/Task (in the graph or in this paper)
    non_method = {e["key"]: e["label"] for e in entities if e["label"] != "Method"}
    non_method.update({norm(n): "Dataset" for n in sem.get("datasets", []) if norm(n)})
    non_method.update({norm(n): "Task" for n in sem.get("tasks", []) if norm(n)})
    limitation_keys = [e["key"] for e in entities if e["label"] == "Limitation"]

    groups: dict[tuple[str, str], list[dict]] = {}
    for field, (default_label, rel) in ENTITY_RELS.items():
        for n in sem.get(field, []):
            key = norm(n)
            if not key:
                continue
            label = non_method.get(key, "Method") if default_label == "Method" else default_label
            if label == "Limitation":
                key = _canonical_limitation(key, limitation_keys)
                limitation_keys.append(key)
            groups.setdefault((label, rel), []).append({"key": key, "name": n})

    new_ids: list[str] = []
    for (label, rel), items in groups.items():
        rows = db.run(
            f"""
            MATCH (p:Paper {{id: $pid}})
            UNWIND $items AS item
            OPTIONAL MATCH (existing:{label} {{key: item.key}})
            WITH p, item, existing IS NULL AS is_new
            MERGE (e:{label} {{key: item.key}}) ON CREATE SET e.name = item.name
            MERGE (p)-[:{rel}]->(e)
            RETURN item.key AS key, is_new
            """,
            pid=paper_id,
            items=items,
        )
        new_ids += [node_id(label, r["key"]) for r in rows if r["is_new"]]
    return list(dict.fromkeys(new_ids))


def _canonical_limitation(key: str, existing: list[str]) -> str:
    """Reuse an existing Limitation key when the wording is nearly the same."""
    best = max(existing, key=lambda k: difflib.SequenceMatcher(None, key, k).ratio(), default=None)
    if best and difflib.SequenceMatcher(None, key, best).ratio() >= LIMITATION_MATCH:
        return best
    return key


def link_limitations(paper_id: str, text: str, entities: list[dict]) -> tuple[dict, list[str]]:
    """Own limitations + RESOLVES links to limitations of the papers this paper cites."""
    candidates = db.run(
        """
        MATCH (:Paper {id: $pid})-[:CITES]->(c:Paper)-[:HAS_LIMITATION]->(l:Limitation)
        RETURN c.title AS paper, l.name AS limitation
        """,
        pid=paper_id,
    )
    lim = extraction.extract_limitations(text, candidates)
    return lim, merge_entities(paper_id, lim, entities)


def merge_authors(paper_id: str, authors: list[dict]) -> list[str]:
    """Authors + institutions in one round-trip. Returns ids of NEW nodes."""
    rows = [
        {"name": a["name"].strip(), "inst": (a.get("institution") or "").strip(), "order": i}
        for i, a in enumerate(authors)
        if (a.get("name") or "").strip()
    ]
    if not rows:
        return []
    result = db.run(
        """
        MATCH (p:Paper {id: $pid})
        UNWIND $rows AS a
        OPTIONAL MATCH (ea:Author {name: a.name})
        OPTIONAL MATCH (ei:Institution {name: a.inst})
        WITH p, a, ea IS NULL AS new_author, (a.inst <> '' AND ei IS NULL) AS new_inst
        MERGE (au:Author {name: a.name})
        MERGE (p)-[w:WRITTEN_BY]->(au) SET w.order = a.order
        FOREACH (_ IN CASE WHEN a.inst <> '' THEN [1] ELSE [] END |
          MERGE (i:Institution {name: a.inst})
          MERGE (au)-[:AFFILIATED_WITH]->(i))
        RETURN a.name AS name, a.inst AS inst, new_author, new_inst
        """,
        pid=paper_id, rows=rows,
    )
    new_ids = [node_id("Author", r["name"]) for r in result if r["new_author"]]
    new_ids += [node_id("Institution", r["inst"]) for r in result if r["new_inst"]]
    return list(dict.fromkeys(new_ids))


# ---------- base graph ----------

def load_base(log=print):
    """Load data/base_papers.json + data/pdf/base/*.pdf into Neo4j (idempotent)."""
    db.setup_schema()
    papers = json.loads((config.DATA_DIR / "base_papers.json").read_text(encoding="utf-8"))
    pdf_dir = config.DATA_DIR / "pdf" / "base"

    # 1) structure from metadata
    db.run(
        """
        UNWIND $papers AS row
        MERGE (p:Paper {id: row.id})
        SET p.title = row.title, p.title_norm = row.tn, p.year = row.year,
            p.is_stub = false, p.source = 'base', p.was_stub = false
        MERGE (v:Venue {name: row.venue})
        MERGE (p)-[:PUBLISHED_IN]->(v)
        """,
        papers=[{"id": p["id"], "title": p["title"], "tn": norm(p["title"]), "year": p["year"], "venue": p["venue"]}
                for p in papers],
    )
    for p in papers:
        merge_authors(p["id"], p["authors"])
    db.run(
        """
        UNWIND $cites AS c
        MATCH (src:Paper {id: c.src})
        MERGE (dst:Paper {id: c.dst})
          ON CREATE SET dst.title = c.title, dst.title_norm = c.tn,
                        dst.is_stub = true, dst.source = 'stub-base'
        MERGE (src)-[r:CITES]->(dst) SET r.intent = c.intent
        """,
        cites=[{"src": p["id"], "dst": c["id"], "title": c["title"], "tn": norm(c["title"]), "intent": c["intent"]}
               for p in papers for c in p["cites"]],
    )
    log(f"Loaded structure for {len(papers)} papers")

    # 2) meaning from the PDFs (LLM extraction) + embeddings.
    # Oldest first, so the limitations of cited papers exist before later papers are read.
    for p in sorted(papers, key=lambda p: (p["year"], p["id"])):
        text = extraction.pdf_to_text(pdf_dir / p["pdf_file"])
        abstract = extraction.find_abstract(text)
        db.run(
            "MATCH (p:Paper {id: $id}) SET p.abstract = $abstract, p.is_survey = $survey, p.embedding = $emb",
            id=p["id"], abstract=abstract, survey=extraction.is_survey(text),
            emb=llm.embed(f"{p['title']}\n\n{abstract}"),
        )
        snap = snapshot()
        sem = extraction.extract_semantic(text, known_entities(snap))
        merge_entities(p["id"], sem, snap["entities"])
        lim, _ = link_limitations(p["id"], text, snapshot()["entities"])
        log(f"  {p['id']}: {len(sum(sem.values(), []))} entities, "
            f"limitations {lim['limitations']}, resolves {lim['resolves']}")

    algo = db.run_graph_algorithms()
    stubs = db.run("MATCH (s:Paper {is_stub: true}) RETURN s.id AS id, COUNT { (s)<-[:CITES]-() } AS cited_by")
    log(f"Graph algorithms: {algo}. Stub papers (cited but not loaded): {stubs}")


# ---------- live upload ----------

def paper_links(paper_id: str) -> list[dict]:
    rows = db.run(
        """
        MATCH (p:Paper {id: $pid})-[r]-(n)
        RETURN startNode(r) = p AS outgoing, type(r) AS type,
               labels(n)[0] AS label, coalesce(n.id, n.key, n.name) AS key
        """,
        pid=paper_id,
    )
    me = node_id("Paper", paper_id)
    links = []
    for r in rows:
        other = node_id(r["label"], r["key"])
        src, dst = (me, other) if r["outgoing"] else (other, me)
        links.append({"source": src, "target": dst, "type": r["type"]})
    return links


def ingest_upload(pdf_path: Path) -> dict:
    snap = snapshot()
    text = extraction.pdf_to_text(pdf_path)
    data = extraction.extract_full(text, known_entities(snap))
    title = (data.get("title") or pdf_path.stem).strip()

    match = find_paper_by_title(title, snap["papers"])
    if match and not match["is_stub"]:
        return {"status": "exists", "paper": {"id": match["id"], "title": title}}

    filled_stub = bool(match)
    paper_id = match["id"] if match else upload_paper_id(title, snap["papers"])
    new_nodes = [] if filled_stub else [node_id("Paper", paper_id)]

    # paper + venue + embedding in one write; also reports citations that already pointed here
    incoming = db.run(
        """
        MERGE (p:Paper {id: $id})
        WITH p, COUNT { (p)<-[:CITES]-() } AS incoming
        SET p.title = $title, p.title_norm = $tn, p.year = $year, p.abstract = $abstract,
            p.is_stub = false, p.source = 'upload', p.was_stub = $was_stub,
            p.is_survey = $survey, p.embedding = $emb
        FOREACH (_ IN CASE WHEN $venue <> '' THEN [1] ELSE [] END |
          MERGE (v:Venue {name: $venue})
          MERGE (p)-[:PUBLISHED_IN]->(v))
        RETURN incoming
        """,
        id=paper_id, title=title, tn=norm(title), year=data.get("year"), abstract=data["abstract"],
        was_stub=filled_stub, survey=extraction.is_survey(text),
        emb=llm.embed(f"{title}\n\n{data['abstract']}"), venue=(data.get("venue") or "").strip(),
    )[0]["incoming"]

    new_nodes += merge_authors(paper_id, data["authors"])

    # references: resolve against the snapshot, then write all CITES in one go
    resolved_refs, ref_rows = [], []
    for ref in data["references"]:
        ref_title = (ref.get("title") or "").strip()
        if not ref_title:
            continue
        target = find_paper_by_title(ref_title, snap["papers"])
        target_id = target["id"] if target else short_id("S", ref_title)
        if not target:
            new_nodes.append(node_id("Paper", target_id))
        ref_rows.append({"id": target_id, "title": ref_title, "tn": norm(ref_title),
                         "intent": ref.get("intent", "background")})
        resolved_refs.append({"title": ref_title, "matched_id": target_id if target else None})
    if ref_rows:
        db.run(
            """
            MATCH (p:Paper {id: $pid})
            UNWIND $refs AS r
            MERGE (t:Paper {id: r.id})
              ON CREATE SET t.title = r.title, t.title_norm = r.tn,
                            t.is_stub = true, t.source = 'stub-upload'
            MERGE (p)-[c:CITES]->(t) SET c.intent = r.intent
            """,
            pid=paper_id, refs=ref_rows,
        )

    new_nodes += merge_entities(paper_id, data, snap["entities"])
    lim, lim_new = link_limitations(paper_id, text, snap["entities"])
    data.update(lim)
    new_nodes += lim_new
    db.run_graph_algorithms()

    return {
        "status": "ingested",
        "paper": {"id": paper_id, "title": title, "year": data.get("year"), "filled_stub": filled_stub},
        "citations_lit_up": incoming,
        "references": resolved_refs,
        "extracted": {k: data.get(k, []) for k in
                      ("authors", "proposes", "uses", "datasets", "tasks", "limitations", "resolves")},
        "new_nodes": list(dict.fromkeys(new_nodes)),
        "new_links": paper_links(paper_id),
    }


def reset_demo() -> dict:
    """Undo all live uploads so the demo can be rehearsed again."""
    restored = db.run(
        """
        MATCH (p:Paper {source: 'upload', was_stub: true})
        OPTIONAL MATCH (p)-[r]->()
        DELETE r
        WITH DISTINCT p
        REMOVE p.abstract, p.embedding, p.year, p.is_survey
        SET p.is_stub = true, p.source = 'stub-base', p.was_stub = false
        RETURN count(p) AS n
        """
    )[0]["n"]
    removed = db.run(
        "MATCH (p:Paper) WHERE p.source = 'upload' OR p.source = 'stub-upload' "
        "DETACH DELETE p RETURN count(*) AS n"
    )[0]["n"]
    db.run("MATCH (a:Author) WHERE NOT (a)<-[:WRITTEN_BY]-() DETACH DELETE a")
    db.run(
        """
        MATCH (n)
        WHERE (n:Institution AND NOT (n)<-[:AFFILIATED_WITH]-())
           OR (n:Venue AND NOT (n)<-[:PUBLISHED_IN]-())
           OR ((n:Method OR n:Dataset OR n:Task OR n:Limitation) AND NOT (n)--())
        DELETE n
        """
    )
    db.run_graph_algorithms()
    return {"restored_stubs": restored, "removed_papers": removed}
