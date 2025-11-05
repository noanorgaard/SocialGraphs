import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

def vectorize_texts(corpus_texts: list[str], max_features: int = 120000, ngram_range: tuple[int, int] = (1, 2)) -> tuple[np.ndarray, TfidfVectorizer]:
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words='english',
        ngram_range=ngram_range,
        max_df=0.85,
        min_df=5,
        max_features=max_features
    )
    X = vectorizer.fit_transform(corpus_texts)
    return X, vectorizer

def perform_knn(X: np.ndarray, n_neighbors: int = 10) -> tuple[np.ndarray, np.ndarray]:
    nbrs = NearestNeighbors(n_neighbors=n_neighbors + 1, metric='cosine', algorithm='brute').fit(X)
    distances, indices = nbrs.kneighbors(X)
    return distances, indices

def get_similar_books(corpus_ids: list[int], distances: np.ndarray, indices: np.ndarray, sim_threshold: float = 0.25) -> list[tuple[int, int, float]]:
    edges = []
    for i, (drow, irow) in enumerate(zip(distances, indices)):
        src = corpus_ids[i]
        for dist, j in zip(drow[1:], irow[1:]):  # skip self
            sim = 1 - dist
            if sim >= sim_threshold:
                tgt = corpus_ids[j]
                edges.append((src, tgt, {'weight': float(sim)}))
    return edges