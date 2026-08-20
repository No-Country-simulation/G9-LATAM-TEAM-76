# TechMind — Modelo semántico multilingüe

TechMind es un pipeline reproducible de representación y búsqueda semántica multilingüe para inglés, español y portugués. Usa `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` preentrenado, embeddings normalizados de 384 dimensiones y distancia coseno. **No es un clasificador supervisado**: no inventa categorías, labels ni clases y no realiza fine-tuning.

## Arquitectura y ejecución

`DATA → REPRESENTATION → INDEX → SEARCH → EVALUATION → PERSISTENCE`

Ejecuta los notebooks en orden: `01_eda_dataset`, `02_semantic_embeddings`, `03_semantic_index`, `04_semantic_search` y `05_multilingual_evaluation`. La lógica reutilizable vive en `src/techmind/`; la configuración central está en `config.py`. Instala con `pip install -r requirements.txt` y ejecuta tests con `pytest`.

## Módulos

1. EDA/preparación carga exclusivamente `AI-Culture-Commons/ai-culture-multilingual-json-dolma`, filtra `en/es/pt`, limpia Unicode NFC y selecciona 300 grupos paralelos reproducibles (`random_state=42`), produciendo 900 documentos.
2. Embeddings combina `titulo + texto`, usa `batch_size=32`, `normalize_embeddings=True` y guarda `float32` en `models/embeddings.npy`.
3. El índice usa `NearestNeighbors(metric="cosine", algorithm="brute")`. `fit()` solo almacena vectores para vecinos; no entrena clases.
4. Search codifica una consulta en cualquiera de los tres idiomas y transforma distancia coseno en similitud (`1 - distancia`).
5. Evaluation compara únicamente documentos realmente paralelos por `original_url` en pares EN-ES, EN-PT y ES-PT; reporta estadísticas descriptivas, no accuracy/F1.
6. Persistence centraliza el contrato de artefactos y `model_config.json`.

## Estructura

`data/` contiene entradas y datos procesados; `notebooks/` demuestra cada etapa; `src/techmind/` contiene código reusable; `models/` contiene dataset, documentos, embeddings, índice y configuración; `reports/` contiene EDA/evaluación; `tests/` contiene pruebas unitarias.

## Artefactos y límites

Se generan `dataset_procesado.json`, `documents.json`, `embeddings.npy`, `semantic_index.joblib` y `model_config.json`. El índice brute-force es apropiado para el prototipo, pero debe sustituirse por una solución aproximada al escalar. La similitud semántica es una señal de evaluación, no una verdad absoluta.

La arquitectura queda lista para una API futura: una capa HTTP puede cargar los artefactos y llamar a `search_related` sin duplicar el pipeline.
