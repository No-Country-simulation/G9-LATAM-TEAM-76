"""Pairwise multilingual evaluation without invented labels."""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from techmind.data.preprocessing import parallel_pairs

def evaluate_parallel_documents(documents: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    """Calculate similarity for EN↔ES, EN↔PT, and ES↔PT original_url pairs."""
    pairs = parallel_pairs(documents)
    positions = {doc_id: i for i, doc_id in enumerate(documents["id"])}
    rows = []
    for pair in pairs.to_dict("records"):
        score = cosine_similarity(embeddings[positions[pair["id_a"]]].reshape(1, -1), embeddings[positions[pair["id_b"]]].reshape(1, -1))[0, 0]
        rows.append({**pair, "similitud": float(score)})
    return pd.DataFrame(rows, columns=["original_url", "id_a", "idioma_a", "id_b", "idioma_b", "similitud"])

def descriptive_statistics(scores: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics by language pair."""
    if scores.empty: return pd.DataFrame()
    frame = scores.copy()
    frame["par_idiomas"] = frame.apply(lambda row: f"{row.idioma_a}-{row.idioma_b}", axis=1)
    return frame.groupby("par_idiomas")["similitud"].describe()[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
