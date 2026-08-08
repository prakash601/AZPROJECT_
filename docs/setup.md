# Local Development Setup

Complete guide to run Problem Finder on your machine.

## Prerequisites

| Tool   | Version  | Purpose                          |
|--------|----------|----------------------------------|
| Python | 3.11+    | Backend runtime                  |
| Node   | 18+      | Frontend build & dev server      |
| Docker | 20.10+   | Local PostgreSQL + pgvector      |
| pip    | 23+      | Python package manager           |
| npm    | 9+       | Node package manager             |

## 1. Clone & Configure

```bash
git clone <repo-url>
cd AZPROJECT
```

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=azproject
DB_USER=azuser
DB_PASSWORD=azpass
SECRET_KEY=your-secret-key-here
FRONTEND_ORIGIN=http://localhost:5173
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=
```

> Leave `VITE_API_BASE_URL` empty in development — Vite proxies `/api` to the backend automatically.

## 2. Start the Database

```bash
docker compose up -d postgres
```

This starts PostgreSQL 16 with:
- `pgvector` extension (vector similarity search)
- `pg_trgm` extension (fuzzy text matching)
- Schema auto-applied from `init.sql`

Verify it's running:

```bash
docker compose ps
docker compose exec postgres pg_isready -U azuser -d azproject
```

## 3. Set Up the Backend

```bash
pip install -r requirements.txt
```

Download required NLTK data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### First-Time Data Load

Two one-time scripts populate the database:

```bash
# Step 1: Migrate problem data from text files → PostgreSQL
python migrate.py

# Step 2: Generate 384-dim embeddings for all problems
python generate_embeddings.py
```

> `generate_embeddings.py` downloads the `all-MiniLM-L6-v2` model (~90MB) on first run and creates an HNSW index for fast vector search.

### Run the API

```bash
uvicorn main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 4. Set Up the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` requests to the backend on port 8000.

## 5. Verify Everything Works

```bash
# Health check
curl http://localhost:8000/api/health

# Search
curl "http://localhost:8000/api/search?q=two+sum&limit=5"

# Autocomplete
curl "http://localhost:8000/api/autocomplete?prefix=two&limit=5"
```

## Project Scripts Reference

### Backend

| Command                          | Purpose                                  |
|----------------------------------|------------------------------------------|
| `uvicorn main:app --reload`      | Start dev server with hot reload         |
| `python migrate.py`              | Load problem data into PostgreSQL        |
| `python generate_embeddings.py`  | Generate embeddings + HNSW index         |
| `bash build.sh`                  | Full build (deps + NLTK + ONNX model)    |

### Frontend

| Command                | Purpose                            |
|------------------------|------------------------------------|
| `npm run dev`          | Start dev server (port 5173)       |
| `npm run build`        | Production build to `frontend/dist`|
| `npm run lint`         | Run ESLint                         |
| `npm run format`       | Run Prettier                       |
| `npm test`             | Run tests once                     |
| `npm run test:watch`   | Run tests in watch mode            |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `connection refused` to database | Ensure Docker container is running: `docker compose up -d postgres` |
| `embedding IS NULL` in search results | Run `python generate_embeddings.py` |
| `punkt` NLTK error | Run `python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"` |
| CORS errors in browser | Verify `FRONTEND_ORIGIN` in `.env` matches your dev server URL |
| Port 8000 already in use | Kill the process or use `uvicorn main:app --reload --port 8001` |
| Port 5173 already in use | Vite will auto-assign a new port — check terminal output |
