"""
Unified search: FTS + Vector + Trigram with RRF (Reciprocal Rank Fusion).

All SQL uses parameterized queries — no string interpolation for user input.
Returns results with clean key names: url, title, description, platform, score.
"""
from sentence_transformers import SentenceTransformer
from db import get_cursor

MODEL_NAME = "all-MiniLM-L6-v2"

# Eager-load model at import time to avoid cold start on first request
_model = SentenceTransformer(MODEL_NAME)


def get_model():
    return _model


def search(query: str, limit: int = 30, offset: int = 0):
    """
    Combined search using Reciprocal Rank Fusion (RRF).
    Merges semantic (vector), keyword (FTS), and fuzzy (trigram) results.

    Returns list of dicts with keys: id, platform, title, url, description, score
    """
    model = get_model()
    query_embedding = model.encode(query).tolist()

    sql = """
    WITH semantic AS (
        SELECT id,
               1.0 / (10 + ROW_NUMBER() OVER (
                   ORDER BY embedding <=> %s::vector
               )) AS rrf_score
        FROM problems
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT 100
    ),
    keyword AS (
        SELECT id,
               1.0 / (10 + ROW_NUMBER() OVER (
                   ORDER BY ts_rank_cd(search_vector, plainto_tsquery('english', %s)) DESC
               )) AS rrf_score
        FROM problems
        WHERE search_vector @@ plainto_tsquery('english', %s)
        ORDER BY ts_rank_cd(search_vector, plainto_tsquery('english', %s)) DESC
        LIMIT 100
    ),
    fuzzy AS (
        SELECT id,
               1.0 / (10 + ROW_NUMBER() OVER (
                   ORDER BY similarity(title, %s) DESC
               )) AS rrf_score
        FROM problems
        WHERE similarity(title, %s) > 0.3
        ORDER BY similarity(title, %s) DESC
        LIMIT 50
    )
    SELECT p.id, p.platform, p.title, p.url, p.description,
           COALESCE(s.rrf_score, 0) + COALESCE(k.rrf_score, 0) + COALESCE(f.rrf_score, 0) AS score
    FROM problems p
    LEFT JOIN semantic s ON p.id = s.id
    LEFT JOIN keyword k ON p.id = k.id
    LEFT JOIN fuzzy f ON p.id = f.id
    WHERE s.id IS NOT NULL OR k.id IS NOT NULL OR f.id IS NOT NULL
    ORDER BY score DESC
    LIMIT %s OFFSET %s
    """

    with get_cursor(commit=False) as cur:
        cur.execute(sql, (
            query_embedding, query_embedding,   # semantic (2 refs)
            query, query, query,                # keyword  (3 refs to plainto_tsquery)
            query, query, query,                # fuzzy    (3 refs)
            limit, offset
        ))
        rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "platform": r[1],
            "title": r[2],
            "url": r[3],
            "description": r[4],
            "score": float(r[5])
        }
        for r in rows
    ]


def autocomplete(prefix: str, limit: int = 10):
    """Fast autocomplete with prefix + fuzzy matching."""
    sql = """
    SELECT id, title, url, platform
    FROM problems
    WHERE title %% %s OR title ILIKE %s
    ORDER BY
        CASE WHEN title ILIKE %s THEN 0 ELSE 1 END,
        similarity(title, %s) DESC
    LIMIT %s
    """
    like_pattern = f"{prefix}%"

    with get_cursor(commit=False) as cur:
        cur.execute(sql, (prefix, like_pattern, like_pattern, prefix, limit))
        rows = cur.fetchall()

    return [
        {"id": r[0], "title": r[1], "url": r[2], "platform": r[3]}
        for r in rows
    ]
