import numpy as np
import pandas as pd
import techmind.search.semantic_search as semantic_search
from techmind.search.semantic_search import build_index, search_related

def test_index_is_cosine_brute_and_limit_is_bounded():
    index = build_index(np.eye(3, dtype=np.float32))
    docs = pd.DataFrame({"id": ["a", "b", "c"], "titulo": ["A", "B", "C"], "idioma": ["en"] * 3})
    distances, indices = index.kneighbors(np.array([[1, 0, 0]], dtype=np.float32), n_neighbors=2)
    assert index.metric == "cosine"
    assert len(indices[0]) == 2
    assert 0 <= 1 - distances[0, 0] <= 1

def test_search_related_returns_ordered_dataframe(monkeypatch):
    index = build_index(np.eye(3, dtype=np.float32))
    docs = pd.DataFrame({
        "id": ["a", "b", "c"],
        "titulo": ["A", "B", "C"],
        "idioma": ["en", "es", "pt"],
    })
    monkeypatch.setattr(semantic_search, "encode_query", lambda query, model_name: np.array([1, 0, 0], dtype=np.float32))
    result = search_related("consulta", limit=2, index=index, documents=docs, model_name="test-model")
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["id", "titulo", "idioma", "similitud"]
    assert list(result.id) == ["a", "b"]
    assert result.similitud.between(-1, 1).all()

def test_search_related_rejects_misaligned_documents():
    index = build_index(np.eye(3, dtype=np.float32))
    docs = pd.DataFrame({"id": ["a"], "titulo": ["A"], "idioma": ["en"]})
    try:
        search_related("consulta", index=index, documents=docs)
    except ValueError as error:
        assert "mismo número de filas" in str(error)
    else:
        raise AssertionError("Expected a ValueError for an index/document mismatch")
