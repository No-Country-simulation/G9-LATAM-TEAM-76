"""Cosine-neighbor indexing and tabular semantic retrieval."""
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from techmind.embeddings.encoder import encode_query
from techmind.config import MODEL_NAME

SEARCH_COLUMNS = ["id", "titulo", "idioma", "similitud"]

def build_index(embeddings: np.ndarray) -> NearestNeighbors:
    """Build a brute-force cosine index; fit stores vectors, not classes."""
    return NearestNeighbors(metric="cosine", algorithm="brute").fit(embeddings)

def search_related(
    query: str,
    limit: int = 3,
    index: NearestNeighbors | None = None,
    documents: pd.DataFrame | None = None,
    model_name: str = MODEL_NAME,
) -> pd.DataFrame:
    """Search documents related to a text query.

    Parameters
    ----------
    query : str
        Textual query in English, Spanish, Portuguese, or another language
        supported by the configured multilingual model.
    limit : int, default=3
        Maximum number of rows to return. If it exceeds the corpus size, the
        result is limited to the number of available documents.
    index : NearestNeighbors
        Fitted cosine index built with :func:`build_index`.
    documents : pandas.DataFrame
        Documents in exactly the same row order used to fit ``index``.
    model_name : str, default=MODEL_NAME
        SentenceTransformer model used for the query embedding. It must be
        the same model used for the document embeddings.

    Returns
    -------
    pandas.DataFrame
        A table with columns ``id``, ``titulo``, ``idioma`` and
        ``similitud``. Results are ordered from highest to lowest similarity.

    Notes
    -----
    The function intentionally returns a DataFrame rather than a list. The
    notebook pipeline works with tabular document metadata, and this format
    preserves column names and supports filtering/exporting. An API layer can
    later call ``result.to_dict(orient="records")`` when JSON is required.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query debe ser un texto no vacío.")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit debe ser un entero mayor que cero.")
    if index is None or documents is None:
        raise ValueError("index y documents son obligatorios.")
    missing = set(SEARCH_COLUMNS[:3]).difference(documents.columns)
    if missing:
        raise ValueError(f"documents no contiene las columnas requeridas: {sorted(missing)}")
    if documents.empty:
        return pd.DataFrame(columns=SEARCH_COLUMNS)
    fitted_size = getattr(index, "n_samples_fit_", None)
    if fitted_size is not None and fitted_size != len(documents):
        raise ValueError("El índice y documents no tienen el mismo número de filas u orden compatible.")

    query_embedding = encode_query(query, model_name=model_name).reshape(1, -1)
    distances, indices = index.kneighbors(query_embedding, n_neighbors=min(limit, len(documents)))
    result = documents.iloc[indices[0]][["id", "titulo", "idioma"]].copy()
    # Cosine similarity is mathematically [-1, 1]. Clipping only protects the
    # public contract from tiny floating-point overshoots at either boundary.
    result["similitud"] = np.clip(1.0 - distances[0], -1.0, 1.0)
    return result[SEARCH_COLUMNS].reset_index(drop=True)
