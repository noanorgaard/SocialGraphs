import pathlib
import pandas as pd
from tqdm import tqdm
from typing import Optional

def strip_pg_boilerplate(txt: str) -> str:
    _START_RE = re.compile(r"\*\*\*\s*START OF (THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
    _END_RE = re.compile(r"\*\*\*\s*END OF (THIS|THE) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
    
    s = _START_RE.search(txt)
    e = _END_RE.search(txt)
    if s: 
        txt = txt[s.end():]
    if e: 
        txt = txt[:e.start()]
    return txt.replace("\r", " ").strip()

def download_texts(df: pd.DataFrame, text_dir: pathlib.Path) -> pd.DataFrame:
    paths = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Downloading PG texts"):
        pgid = row["pg_id"]
        p = text_dir / f"pg_{pgid}.txt"
        if not p.exists():
            try:
                r = http_get(row["text_url"])
                txt = strip_pg_boilerplate(r.text or "")
                if len(txt) < 2000:
                    paths.append(None)
                    continue
                p.write_text(txt, encoding="utf-8")
            except Exception:
                paths.append(None)
                continue
        paths.append(str(p))
    df = df.copy()
    df["text_path"] = paths
    df = df[df["text_path"].notna()].reset_index(drop=True)
    return df