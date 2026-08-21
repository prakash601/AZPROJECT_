"""
Problem Finder — API (FastAPI).

Pure JSON API serving the React SPA. All search/autocomplete/correction
logic lives in search.py / correct.py / db.py (unchanged). This file is
only the web layer.

Run dev:  uvicorn main:app --reload
Run prod: uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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


app.include_router(api_router)
