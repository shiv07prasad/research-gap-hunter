"""PDF -> text -> structured JSON via the LLM."""
import re
from pathlib import Path

import pymupdf

from . import config, llm


def pdf_to_text(path: Path) -> str:
    with pymupdf.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def find_abstract(text: str) -> str:
    match = re.search(
        r"Abstract[:\s]*(.+?)\s*(?:Keywords|Key words|1\.?\s+Introduction)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    abstract = match.group(1) if match else text[:1500]
    return re.sub(r"\s+", " ", abstract).strip()


ENTITY_RULES = """\
Entity rules:
- "proposes": new methods/systems/benchmarks this paper introduces (usually named in the title).
- "uses": existing methods, techniques, models or concepts the paper builds on or relies on.
- "datasets": datasets or benchmarks the paper evaluates on or builds.
- "tasks": problems the paper addresses.
- Use short canonical names (e.g. "Knowledge Graph", "Small Language Model", "Medical QA").
- "uses" must contain BOTH the named systems the paper builds on AND the general technique
  categories it relies on, even when the paper describes them in its own words. Always add:
  "Knowledge Graph" if it grounds, stores or verifies facts as structured entities/relations;
  "Small Language Model" if it uses a compact/lightweight model (under ~8B parameters);
  "Large Language Model" if it relies on a large model (tens of billions of parameters).
- "tasks" must include the general problem too: "Hallucination Reduction" if it reduces
  fabricated or unsupported output; "Medical QA" only if the paper itself answers
  medical/clinical questions (not if medicine is only mentioned as future work or elsewhere).
- Survey/review papers discuss other work but do not use it: for a survey, leave "proposes",
  "uses" and "datasets" empty and only list the overall topic in "tasks".
- KNOWN NAMES below already exist in our graph. If an entity means the same thing as a known
  name - even with different wording or synonyms (e.g. "entity-relation store" means
  "Knowledge Graph", "lightweight model" means "Small Language Model", "avoiding fabricated
  output" means "Hallucination Reduction") - output the known name exactly.
"""

SEMANTIC_SYSTEM = f"""You extract research knowledge from academic papers.
Return a JSON object: {{"proposes": [], "uses": [], "datasets": [], "tasks": []}} (lists of strings).
{ENTITY_RULES}"""

OWN_LIMITATIONS_SYSTEM = """You read one academic paper and list the weaknesses of ITS OWN proposed method.
Return JSON: {"limitations": [str]}
- 1-3 items, taken from what this paper says about its own method in its results or conclusion
  (e.g. "still ...", "remains ...", "limitation", "cannot ...", "requires ...").
- Ignore weaknesses the paper attributes to other work, baselines or cited papers.
- Each item is a short general phrase of 3-6 words, e.g. "Requires data-center hardware",
  "Weak multi-hop reasoning", "Fabricates drug interactions"."""

RESOLVES_SYSTEM = """You decide which weaknesses of earlier work a paper overcomes.
You get CANDIDATE weaknesses (each from a paper this paper cites) and the paper text.
For EVERY candidate decide whether this paper's own method overcomes it.
Be strict - "overcome" is true ONLY when the paper's main contribution directly removes that
weakness and the text shows it (e.g. a 3B on-device model overcomes "requires data-center
hardware"; graph-based multi-step evidence overcomes "weak multi-hop reasoning").
It also counts when the paper reports that it substantially reduces that weakness
(e.g. "closes most of X's multi-hop gap").
It is FALSE when the paper merely cites, uses, extends, evaluates or builds on that work, when it
still has the same weakness, or when the weakness is unrelated to what the paper does.
Default to false when unsure. Most candidates should be false.
Return JSON: {"decisions": [{"limitation": str, "evidence": str, "overcome": bool}]}
Copy each candidate's text exactly into "limitation". Write "evidence" (one short quote or
paraphrase from THIS paper) before deciding "overcome"."""

FULL_SYSTEM = f"""You extract structured metadata and research knowledge from academic papers.
Return a JSON object with exactly these keys:
{{
  "title": str,
  "authors": [{{"name": str, "institution": str}}],
  "venue": str,
  "year": int,
  "references": [{{"title": str, "intent": "background" | "method" | "result"}}],
  "proposes": [str], "uses": [str], "datasets": [str], "tasks": [str]
}}
For each reference, read how the body text uses it: "method" if the paper builds on or reuses
its method, "result" if it compares against or reuses its results/benchmark, else "background".
Reference titles must be copied exactly from the References section, without authors or venue.
{ENTITY_RULES}"""


def _known_block(known: dict[str, list[str]]) -> str:
    lines = [f"KNOWN {label.upper()} NAMES: {', '.join(sorted(names)) or '(none)'}" for label, names in known.items()]
    return "\n".join(lines)


def is_survey(text: str) -> bool:
    """Surveys discuss methods without using them, so they must not 'cover' an idea."""
    return bool(re.search(r"\b(a survey|survey of|a review|review of)\b", text[:400], re.IGNORECASE))


FIELD_FOR_LABEL = {"Method": "uses", "Dataset": "datasets", "Task": "tasks"}


def _add_literal_mentions(data: dict, text: str, known: dict[str, list[str]]) -> dict:
    """Safety net: a known entity named verbatim in the title/abstract is always linked."""
    head = (text[:300] + " " + find_abstract(text)).lower()
    present = {n.lower() for k in FIELD_FOR_LABEL.values() for n in data.get(k, [])}
    present |= {n.lower() for n in data.get("proposes", [])}
    for label, names in known.items():
        field = FIELD_FOR_LABEL.get(label)
        if not field:  # limitations are phrases, not names - no literal matching
            continue
        for name in names:
            if len(name) >= 6 and name.lower() not in present and re.search(rf"\b{re.escape(name.lower())}\b", head):
                data.setdefault(field, []).append(name)
                present.add(name.lower())
    return data


def _drop_survey_usage(data: dict, text: str) -> dict:
    if is_survey(text):
        for k in ("proposes", "uses", "datasets", "limitations", "resolves"):
            data[k] = []
    return data


ENTITY_FIELDS = ("proposes", "uses", "datasets", "tasks")


def extract_limitations(text: str, candidates: list[dict]) -> dict:
    """Own limitations + which cited-paper limitations this paper resolves.

    `candidates` come from the graph: limitations of the papers this paper cites,
    so "resolves" can only point at Limitation nodes that really exist.
    """
    if is_survey(text):
        return {"limitations": [], "resolves": []}
    own = llm.chat_json(OWN_LIMITATIONS_SYSTEM, f"PAPER TEXT:\n{text}", cache_key=OWN_LIMITATIONS_SYSTEM + text)
    resolves = []
    if candidates:
        cand_text = "\n".join(f"- {c['limitation']}  (weakness of: {c['paper']})" for c in candidates)
        data = llm.chat_json(
            RESOLVES_SYSTEM,
            f"CANDIDATES:\n{cand_text}\n\nPAPER TEXT:\n{text}",
            cache_key=RESOLVES_SYSTEM + cand_text + text,
            model=config.OPENAI_JUDGE_MODEL,
        )
        names = {c["limitation"].lower(): c["limitation"] for c in candidates}
        # keep only exact candidate names, so RESOLVES always lands on a real node
        resolves = [
            names[d["limitation"].strip().lower()]
            for d in data.get("decisions", [])
            if d.get("overcome") is True and (d.get("limitation") or "").strip().lower() in names
        ]
    return {
        "limitations": [s.strip() for s in own.get("limitations", []) if s and s.strip()][:3],
        "resolves": list(dict.fromkeys(resolves)),
    }


def extract_semantic(text: str, known: dict[str, list[str]]) -> dict:
    data = llm.chat_json(SEMANTIC_SYSTEM, f"{_known_block(known)}\n\nPAPER TEXT:\n{text}", cache_key=SEMANTIC_SYSTEM + text)
    data = {k: [s.strip() for s in data.get(k, []) if s and s.strip()] for k in ENTITY_FIELDS}
    return _drop_survey_usage(_add_literal_mentions(data, text, known), text)


def extract_full(text: str, known: dict[str, list[str]]) -> dict:
    data = llm.chat_json(FULL_SYSTEM, f"{_known_block(known)}\n\nPAPER TEXT:\n{text}", cache_key=FULL_SYSTEM + text)
    for k in (*ENTITY_FIELDS, "references", "authors"):
        data.setdefault(k, [])
    data["abstract"] = find_abstract(text)
    return _drop_survey_usage(_add_literal_mentions(data, text, known), text)
