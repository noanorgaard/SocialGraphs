# download_texts.py
import re, requests
from pathlib import Path
from tqdm import tqdm
from config import TEXT_DIR

def _safe_name(s: str, maxlen=90) -> str:
    s = re.sub(r"[^\w\-\.]+", "_", s.strip())
    return s[:maxlen].strip("_") or "book"

def download_texts(df, limit=None):
    """
    Download text/html files for rows with 'text_url'.
    Returns a copy of df with 'local_path'.
    """
    rows = df.head(limit) if limit else df
    local_paths = []
    for _, row in tqdm(rows.iterrows(), total=len(rows), desc="Downloading texts"):
        url = row.get("text_url")
        if not url:
            local_paths.append(None); continue
        try:
            r = requests.get(url, timeout=45, allow_redirects=True)
            if not r.ok:
                local_paths.append(None); continue
            content_type = r.headers.get("Content-Type", row.get("chosen_mime") or "")
            text = r.content.decode("utf-8", errors="replace")
            fname = f"pg_{row['pg_id']}_{_safe_name(row['title'] or str(row['pg_id']))}.txt"
            path = TEXT_DIR / fname
            path.write_text(text, encoding="utf-8")
            local_paths.append(str(path))
        except Exception:
            local_paths.append(None)
    out = df.copy()
    out["local_path"] = local_paths
    return out
