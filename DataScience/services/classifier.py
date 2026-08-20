from pathlib import Path
from typing import Optional

import joblib


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "modelo.joblib"
VECTORIZER_PATH = ROOT / "models" / "vectorizador.joblib"

FALLBACK_RULES = {
    "Artificial Intelligence": {"ai", "artificial intelligence", "inteligencia artificial", "neural", "deep learning", "nlp", "transformer"},
    "Software Engineering": {"software", "api", "rest", "java", "spring", "backend", "testing", "programming", "programación"},
    "Information Security": {"security", "seguridad", "cybersecurity", "ciberseguridad", "malware", "encryption", "cifrado", "threat", "vulnerability"},
    "Computer Vision": {"computer vision", "visión", "vision", "image", "imagen", "object detection", "opencv", "segmentation"},
    "Databases": {"database", "databases", "base de datos", "sql", "nosql", "query", "postgresql", "mongodb"},
    "Networks": {"network", "networks", "redes", "tcp", "ip", "routing", "protocol", "protocolo", "distributed"},
    "Machine Learning": {"machine learning", "aprendizaje automático", "classification", "clasificación", "regression", "model", "modelo", "training", "entrenamiento"},
}


class TechnicalContentClassifier:
    """Clasifica texto con el modelo exportado o un fallback local."""

    def __init__(self, model_path: Path = MODEL_PATH, vectorizer_path: Path = VECTORIZER_PATH):
        self.model = joblib.load(model_path) if model_path.exists() else None
        self.vectorizer = joblib.load(vectorizer_path) if vectorizer_path.exists() else None

    def predict(self, title: str, text: str) -> dict:
        content = f"{title} {text}".strip()
        if self.model is not None and self.vectorizer is not None:
            matrix = self.vectorizer.transform([content])
            probabilities = self.model.predict_proba(matrix)[0]
            index = probabilities.argmax()
            return {"categoria": str(self.model.classes_[index]), "probabilidad": float(probabilities[index])}
        return self._fallback_predict(content)

    @staticmethod
    def _fallback_predict(content: str) -> dict:
        normalized = content.lower()
        scores = {category: sum(1 for term in terms if term in normalized) for category, terms in FALLBACK_RULES.items()}
        category, score = max(scores.items(), key=lambda item: item[1])
        if score == 0:
            return {"categoria": "Software Engineering", "probabilidad": 0.35}
        confidence = min(0.55 + score * 0.1, 0.95)
        return {"categoria": category, "probabilidad": confidence}

