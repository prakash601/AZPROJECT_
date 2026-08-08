# Deployment Guide

Deploying Problem Finder to various targets.

## Overview

| Component | Deployment Target | Port |
|-----------|------------------|------|
| Backend API | Render | `$PORT` |
| Frontend SPA | Vercel / Netlify | 443 |
| Full Stack (API + SPA) | Docker (any platform) | 7860 |

---

## Backend — Render

The `render.yaml` config deploys the FastAPI app on Render.

### Prerequisites

- A Render account
- A PostgreSQL database with pgvector (Render PostgreSQL or Supabase)

### Steps

1. **Create a PostgreSQL database** on Render or Supabase with pgvector enabled.

2. **Apply the schema:**
   ```bash
   psql $DATABASE_URL -f init.sql
   ```

3. **Create a new Web Service** on Render:
   - Connect your GitHub repo
   - Environment: `Python`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set environment variables:**

   | Variable          | Value                        |
   |-------------------|------------------------------|
   | `PYTHON_VERSION`  | `3.11.7`                     |
   | `DB_HOST`         | Your database host           |
   | `DB_PORT`         | Database port (e.g., `5432`) |
   | `DB_NAME`         | Database name                |
   | `DB_USER`         | Database user                |
   | `DB_PASSWORD`     | Database password            |
   | `SECRET_KEY`      | Random secret                |
   | `FRONTEND_ORIGIN` | Your deployed frontend URL   |

5. **Run build script** (Render runs `bash build.sh` or equivalent):
   ```bash
   pip install -r requirements.txt
   python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"
   python -c "from optimum.onnxruntime import ORTModelForFeatureExtraction; from transformers import AutoTokenizer; m='sentence-transformers/all-MiniLM-L6-v2'; AutoTokenizer.from_pretrained(m); ORTModelForFeatureExtraction.from_pretrained(m, export=True)"
   ```

6. **After first deploy**, run data migration (one-time):
   ```bash
   # Connect to the deployed database and run locally:
   export DB_HOST=<render-db-host>
   export DB_PORT=<render-db-port>
   export DB_NAME=<db-name>
   export DB_USER=<db-user>
   export DB_PASSWORD=<db-password>

   python migrate.py
   python generate_embeddings.py
   ```

---

## Frontend — Vercel

### Prerequisites

- A Vercel account
- Backend API already deployed

### Steps

1. **Connect your repo** to Vercel and configure:
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `dist`

2. **Set environment variable:**

   | Variable            | Value                    |
   |---------------------|--------------------------|
   | `VITE_API_BASE_URL` | Your deployed API URL    |

3. **Deploy.** Vercel auto-builds on push.

### Alternative: Netlify

Same configuration as Vercel. Set:
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `dist`

---

## Full Stack — Docker

The Dockerfile builds a single container running both the API and serving the built frontend.

### Build

```bash
docker build -t problem-finder .
```

### Run

```bash
docker run -p 7860:7860 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=azproject \
  -e DB_USER=azuser \
  -e DB_PASSWORD=azpass \
  -e SECRET_KEY=your-secret \
  problem-finder
```

Access at http://localhost:7860

### Docker Compose (Local)

For local development with both database and app:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: azproject
      POSTGRES_USER: azuser
      POSTGRES_PASSWORD: azpass
    ports:
      - "5432:5432"
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: azproject
      DB_USER: azuser
      DB_PASSWORD: azpass
      SECRET_KEY: local-dev-secret
    depends_on:
      - postgres
```

---

## Hugging Face Spaces

The Dockerfile exposes port 7860, which is the default for HF Spaces.

1. Create a new Space with Docker SDK
2. Set `DB_*` environment variables in the Space settings
3. Push your code — the Space auto-deploys

---

## Environment Variables Reference

| Variable          | Required | Description                          |
|-------------------|----------|--------------------------------------|
| `DB_HOST`         | Yes      | PostgreSQL host                      |
| `DB_PORT`         | Yes      | PostgreSQL port                      |
| `DB_NAME`         | Yes      | Database name                        |
| `DB_USER`         | Yes      | Database user                        |
| `DB_PASSWORD`     | Yes      | Database password                    |
| `SECRET_KEY`      | No       | Application secret (auto-generated)  |
| `FRONTEND_ORIGIN` | No       | Allowed CORS origin for frontend     |
| `VITE_API_BASE_URL` | No*    | Backend URL for frontend (*required in prod) |
