# Data Pipeline

How problem data is ingested, embedded, and indexed.

## Overview

```
Raw Text Files                 PostgreSQL
┌──────────────────┐          ┌──────────────────────────┐
│ Qindex.txt       │          │                          │
│ (16,335 URLs)    │──┐      │  problems table          │
│                  │  │      │  ┌────────────────────┐  │
│ index.txt        │  ├────▶│  │ id, platform,      │  │
│ (16,335 titles)  │  │migrate│ │ title, url,        │  │
│                  │  │  .py  │ │ description,       │  │
│ platform_name.txt│  │      │ │ difficulty, tags   │  │
│ (16,335 platforms)│ │      │ │ search_vector (FTS)│  │
│                  │  │      │ │ embedding (384d)   │  │
│ qdata.txt        │──┘      │  └────────────────────┘  │
│ (16,335 descs)   │         │                          │
└──────────────────┘         │  Indexes:                │
                             │  - GIN (FTS)             │
│ Qdata/{id}/{id}.txt ──────▶│  - GIN (trigram)        │
│ (individual files,          │  - HNSW (vector)        │
│  fallback source)           │                          │
                             └──────────────────────────┘
                                        │
                               generate_embeddings.py
                                        │
                                        ▼
                             ┌──────────────────────────┐
                             │ all-MiniLM-L6-v2 (ONNX)  │
                             │                          │
                             │ title + desc[:1000]      │
                             │ → 384-dim vector         │
                             │ → L2 normalized          │
                             └──────────────────────────┘
```

## Source Data

### Primary Files

All files are **line-aligned** (line N in each file corresponds to the same problem):

| File | Path | Content | Count |
|------|------|---------|-------|
| URLs | `data/Question_scrapper/Qdata/Qindex.txt` | Problem URLs | 16,335 |
| Titles | `data/Question_scrapper/Qdata/index.txt` | Problem titles | 16,335 |
| Platforms | `data/TF_IDF/platform_name.txt` | Source platform names | 16,335 |
| Descriptions | `data/TF_IDF/qdata.txt` | Problem descriptions | 16,335 |

### Fallback Files

Individual problem descriptions at `data/Question_scrapper/Qdata/{id}/{id}.txt` are used as fallback if `qdata.txt` has an empty line.

## Migration (`migrate.py`)

Reads the four index files and bulk-inserts into PostgreSQL.

### Process

1. Read all four files into memory (line-aligned)
2. Assert equal lengths (sanity check)
3. Batch in groups of 1,000
4. Use `ON CONFLICT (url) DO NOTHING` for idempotency
5. Skip entries with empty URL or title

### Performance

- ~16,335 rows in ~17 batches of 1,000
- Takes ~30 seconds on local PostgreSQL

### Re-running

Safe to re-run — `ON CONFLICT` prevents duplicates.

---

## Embedding Generation (`generate_embeddings.py`)

Generates 384-dim semantic embeddings for all problems.

### Process

1. Load `all-MiniLM-L6-v2` model via `sentence-transformers`
2. Query rows where `embedding IS NULL` (skip already-processed)
3. Encode in batches of 64:
   - Input: `"{title}. {description[:1000]}"`
   - Output: 384-dim float vector
4. Update each row with its embedding
5. Commit after each batch (progress is saved incrementally)
6. Create HNSW index when complete

### Key Design Decisions

- **No OFFSET pagination**: Updated rows disappear from `WHERE embedding IS NULL`, so we always query from offset 0. This prevents skipping rows.
- **Batch commits**: Progress is saved even if the process is interrupted.
- **HNSW index**: Created after all embeddings exist for optimal index build.

### Performance

- Model download: ~90MB (first run only)
- Inference: ~64 problems per batch
- Total time: ~15-20 minutes for 16,335 problems (CPU)
- HNSW index build: ~1-2 minutes

### Re-running

Safe — only processes rows with `embedding IS NULL`.

---

## Database Schema After Pipeline

After both scripts complete, the `problems` table has:

| Column | Population |
|--------|-----------|
| `id` | Auto-generated |
| `platform` | From `platform_name.txt` |
| `title` | From `index.txt` |
| `url` | From `Qindex.txt` |
| `description` | From `qdata.txt` (or individual files) |
| `difficulty` | Null (populated externally if needed) |
| `tags` | Null (populated externally if needed) |
| `search_vector` | Auto-generated from title + description |
| `embedding` | 384-dim vector (from `generate_embeddings.py`) |

### Indexes Created

```sql
-- Created by init.sql
CREATE INDEX idx_problems_fts ON problems USING GIN (search_vector);
CREATE INDEX idx_problems_trgm ON problems USING GIN (title gin_trgm_ops);
CREATE INDEX idx_problems_platform ON problems (platform);

-- Created by generate_embeddings.py
CREATE INDEX idx_problems_embedding ON problems USING hnsw (embedding vector_cosine_ops);
```

---

## Adding New Problems

To add new problems to an existing database:

1. Append to the four index files (maintaining line alignment)
2. Re-run `python migrate.py` — new entries are inserted, existing ones skipped
3. Re-run `python generate_embeddings.py` — only new rows get embeddings
