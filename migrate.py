#!/usr/bin/env python3
"""
Migrate text files to PostgreSQL.

Reads from:
  - data/Question_scrapper/Qdata/Qindex.txt   (URLs)
  - data/Question_scrapper/Qdata/index.txt     (titles)
  - data/TF_IDF/platform_name.txt              (platforms)
  - data/TF_IDF/qdata.txt                      (descriptions — one per line)

Uses qdata.txt as the primary description source (16,335 lines, index-aligned)
instead of reading 16K individual Qdata/{id}/{id}.txt files.
"""
import os
import sys
from pathlib import Path
from tqdm import tqdm
from db import get_cursor

QDATA_DIR = Path("data/Question_scrapper/Qdata")
TFIDF_DIR = Path("data/TF_IDF")
BATCH_SIZE = 1000


def read_index_files():
    """Read all four index files (they are line-aligned)."""
    with open(QDATA_DIR / "Qindex.txt") as f:
        urls = [line.rstrip('\n') for line in f]
    with open(QDATA_DIR / "index.txt") as f:
        titles = [line.rstrip('\n') for line in f]
    with open(TFIDF_DIR / "platform_name.txt") as f:
        platforms = [line.rstrip('\n') for line in f]
    with open(TFIDF_DIR / "qdata.txt") as f:
        descriptions = [line.rstrip('\n') for line in f]

    assert len(urls) == len(titles) == len(platforms) == len(descriptions), (
        f"Index files length mismatch: urls={len(urls)}, titles={len(titles)}, "
        f"platforms={len(platforms)}, descriptions={len(descriptions)}"
    )
    return urls, titles, platforms, descriptions


def migrate():
    urls, titles, platforms, descriptions = read_index_files()
    total = len(urls)
    print(f"Migrating {total} problems...")

    inserted = 0
    skipped = 0

    with get_cursor() as cur:
        for i in tqdm(range(0, total, BATCH_SIZE), desc="Batches"):
            batch = []
            for j in range(i, min(i + BATCH_SIZE, total)):
                url = urls[j].strip()
                title = titles[j].strip()
                platform = platforms[j].strip()
                description = descriptions[j].strip()

                if not url or not title:
                    skipped += 1
                    continue

                if not description:
                    # Fallback: try reading from individual file
                    problem_id = j + 1
                    desc_file = QDATA_DIR / str(problem_id) / f"{problem_id}.txt"
                    if desc_file.exists():
                        description = desc_file.read_text(encoding='utf-8', errors='ignore').strip()

                if not description:
                    skipped += 1
                    continue

                batch.append((platform, title, url, description))

            if batch:
                cur.executemany("""
                    INSERT INTO problems (platform, title, url, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                """, batch)
                inserted += len(batch)

    print(f"Done. Inserted: {inserted}, Skipped: {skipped}")


if __name__ == "__main__":
    migrate()
