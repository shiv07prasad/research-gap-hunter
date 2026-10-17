"""Hugging Face Spaces entry point.

The Space uses the (free) Gradio SDK, which simply runs `python app.py`. Instead of a
Gradio UI we start our own FastAPI app on port 7860; it serves the API under /api and the
prebuilt React UI (frontend/dist) at /. Secrets come from the Space settings:
OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD.
"""
import sys
from pathlib import Path

import uvicorn

# backend/ first on the path, so `app` resolves to the backend package, not this file
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.main import app as fastapi_app  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)
