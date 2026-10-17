"""Score the LLM extraction of the 3 upload PDFs against data/upload_ground_truth.json.

Run from the backend folder AFTER load_base (it uses the base graph's vocabulary):
    python -m scripts.score_extraction

Side effect: the extractions are cached in data/cache, so the live demo upload
reuses them (works offline, same result every time).
"""
import json

from app import config, extraction, ingest


def prf(pred: list[str], gold: list[str]) -> tuple[int, int, int]:
    p = {ingest.norm(x) for x in pred}
    g = {ingest.norm(x) for x in gold}
    return len(p & g), len(p), len(g)


def main():
    truth = json.loads((config.DATA_DIR / "upload_ground_truth.json").read_text(encoding="utf-8"))
    known = ingest.known_entities()
    totals = {}
    for paper in truth:
        text = extraction.pdf_to_text(config.DATA_DIR / "pdf" / "upload" / paper["pdf_file"])
        data = extraction.extract_full(text, known)
        gold = dict(paper["ground_truth"])
        gold["references"] = [c["title"] for c in paper["cites"]]
        gold["authors"] = [a["name"] for a in paper["authors"]]
        pred = {k: data.get(k, []) for k in ("proposes", "uses", "datasets", "tasks")}
        pred["references"] = [r.get("title", "") for r in data.get("references", [])]
        pred["authors"] = [a.get("name", "") for a in data.get("authors", [])]

        print(f"\n{paper['id']}  {paper['title']}")
        for field in gold:
            hit, np_, ng = prf(pred[field], gold[field])
            t = totals.setdefault(field, [0, 0, 0])
            t[0] += hit; t[1] += np_; t[2] += ng
            missed = sorted({ingest.norm(x) for x in gold[field]} - {ingest.norm(x) for x in pred[field]})
            print(f"  {field:<11} {hit}/{ng} found" + (f"   missed: {missed}" if missed else ""))

    print("\nOverall")
    hit_all = gold_all = pred_all = 0
    for field, (hit, np_, ng) in totals.items():
        hit_all += hit; pred_all += np_; gold_all += ng
        print(f"  {field:<11} precision {hit / max(np_, 1):.0%}  recall {hit / max(ng, 1):.0%}")
    print(f"  ALL         precision {hit_all / max(pred_all, 1):.0%}  recall {hit_all / max(gold_all, 1):.0%}")


if __name__ == "__main__":
    main()
