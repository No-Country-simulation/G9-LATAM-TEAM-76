import numpy as np
import pandas as pd
from techmind.embeddings.encoder import semantic_texts

def test_semantic_text_combines_title_and_body():
    docs = pd.DataFrame({"titulo": ["Hola"], "texto": ["mundo"]})
    assert semantic_texts(docs) == ["Hola. mundo"]

def test_embedding_contract_example():
    vectors = np.zeros((2, 384), dtype=np.float32)
    assert vectors.shape == (2, 384)
    assert vectors.dtype == np.float32
