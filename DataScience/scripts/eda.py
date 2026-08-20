"""Ejecuta un EDA reproducible sobre el dataset original de ArXiv.

Uso:
    python scripts/eda.py
    python scripts/eda.py --input data/arxiv.csv --sample-size 20000
"""
from __future__ import annotations

import argparse
import json
import re
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "arxiv.csv"
DEFAULT_OUTPUT = ROOT / "reports" / "eda"
RANDOM_STATE = 42
TEXT_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "are", "using", "into",
    "their", "which", "based", "have", "has", "was", "were", "will", "our", "can",
    "una", "uno", "para", "con", "los", "las", "del", "por", "que", "como", "sus",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV original de ArXiv")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Directorio de reportes")
    parser.add_argument("--sample-size", type=int, default=20000, help="Filas para gráficos y análisis de texto")
    return parser.parse_args()


def _json_value(value):
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _write_plot(path: Path):
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def _token_counts(texts: pd.Series, top_n: int = 30) -> pd.DataFrame:
    counts: dict[str, int] = {}
    for text in texts.fillna(""):
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())
        for token in tokens:
            if token not in TEXT_STOPWORDS:
                counts[token] = counts.get(token, 0) + 1
    return pd.DataFrame(sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top_n], columns=["termino", "frecuencia"])


def _category_pairs(categories: pd.Series) -> pd.DataFrame:
    counts: dict[tuple[str, str], int] = {}
    for value in categories.fillna(""):
        labels = sorted(set(str(value).split()))
        for pair in combinations(labels, 2):
            counts[pair] = counts.get(pair, 0) + 1
    rows = [{"categoria_1": pair[0], "categoria_2": pair[1], "frecuencia": count} for pair, count in counts.items()]
    return pd.DataFrame(rows).sort_values("frecuencia", ascending=False) if rows else pd.DataFrame(columns=["categoria_1", "categoria_2", "frecuencia"])


def run_eda(input_path: Path = DEFAULT_INPUT, output_dir: Path = DEFAULT_OUTPUT, sample_size: int = 20000) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(input_path)
    required = {"paper_id", "title", "abstract", "year", "primary_category", "categories"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    # `names=` was added to Series.reset_index in newer pandas versions.
    # Keep this compatible with older environments as well.
    nulls = (
        frame.isna().sum()
        .rename("nulos")
        .reset_index()
        .rename(columns={"index": "columna"})
    )
    duplicate_counts = {
        "paper_id": int(frame["paper_id"].duplicated().sum()),
        "title": int(frame["title"].duplicated().sum()),
        "abstract": int(frame["abstract"].duplicated().sum()),
        "rows_completely_duplicated": int(frame.duplicated().sum()),
    }
    incomplete = int(frame[["title", "abstract", "primary_category"]].isna().any(axis=1).sum())
    frame["year_parsed"] = pd.to_datetime(frame["year"], errors="coerce").dt.year
    frame["title_length"] = frame["title"].fillna("").astype(str).str.len()
    frame["abstract_length"] = frame["abstract"].fillna("").astype(str).str.len()
    sample = frame.sample(n=min(sample_size, len(frame)), random_state=RANDOM_STATE) if len(frame) else frame.copy()

    primary_counts = frame["primary_category"].value_counts(dropna=False).rename_axis("primary_category").reset_index(name="count")
    year_counts = frame["year_parsed"].value_counts(dropna=False).sort_index().rename_axis("year").reset_index(name="count")
    length_stats = frame[["title_length", "abstract_length"]].describe().round(2).reset_index()
    top_terms = _token_counts(sample["abstract"])
    category_pairs = _category_pairs(sample["categories"])

    nulls.to_csv(output_dir / "nulls.csv", index=False)
    primary_counts.to_csv(output_dir / "primary_categories.csv", index=False)
    year_counts.to_csv(output_dir / "years.csv", index=False)
    length_stats.to_csv(output_dir / "text_length_stats.csv", index=False)
    top_terms.to_csv(output_dir / "top_terms.csv", index=False)
    category_pairs.to_csv(output_dir / "category_cooccurrence.csv", index=False)

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 7))
    sns.barplot(data=primary_counts.head(20), y="primary_category", x="count", color="#0d6efd")
    plt.title("Top 20 categorías primarias")
    plt.xlabel("Registros")
    plt.ylabel("Categoría")
    _write_plot(output_dir / "primary_categories.png")

    plt.figure(figsize=(12, 5))
    sns.lineplot(data=year_counts.dropna(subset=["year"]), x="year", y="count", marker="o", color="#6f42c1")
    plt.title("Distribución temporal de publicaciones")
    plt.xlabel("Año")
    plt.ylabel("Registros")
    _write_plot(output_dir / "years.png")

    lengths = sample[["title_length", "abstract_length"]].melt(var_name="campo", value_name="caracteres")
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=lengths, x="campo", y="caracteres", color="#20c997", showfliers=False)
    plt.title("Longitud del título y resumen (muestra)")
    _write_plot(output_dir / "text_lengths.png")

    plt.figure(figsize=(12, 7))
    sns.barplot(data=top_terms, y="termino", x="frecuencia", color="#fd7e14")
    plt.title("Términos más frecuentes en abstracts (muestra)")
    _write_plot(output_dir / "top_terms.png")

    summary = {
        "input": str(input_path),
        "rows": int(len(frame)),
        "columns": list(frame.columns[:6]),
        "sample_size": int(len(sample)),
        "random_state": RANDOM_STATE,
        "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        "nulls": {row.columna: int(row.nulos) for row in nulls.itertuples()},
        "duplicate_counts": duplicate_counts,
        "incomplete_records": incomplete,
        "unique_primary_categories": int(frame["primary_category"].nunique(dropna=True)),
        "year_min": _json_value(frame["year_parsed"].min()),
        "year_max": _json_value(frame["year_parsed"].max()),
        "text_length_means": {column: float(frame[column].mean()) for column in ["title_length", "abstract_length"]},
        "top_primary_categories": {str(row.primary_category): int(row.count) for row in primary_counts.head(20).itertuples()},
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    arguments = parse_args()
    result = run_eda(arguments.input, arguments.output, arguments.sample_size)
    print(json.dumps(result, ensure_ascii=False, indent=2))
