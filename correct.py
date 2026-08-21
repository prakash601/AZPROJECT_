"""Spell correction for search queries (Norvig-style, cached and guarded)."""
import logging
import os
import re
from collections import Counter
from functools import lru_cache

# Point NLTK at a private, writable dir (Render's shared /opt/render/nltk_data
# is world-writable and rejected by the downloader) BEFORE importing nltk.
_PROJECT_NLTK_DATA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "nltk_data"
)
os.environ.setdefault("NLTK_DATA", _PROJECT_NLTK_DATA)

import nltk
from num2words import num2words

from db import get_cursor

logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        os.makedirs(_PROJECT_NLTK_DATA, exist_ok=True)
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except Exception:
        logger.warning("Could not pre-download NLTK punkt data; will retry lazily")

WORDS_CACHE = None

# Guards so a pathological query can't stall the request
MAX_TOKENS = 12        # correct at most this many tokens per query
MAX_CORRECTABLE_LEN = 16  # skip edit-distance search for very long words


def words(text):
    return re.findall(r'\w+', text.lower())


def get_words():
    global WORDS_CACHE
    if WORDS_CACHE is None:
        try:
            with get_cursor(commit=False) as cur:
                cur.execute("SELECT title, description FROM problems LIMIT 5000")
                rows = cur.fetchall()
            text = " ".join([f"{r[0]} {r[1]}" for r in rows])
            WORDS_CACHE = Counter(words(text))
            logger.info("Vocabulary loaded: %d tokens", sum(WORDS_CACHE.values()))
        except Exception:
            logger.exception("Failed to load vocabulary from database; "
                             "spell correction disabled for this process")
            WORDS_CACHE = Counter()
    return WORDS_CACHE


def P(word):
    w = get_words()
    N = sum(w.values()) or 1
    return w[word] / N


@lru_cache(maxsize=65536)
def correction(word):
    return max(candidates(word), key=P)


def candidates(word):
    # Only alphabetic tokens of reasonable length benefit from edit-distance search
    if not word.isalpha() or len(word) > MAX_CORRECTABLE_LEN:
        return [word]
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])


def known(words_list):
    w = get_words()
    return set(x for x in words_list if x in w)


def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """Lazy generator of edit-distance-2 variants (never materialized fully)."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def _ensure_punkt():
    """Download punkt data on first use if it's missing."""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        logger.info("NLTK punkt missing; downloading")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)


def correct_query(text):
    line = text.strip()
    if not line:
        return line
    _ensure_punkt()
    tokens = nltk.word_tokenize(line)
    corrected_tokens = []
    for token in tokens[:MAX_TOKENS]:
        if token.isdigit():
            corrected_tokens.append(num2words(int(token)))
        else:
            corrected_tokens.append(correction(token))
    return ' '.join(corrected_tokens)
