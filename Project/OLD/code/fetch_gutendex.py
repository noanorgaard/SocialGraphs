import requests
from tqdm import tqdm
import pandas as pd
from typing import Optional, Dict, Any

GUTENDEX = "https://gutendex.com/books"

def normalize(s: str) -> str:
    return s.strip()

def pick_text_url(formats: Dict[str, str], only_plain=True) -> Optional[str]:
    preferred = [
        "text/plain; charset=utf-8",
        "text/plain; charset=us-ascii",
        "text/plain",
    ]
    if not only_plain:
        preferred += [
            "text/html; charset=utf-8",
            "text/html",
        ]
    for key in preferred:
        if key in formats:
            url = formats[key]
            if not url.endswith((".zip", ".gz")):
                return url
    for k, url in formats.items():
        if k.startswith("text/") and not url.endswith((".zip", ".gz")):
            return url
    return None

def fetch_gutendex(query: str, limit: int, languages: Optional[set[str]] = None,
                   min_downloads: int = 0, only_plain=True) -> pd.DataFrame:
    books = []
    url = GUTENDEX
    params = {"search": query, "page": 1}

    pbar = tqdm(total=limit, desc=f"Gutendex search: '{query}'")
    while len(books) < limit and url:
        r = requests.get(url, params=params)
        r.raise_for_status()
        js = r.json()
        results = js.get("results", []) or []
        for b in results:
            langs = set(b.get("languages") or [])
            if languages and languages.isdisjoint(langs):
                continue
            dl = int(b.get("download_count") or 0)
            if dl < min_downloads:
                continue
            text_url = pick_text_url(b.get("formats") or {}, only_plain=only_plain)
            if not text_url:
                continue

            book = {
                "pg_id": int(b["id"]),
                "title": normalize(b.get("title") or ""),
                "authors": [normalize(a.get("name") or "") for a in (b.get("authors") or [])],
                "languages": sorted(langs),
                "download_count": dl,
                "subjects": b.get("subjects") or [],
                "bookshelves": b.get("bookshelves") or [],
                "text_url": text_url
            }
            books.append(book)
            pbar.update(1)
            if len(books) >= limit:
                break

        url = js.get("next")
        params = None
        if not results:
            break

    pbar.close()
    df = pd.DataFrame(books).drop_duplicates(subset="pg_id").reset_index(drop=True)
    return df