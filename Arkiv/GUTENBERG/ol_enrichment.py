import time, re, unicodedata, difflib, requests
import pandas as pd
from tqdm import tqdm
from config import (OL_USER_AGENT, OL_FIELDS, OL_MIN_SCORE, OL_MAX_PAGES, RATE_LIMIT_S, RAW_DIR)

OL_SEARCH = "https://openlibrary.org/search.json"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": OL_USER_AGENT})
import logging
def _norm(s: str) -> str:
    if not s: return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[\W_]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _best_author(authors):
    if isinstance(authors, (list, tuple)) and authors:
        return authors[0]
    return ""

def _choose_best(pg_title, pg_author, docs):
    t0, a0 = _norm(pg_title), _norm(pg_author)
    best, score = None, -1.0
    for d in docs:
        t = _norm(d.get("title", ""))
        a = _norm((d.get("author_name") or [None])[0] or "")
        t_sim = difflib.SequenceMatcher(None, t0, t).ratio()
        a_sim = difflib.SequenceMatcher(None, a0, a).ratio() if a0 else 0.0
        langs = [x.lower() for x in (d.get("language") or [])]
        bonus = 0.02 if "eng" in langs else 0.0
        sc = 0.7 * t_sim + 0.3 * a_sim + bonus
        if sc > score:
            best, score = d, sc
    return best, score

# add simple logger
LOG_PATH = RAW_DIR / "ol_errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(message)s")

def _search_ol(title, author, page=1, limit=20, retries=3, backoff=0.5):
    """Search OL with simple retry/backoff on transient errors. Returns list of docs or [] on persistent failure."""
    params = {"title": title, "author": author, "fields": OL_FIELDS, "page": page, "limit": limit}
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            time.sleep(RATE_LIMIT_S)
            r = SESSION.get(OL_SEARCH, params=params, timeout=30)
            # If OL returns 5xx, treat as transient and retry
            if 500 <= r.status_code < 600:
                logging.warning(f"OL server error {r.status_code} for title={title!r} page={page} attempt={attempt}")
                time.sleep(backoff * attempt)
                continue
            r.raise_for_status()
            return r.json().get("docs", []) or []
        except requests.exceptions.RequestException as e:
            logging.warning(f"OL request failed for title={title!r} page={page} attempt={attempt}: {e}")
            time.sleep(backoff * attempt)
            continue
    # persistent failure -> return empty list (do not raise)
    logging.error(f"OL search failed (giving up) for title={title!r} after {retries} attempts. Last params: {params}")
    return []

def enrich_openlibrary(df, min_score=OL_MIN_SCORE, max_pages=OL_MAX_PAGES, save_csv=True):
    rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="OpenLibrary enrichment"):
        pgid = row.get("pg_id")
        title = (row.get("title") or "").strip()
        author = _best_author(row.get("authors"))
        if not title:
            rows.append({"pg_id": pgid}); continue

        docs = []
        try:
            for p in range(1, max_pages + 1):
                res = _search_ol(title, author, page=p, limit=20)
                if not res:
                    break
                docs += res
                if len(docs) > 1000:
                    break
        except Exception as e:
            logging.exception(f"Unexpected error during OL enrichment for title={title!r}: {e}")
            docs = []

        best, score = _choose_best(title, author, docs) if docs else (None, 0.0)
        if best and score >= min_score:
            rows.append({
                "pg_id": pgid,
                "ol_work_key": best.get("key"),
                "ol_title": best.get("title"),
                "ol_author_name": best.get("author_name"),
                "ol_first_publish_year": best.get("first_publish_year"),
                "ol_subjects": best.get("subject"),
                "ol_edition_count": best.get("edition_count"),
                "ol_languages": best.get("language"),
                "ol_match_score": score
            })
        else:
            rows.append({"pg_id": pgid})

    df_ol = pd.DataFrame(rows)
    # merge on pg_id if present, else concatenate
    if "pg_id" in df.columns:
        merged = df.reset_index(drop=True).merge(df_ol, on="pg_id", how="left")
    else:
        merged = pd.concat([df.reset_index(drop=True), df_ol], axis=1)

    if save_csv:
        outpath = RAW_DIR / "openlibrary_enrichment.csv"
        try:
            merged.to_csv(outpath, index=False)
        except Exception as e:
            logging.warning(f"Failed to save OL enrichment CSV: {e}")

    return merged
