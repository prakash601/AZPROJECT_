# Problem Finder

Hybrid search engine for coding problems — **semantic + keyword + fuzzy** search
merged via Reciprocal Rank Fusion (RRF), backed by PostgreSQL + pgvector.

## Architecture

```
┌─────────────────┐     /api/search       ┌──────────────────┐
│  React SPA      │ ─────────────────────▶ │  FastAPI         │
│  (Vite, dark    │  /api/autocomplete     │  (uvicorn)       │
│   mode, a11y)   │ ◀──────────────────── │                  │
└─────────────────┘     JSON                └────────┬─────────┘
                                                      │
                                    ┌─────────────────┴────────────┐
                                    │  search.py (RRF fusion)     │
                                    │  correct.py (spell-check)   │
                                    │  sentence-transformers       │
                                    │  (all-MiniLM-L6-v2, 384d)   │
                                    └─────────────────┬────────────┘
                                                      │
                                    ┌─────────────────┴────────────┐
                                    │  PostgreSQL + pgvector      │
                                    │  (FTS, trigram, HNSW index) │
                                    └────────────────────────────┘
```

- **`main.py`** — FastAPI app setup, middleware, and router registration.
- **`api/routes.py`** — HTTP API routes and response models: `/api/health`,
  `/api/search`, and `/api/autocomplete`. Interactive docs at `/docs`.
- **`search.py`** — RRF search (semantic + FTS + trigram) and autocomplete.
- **`correct.py`** — Norvig spell-correct + `correct_query()` for "Did you mean".
- **`db.py`** — Threaded PostgreSQL connection pool with pgvector support.
- **`generate_embeddings.py`** — Batch-embed problems with all-MiniLM-L6-v2.
- **`migrate.py`** — Load problem data into PostgreSQL.
- **`init.sql`** — Schema: `problems` table with `search_vector` (FTS),
  `embedding vector(384)`, trigram + HNSW indexes.
- **`frontend/`** — React + Vite SPA. See `frontend/README.md`.

## Quick Start (local dev)

### 1. Database

```bash
docker compose up -d postgres      # pgvector/pgvector:pg16
```

### 2. Backend (FastAPI)

```bash
pip install -r requirements.txt
export $(cat .env | xargs)         # DB credentials
uvicorn main:app --reload          # http://localhost:8000
```

First run: migrate data and generate embeddings (one-time):

```bash
python migrate.py
python generate_embeddings.py
```

### 3. Frontend (React SPA)

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The Vite dev server proxies `/api` → `http://127.0.0.1:8000`, so the SPA and
API work together with no CORS configuration in development.

## API

| Endpoint                       | Description                                  |
| ------------------------------ | -------------------------------------------- |
| `GET /api/health`              | Liveness check                               |
| `GET /api/search?q=&limit=&offset=` | Hybrid search (semantic+FTS+trigram)  |
| `GET /api/autocomplete?prefix=&limit=` | Prefix + trigram suggestions           |

FastAPI auto-generates interactive docs at `/docs` and `/redoc`.

## Deployment

- **Backend:** Render (`render.yaml`). `uvicorn main:app --host 0.0.0.0 --port $PORT`.
  Set env vars: `DB_*`, `SECRET_KEY`, `FRONTEND_ORIGIN`.
- **Frontend:** Vercel/Netlify (`frontend/vercel.json`). Build: `npm run build`,
  output: `dist`. Set `VITE_API_BASE_URL` to the deployed API URL.

## Documentation

| Document                              | Description                               |
| ------------------------------------- | ----------------------------------------- |
| [docs/setup.md](docs/setup.md)        | Local development setup guide             |
| [docs/architecture.md](docs/architecture.md) | System design & search pipeline    |
| [docs/api-reference.md](docs/api-reference.md) | API reference with examples    |
| [docs/deployment.md](docs/deployment.md) | Deployment guide (Render, Vercel, Docker) |
| [docs/data-pipeline.md](docs/data-pipeline.md) | Data ingestion & embedding pipeline |

## Tech Stack

| Layer    | Technology                                            |
| -------- | ----------------------------------------------------- |
| Frontend | React 19, Vite, CSS Modules, Vitest + Testing Library |
| Backend  | FastAPI, uvicorn, Pydantic                            |
| Search   | sentence-transformers (all-MiniLM-L6-v2), NLTK        |
| Database | PostgreSQL 16, pgvector, pg_trgm                      |
| Deploy   | Render (API), Vercel (SPA)                            |
