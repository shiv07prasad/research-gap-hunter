"""Neo4j connection, schema setup and graph algorithms."""
from neo4j import GraphDatabase

from . import config

_driver = None


def driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
            notifications_min_severity="OFF",  # keep server deprecation hints out of the logs
        )
    return _driver


def run(query: str, **params) -> list[dict]:
    """Run a write-capable query and return records as dicts."""
    records, _, _ = driver().execute_query(query, params, database_=config.NEO4J_DATABASE)
    return [r.data() for r in records]


def run_read(query: str, **params) -> list[dict]:
    """Run a query in a READ transaction (Neo4j rejects any write)."""
    with driver().session(database=config.NEO4J_DATABASE) as session:
        return session.execute_read(lambda tx: [r.data() for r in tx.run(query, params)])


ENTITY_LABELS = ["Method", "Dataset", "Task", "Limitation"]
_gds_available: bool | None = None  # checked once, then remembered


def setup_schema():
    run("CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE")
    run("CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE")
    run("CREATE CONSTRAINT inst_name IF NOT EXISTS FOR (i:Institution) REQUIRE i.name IS UNIQUE")
    run("CREATE CONSTRAINT venue_name IF NOT EXISTS FOR (v:Venue) REQUIRE v.name IS UNIQUE")
    for label in ENTITY_LABELS:
        run(f"CREATE CONSTRAINT {label.lower()}_key IF NOT EXISTS FOR (n:{label}) REQUIRE n.key IS UNIQUE")
    run(
        "CREATE VECTOR INDEX paper_embedding IF NOT EXISTS FOR (p:Paper) ON p.embedding "
        "OPTIONS {indexConfig: {`vector.dimensions`: $dims, `vector.similarity_function`: 'cosine'}}",
        dims=config.EMBED_DIMENSIONS,
    )


def _python_graph_algorithms():
    """PageRank + label-propagation communities in plain Python.

    Used when the GDS plugin is missing (e.g. Aura Free). Same PageRank formula
    as GDS (damping 0.85, unnormalised), fine for a graph of a few hundred papers.
    """
    rows = run("MATCH (p:Paper) OPTIONAL MATCH (p)-[:CITES]->(t:Paper) RETURN p.id AS id, collect(t.id) AS cites")
    ids = [r["id"] for r in rows]
    edges = [(r["id"], t) for r in rows for t in r["cites"]]
    out_deg = {i: 0 for i in ids}
    incoming = {i: [] for i in ids}
    neighbours = {i: set() for i in ids}
    for s, t in edges:
        out_deg[s] += 1
        incoming[t].append(s)
        neighbours[s].add(t)
        neighbours[t].add(s)

    rank = {i: 1.0 for i in ids}
    for _ in range(40):
        rank = {i: 0.15 + 0.85 * sum(rank[s] / out_deg[s] for s in incoming[i]) for i in ids}

    community = {i: n for n, i in enumerate(sorted(ids))}
    for _ in range(10):
        changed = False
        for i in sorted(ids):
            if not neighbours[i]:
                continue
            counts: dict[int, int] = {}
            for n in neighbours[i]:
                counts[community[n]] = counts.get(community[n], 0) + 1
            best = min(counts, key=lambda c: (-counts[c], c))
            if best != community[i]:
                community[i], changed = best, True
        if not changed:
            break

    run(
        "UNWIND $rows AS row MATCH (p:Paper {id: row.id}) SET p.pagerank = row.pr, p.community = row.c",
        rows=[{"id": i, "pr": rank[i], "c": community[i]} for i in ids],
    )


def run_graph_algorithms() -> str:
    """PageRank (directed citations) + Louvain communities (undirected).

    Uses the GDS plugin when available, otherwise computes the same in Python.
    """
    global _gds_available
    if _gds_available is None:
        try:
            run("RETURN gds.version() AS v")
            _gds_available = True
        except Exception:
            _gds_available = False
    if not _gds_available:
        _python_graph_algorithms()
        return "python"
    try:
        for name in ("cit_dir", "cit_und"):
            run("CALL gds.graph.drop($name, false) YIELD graphName RETURN graphName", name=name)
        run("CALL gds.graph.project('cit_dir', 'Paper', 'CITES') YIELD graphName RETURN graphName")
        run(
            "CALL gds.graph.project('cit_und', 'Paper', {CITES: {orientation: 'UNDIRECTED'}}) "
            "YIELD graphName RETURN graphName"
        )
        run("CALL gds.pageRank.write('cit_dir', {writeProperty: 'pagerank'}) YIELD nodePropertiesWritten RETURN 1")
        run("CALL gds.louvain.write('cit_und', {writeProperty: 'community'}) YIELD communityCount RETURN 1")
        for name in ("cit_dir", "cit_und"):
            run("CALL gds.graph.drop($name, false) YIELD graphName RETURN graphName", name=name)
        return "gds"
    except Exception:
        _python_graph_algorithms()
        return "python"
