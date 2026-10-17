"""Settings loaded from the project-root .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
LIVE_UPLOAD_DIR = DATA_DIR / "pdf" / "uploaded_live"

load_dotenv(ROOT_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
# stronger model for the one judgment the small model gets wrong (does paper B fix A's weakness?)
OPENAI_JUDGE_MODEL = os.getenv("OPENAI_JUDGE_MODEL", "gpt-4o")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
EMBED_DIMENSIONS = 1536  # text-embedding-3-small

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# Aura's credentials file uses NEO4J_USERNAME (often the instance id, not "neo4j")
NEO4J_USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or None

CACHE_DIR.mkdir(parents=True, exist_ok=True)
LIVE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
