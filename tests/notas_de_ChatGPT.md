# `readme_dataModel.md`

## Diagnóstico del pipeline de datos y modelado — TechMind

Este diagnóstico revisa los archivos y notebooks del proyecto frente a los **6 puntos mandatorios** solicitados. El proyecto implementa un pipeline de **búsqueda semántica multilingüe** basado en embeddings, no un modelo supervisado clásico de clasificación.

---

## 1. Exploración y limpieza de datos — EDA

**Estado:** `[CUMPLE]`

### Evidencia encontrada

El EDA y la limpieza se abordan principalmente en:

- `notebooks/01_eda_dataset.ipynb`
- `src/techmind/data/preprocessing.py`

En `01_eda_dataset.ipynb` se documenta explícitamente que el módulo:

- Carga el dataset `AI-Culture-Commons/ai-culture-multilingual-json-dolma`.
- Inspecciona estructura del dataset.
- Revisa:
  - valores nulos,
  - duplicados,
  - distribución por idioma,
  - longitudes de títulos y textos.
- Filtra los idiomas `en`, `es` y `pt`.
- Genera un subconjunto reproducible de 900 documentos.

Código relevante del notebook:

```python
raw = load_source_dataset()
documents = prepare_documents(raw)
prototype = select_parallel_prototype(documents, PROTOTYPE_PER_LANGUAGE)
save_documents(prototype, paths.dataset)
save_documents(prototype, paths.documents)
display(prototype.groupby('idioma').size())
display(prototype.assign(words=prototype.texto.str.split().str.len()).describe(include='all'))
```


En `src/techmind/data/preprocessing.py`, la limpieza está implementada mediante:

```python
def clean_text(value: Any) -> str:
    """Normalize Unicode and spacing while preserving multilingual characters."""
    text = "" if pd.isna(value) else unicodedata.normalize("NFC", str(value))
    text = "".join(c for c in text if unicodedata.category(c) not in {"Cc", "Cf"} or c in "\n\t")
    return re.sub(r"\s+", " ", text).strip()
```


También se validan condiciones mínimas del dataset:

```python
def validate_documents(documents: pd.DataFrame) -> None:
    """Raise a clear error when the prepared document contract is violated."""
    if list(documents.columns) != FINAL_COLUMNS: raise ValueError(f"Esquema inválido; se esperaba {FINAL_COLUMNS}")
    if not documents["idioma"].isin(LANGUAGES).all(): raise ValueError("Hay idiomas fuera de EN/ES/PT.")
    if documents["id"].eq("").any() or documents["texto"].eq("").any(): raise ValueError("No se permiten IDs o textos vacíos.")
    if documents["id"].duplicated().any(): raise ValueError("Hay IDs duplicados.")
```


Además, el notebook muestra resultados de distribución por idioma:

```plain text
en    300
es    300
pt    300
```


Y estadísticas descriptivas sobre los textos, incluyendo conteo de palabras.

### Observación

El punto se considera cumplido porque existe una etapa clara de exploración, limpieza, validación de esquema, filtrado de idiomas y selección reproducible del subconjunto.

### Mejora recomendada

Para una versión de producción, sería recomendable persistir el reporte EDA en archivos dentro de `reports/eda/`, por ejemplo:

- distribución por idioma,
- porcentaje de nulos,
- duplicados eliminados,
- distribución de longitud de texto,
- outliers de longitud extrema.

Actualmente se muestran los resultados en notebook, pero no se observa una exportación formal del reporte EDA.

---

## 2. Procesamiento de textos: tokenización, remoción de stopwords, lematización, etc.

**Estado:** `[CUMPLE PARCIALMENTE]`

### Evidencia encontrada

El procesamiento textual implementado se encuentra en:

- `src/techmind/data/preprocessing.py`
- `src/techmind/embeddings/encoder.py`
- `notebooks/01_eda_dataset.ipynb`
- `notebooks/02_semantic_embeddings.ipynb`

El archivo `preprocessing.py` realiza limpieza básica:

```python
def clean_text(value: Any) -> str:
    """Normalize Unicode and spacing while preserving multilingual characters."""
    text = "" if pd.isna(value) else unicodedata.normalize("NFC", str(value))
    text = "".join(c for c in text if unicodedata.category(c) not in {"Cc", "Cf"} or c in "\n\t")
    return re.sub(r"\s+", " ", text).strip()
```


También renombra campos y limpia columnas textuales:

```python
for column in ("id", "titulo", "texto", "url", "original_url"):
    frame[column] = frame[column].map(clean_text)
```


En `src/techmind/embeddings/encoder.py` se construye la representación textual final usada por el modelo:

```python
def semantic_texts(documents: pd.DataFrame) -> list[str]:
    """Combine title and body into the text represented by the encoder."""
    return (documents["titulo"].fillna("").str.strip() + ". " + documents["texto"].fillna("").str.strip()).tolist()
```


### Elementos cubiertos

El proyecto sí realiza:

- normalización Unicode,
- limpieza de caracteres de control,
- normalización de espacios,
- eliminación de textos vacíos,
- combinación de título y cuerpo,
- preservación de caracteres multilingües.

### Elementos no encontrados

No se encontró implementación explícita de:

- tokenización manual,
- remoción de stopwords,
- lematización,
- stemming,
- normalización morfológica,
- eliminación de puntuación,
- lowercasing generalizado.

### Justificación técnica

Aunque el punto se pide en términos clásicos de NLP, el enfoque del proyecto usa embeddings con `sentence-transformers`. En este tipo de modelos, **no siempre es recomendable remover stopwords o lematizar manualmente**, porque el modelo preentrenado utiliza el contexto completo de la frase y fue entrenado con texto natural.

Por eso, la ausencia de stopwords/lematización no invalida necesariamente la solución, pero sí debe documentarse como una decisión metodológica.

### Mejora recomendada

Agregar una nota explícita en el notebook o README indicando que no se aplican stopwords ni lematización porque el pipeline usa embeddings semánticos contextuales/multilingües.

También sería útil crear una función documentada, por ejemplo:

```python
def normalize_for_embeddings(text: str) -> str:
    ...
```


para centralizar la política de preprocesamiento textual.

---

## 3. Transformación de datos a formato adecuado para modelado: vectorización / embeddings

**Estado:** `[CUMPLE]`

### Evidencia encontrada

La transformación a vectores está claramente implementada en:

- `notebooks/02_semantic_embeddings.ipynb`
- `src/techmind/embeddings/encoder.py`

En el notebook `02_semantic_embeddings.ipynb` se cargan los documentos procesados y se generan embeddings:

```python
paths = get_paths(); documents = load_documents(paths.dataset)
embeddings = encode_texts(semantic_texts(documents), model_name=MODEL_NAME, batch_size=32)
np.save(paths.embeddings, embeddings.astype(np.float32))
print(f'[TechMind] Embedding shape: {embeddings.shape}')
assert embeddings.shape == (len(documents), 384)
```


En `encoder.py` se utiliza `SentenceTransformer`:

```python
def encode_texts(texts: list[str], model_name: str = MODEL_NAME, batch_size: int = 32) -> np.ndarray:
    """Generate normalized float32 embeddings with SentenceTransformer."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc: raise ImportError("Instale 'sentence-transformers' para generar embeddings.") from exc
    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, batch_size=batch_size, normalize_embeddings=NORMALIZE_EMBEDDINGS, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)
```


El modelo usado está configurado en `src/techmind/config.py`:

```python
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384
NORMALIZE_EMBEDDINGS = True
```


Además, el notebook valida la dimensión esperada:

```python
assert embeddings.shape == (len(documents), 384)
```


### Observación

Este punto se cumple correctamente. Los textos se transforman a una matriz numérica `float32` de embeddings normalizados, adecuada para búsqueda semántica con similitud coseno.

### Mejora recomendada

Actualmente el notebook valida explícitamente dimensión `384`, pero también existe la constante:

```python
EMBEDDING_DIMENSION = 384
```


Sería mejor usar esa constante en el `assert` para evitar duplicación:

```python
assert embeddings.shape == (len(documents), EMBEDDING_DIMENSION)
```


---

## 4. Entrenamiento y evaluación de modelos

**Estado:** `[CUMPLE PARCIALMENTE]`

### Evidencia encontrada

El proyecto no entrena un modelo supervisado. Usa un modelo preentrenado de embeddings:

```python
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```


En `02_semantic_embeddings.ipynb` se aclara que no hay fine-tuning:

```plain text
TechMind utiliza sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,
sin entrenamiento adicional ni fine-tuning.
```


El componente más cercano a “entrenamiento” es la construcción del índice de vecinos en:

- `notebooks/03_semantic_index.ipynb`
- `src/techmind/search/semantic_search.py`

Código relevante:

```python
def build_index(embeddings: np.ndarray) -> NearestNeighbors:
    """Build a brute-force cosine index; fit stores vectors, not classes."""
    return NearestNeighbors(metric="cosine", algorithm="brute").fit(embeddings)
```


El notebook `03_semantic_index.ipynb` también explica correctamente que:

```plain text
fit() no es entrenamiento supervisado.
NearestNeighbors no recibe una variable objetivo y no realiza clasificación.
fit() solamente almacena o estructura los vectores.
```


La evaluación está implementada en:

- `notebooks/05_multilingual_evaluation.ipynb`
- `src/techmind/evaluation/multilingual.py`

Código relevante:

```python
scores = evaluate_parallel_documents(documents, embeddings)
stats = descriptive_statistics(scores)
scores.to_csv(paths.reports / 'evaluation' / 'multilingual_scores.csv', index=False)
stats.to_csv(paths.reports / 'evaluation' / 'multilingual_statistics.csv')
display(stats)
```


Y en `multilingual.py`:

```python
def evaluate_parallel_documents(documents: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
    """Calculate similarity for EN↔ES, EN↔PT, and ES↔PT original_url pairs."""
    pairs = parallel_pairs(documents)
    positions = {doc_id: i for i, doc_id in enumerate(documents["id"])}
    rows = []
    for pair in pairs.to_dict("records"):
        score = cosine_similarity(
            embeddings[positions[pair["id_a"]]].reshape(1, -1),
            embeddings[positions[pair["id_b"]]].reshape(1, -1)
        )[0, 0]
        rows.append({**pair, "similitud": float(score)})
    return pd.DataFrame(rows, columns=["original_url", "id_a", "idioma_a", "id_b", "idioma_b", "similitud"])
```


### Observación

El punto se cumple parcialmente porque:

- Sí hay construcción de un índice de búsqueda semántica.
- Sí hay evaluación con pares multilingües relacionados.
- No hay entrenamiento supervisado.
- No hay partición train/test.
- No hay fine-tuning del modelo de embeddings.
- No hay validación cruzada.

Esto es coherente con una solución de recuperación semántica, pero no cumple completamente si el requisito exige entrenamiento formal de un modelo predictivo.

### Mejora recomendada

Si el proyecto debe demostrar entrenamiento/evaluación tradicional, se recomienda agregar una de estas alternativas:

1. **Clasificador supervisado sobre embeddings**
   - Usar embeddings como features.
   - Definir una etiqueta real si existe.
   - Entrenar `LogisticRegression`, `RandomForestClassifier` o similar.
   - Evaluar con train/test split.

2. **Evaluación de recuperación de información**
   - Crear pares positivos y negativos usando `original_url`.
   - Medir Recall@K, Precision@K, MRR o nDCG.
   - Esto sería más apropiado para una solución de búsqueda semántica.

La segunda opción encaja mejor con la arquitectura actual.

---

## 5. Métricas de rendimiento apropiadas para la solución propuesta: Accuracy, F1-score, etc.

**Estado:** `[CUMPLE PARCIALMENTE]`

### Evidencia encontrada

El proyecto usa métricas/descriptivos adecuados para similitud semántica:

- similitud coseno,
- media,
- desviación estándar,
- mínimos,
- percentiles,
- máximos,
- conteo por par de idiomas.

En `05_multilingual_evaluation.ipynb` se generan estadísticas como:

```plain text
par_idiomas   count   mean      std       min       25%       50%       75%       max
en-es         300     0.887545  0.060946  0.627415  ...
en-pt         300     0.879141  0.065404  0.549464  ...
es-pt         300     0.943079  0.044298  0.652681  ...
```


La función usada para evaluación está en `src/techmind/evaluation/multilingual.py`:

```python
def descriptive_statistics(scores: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics by language pair."""
    if scores.empty: return pd.DataFrame()
    frame = scores.copy()
    frame["par_idiomas"] = frame.apply(lambda row: f"{row.idioma_a}-{row.idioma_b}", axis=1)
    return frame.groupby("par_idiomas")["similitud"].describe()[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
```


Además, en `04_semantic_search.ipynb` se muestran resultados de búsqueda con columna `similitud`.

Código relevante en `src/techmind/search/semantic_search.py`:

```python
distances, indices = index.kneighbors(query_embedding, n_neighbors=min(limit, len(documents)))
result = documents.iloc[indices[0]][["id", "titulo", "idioma"]].copy()
result["similitud"] = np.clip(1.0 - distances[0], -1.0, 1.0)
```


### Elementos no encontrados

No se encontró implementación de métricas supervisadas como:

- Accuracy,
- Precision,
- Recall,
- F1-score,
- matriz de confusión,
- ROC-AUC.

### Justificación técnica

El notebook `05_multilingual_evaluation.ipynb` aclara correctamente que no se usan métricas de clasificación:

```plain text
No utiliza accuracy, F1, train/test split de clasificación, categorías ni modelos supervisados.
Es una evaluación basada en relaciones explícitas del dataset.
```


Esto es metodológicamente válido para búsqueda semántica; sin embargo, el requisito menciona explícitamente métricas como Accuracy y F1-score, por lo que el cumplimiento es parcial.

### Mejora recomendada

Para una solución de recuperación semántica, serían más apropiadas estas métricas:

- `Recall@K`
- `Precision@K`
- `Mean Reciprocal Rank`
- `nDCG@K`
- `Hit Rate@K`
- evaluación con pares positivos/negativos por `original_url`

Ejemplo conceptual:

```python
# Métrica recomendada para búsqueda semántica:
# Para cada documento, consultar sus vecinos y verificar si recupera documentos
# con el mismo original_url dentro del top-k.
recall_at_k = recovered_relevant_documents / total_relevant_documents
```


Si se requiere estrictamente Accuracy/F1, habría que formular el problema como clasificación binaria de pares:

- par relacionado: misma `original_url`,
- par no relacionado: distinta `original_url`.

Luego se podría calcular F1-score sobre un umbral de similitud coseno.

---

## 6. Serialización del modelo: uso explícito de joblib o pickle

**Estado:** `[CUMPLE]`

### Evidencia encontrada

La serialización está implementada explícitamente con `joblib`.

En `notebooks/03_semantic_index.ipynb`:

```python
import joblib
...
index = build_index(embeddings); joblib.dump(index, paths.index)
print('[TechMind] Semantic index persisted.')
```


El archivo de destino está definido en `src/techmind/config.py`:

```python
@property
def index(self) -> Path: return self.models / "semantic_index.joblib"
```


La carga del índice también se implementa en `src/techmind/persistence/artifacts.py`:

```python
def load_index(path: Path):
    """Load the index or identify the missing previous module."""
    if not path.exists(): raise FileNotFoundError("Falta semantic_index.joblib; ejecute primero el Módulo 03.")
    return joblib.load(path)
```


Y en `notebooks/04_semantic_search.ipynb`:

```python
import joblib
...
index = joblib.load(paths.index)
```


Además, otros artefactos se persisten de forma consistente:

- `models/dataset_procesado.json`
- `models/documents.json`
- `models/embeddings.npy`
- `models/semantic_index.joblib`
- `models/model_config.json`

En `notebooks/06_persistence_config.ipynb` se guarda configuración del modelo:

```python
save_model_config(paths.model_config, len(documents), embeddings.shape[1])
```


Y en `src/techmind/persistence/artifacts.py`:

```python
def save_model_config(path: Path, documents: int, embedding_dimension: int) -> None:
    """Persist model parameters for downstream consumers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_name": MODEL_NAME,
        "normalize_embeddings": NORMALIZE_EMBEDDINGS,
        "similarity_metric": "cosine",
        "documents": documents,
        "embedding_dimension": embedding_dimension
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
```


### Observación

El punto se cumple completamente porque el índice semántico se serializa de forma explícita con `joblib`.

### Mejora recomendada

Aunque el índice se serializa, el modelo `SentenceTransformer` no se guarda localmente. En producción podría ser conveniente:

- cachear o versionar el modelo preentrenado,
- registrar hash o versión exacta,
- validar al cargar que el modelo usado para consulta coincide con el usado para generar embeddings,
- guardar metadatos de fecha, tamaño del corpus y versión del código.

---

# Resumen ejecutivo

| Punto | Estado | Diagnóstico breve |
|---|---|---|
| 1. EDA y limpieza | `[CUMPLE]` | Hay notebook dedicado, limpieza Unicode, validación, filtrado de idiomas y estadísticas descriptivas. |
| 2. Procesamiento de textos | `[CUMPLE PARCIALMENTE]` | Hay limpieza textual básica, pero no tokenización, stopwords ni lematización explícitas. |
| 3. Vectorización / transformación | `[CUMPLE]` | Se generan embeddings multilingües normalizados de dimensión 384 y se guardan en `.npy`. |
| 4. Entrenamiento y evaluación | `[CUMPLE PARCIALMENTE]` | No hay entrenamiento supervisado; sí hay construcción de índice y evaluación semántica. |
| 5. Métricas de rendimiento | `[CUMPLE PARCIALMENTE]` | Usa similitud coseno y descriptivos; no usa Accuracy/F1 porque no es clasificación. |
| 6. Serialización | `[CUMPLE]` | El índice se serializa explícitamente con `joblib` en `semantic_index.joblib`. |

---

# Sugerencias técnicas de optimización

## 1. Documentar explícitamente la decisión de no usar stopwords/lematización

Dado que el modelo usa embeddings contextuales, la remoción de stopwords o lematización puede degradar el rendimiento. Sin embargo, debe quedar documentado como decisión técnica.

## 2. Agregar métricas de recuperación semántica

Para este tipo de solución son más apropiadas:

- `Recall@K`
- `Precision@K`
- `MRR`
- `nDCG@K`
- `Hit Rate@K`

Esto fortalecería el punto 5 sin forzar métricas de clasificación inadecuadas.

## 3. Crear evaluación con pares positivos y negativos

Usar `original_url` para construir:

- pares positivos: documentos con la misma `original_url`,
- pares negativos: documentos con distinta `original_url`.

Con esto se podría calcular:

- F1-score sobre un umbral de similitud,
- precision/recall binarios,
- curva de selección de umbral.

## 4. Persistir reportes EDA

Actualmente el EDA se visualiza en notebook. Para trazabilidad sería mejor guardar archivos como:

```plain text
reports/eda/language_distribution.csv
reports/eda/text_length_summary.csv
reports/eda/nulls_summary.csv
reports/eda/duplicates_summary.csv
```


## 5. Centralizar validaciones de dimensiones

El notebook usa directamente `384`:

```python
assert embeddings.shape == (len(documents), 384)
```


Sería preferible usar la constante `EMBEDDING_DIMENSION` definida en `config.py`.

## 6. Validar compatibilidad entre índice, embeddings y configuración

Antes de ejecutar búsquedas, conviene validar que:

- `model_config.json` existe,
- el modelo usado en consulta coincide con el modelo usado para embeddings,
- la dimensión del embedding de consulta coincide con el índice,
- el número de documentos coincide con `index.n_samples_fit_`.

## 7. Considerar índices vectoriales escalables

Actualmente se usa:

```python
NearestNeighbors(metric="cosine", algorithm="brute")
```


Es adecuado para prototipo, pero para producción convendría evaluar:

- FAISS,
- HNSW,
- Annoy,
- ScaNN.

## 8. Evitar recargar el modelo en cada consulta

La función `encode_query()` llama internamente a `encode_texts()`, y esta instancia `SentenceTransformer` cada vez:

```python
model = SentenceTransformer(model_name)
```


Para producción, conviene cargar el modelo una sola vez y reutilizarlo, especialmente en una API.

## 9. Versionar artefactos

Se recomienda agregar al `model_config.json`:

- fecha de generación,
- versión del código,
- nombre del dataset,
- split usado,
- número de documentos,
- dimensión,
- métrica,
- normalización,
- versión del modelo,
- hash o checksum de artefactos.

## 10. Agregar pruebas unitarias para evaluación y búsqueda

Ya existe evidencia de pruebas de preprocesamiento, pero sería recomendable agregar pruebas para:

- `semantic_texts`,
- `encode_texts` con mocks,
- `build_index`,
- `search_related`,
- `evaluate_parallel_documents`,
- validación de errores cuando índice y documentos no coinciden.

---

# Conclusión

El proyecto cumple correctamente con las etapas esenciales de un pipeline de búsqueda semántica multilingüe: EDA, limpieza, generación de embeddings, construcción de índice, evaluación por similitud y serialización con `joblib`.

Los principales puntos débiles frente a los requisitos mandatorios son:

1. No existe tokenización, stopword removal ni lematización explícita.
2. No hay entrenamiento supervisado.
3. No se calculan métricas tipo Accuracy/F1-score.

Sin embargo, estas ausencias son coherentes con la naturaleza de la solución propuesta, que está basada en embeddings semánticos y recuperación de documentos, no en clasificación supervisada. Para robustecer el cumplimiento académico/técnico, se recomienda agregar métricas de recuperación y documentar explícitamente por qué no se aplican ciertos pasos clásicos de NLP.
