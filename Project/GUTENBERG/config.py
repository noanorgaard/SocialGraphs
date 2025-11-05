# config.py
from pathlib import Path

# --- Project paths
DATA_DIR     = Path("data")
RAW_DIR      = DATA_DIR / "raw"
TEXT_DIR     = DATA_DIR / "texts"
CLEAN_DIR    = DATA_DIR / "cleaned"
OUT_DIR      = DATA_DIR / "outputs"
for p in (DATA_DIR, RAW_DIR, TEXT_DIR, CLEAN_DIR, OUT_DIR):
    p.mkdir(parents=True, exist_ok=True)

# --- Gutendex fetch settings
TOPIC             = "romance"     # bookshelf/subject filter (Gutendex 'topic')  # see docs  [1](https://gutendex.com/)
LANGS             = "en"          # 2-letter codes, CSV accepted  [1](https://gutendex.com/)
COPYRIGHT         = "false"       # false => public domain in USA                  [1](https://gutendex.com/)
MAX_BOOKS         = 30          # how many entries to pull
RATE_LIMIT_S      = 0.15

# --- Download preferences (prefer UTF-8 plain text)
PREFERRED_MIME = [
    "text/plain; charset=utf-8",
    "text/plain",
    "text/html; charset=utf-8",
    "text/html",
]

# --- Open Library (OL) enrichment
OL_USER_AGENT = "dtu-romance-project/1.0 (contact: anna.noa@example.com)"  # OL requests UA for frequent calls  [3](https://openlibrary.org/developers/api)
OL_FIELDS     = ",".join(["key", "title", "author_name", "first_publish_year",
                          "subject", "edition_count", "language"])          # Search API fields parameter  [2](https://openlibrary.org/dev/docs/api/search)
OL_MIN_SCORE  = 0.62
OL_MAX_PAGES  = 2

# --- Preprocessing
LOWERCASE     = True
STRIP_HTML    = True   # if file is HTML, strip tags into text
REMOVE_GUTENBERG_HEADERS = True

# --- Vectorization & kNN
TFIDF_MAX_FEATURES = 100_000
TFIDF_MIN_DF       = 5
TFIDF_MAX_DF       = 0.85
NGRAM_RANGE        = (1, 2)
K_NEIGHBORS        = 10
SIM_THRESHOLD      = 0.25     # cosine similarity cutoff for edges

# --- Subject-tag graph
JACCARD_MIN        = 0.10
TOPK_TAG_NEIGHBORS = 10
