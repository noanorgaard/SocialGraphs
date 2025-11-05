import networkx as nx
import pandas as pd

def build_semantic_graph(df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    
    for _, row in df.iterrows():
        pg_id = row['pg_id']
        G.add_node(pg_id, title=row['title'], authors=row['authors'], languages=row['languages'], downloads=row['download_count'], subjects=row['subjects'], bookshelves=row['bookshelves'])
    
    return G

def build_subject_graph(df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    
    for _, row in df.iterrows():
        pg_id = row['pg_id']
        subjects = row['ol_subjects']
        G.add_node(pg_id, title=row['title'], authors=row['authors'], year=row['first_publish_year'])
        
        for subject in subjects:
            G.add_node(subject)
            G.add_edge(pg_id, subject)
    
    return G

def add_edges_from_similarity(G: nx.Graph, edges: list) -> None:
    G.add_edges_from(edges)