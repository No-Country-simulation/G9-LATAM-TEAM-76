"""Read and write the stable artifact contract."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from techmind.config import MODEL_NAME, NORMALIZE_EMBEDDINGS

def save_documents(documents: pd.DataFrame, path: Path) -> None:
    """Save document metadata as UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    documents.to_json(path, orient="records", force_ascii=False, indent=2)

def load_documents(path: Path) -> pd.DataFrame:
    """Load documents or identify the missing previous module."""
    if not path.exists(): raise FileNotFoundError("Falta dataset_procesado.json; ejecute primero el Módulo 01.")
    return pd.read_json(path)

def load_embeddings(path: Path) -> np.ndarray:
    """Load embeddings or identify the missing previous module."""
    if not path.exists(): raise FileNotFoundError("Falta embeddings.npy; ejecute primero el Módulo 02.")
    return np.load(path)

def load_index(path: Path):
    """Load the index or identify the missing previous module."""
    if not path.exists(): raise FileNotFoundError("Falta semantic_index.joblib; ejecute primero el Módulo 03.")
    return joblib.load(path)

def save_model_config(path: Path, documents: int, embedding_dimension: int) -> None:
    """Persist model parameters for downstream consumers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model_name": MODEL_NAME, "normalize_embeddings": NORMALIZE_EMBEDDINGS, "similarity_metric": "cosine", "documents": documents, "embedding_dimension": embedding_dimension}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
