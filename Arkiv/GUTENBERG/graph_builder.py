# graph_builder.py
import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from config import (JACCARD_MIN, TOPK_TAG_NEIGHBORS, OUT_DIR)
import json
from typing import Any

def _serialize_attr(v: Any):
    """Convert lists/dicts to JSON string, None -> empty string, keep numbers as-is, else str."""
    if v is None:
        return ""
    if isinstance(v, (list, dict, tuple)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except Exception:
            return str(v)
    if isinstance(v, (int, float, str)):
        return v
    return str(v)

def build_semantic_graph(df, edges):
    G = nx.Graph()
    # add nodes (+ useful attributes for analysis)
    for i, row in df.iterrows():
        G.add_node(i, **{
            "pg_id": _serialize_attr(row.get("pg_id")),
            "title": _serialize_attr(row.get("title")),
            "authors": _serialize_attr(row.get("authors")),
            "downloads": _serialize_attr(row.get("download_count")),
            "year": _serialize_attr(row.get("ol_first_publish_year")),
            "edition_count": _serialize_attr(row.get("ol_edition_count")),
            "subjects": _serialize_attr(row.get("ol_subjects")),
            "bookshelves": _serialize_attr(row.get("bookshelves")),
        })
    # add weighted edges (cosine similarity)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    nx.write_graphml(G, OUT_DIR / "semantic.graphml")
    return G

def _build_subject_incidence(df):
    subs = df["ol_subjects"].apply(lambda s: s if isinstance(s, list) else []).tolist()
    vocab = {}
    rows, cols, vals = [], [], []
    for i, ss in enumerate(subs):
        for s in ss:
            if s not in vocab: vocab[s] = len(vocab)
            rows.append(i); cols.append(vocab[s]); vals.append(1)
    S = csr_matrix((vals, (rows, cols)), shape=(len(subs), len(vocab)))
    return S, vocab

def build_subject_graph(df):
    # Create incidence matrix and cosine neighbors for candidate pairs
    S, vocab = _build_subject_incidence(df)
    nn = NearestNeighbors(n_neighbors=TOPK_TAG_NEIGHBORS+1, metric="cosine", algorithm="brute").fit(S)
    dist, idx = nn.kneighbors(S)

    def jaccard(a, b):
        A, B = set(a), set(b)
        if not A and not B: return 0.0
        return len(A & B) / len(A | B)

    subs = df["ol_subjects"].apply(lambda s: s if isinstance(s, list) else []).tolist()
    G = nx.Graph()
    for i, row in df.iterrows():
        G.add_node(i, **{
            "pg_id": _serialize_attr(row.get("pg_id")),
            "title": _serialize_attr(row.get("title")),
            "authors": _serialize_attr(row.get("authors")),
            "downloads": _serialize_attr(row.get("download_count")),
            "year": _serialize_attr(row.get("ol_first_publish_year")),
            "edition_count": _serialize_attr(row.get("ol_edition_count")),
            "subjects": _serialize_attr(row.get("ol_subjects")),
        })

    for i, neighs in enumerate(idx):
        for j in neighs[1:]:
            jac = jaccard(subs[i], subs[j])
            if jac >= JACCARD_MIN:
                G.add_edge(i, j, weight=float(jac))
    nx.write_graphml(G, OUT_DIR / "subjects.graphml")
    return G
