"""
Problem Finder — API (FastAPI).

Pure JSON API serving the React SPA. All search/autocomplete/correction
logic lives in search.py / correct.py / db.py (unchanged). This file is
only the web layer.

Run dev:  uvicorn main:app --reload
Run prod: uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import os
import time
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from correct import correct_query
from search import search as pg_search, autocomplete

app = FastAPI(
    title="Problem Finder API",
    description="Hybrid search (semantic + FTS + trigram via RRF) for coding problems.",
    version="2.0.0",
)

# CORS — allow the SPA (dev: Vite on 5173, prod: configured via FRONTEND_ORIGIN)
_allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_frontend_origin = os.getenv("FRONTEND_ORIGIN")
if _frontend_origin:
    _allowed_origins.append(_frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Response models (mirror the problems schema in init.sql)
# ---------------------------------------------------------------------------

class SearchResult(BaseModel):
    id: int
    platform: str
    title: str
    url: str
    description: str
    difficulty: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    score: float


class SearchResponse(BaseModel):
    query: str
    corrected_query: Optional[str] = None
    execution_time_ms: int
    count: int
    results: list[SearchResult]


class AutocompleteSuggestion(BaseModel):
    id: int
    title: str
    url: str
    platform: str


class AutocompleteResponse(BaseModel):
    prefix: str
    suggestions: list[AutocompleteSuggestion]


class HealthResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/api/search", response_model=SearchResponse, tags=["search"])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(30, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Hybrid search (semantic + keyword + fuzzy). Returns a spell-corrected
    query for 'Did you mean ...?' UX."""
    start = time.perf_counter()
    results = pg_search(q, limit=limit, offset=offset)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    corrected = correct_query(q) if q.strip() else None
    # Only surface correction when it differs from the original.
    if corrected and corrected.strip().lower() == q.strip().lower():
        corrected = None

    return {
        "query": q,
        "corrected_query": corrected,
        "execution_time_ms": elapsed_ms,
        "count": len(results),
        "results": results,
    }


@app.get("/api/autocomplete", response_model=AutocompleteResponse, tags=["search"])
def get_autocomplete(
    prefix: str = Query(..., min_length=1, description="Prefix to complete"),
    limit: int = Query(10, ge=1, le=50, description="Max suggestions"),
):
    """Fast autocomplete via prefix + trigram matching."""
    suggestions = autocomplete(prefix, limit=limit)
    return {"prefix": prefix, "suggestions": suggestions}
