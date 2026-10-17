# Research Gap Hunter: one container that serves the React UI and the FastAPI backend.
# Deployed on Render (see render.yaml); also works on any Docker host. Secrets come from
# the host's environment settings:
#   OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# --- 1) build the React frontend ---
FROM node:20-slim AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# --- 2) Python backend that also serves the built frontend ---
FROM python:3.10-slim
# Spaces run the container as user 1000; data/ must be writable for the LLM cache and uploads
RUN useradd -m -u 1000 user
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY --chown=user backend/ backend/
COPY --chown=user data/ data/
COPY --from=frontend --chown=user /build/dist frontend/dist

USER user
ENV PYTHONUNBUFFERED=1
EXPOSE 7860
# Render tells the app which port to use through $PORT; default to 7860 elsewhere
CMD ["sh", "-c", "python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-7860}"]
