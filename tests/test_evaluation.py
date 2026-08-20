import numpy as np
import pandas as pd
from techmind.evaluation.multilingual import descriptive_statistics, evaluate_parallel_documents
from techmind.data.preprocessing import prepare_documents

def test_evaluation_only_uses_parallel_pairs():
    raw = pd.DataFrame([
        {"id":"1", "title":"A", "content":"x", "language":"en", "url":"1", "original_url":"same"},
        {"id":"2", "title":"B", "content":"x", "language":"es", "url":"2", "original_url":"same"},
        {"id":"3", "title":"C", "content":"x", "language":"pt", "url":"3", "original_url":"other"},
    ])
    docs = prepare_documents(raw)
    scores = evaluate_parallel_documents(docs, np.eye(3, dtype=np.float32))
    assert len(scores) == 1 and scores.iloc[0].original_url == "same"
    assert set(descriptive_statistics(scores).columns) == {"count", "mean", "std", "min", "25%", "50%", "75%", "max"}
