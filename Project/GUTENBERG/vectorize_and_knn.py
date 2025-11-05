# vectorize_and_knn.py
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
from config import (TFIDF_MAX_FEATURES, TFIDF_MIN_DF, TFIDF_MAX_DF, NGRAM_RANGE,
                    K_NEIGHBORS, SIM_THRESHOLD, OUT_DIR)

def _read(path):
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def vectorize_corpus(df):
    corpus_ids   = df.index.tolist()
    corpus_paths = df["clean_path"].tolist()
    texts = [ _read(p) if p else "" for p in tqdm(corpus_paths, desc="Reading cleaned texts") ]
    vect = TfidfVectorizer(lowercase=False, stop_words="english",
                           max_features=TFIDF_MAX_FEATURES, min_df=TFIDF_MIN_DF,
                           max_df=TFIDF_MAX_DF, ngram_range=NGRAM_RANGE)
    X = vect.fit_transform(texts)
    # save shapes
    (OUT_DIR / "tfidf_shape.txt").write_text(str(X.shape))
    return X, vect, corpus_ids

def knn_edges(X, corpus_ids, k=K_NEIGHBORS, sim_threshold=SIM_THRESHOLD):
    nn = NearestNeighbors(n_neighbors=k+1, metric="cosine", algorithm="brute")
    nn.fit(X)
    dist, idx = nn.kneighbors(X)
    # Build edge list: sim = 1 - dist
    edges = []
    for i, (drow, neighs) in enumerate(zip(dist, idx)):
        src = corpus_ids[i]
        for d, j in zip(drow[1:], neighs[1:]):   # skip self
            sim = 1.0 - d
            if sim >= sim_threshold:
                edges.append((src, corpus_ids[j], float(sim)))
    return edges
