import re
import unicodedata

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()

def clean_text(text: str) -> str:
    # Normalize the text
    text = normalize_text(text)
    # Additional cleaning steps can be added here
    return text

def preprocess_texts(texts: list[str]) -> list[str]:
    return [clean_text(text) for text in texts]