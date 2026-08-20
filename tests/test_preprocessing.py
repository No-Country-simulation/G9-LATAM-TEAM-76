import pandas as pd
from techmind.data.preprocessing import FINAL_COLUMNS, clean_text, parallel_pairs, prepare_documents

def sample_documents():
    return pd.DataFrame([
        {"id":"1", "title":"Título\t", "content":"á\n texto", "language":"en", "url":"u1", "original_url":"o1"},
        {"id":"2", "title":"Título ES", "content":"texto", "language":"es", "url":"u2", "original_url":"o1"},
        {"id":"3", "title":"Título PT", "content":"texto", "language":"pt", "url":"u3", "original_url":"o1"},
    ])

def test_clean_text_preserves_accents_and_normalizes_space():
    assert clean_text("  á\t  ñ  ") == "á ñ"

def test_prepare_schema_languages_and_pairs():
    documents = prepare_documents(sample_documents())
    assert list(documents.columns) == FINAL_COLUMNS
    assert set(documents.idioma) == {"en", "es", "pt"}
    assert len(parallel_pairs(documents)) == 3
