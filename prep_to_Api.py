"""Preparación de entrada y salida para una futura API REST de TechMind.

Este módulo recibe una entrada JSON con el formato:

{
    "titulo": "Aquí va el título",
    "texto": "Aquí va el texto"
}

Y devuelve una salida JSON basada en búsqueda semántica:

{
    "consulta": {
        "titulo": "Introducción a Spring Boot",
        "texto": "En este contenido se presentan los conceptos básicos..."
    },
    "query_generada": "Introducción a Spring Boot. En este contenido...",
    "total_resultados": 3,
    "documentos_relacionados": [
        {
            "id": "es/example",
            "titulo": "Documento relacionado",
            "idioma": "es",
            "similitud": 0.82
        }
    ]
}

Importante:
Este archivo no implementa un clasificador supervisado ni reglas manuales
de categorías. Usa los artefactos semánticos existentes del proyecto:
documents.json y semantic_index.joblib.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from techmind.config import MODEL_NAME, get_paths
from techmind.persistence.artifacts import load_documents, load_index
from techmind.search.semantic_search import search_related


class InputValidationError(ValueError):
    """Error para entradas inválidas recibidas por la futura API."""


def normalize_text(value: Any) -> str:
    """Normaliza texto preservando acentos y caracteres multilingües."""
    if value is None:
        return ""

    text = unicodedata.normalize("NFC", str(value))
    text = "".join(
        character
        for character in text
        if unicodedata.category(character) not in {"Cc", "Cf"}
        or character in "\n\t"
    )
    return re.sub(r"\s+", " ", text).strip()


def validate_payload(payload: Any) -> dict[str, str]:
    """Valida que la entrada tenga el contrato esperado por la API.

    La entrada debe ser un diccionario con los campos obligatorios:

    - titulo
    - texto
    """
    if not isinstance(payload, dict):
        raise InputValidationError("La entrada debe ser un objeto JSON.")

    required_fields = {"titulo", "texto"}
    missing_fields = required_fields.difference(payload)

    if missing_fields:
        raise InputValidationError(
            f"Faltan campos obligatorios: {sorted(missing_fields)}."
        )

    titulo = normalize_text(payload.get("titulo"))
    texto = normalize_text(payload.get("texto"))

    if not titulo:
        raise InputValidationError("El campo 'titulo' no puede estar vacío.")

    if not texto:
        raise InputValidationError("El campo 'texto' no puede estar vacío.")

    if len(titulo) > 300:
        raise InputValidationError(
            "El campo 'titulo' no debe superar 300 caracteres."
        )

    if len(texto) > 20_000:
        raise InputValidationError(
            "El campo 'texto' no debe superar 20000 caracteres."
        )

    return {
        "titulo": titulo,
        "texto": texto,
    }


def build_content_text(payload: dict[str, str]) -> str:
    """Une título y texto para crear la consulta semántica."""
    return f"{payload['titulo']}. {payload['texto']}"


def validate_limit(limit: Any) -> int:
    """Valida el número máximo de resultados a recuperar."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise InputValidationError("El parámetro 'limit' debe ser un entero.")

    if limit < 1:
        raise InputValidationError("El parámetro 'limit' debe ser mayor que cero.")

    if limit > 20:
        raise InputValidationError("El parámetro 'limit' no debe superar 20.")

    return limit


def dataframe_results_to_json_records(results: Any) -> list[dict[str, Any]]:
    """Convierte los resultados tabulares de búsqueda a registros JSON."""
    records = results.to_dict(orient="records")

    for record in records:
        if "similitud" in record:
            record["similitud"] = round(float(record["similitud"]), 6)

    return records


def process_content(payload: Any, limit: int = 3) -> dict[str, Any]:
    """Procesa una entrada JSON y devuelve documentos relacionados.

    Esta función es la pieza principal para una futura API REST. No clasifica
    manualmente el contenido. En su lugar, reutiliza el índice semántico del
    proyecto para recuperar documentos cercanos por similitud coseno.

    Parameters
    ----------
    payload:
        Diccionario con los campos ``titulo`` y ``texto``.
    limit:
        Número máximo de documentos relacionados a devolver.

    Returns
    -------
    dict[str, Any]
        Resultado serializable como JSON.
    """
    validated_payload = validate_payload(payload)
    validated_limit = validate_limit(limit)
    query = build_content_text(validated_payload)

    paths = get_paths()
    documents = load_documents(paths.documents)
    index = load_index(paths.index)

    results = search_related(
        query=query,
        limit=validated_limit,
        index=index,
        documents=documents,
        model_name=MODEL_NAME,
    )

    json_results = dataframe_results_to_json_records(results)

    return {
        "consulta": validated_payload,
        "query_generada": query,
        "total_resultados": len(json_results),
        "documentos_relacionados": json_results,
    }


def process_json_string(raw_json: str, limit: int = 3) -> dict[str, Any]:
    """Procesa una cadena JSON y devuelve documentos relacionados."""
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise InputValidationError("La entrada no contiene un JSON válido.") from exc

    return process_content(payload, limit=limit)


def safe_process_content(payload: Any, limit: int = 3) -> dict[str, Any]:
    """Procesa contenido y devuelve errores controlados para una futura API REST."""
    try:
        return {
            "ok": True,
            "resultado": process_content(payload, limit=limit),
            "error": None,
        }
    except InputValidationError as exc:
        return {
            "ok": False,
            "resultado": None,
            "error": {
                "tipo": "VALIDATION_ERROR",
                "mensaje": str(exc),
            },
        }
    except FileNotFoundError as exc:
        return {
            "ok": False,
            "resultado": None,
            "error": {
                "tipo": "ARTIFACT_NOT_FOUND",
                "mensaje": str(exc),
                "sugerencia": (
                    "Ejecute primero los notebooks 01, 02 y 03 para generar "
                    "documents.json, embeddings.npy y semantic_index.joblib."
                ),
            },
        }
    except Exception as exc:
        return {
            "ok": False,
            "resultado": None,
            "error": {
                "tipo": "INTERNAL_ERROR",
                "mensaje": "Ocurrió un error inesperado al procesar el contenido.",
                "detalle": str(exc),
            },
        }


def parse_args() -> argparse.Namespace:
    """Lee una entrada JSON opcional desde la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Procesa un contenido JSON usando búsqueda semántica."
    )

    parser.add_argument(
        "datos_json",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Cadena de texto en formato JSON válido. "
            "Ejemplo: "
            '\'{"titulo":"Introducción a Spring Boot","texto":"Creación de una API REST"}\''
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Número máximo de documentos relacionados a devolver. Valor por defecto: 3.",
    )

    return parser.parse_args()


def get_default_payload() -> dict[str, str]:
    """Devuelve una entrada de ejemplo cuando no se recibe JSON por consola."""
    return {
        "titulo": "Introducción a Spring Boot",
        "texto": (
            "En este contenido se presentan los conceptos básicos para la "
            "creación de una API REST usando Java y Spring Boot."
        ),
    }


if __name__ == "__main__":
    args = parse_args()

    try:
        if args.datos_json is None:
            payload = get_default_payload()
        else:
            payload = json.loads(args.datos_json)

        print("Entrada recibida:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print()

        response = safe_process_content(payload, limit=args.limit)

        print("Salida JSON:")
        print(json.dumps(response, ensure_ascii=False, indent=2))

    except json.JSONDecodeError:
        print("Error: La cadena ingresada no es un JSON válido. Revisa las comillas.")