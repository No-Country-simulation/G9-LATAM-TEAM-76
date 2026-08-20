"""Preparation of the multilingual parallel-document dataset."""
import re
import unicodedata
from itertools import combinations
from typing import Any
import pandas as pd
from techmind.config import DATASET_CONFIG, DATASET_NAME, DATASET_SPLIT, LANGUAGES, PROTOTYPE_PER_LANGUAGE, RANDOM_STATE

FINAL_COLUMNS = ["id", "titulo", "texto", "idioma", "url", "original_url"]

def clean_text(value: Any) -> str:
    """Normalize Unicode and spacing while preserving multilingual characters."""
    text = "" if pd.isna(value) else unicodedata.normalize("NFC", str(value))
    text = "".join(c for c in text if unicodedata.category(c) not in {"Cc", "Cf"} or c in "\n\t")
    return re.sub(r"\s+", " ", text).strip()

def load_source_dataset() -> pd.DataFrame:
    """Download the configured Hugging Face train split."""
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise ImportError("Instale 'datasets' para ejecutar el Módulo 01.") from exc
    dataset = load_dataset(DATASET_NAME, name=DATASET_CONFIG, split=DATASET_SPLIT)
    return dataset.to_pandas()

def prepare_documents(raw: pd.DataFrame) -> pd.DataFrame:
    """Filter EN/ES/PT, rename fields, clean text, and validate the schema."""
    required = {"id", "title", "content", "language", "url", "original_url"}
    missing = required.difference(raw.columns)
    if missing: raise ValueError(f"Faltan columnas del dataset: {sorted(missing)}")
    frame = raw.loc[raw["language"].isin(LANGUAGES), ["id", "title", "content", "language", "url", "original_url"]].copy()
    frame = frame.rename(columns={"title": "titulo", "content": "texto", "language": "idioma"})
    for column in ("id", "titulo", "texto", "url", "original_url"): frame[column] = frame[column].map(clean_text)
    frame = frame[FINAL_COLUMNS].drop_duplicates().reset_index(drop=True)
    validate_documents(frame)
    return frame

def validate_documents(documents: pd.DataFrame) -> None:
    """Raise a clear error when the prepared document contract is violated."""
    if list(documents.columns) != FINAL_COLUMNS: raise ValueError(f"Esquema inválido; se esperaba {FINAL_COLUMNS}")
    if not documents["idioma"].isin(LANGUAGES).all(): raise ValueError("Hay idiomas fuera de EN/ES/PT.")
    if documents["id"].eq("").any() or documents["texto"].eq("").any(): raise ValueError("No se permiten IDs o textos vacíos.")
    if documents["id"].duplicated().any(): raise ValueError("Hay IDs duplicados.")

def select_parallel_prototype(documents: pd.DataFrame, per_language: int = PROTOTYPE_PER_LANGUAGE) -> pd.DataFrame:
    """Select reproducibly complete original_url groups, one document per language."""
    complete = [url for url, group in documents.groupby("original_url") if set(group["idioma"]) >= set(LANGUAGES)]
    if len(complete) < per_language: raise ValueError(f"Solo hay {len(complete)} grupos completos; se requieren {per_language}.")
    chosen = pd.Series(complete).sample(n=per_language, random_state=RANDOM_STATE).tolist()
    # A URL can occasionally contain more than one record per language; the
    # prototype contract explicitly requires exactly one document per language.
    result = documents[documents["original_url"].isin(chosen)].copy()
    result = result.sort_values("id").groupby(["original_url", "idioma"], as_index=False).head(1)
    result["_order"] = result["idioma"].map({lang: i for i, lang in enumerate(LANGUAGES)})
    return result.sort_values(["original_url", "_order"])[FINAL_COLUMNS].reset_index(drop=True)

def parallel_pairs(documents: pd.DataFrame) -> pd.DataFrame:
    """Return language pairs sharing the same original_url."""
    rows = []
    for url, group in documents.groupby("original_url"):
        by_language = {lang: item.iloc[0] for lang, item in group.groupby("idioma") if lang in LANGUAGES}
        for left, right in combinations(LANGUAGES, 2):
            if left in by_language and right in by_language:
                rows.append({"original_url": url, "id_a": by_language[left]["id"], "idioma_a": left, "id_b": by_language[right]["id"], "idioma_b": right})
    return pd.DataFrame(rows, columns=["original_url", "id_a", "idioma_a", "id_b", "idioma_b"])
