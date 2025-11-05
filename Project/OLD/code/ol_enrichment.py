import requests

def ol_search(title: str, author: str | None = None, page_sz=50) -> Optional[dict]:
    params = {"title": title, "limit": page_sz}
    if author:
        params["author"] = author
    r = http_get("https://openlibrary.org/search.json", params=params)
    js = r.json()
    docs = js.get("docs", []) or []
    return docs

def norm_tokens(s: str) -> set[str]:
    s = normalize(s.lower())
    s = re.sub(r"[^\w\s]", " ", s)
    toks = set([t for t in s.split() if t])
    return toks

def best_ol_match(title: str, author: str | None, docs: list[dict]) -> Optional[dict]:
    t_tokens = norm_tokens(title)
    a_tokens = norm_tokens(author) if author else set()
    best, best_score = None, 0.0

    for d in docs:
        dt = d.get("title") or ""
        dat = d.get("author_name") or []
        dtok = norm_tokens(dt)
        j_title = len(t_tokens & dtok) / (len(t_tokens | dtok) or 1)
        j_author = 0.0
        if a_tokens and dat:
            j_author = max((len(a_tokens & norm_tokens(x)) / (len(a_tokens | norm_tokens(x)) or 1)) for x in dat)
        score = 0.75 * j_title + 0.25 * j_author
        if score > best_score:
            best, best_score = d, score

    if best_score >= 0.5:
        return best
    return None

# Run enrichment
enriched = []
for _, row in tqdm(df_pg.iterrows(), total=len(df_pg), desc="Enriching via OL"):
    title = row["title"]
    author = row["authors"][0] if row["authors"] else None
    docs = ol_search(title, author)
    match = best_ol_match(title, author, docs or [])
    if match:
        enriched.append({
            "pg_id": row["pg_id"],
            "ol_work_key": match.get("key"),
            "first_publish_year": match.get("first_publish_year"),
            "edition_count": match.get("edition_count"),
            "ol_subjects": match.get("subject") or []
        })
    else:
        enriched.append({
            "pg_id": row["pg_id"],
            "ol_work_key": None,
            "first_publish_year": None,
            "edition_count": None,
            "ol_subjects": []
        })

df_ol = pd.DataFrame(enriched)
df_all = df_pg.merge(df_ol, on="pg_id", how="left")
df_all.to_csv(DATA_DIR / f"pg_{QUERY}_with_ol.csv", index=False)
df_all.head(3)