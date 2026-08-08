"""HTTP routes and response models for the Problem Finder API."""

import time
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from correct import correct_query
from search import autocomplete, search as pg_search

router = APIRouter(prefix="/api")


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


@router.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    return {"status": "ok"}


@router.get("/search", response_model=SearchResponse, tags=["search"])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(30, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Hybrid search with optional spell correction."""
    start = time.perf_counter()
    results = pg_search(q, limit=limit, offset=offset)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    corrected = correct_query(q) if q.strip() else None
    if corrected and corrected.strip().lower() == q.strip().lower():
        corrected = None

    return {
        "query": q,
        "corrected_query": corrected,
        "execution_time_ms": elapsed_ms,
        "count": len(results),
        "results": results,
    }


@router.get(
    "/autocomplete",
    response_model=AutocompleteResponse,
    tags=["search"],
)
def get_autocomplete(
    prefix: str = Query(..., min_length=1, description="Prefix to complete"),
    limit: int = Query(10, ge=1, le=50, description="Max suggestions"),
):
    """Fast autocomplete via prefix and trigram matching."""
    suggestions = autocomplete(prefix, limit=limit)
    return {"prefix": prefix, "suggestions": suggestions}
