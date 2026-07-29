import re
import nltk
from collections import Counter
from num2words import num2words
from db import get_cursor

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

WORDS_CACHE = None

def words(text): 
    return re.findall(r'\w+', text.lower())

def get_words():
    global WORDS_CACHE
    if WORDS_CACHE is None:
        try:
            with get_cursor(commit=False) as cur:
                cur.execute("SELECT title, description FROM problems LIMIT 5000")  # Limit or fetch titles to keep fast
                rows = cur.fetchall()
            text = " ".join([f"{r[0]} {r[1]}" for r in rows])
            WORDS_CACHE = Counter(words(text))
        except Exception:
            WORDS_CACHE = Counter()
    return WORDS_CACHE

def P(word):
    w = get_words()
    N = sum(w.values()) or 1
    return w[word] / N

def correction(word):
    return max(candidates(word), key=P)

def candidates(word):
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words_list):
    w = get_words()
    return set(x for x in words_list if x in w)

def edits1(word):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def correct_query(text):
    line = text.strip()
    if not line:
        return line
    tokens = nltk.word_tokenize(line)
    corrected_tokens = []
    for token in tokens:
        if token.isdigit():
            corrected_tokens.append(num2words(int(token)))
        else:
            corrected_tokens.append(correction(token))
    return ' '.join(corrected_tokens)