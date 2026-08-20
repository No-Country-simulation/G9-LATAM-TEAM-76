import re
from collections import Counter
from typing import Optional


STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "using", "una", "uno", "las", "los", "del", "para", "con", "que", "por", "como", "una", "este", "esta", "sobre", "en", "de", "y", "a", "el", "la"
}


def extract_keywords(text: str, vectorizer=None, top_n: int = 5) -> list[str]:
    """Extrae términos TF-IDF si existe vectorizador; si no, usa frecuencia."""
    if not text.strip():
        return []
    if vectorizer is not None:
        row = vectorizer.transform([text])
        terms = vectorizer.get_feature_names_out()
        ranked = row.toarray()[0].argsort()[::-1]
        return [str(terms[index]) for index in ranked if row[0, index] > 0][:top_n]
    tokens = re.findall(r"[a-záéíóúñ][a-záéíóúñ0-9+#.-]{2,}", text.lower())
    counts = Counter(token for token in tokens if token not in STOPWORDS)
    return [token for token, _ in counts.most_common(top_n)]

