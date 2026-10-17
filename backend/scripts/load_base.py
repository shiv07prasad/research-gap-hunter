"""Load the 17 base papers into Neo4j.

Run from the backend folder:
    python -m scripts.load_base          # idempotent load (MERGE)
    python -m scripts.load_base --wipe   # delete everything in the database first
"""
import sys

from app import db, ingest


def main():
    if "--wipe" in sys.argv:
        db.run("MATCH (n) DETACH DELETE n")
        print("Database wiped")
    ingest.load_base()
    print("Done. Open http://localhost:7474 and run: MATCH (n) RETURN n")


if __name__ == "__main__":
    main()
