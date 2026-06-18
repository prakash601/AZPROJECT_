#!/usr/bin/env python3
"""
Generate embeddings for all problems using all-MiniLM-L6-v2 (384 dims).
Run AFTER migrate.py completes.

Fixes applied:
- No OFFSET pagination — updated rows drop out of the WHERE embedding IS NULL filter,
  so we always query from offset 0 to avoid skipping rows.
"""
import sys
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from db import get_cursor

MODEL_NAME = "all-MiniLM-L6-v2"  # 384 dimensions, ~90MB, fast
BATCH_SIZE = 64


def generate_embeddings():
    # Load model (downloads ~90MB on first run, caches locally)
    print(f"Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.")

    with get_cursor(commit=False) as cur:
        # Count total rows needing embeddings
        cur.execute("SELECT COUNT(*) FROM problems WHERE embedding IS NULL")
        total = cur.fetchone()[0]
        print(f"Generating embeddings for {total} problems...")

        if total == 0:
            print("All embeddings already exist.")
            return

        # Process in batches — no OFFSET needed since updated rows
        # disappear from the WHERE embedding IS NULL filter
        with tqdm(total=total, desc="Embedding") as pbar:
            while True:
                cur.execute("""
                    SELECT id, title, description
                    FROM problems
                    WHERE embedding IS NULL
                    ORDER BY id
                    LIMIT %s
                """, (BATCH_SIZE,))

                rows = cur.fetchall()
                if not rows:
                    break

                # Prepare texts for embedding
                texts = []
                ids = []
                for pid, title, desc in rows:
                    # Combine title + truncated description (~512 tokens)
                    text = f"{title}. {desc[:1000]}"
                    texts.append(text)
                    ids.append(pid)

                # Generate embeddings
                embeddings = model.encode(
                    texts, batch_size=BATCH_SIZE, show_progress_bar=False
                )

                # Update database
                update_data = [
                    (emb.tolist(), pid)
                    for emb, pid in zip(embeddings, ids)
                ]
                cur.executemany(
                    "UPDATE problems SET embedding = %s WHERE id = %s",
                    update_data
                )

                # Commit after each batch so progress is saved
                cur.connection.commit()
                pbar.update(len(rows))

        # Create HNSW index for fast vector similarity search
        print("Creating HNSW index (this may take a minute)...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_problems_embedding
            ON problems USING hnsw (embedding vector_cosine_ops)
        """)
        cur.connection.commit()
        print("HNSW index created.")


if __name__ == "__main__":
    generate_embeddings()
