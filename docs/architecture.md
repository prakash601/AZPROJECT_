# Architecture

System design and search pipeline for Problem Finder.

## Overview

Problem Finder is a **hybrid search engine** for coding problems that combines three search strategies — semantic, keyword, and fuzzy — merged via Reciprocal Rank Fusion (RRF) into a single relevance-ranked result set.

```
┌─────────────────────┐      /api/search       ┌──────────────────────┐
│                     │ ──────────────────────▶ │                      │
│  React SPA          │  /api/autocomplete      │  FastAPI             │
│  (Vite, dark mode,  │ ◀───────────────────── │  (uvicorn)           │
│   CSS Modules)      │  JSON                   │                      │
│                     │                         └──────────┬───────────┘
└─────────────────────┘                                    │
                                               ┌──────────┴───────────┐
                                               │  Search Pipeline     │
                                               │                      │
                                               │  ┌────────────────┐  │
                                               │  │ Query          │  │
                                               │  │ Correction     │  │
                                               │  │ (Norvig)       │  │
                                               │  └───────┬────────┘  │
                                               │          │            │
                                               │  ┌───────▼────────┐  │
                                               │  │ Encode Query   │  │
                                               │  │ (ONNX Runtime) │  │
                                               │  └───────┬────────┘  │
                                               │          │            │
                                               │  ┌───────▼────────┐  │
                                               │  │ RRF Fusion     │  │
                                               │  │ Engine (SQL)    │  │
                                               │  └───────┬────────┘  │
                                               │          │            │
                                               │  ┌───────┴────┐       │
                                               │  ▼            ▼       │
                                               │ Semantic   Keyword   │
                                               │ (HNSW)     (GIN)     │
                                               │            Fuzzy      │
                                               │            (trgm)     │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────┴───────────┐
                                               │  PostgreSQL +        │
                                               │  pgvector + pg_trgm  │
                                               │                      │
                                               │  16,335 problems     │
                                               │  384-dim embeddings  │
                                               └──────────────────────┘
```

## Components

### Backend (`main.py`)

The web layer — pure JSON API with three endpoints:

- **`GET /api/health`** — Liveness probe
- **`GET /api/search`** — Hybrid search with spell correction
- **`GET /api/autocomplete`** — Type-ahead suggestions

Handles CORS, request validation (Pydantic), and timing.

### Search Engine (`search.py`)

The core search pipeline:

1. **Query Encoding** — Converts the search string into a 384-dim normalized vector using `sentence-transformers/all-MiniLM-L6-v2` via ONNX Runtime for fast inference.
2. **Reciprocal Rank Fusion** — Runs three sub-queries and merges results:
   - **Semantic** — Cosine similarity on embeddings (HNSW index)
   - **Keyword** — Full-text search with `ts_rank_cd` (GIN index on `tsvector`)
   - **Fuzzy** — Trigram similarity on titles (GIN index with `gin_trgm_ops`)
3. **Autocomplete** — Prefix matching (`ILIKE`) combined with trigram similarity for typo-tolerant suggestions.

### Spell Corrector (`correct.py`)

Peter Norvig's algorithm adapted for coding problem queries:

- Tokenizes with NLTK
- Converts digits to words (e.g., `"2"` → `"two"`) for better matching
- Builds a word frequency corpus from the problem database
- Generates candidates via edit distance 1 and 2
- Selects the candidate with highest probability in the corpus

### Database Layer (`db.py`)

- Threaded connection pool (min 1, max 10)
- pgvector type registration on every connection
- Context-managed cursors with automatic commit/rollback

### Frontend (`frontend/`)

React 19 SPA with:

| Feature | Implementation |
|---------|---------------|
| Search state | Custom `useSearch` hook with debouncing |
| Autocomplete | `useAutocomplete` hook + dropdown component |
| Theming | CSS variables + `ThemeContext` (dark/light) |
| Routing | URL query parameter sync (shareable searches) |
| Styling | CSS Modules + design tokens |
| Testing | Vitest + Testing Library |

## Search Pipeline Detail

### Reciprocal Rank Fusion (RRF)

Each sub-search produces a ranked list. The RRF score for a document is:

```
RRF_score(d) = Σ  1 / (k + rank_i(d))
```

Where `k = 10` (smoothing constant) and `rank_i(d)` is the rank of document `d` in search strategy `i`. Documents not present in a sub-search contribute 0.

The three strategies:

| Strategy | SQL Mechanism | Index | Limit |
|----------|--------------|-------|-------|
| Semantic | `embedding <=> query_vector` (cosine distance) | HNSW | 100 |
| Keyword | `ts_rank_cd(search_vector, query)` | GIN (tsvector) | 100 |
| Fuzzy | `similarity(title, query)` | GIN (trgm) | 50 |

Results are fused in a single SQL query using CTEs and `LEFT JOIN`, then sorted by total RRF score.

### Why RRF?

- No score normalization needed across strategies
- Naturally handles missing results (document found by only one strategy still ranks)
- Robust to different score distributions
- Simple constant `k` controls the rank discount

## Database Schema

```sql
CREATE TABLE problems (
    id          BIGSERIAL PRIMARY KEY,
    platform    VARCHAR(50) NOT NULL,
    title       TEXT NOT NULL,
    url         TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty  VARCHAR(20),
    tags        TEXT[],
    search_vector  tsvector GENERATED ALWAYS AS (...) STORED,
    embedding   vector(384),
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Indexes

| Index | Type | Purpose |
|-------|------|---------|
| `idx_problems_fts` | GIN | Full-text search on `search_vector` |
| `idx_problems_trgm` | GIN | Trigram similarity on `title` |
| `idx_problems_embedding` | HNSW | Cosine similarity on `embedding` |
| `idx_problems_platform` | B-tree | Filter by platform |

## Model

**`sentence-transformers/all-MiniLM-L6-v2`**
- 384 dimensions
- ~90MB size
- Runs via ONNX Runtime (exported on first load)
- Mean pooling over token embeddings + L2 normalization
- Max sequence length: 128 tokens (queries), 1000 chars (problem text)

## Request Flow

```
Browser
  │
  ▼ GET /api/search?q=two+sum&limit=30
FastAPI (main.py)
  │
  ├─ correct_query("two sum") → Norvig spell check → "two sum" (no change)
  │
  ├─ encode_query("two sum") → ONNX inference → [0.012, -0.045, ...] (384-dim)
  │
  ├─ search("two sum", limit=30) → RRF SQL query → ranked results
  │
  └─ Return JSON: { query, corrected_query, execution_time_ms, count, results }
```
