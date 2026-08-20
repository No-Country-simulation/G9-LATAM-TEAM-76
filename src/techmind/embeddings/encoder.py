"""Encoding helpers; no training or fine-tuning occurs here."""
import numpy as np
import pandas as pd
from techmind.config import MODEL_NAME, NORMALIZE_EMBEDDINGS

def semantic_texts(documents: pd.DataFrame) -> list[str]:
    """Combine title and body into the text represented by the encoder."""
    return (documents["titulo"].fillna("").str.strip() + ". " + documents["texto"].fillna("").str.strip()).tolist()

def encode_texts(texts: list[str], model_name: str = MODEL_NAME, batch_size: int = 32) -> np.ndarray:
    """Generate normalized float32 embeddings with SentenceTransformer."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc: raise ImportError("Instale 'sentence-transformers' para generar embeddings.") from exc
    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=NORMALIZE_EMBEDDINGS, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)

def encode_query(query: str, model_name: str = MODEL_NAME) -> np.ndarray:
    """Encode one multilingual search query with the same representation contract."""
    return encode_texts([query], model_name=model_name, batch_size=1)[0]
