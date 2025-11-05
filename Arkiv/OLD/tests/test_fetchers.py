import pytest
from src.fetch_gutendex import fetch_gutendex

def test_fetch_gutendex_valid_query():
    query = "romance"
    limit = 5
    languages = {"en"}
    min_downloads = 50
    df = fetch_gutendex(query, limit, languages, min_downloads)
    assert df is not None
    assert len(df) <= limit
    assert all(lang in languages for lang in df["languages"].explode().unique())

def test_fetch_gutendex_no_results():
    query = "nonexistentbooktitle"
    limit = 5
    languages = {"en"}
    min_downloads = 50
    df = fetch_gutendex(query, limit, languages, min_downloads)
    assert df.empty

def test_fetch_gutendex_invalid_language():
    query = "romance"
    limit = 5
    languages = {"xx"}  # Invalid language code
    min_downloads = 50
    df = fetch_gutendex(query, limit, languages, min_downloads)
    assert df.empty

def test_fetch_gutendex_min_downloads():
    query = "romance"
    limit = 10
    languages = {"en"}
    min_downloads = 1000  # High threshold
    df = fetch_gutendex(query, limit, languages, min_downloads)
    assert df.empty  # Expecting no results due to high download count filter