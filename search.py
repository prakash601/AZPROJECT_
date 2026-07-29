import numpy as np
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer
from db import get_cursor

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Lazy-loaded globals
_tokenizer = None
_model = None

def get_onnx_model():
    """Lazily load tokenizer and ONNX Runtime session."""
    global _tokenizer, _model
    if _model is None or _tokenizer is None:
        print("Loading ONNX model and tokenizer...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # export=True converts PyTorch weights to ONNX format on first run
        _model = ORTModelForFeatureExtraction.from_pretrained(
            MODEL_NAME, export=True
        )
        print("ONNX model loaded successfully.")
    return _tokenizer, _model

def mean_pooling(model_output, attention_mask):
    """Perform mean pooling over token embeddings."""
    token_embeddings = model_output[0]  # First element contains token embeddings
    input_mask_expanded = np.expand_dims(attention_mask, axis=-1)
    sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask

def encode_query(query: str):
    """Encode string query into a 384-dim normalized embedding using ONNX."""
    tokenizer, model = get_onnx_model()
    
    # Tokenize text input
    inputs = tokenizer(
        query, padding=True, truncation=True, max_length=128, return_tensors="np"
    )
    
    # Run inference with ONNX Runtime
    outputs = model(**inputs)
    
    # Mean pooling + L2 normalization
    embeddings = mean_pooling(outputs, inputs["attention_mask"])
    norm = np.linalg.norm(embeddings, ord=2, axis=1, keepdims=True)
    normalized_embedding = (embeddings / np.clip(norm, a_min=1e-12, a_max=None))[0]
    
    return normalized_embedding.tolist()

def search(query: str, limit: int = 30, offset: int = 0):
    """Combined search using Reciprocal Rank Fusion (RRF)."""
    query_embedding = encode_query(query)
    
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
           p.difficulty, p.tags,
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
            query_embedding, query_embedding,
            query, query, query,
            query, query, query,
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
            "difficulty": r[5],
            "tags": r[6] if r[6] else [],
            "score": float(r[7])
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