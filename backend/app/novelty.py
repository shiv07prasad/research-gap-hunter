"""Research idea -> novelty verdict.

Pipeline: decompose idea (LLM) -> vector seeds -> graph expansion
-> re-rank -> novelty matrix (LLM) -> graph gap check -> verdict + evidence.
"""
import json
from itertools import combinations

from . import db, llm
from .ingest import known_entities, node_id, norm

DECOMPOSE_SYSTEM = """You break a research idea into its 3-6 essential components.
Every distinct requirement in the idea must become exactly one component: the core approach,
any model constraint (e.g. model size), the problem/task, the application domain together with
its task (do not split "medical" and "medical QA" into two), and any named dataset.
Never drop a requirement the idea states explicitly.
Return JSON: {"components": [{"label": str, "entity": str | null, "entity_type": "Method" | "Dataset" | "Task" | null}]}
- "label": a short, specific, UNIQUE name for what the component is (2-4 words), e.g.
  "Knowledge graph grounding", "Medical domain", "Small language models", "Hallucination reduction".
  Never use category names like "Task" or "Core Approach".
- "entity": if the component means the same as one of the KNOWN names (synonyms count), copy that name exactly; else null.
- Only use names from the KNOWN lists for "entity"."""

MATRIX_SYSTEM = """You compare a research idea against existing papers.
For every paper and every component, decide coverage: "yes" (paper clearly does this),
"partial" (related but weaker/different), or "no".
Return JSON: {
  "rows": [{"paper_id": str, "cells": {"<component label>": "yes"|"partial"|"no"}, "note": str}],
  "summary": str,   // 2-3 sentences: what already exists and how close it is
  "gap": str        // 1-2 sentences: what exact combination is still open, or "none" if fully covered
}
"note": one short sentence on how this paper relates to the idea. Base answers only on the given paper info.
Be strict:
- "yes" only if the paper explicitly does that component.
- "partial" only for a weaker or adjacent version of the same thing (e.g. clinical drug lookup vs medical QA).
- The opposite of a requirement is "no", not "partial" (e.g. a 70B model when small models are required;
  a general-domain paper when a medical domain is required; a different dataset when a named dataset is required)."""

SEED_K = 8
MATRIX_PAPERS = 7


def _decompose(idea: str) -> list[dict]:
    known = {k: v for k, v in known_entities().items() if k != "Limitation"}
    known_text = "\n".join(f"KNOWN {k.upper()}: {', '.join(sorted(v))}" for k, v in known.items())
    # cached per idea so the matrix columns stay identical before and after uploads
    comps = llm.chat_json(
        DECOMPOSE_SYSTEM, f"{known_text}\n\nIDEA: {idea}", cache_key=DECOMPOSE_SYSTEM + idea
    ).get("components", [])
    known_keys = {(label, norm(n)) for label, names in known.items() for n in names}
    seen: dict[str, int] = {}
    for c in comps:
        label = c.get("label") or "Component"
        seen[label] = seen.get(label, 0) + 1
        c["label"] = label if seen[label] == 1 else f"{label} ({seen[label]})"
        valid = (c.get("entity_type"), norm(c.get("entity") or "")) in known_keys
        c["key"] = norm(c["entity"]) if valid else None
        if not valid:
            c["entity"] = c["entity_type"] = None
    return comps


def _similarities(idea: str) -> dict[str, float]:
    """Text similarity of the idea to every embedded paper, highest first."""
    rows = db.run(
        "CALL db.index.vector.queryNodes('paper_embedding', $k, $v) YIELD node, score "
        "RETURN node.id AS id, score ORDER BY score DESC",
        k=200, v=llm.embed(idea),
    )
    return {r["id"]: r["score"] for r in rows}


def _new_cand() -> dict:
    return {"reasons": [], "cited_by_seeds": 0, "cites_seeds": 0, "overlap": 0}


def _idea_links(components: list[dict]) -> dict[str, set[tuple[str, str]]]:
    """Paper id -> which of the idea's components (label, key) it links to. One round-trip."""
    ents = [{"label": c["entity_type"], "key": c["key"]} for c in components if c.get("key")]
    if not ents:
        return {}
    rows = db.run(
        """
        UNWIND $ents AS ent
        MATCH (p:Paper)-->(e {key: ent.key}) WHERE ent.label IN labels(e)
        RETURN p.id AS id, collect(DISTINCT [ent.label, ent.key]) AS links
        """,
        ents=ents,
    )
    return {r["id"]: {tuple(x) for x in r["links"]} for r in rows}


def _expand(seed_ids: list[str], overlap: dict[str, int]) -> dict[str, dict]:
    cands: dict[str, dict] = {}

    def add(pid, reason, **signals):
        c = cands.setdefault(pid, _new_cand())
        c["reasons"].append(reason)
        c.update(signals)

    rows = db.run(
        """
        CALL {
          MATCH (s:Paper)-[:CITES]->(f:Paper)
          WHERE s.id IN $seeds AND NOT f.id IN $seeds
          WITH f, count(DISTINCT s) AS support WHERE support >= 2
          RETURN f.id AS id, support, 'cited_by' AS kind
          UNION
          MATCH (f:Paper)-[:CITES]->(s:Paper)
          WHERE s.id IN $seeds AND NOT f.id IN $seeds
          WITH f, count(DISTINCT s) AS support WHERE support >= 2
          RETURN f.id AS id, support, 'cites' AS kind
        }
        RETURN id, support, kind ORDER BY kind DESC, id
        """,
        seeds=seed_ids,
    )
    for r in rows:
        if r["kind"] == "cited_by":
            add(r["id"], f"cited by {r['support']} of the closest papers", cited_by_seeds=r["support"])
        else:
            add(r["id"], f"builds on {r['support']} of the closest papers", cites_seeds=r["support"])

    for pid, n in overlap.items():
        if n >= 2:
            add(pid, f"shares {n} idea components")
    return cands


def _paper_info(ids: list[str]) -> list[dict]:
    return db.run(
        """
        MATCH (p:Paper) WHERE p.id IN $ids
        OPTIONAL MATCH (p)-[:PROPOSES|USES|EVALUATES_ON|ADDRESSES]->(e)
        WITH p, collect(DISTINCT e.name) AS entities
        OPTIONAL MATCH (p)-[:WRITTEN_BY]->(a:Author)
        RETURN p.id AS id, p.title AS title, p.year AS year, p.abstract AS abstract,
               p.is_stub AS is_stub, coalesce(p.is_survey, false) AS is_survey,
               coalesce(p.pagerank, 0.0) AS pagerank,
               COUNT { (p)<-[:CITES]-() } AS cited_by, entities, collect(DISTINCT a.name) AS authors
        """,
        ids=ids,
    )


def _graph_gaps(components: list[dict], links: dict[str, set[tuple[str, str]]]) -> dict:
    """Which pairs of the idea's components no paper combines (computed from _idea_links)."""
    ents = [c for c in components if c.get("key")]
    pair_counts = []
    for a, b in combinations(ents, 2):
        ka, kb = (a["entity_type"], a["key"]), (b["entity_type"], b["key"])
        n = sum(1 for s in links.values() if ka in s and kb in s)
        pair_counts.append({"a": a["entity"], "b": b["entity"], "papers": n})
    all_n = None
    if len(ents) >= 2:
        wanted = {(c["entity_type"], c["key"]) for c in ents}
        all_n = sum(1 for s in links.values() if wanted <= s)
    return {
        "pairs": pair_counts,
        "never_combined": [p for p in pair_counts if p["papers"] == 0],
        "papers_with_all_components": all_n,
    }


def _weaknesses(paper_ids: list[str]) -> list[dict]:
    """Limitations of the closest papers and whether a later paper resolved them."""
    if not paper_ids:
        return []
    rows = db.run(
        """
        UNWIND range(0, size($ids) - 1) AS i
        MATCH (p:Paper {id: $ids[i]})-[:HAS_LIMITATION]->(l:Limitation)
        OPTIONAL MATCH (f:Paper)-[:RESOLVES]->(l)
        RETURN i, p.id AS paper_id, l.name AS limitation, collect(f.id) AS resolved_by
        ORDER BY i, limitation
        """,
        ids=paper_ids,
    )
    return [{k: r[k] for k in ("paper_id", "limitation", "resolved_by")} for r in rows]


CELL_VALUE = {"yes": 1.0, "partial": 0.5, "no": 0.0}


def _coverage(row: dict, labels: list[str]) -> float:
    cells = row.get("cells", {})
    return sum(CELL_VALUE.get(cells.get(lbl, "no"), 0.0) for lbl in labels) / max(len(labels), 1)


def _verdict(best: float) -> str:
    if best >= 0.99:
        return "exists"
    if best >= 0.5:
        return "partial"
    return "novel"


def check_novelty(idea: str) -> dict:
    components = _decompose(idea)
    labels = [c["label"] for c in components]

    sims = _similarities(idea)
    seeds = list(sims)[:SEED_K]
    links = _idea_links(components)
    overlap = {pid: len(s) for pid, s in links.items()}
    cands = _expand(seeds, overlap)
    for pid in seeds:
        cands.setdefault(pid, _new_cand())
    for pid, c in cands.items():
        c["overlap"] = overlap.get(pid, 0)
        c["vector_score"] = sims.get(pid, 0.0)
        if pid in seeds:
            c["reasons"].insert(0, f"text similarity {sims[pid]:.2f}")

    info = {p["id"]: p for p in _paper_info(list(cands))}
    max_pr = max([p["pagerank"] for p in info.values()] + [1e-9])
    ranked = []
    for pid, c in cands.items():
        p = info.get(pid)
        if not p:
            continue
        c["score"] = (
            c.get("vector_score", 0.0)
            + 0.15 * c["cited_by_seeds"]
            + 0.10 * c["cites_seeds"]
            + 0.50 * c["overlap"]
            + 0.30 * (p["pagerank"] / max_pr)
        )
        ranked.append({**p, **c, "abstract": None})
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # surveys discuss everything but are not prior art, so they stay out of the matrix
    readable = [r for r in ranked if not r["is_stub"] and not r["is_survey"]][:MATRIX_PAPERS]
    surveys = [{"id": r["id"], "title": r["title"], "year": r["year"]} for r in ranked if r["is_survey"]]
    unread = [
        {"id": r["id"], "title": r["title"], "cited_by": r["cited_by"], "reasons": r["reasons"]}
        for r in ranked if r["is_stub"]
    ]

    matrix = {"rows": [], "summary": "", "gap": ""}
    if readable:
        papers_text = json.dumps(
            [
                {"paper_id": r["id"], "title": r["title"], "year": r["year"],
                 "abstract": info[r["id"]]["abstract"], "entities": r["entities"]}
                for r in readable
            ],
            indent=1,
        )
        # cached on the exact idea + paper set, so a rehearsed demo gives the same answer live
        matrix = llm.chat_json(
            MATRIX_SYSTEM,
            f"IDEA: {idea}\nCOMPONENTS: {json.dumps(labels)}\nPAPERS:\n{papers_text}",
        )

    by_id = {r["id"]: r for r in readable}
    rows = []
    for row in matrix.get("rows", []):
        p = by_id.get(row.get("paper_id"))
        if p:
            rows.append({**row, "title": p["title"], "year": p["year"], "authors": p["authors"],
                         "reasons": p["reasons"], "score": round(p["score"], 3),
                         "coverage": round(_coverage(row, labels), 2)})
    rows.sort(key=lambda r: r["coverage"], reverse=True)
    best_coverage = rows[0]["coverage"] if rows else 0.0

    # foundational papers oldest first; stubs (no year known) go last
    reading = sorted(
        [r for r in ranked if r["cited_by_seeds"] >= 2],
        key=lambda r: (r["is_stub"], r["year"] or 0, r["id"]),
    )
    authors: dict[str, int] = {}
    for r in readable:
        for a in r["authors"]:
            authors[a] = authors.get(a, 0) + 1

    highlight = {node_id("Paper", r["id"]) for r in ranked[:12]}
    highlight |= {node_id(c["entity_type"], c["key"]) for c in components if c.get("key")}

    return {
        "idea": idea,
        "verdict": _verdict(best_coverage),
        "best_coverage": best_coverage,
        "components": components,
        "matrix": rows,
        "summary": matrix.get("summary", ""),
        "gap": matrix.get("gap", ""),
        "graph_gaps": _graph_gaps(components, links),
        "unread_stubs": unread,
        "surveys": surveys,
        "weaknesses": _weaknesses([r["paper_id"] for r in rows[:3]]),
        "reading_path": [{"id": r["id"], "title": r["title"], "year": r["year"], "is_stub": r["is_stub"]} for r in reading],
        "people": sorted(authors, key=authors.get, reverse=True)[:5],
        "highlight_nodes": sorted(highlight),
    }
