"""Free-form Q&A agent: OpenAI tool calling over the graph (read-only Cypher + vector search)."""
import json

from . import config, db, llm
from .ingest import node_id

SCHEMA = """Graph schema:
(:Paper {id, title, year, abstract, is_stub, pagerank, community})
(:Author {name}) (:Institution {name}) (:Venue {name})
(:Method {name, key}) (:Dataset {name, key}) (:Task {name, key}) (:Limitation {name, key})
(Paper)-[:CITES {intent: 'background'|'method'|'result'}]->(Paper)
(Paper)-[:WRITTEN_BY]->(Author)-[:AFFILIATED_WITH]->(Institution)
(Paper)-[:PUBLISHED_IN]->(Venue)
(Paper)-[:PROPOSES|USES]->(Method), (Paper)-[:EVALUATES_ON]->(Dataset), (Paper)-[:ADDRESSES]->(Task)
(Paper)-[:HAS_LIMITATION]->(Limitation)<-[:RESOLVES]-(later Paper that overcomes it)
Stub papers (is_stub = true) are cited by others but their text is not loaded yet.
Entity `key` is the lowercased name; match names case-insensitively with toLower()."""

SYSTEM = f"""You are a research assistant answering questions about a graph of research papers.
Use the tools to look things up before answering; never invent papers.
For any question about approaches, their limitations/weaknesses/open problems, or which papers
address them, call explore_limitations first.
{SCHEMA}
Answer concisely and cite paper titles with their ids, e.g. "GraphVerify (P08)".
When listing limitations, say which paper resolved each one, or that it is still open."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_cypher",
            "description": "Run a READ-ONLY Cypher query against the paper graph. Always add a LIMIT.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Semantic search over paper titles and abstracts.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}, "k": {"type": "integer", "default": 5}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explore_limitations",
            "description": (
                "For a research topic: the closest papers, the approaches they propose, each paper's "
                "limitations, and which later papers resolve each limitation (or that it is still open)."
            ),
            "parameters": {
                "type": "object",
                "properties": {"topic": {"type": "string"}, "k": {"type": "integer", "default": 8}},
                "required": ["topic"],
            },
        },
    },
]


def explore_limitations(topic: str, k: int = 8) -> list[dict]:
    """Topic -> Paper -> approaches -> Limitation -> resolving papers. Two round-trips."""
    seeds = db.run_read(
        "CALL db.index.vector.queryNodes('paper_embedding', $k, $v) YIELD node "
        "WHERE coalesce(node.is_survey, false) = false RETURN node.id AS id",
        k=k, v=llm.embed(topic),
    )
    rows = db.run_read(
        """
        UNWIND $ids AS pid
        MATCH (p:Paper {id: pid})-[:HAS_LIMITATION]->(l:Limitation)
        OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
        OPTIONAL MATCH (fix:Paper)-[:RESOLVES]->(l)
        WITH p, l, collect(DISTINCT m {.name, .key}) AS approaches,
             collect(DISTINCT fix {.id, .title, .year}) AS fixes
        RETURN p.id AS paper_id, p.title AS title, p.year AS year, approaches,
               l.name AS limitation, l.key AS key, fixes
        ORDER BY p.year, p.id
        """,
        ids=[s["id"] for s in seeds],
    )
    papers: dict[str, dict] = {}
    for r in rows:
        p = papers.setdefault(r["paper_id"], {
            "paper_id": r["paper_id"], "title": r["title"], "year": r["year"],
            "approaches": r["approaches"], "limitations": [],
        })
        p["limitations"].append({"name": r["limitation"], "key": r["key"], "resolved_by": r["fixes"]})
    return list(papers.values())


def _path_nodes(paths: list[dict]) -> set[str]:
    nodes = set()
    for p in paths:
        nodes.add(node_id("Paper", p["paper_id"]))
        nodes |= {node_id("Method", m["key"]) for m in p["approaches"]}
        for lim in p["limitations"]:
            nodes.add(node_id("Limitation", lim["key"]))
            nodes |= {node_id("Paper", f["id"]) for f in lim["resolved_by"]}
    return nodes


def _run_tool(name: str, args: dict):
    try:
        if name == "explore_limitations":
            return explore_limitations(args["topic"], int(args.get("k", 8)))
        if name == "run_cypher":
            return db.run_read(args["query"])[:50]
        if name == "search_papers":
            return db.run_read(
                "CALL db.index.vector.queryNodes('paper_embedding', $k, $v) YIELD node, score "
                "RETURN node.id AS id, node.title AS title, node.year AS year, score",
                k=int(args.get("k", 5)), v=llm.embed(args["text"]),
            )
    except Exception as exc:  # return the error so the model can fix its query
        return {"error": str(exc)}
    return {"error": f"unknown tool {name}"}


def ask(question: str, max_steps: int = 6) -> dict:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    trace, paths = [], []

    def done(answer: str) -> dict:
        return {"answer": answer, "trace": trace, "paths": paths,
                "highlight_nodes": sorted(_path_nodes(paths))}

    for _ in range(max_steps):
        resp = llm.client().chat.completions.create(
            model=config.OPENAI_CHAT_MODEL, messages=messages, tools=TOOLS, temperature=0
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return done(msg.content)
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = _run_tool(call.function.name, args)
            if call.function.name == "explore_limitations" and isinstance(result, list):
                paths = result  # shown as chains in the UI and highlighted in the graph
            trace.append({"tool": call.function.name, "args": args})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, default=str)})
    return done("I ran out of steps before finishing. Try a more specific question.")
