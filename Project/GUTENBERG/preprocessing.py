# preprocessing.py
import re
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm
from config import CLEAN_DIR, STRIP_HTML, LOWERCASE, REMOVE_GUTENBERG_HEADERS

START_RE = re.compile(r"\*\*\*\s*START OF (THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
END_RE   = re.compile(r"\*\*\*\s*END OF (THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)

def _strip_boilerplate(txt: str) -> str:
    if not REMOVE_GUTENBERG_HEADERS: return txt
    s = START_RE.search(txt); e = END_RE.search(txt)
    if s: txt = txt[s.end():]
    if e: txt = txt[:e.start()]
    return txt

def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]): tag.decompose()
    text = soup.get_text(" ")
    return re.sub(r"\s+", " ", text).strip()

def clean_texts(df):
    """
    Read 'local_path', clean text, write to CLEAN_DIR, return df with 'clean_path'.
    """
    paths = []
    # ensure output dir exists
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Cleaning texts"):
        p = row.get("local_path")
        if not p:
            paths.append(None); continue
        raw = Path(p).read_text(encoding="utf-8", errors="ignore")
        txt = raw
        # If content looks like HTML, optionally strip tags
        if STRIP_HTML and ("<html" in raw.lower() or "</p>" in raw.lower()):
            txt = _html_to_text(raw)
        txt = _strip_boilerplate(txt)
        if LOWERCASE:
            txt = txt.lower()
        out = CLEAN_DIR / (Path(p).stem + "_clean.txt")
        out.write_text(txt, encoding="utf-8")
        paths.append(str(out))
    out_df = df.copy()
    out_df["clean_path"] = paths
    return out_df
