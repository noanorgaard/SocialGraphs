# fetch_gutendex.py
import time, requests
import pandas as pd
from tqdm import tqdm
from config import (TOPIC, LANGS, COPYRIGHT, MAX_BOOKS, RATE_LIMIT_S, RAW_DIR)

BASE = "https://gutendex.com/books"

def _pick_best_text(formats: dict, preferred):
    for m in preferred:
        if m in formats:
            return m, formats[m]
    for k, v in formats.items():
        if k.startswith("text/"):
            return k, v
    return None, None

def fetch_gutendex(preferred_mime, save_csv=True):
    params = {"topic": TOPIC, "languages": LANGS, "copyright": COPYRIGHT}
    url = BASE
    if params:
        q = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{BASE}?{q}"

    books = []
    next_url = url
    pbar = tqdm(total=MAX_BOOKS, desc=f"Gutendex({TOPIC},{LANGS},PD={COPYRIGHT})")
    while next_url and len(books) < MAX_BOOKS:
        r = requests.get(next_url, timeout=30)
        r.raise_for_status()
        js = r.json()
        results = js.get("results", [])
        for b in results:
            mime, dl = _pick_best_text(b.get("formats", {}), preferred_mime)
            books.append({
                "pg_id": b.get("id"),
                "title": b.get("title"),
                "authors": [a.get("name") for a in b.get("authors", []) if a.get("name")],
                "download_count": b.get("download_count"),
                "languages": b.get("languages"),
                "subjects": b.get("subjects"),
                "bookshelves": b.get("bookshelves"),
                "chosen_mime": mime,
                "text_url": dl
            })
            if len(books) >= MAX_BOOKS:
                break
        next_url = js.get("next")
        pbar.update(len(results))
        time.sleep(RATE_LIMIT_S)
    pbar.close()

    df = pd.DataFrame(books)
    if save_csv:
        out = RAW_DIR / f"gutendex_{TOPIC}_{LANGS}_{COPYRIGHT}.csv"
        df.to_csv(out, index=False)
    return df
