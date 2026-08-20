<archivo_diagrama>
# Diagrama técnico de arquitectura y flujo de ejecución

Este documento describe la arquitectura del pipeline de TechMind, el orden recomendado de ejecución y la concatenación entre notebooks, módulos productivos en `src/techmind`, entradas, salidas y artefactos finales.

## Flujo principal del pipeline

```mermaid
graph TD
    A["Inicio del proyecto TechMind"] --> B["Configuracion central src techmind config"]
    B --> C["get_paths"]
    B --> D["ensure_directories"]

    C --> E["Rutas de artefactos"]
    D --> F["Directorios data models reports"]

    E --> N1["Notebook 01 eda dataset"]
    F --> N1

    N1 --> P1["load_source_dataset"]
    P1 --> I1["Entrada dataset Hugging Face"]
    I1 --> O1["raw DataFrame"]

    O1 --> P2["prepare_documents"]
    P2 --> P2A["clean_text"]
    P2A --> P2B["validate_documents"]
    P2B --> O2["documents DataFrame limpio"]

    O2 --> P3["select_parallel_prototype"]
    P3 --> O3["prototype DataFrame 900 documentos"]

    O3 --> P4["save_documents"]
    P4 --> A1["models dataset_procesado json"]
    P4 --> A2["models documents json"]

    A1 --> N2["Notebook 02 semantic embeddings"]
    A2 --> N2

    N2 --> P5["load_documents"]
    P5 --> O4["documents DataFrame procesado"]

    O4 --> P6["semantic_texts"]
    P6 --> O5["lista textos titulo mas texto"]

    O5 --> P7["encode_texts"]
    P7 --> I2["Parametros MODEL_NAME batch_size normalize_embeddings"]
    I2 --> P7
    P7 --> O6["embeddings ndarray float32"]

    O6 --> P8["np save"]
    P8 --> A3["models embeddings npy"]

    A3 --> N3["Notebook 03 semantic index"]
    N3 --> P9["load_embeddings"]
    P9 --> O7["embeddings ndarray"]

    O7 --> P10["build_index"]
    P10 --> I3["NearestNeighbors metric cosine algorithm brute"]
    I3 --> P10
    P10 --> O8["semantic index fitted"]

    O8 --> P11["joblib dump"]
    P11 --> A4["models semantic_index joblib"]

    A2 --> N4["Notebook 04 semantic search"]
    A4 --> N4

    N4 --> P12["load_documents"]
    N4 --> P13["joblib load index"]
    P12 --> O9["documents DataFrame"]
    P13 --> O10["semantic index cargado"]

    U1["Consulta de usuario"] --> P14["search_related"]
    O9 --> P14
    O10 --> P14
    P14 --> P15["encode_query"]
    P15 --> P16["encode_texts"]
    P16 --> O11["query embedding"]
    O11 --> P17["kneighbors"]
    P17 --> O12["distancias e indices"]
    O12 --> P18["similitud igual uno menos distancia"]
    P18 --> O13["resultados id titulo idioma similitud"]

    A1 --> N5["Notebook 05 multilingual evaluation"]
    A3 --> N5

    N5 --> P19["load_documents"]
    N5 --> P20["load_embeddings"]
    P19 --> O14["documents DataFrame evaluacion"]
    P20 --> O15["embeddings ndarray evaluacion"]

    O14 --> P21["evaluate_parallel_documents"]
    O15 --> P21
    P21 --> P22["parallel_pairs"]
    P22 --> O16["pares por original_url"]
    O16 --> P23["cosine_similarity"]
    O15 --> P23
    P23 --> O17["scores DataFrame similitud"]

    O17 --> P24["descriptive_statistics"]
    P24 --> O18["estadisticas por par idiomas"]

    O17 --> A5["reports evaluation multilingual_scores csv"]
    O18 --> A6["reports evaluation multilingual_statistics csv"]

    A2 --> N6["Notebook 06 persistence config"]
    A3 --> N6

    N6 --> P25["load_documents"]
    N6 --> P26["load_embeddings"]
    P25 --> O19["numero documentos"]
    P26 --> O20["dimension embeddings"]

    O19 --> P27["save_model_config"]
    O20 --> P27
    P27 --> I4["Parametros MODEL_NAME normalize_embeddings similarity_metric"]
    I4 --> P27
    P27 --> A7["models model_config json"]

    A1 --> Z["Artefactos finales del pipeline"]
    A2 --> Z
    A3 --> Z
    A4 --> Z
    A5 --> Z
    A6 --> Z
    A7 --> Z
```


## Arquitectura por capas

```mermaid
graph TD
    subgraph L1["Capa de experimentacion notebooks"]
        NB1["01_eda_dataset ipynb"]
        NB2["02_semantic_embeddings ipynb"]
        NB3["03_semantic_index ipynb"]
        NB4["04_semantic_search ipynb"]
        NB5["05_multilingual_evaluation ipynb"]
        NB6["06_persistence_config ipynb"]
    end

    subgraph L2["Capa productiva src techmind"]
        CFG["config py"]
        DATA["data preprocessing py"]
        EMB["embeddings encoder py"]
        SEARCH["search semantic_search py"]
        EVAL["evaluation multilingual py"]
        PERSIST["persistence artifacts py"]
    end

    subgraph L3["Artefactos persistidos"]
        M1["models dataset_procesado json"]
        M2["models documents json"]
        M3["models embeddings npy"]
        M4["models semantic_index joblib"]
        M5["models model_config json"]
        R1["reports evaluation multilingual_scores csv"]
        R2["reports evaluation multilingual_statistics csv"]
    end

    subgraph L4["Capa futura API REST"]
        API1["prep_to_Api py"]
        API2["Endpoint futuro POST procesar contenido"]
        API3["Validacion entrada JSON"]
        API4["Respuesta JSON categoria probabilidad informacion_adicional"]
    end

    NB1 --> CFG
    NB1 --> DATA
    NB1 --> PERSIST

    NB2 --> CFG
    NB2 --> EMB
    NB2 --> PERSIST

    NB3 --> PERSIST
    NB3 --> SEARCH

    NB4 --> PERSIST
    NB4 --> SEARCH
    NB4 --> EMB

    NB5 --> PERSIST
    NB5 --> EVAL
    NB5 --> DATA

    NB6 --> CFG
    NB6 --> PERSIST

    DATA --> M1
    DATA --> M2
    EMB --> M3
    SEARCH --> M4
    EVAL --> R1
    EVAL --> R2
    PERSIST --> M5

    M2 --> API2
    M3 --> API2
    M4 --> API2
    M5 --> API2

    API1 --> API3
    API3 --> API4
```


## Encadenamiento detallado de datos y funciones

```mermaid
graph LR
    D0["Dataset remoto AI Culture Commons"] --> F1["load_source_dataset"]
    F1 --> D1["raw DataFrame"]

    D1 --> F2["prepare_documents"]
    F2 --> F2A["clean_text por columnas textuales"]
    F2A --> F2B["validate_documents"]
    F2B --> D2["documents limpio"]

    D2 --> F3["select_parallel_prototype"]
    F3 --> D3["prototype 300 grupos por 3 idiomas"]

    D3 --> F4["save_documents"]
    F4 --> J1["dataset_procesado json"]
    F4 --> J2["documents json"]

    J1 --> F5["load_documents"]
    F5 --> D4["documents cargado"]

    D4 --> F6["semantic_texts"]
    F6 --> D5["textos concatenados"]

    D5 --> F7["encode_texts"]
    C1["MODEL_NAME"] --> F7
    C2["NORMALIZE_EMBEDDINGS true"] --> F7
    C3["batch_size 32"] --> F7
    F7 --> D6["embeddings float32"]

    D6 --> J3["embeddings npy"]

    J3 --> F8["load_embeddings"]
    F8 --> D7["embeddings cargados"]

    D7 --> F9["build_index"]
    C4["metric cosine"] --> F9
    C5["algorithm brute"] --> F9
    F9 --> D8["indice semantico ajustado"]

    D8 --> F10["joblib dump"]
    F10 --> J4["semantic_index joblib"]

    J2 --> F11["load_documents para search"]
    J4 --> F12["joblib load para search"]
    Q1["query usuario"] --> F13["search_related"]

    F11 --> F13
    F12 --> F13
    F13 --> F14["encode_query"]
    F14 --> D9["query embedding"]
    D9 --> F15["kneighbors"]
    F15 --> D10["indices distancias"]
    D10 --> F16["calcular similitud"]
    F16 --> D11["DataFrame resultados"]

    J1 --> F17["load_documents para evaluacion"]
    J3 --> F18["load_embeddings para evaluacion"]
    F17 --> F19["evaluate_parallel_documents"]
    F18 --> F19
    F19 --> F20["parallel_pairs"]
    F20 --> D12["pares multilingues"]
    D12 --> F21["cosine_similarity"]
    F18 --> F21
    F21 --> D13["scores similitud"]

    D13 --> F22["descriptive_statistics"]
    F22 --> D14["estadisticas descriptivas"]

    D13 --> R1["multilingual_scores csv"]
    D14 --> R2["multilingual_statistics csv"]

    J2 --> F23["load_documents para config"]
    J3 --> F24["load_embeddings para config"]
    F23 --> D15["cantidad documentos"]
    F24 --> D16["dimension embeddings"]
    D15 --> F25["save_model_config"]
    D16 --> F25
    C1 --> F25
    C2 --> F25
    F25 --> J5["model_config json"]
```


## Orden recomendado de ejecucion

```mermaid
graph TD
    S0["Paso 0 instalar dependencias requirements txt"] --> S1["Paso 1 ejecutar 01_eda_dataset"]
    S1 --> S2["Genera dataset_procesado json y documents json"]

    S2 --> S3["Paso 2 ejecutar 02_semantic_embeddings"]
    S3 --> S4["Genera embeddings npy"]

    S4 --> S5["Paso 3 ejecutar 03_semantic_index"]
    S5 --> S6["Genera semantic_index joblib"]

    S6 --> S7["Paso 4 ejecutar 04_semantic_search"]
    S7 --> S8["Valida busqueda semantica con queries"]

    S4 --> S9["Paso 5 ejecutar 05_multilingual_evaluation"]
    S2 --> S9
    S9 --> S10["Genera reportes csv de evaluacion"]

    S2 --> S11["Paso 6 ejecutar 06_persistence_config"]
    S4 --> S11
    S11 --> S12["Genera model_config json"]

    S12 --> S13["Pipeline listo para futura API REST"]
```


## Contrato de entradas y salidas por etapa

| Etapa | Componente ejecutor | Funcion principal | Entrada | Parametros relevantes | Salida |
|---|---|---|---|---|---|
| EDA y preparacion | `01_eda_dataset.ipynb` | `load_source_dataset` | Dataset remoto | `DATASET_NAME`, `DATASET_CONFIG`, `DATASET_SPLIT` | `raw DataFrame` |
| Limpieza | `src/techmind/data/preprocessing.py` | `prepare_documents` | `raw DataFrame` | `LANGUAGES` | `documents DataFrame` |
| Normalizacion textual | `src/techmind/data/preprocessing.py` | `clean_text` | valores textuales | Unicode NFC, regex de espacios | texto normalizado |
| Validacion | `src/techmind/data/preprocessing.py` | `validate_documents` | `documents DataFrame` | `FINAL_COLUMNS`, `LANGUAGES` | validacion o error |
| Seleccion prototipo | `src/techmind/data/preprocessing.py` | `select_parallel_prototype` | `documents DataFrame` | `PROTOTYPE_PER_LANGUAGE`, `RANDOM_STATE` | `prototype DataFrame` |
| Persistencia documentos | `src/techmind/persistence/artifacts.py` | `save_documents` | `prototype DataFrame` | ruta destino | `dataset_procesado.json`, `documents.json` |
| Representacion semantica | `02_semantic_embeddings.ipynb` | `semantic_texts` | documentos procesados | columnas `titulo` y `texto` | lista de textos |
| Vectorizacion | `src/techmind/embeddings/encoder.py` | `encode_texts` | lista de textos | `MODEL_NAME`, `batch_size`, `NORMALIZE_EMBEDDINGS` | matriz `embeddings` |
| Persistencia embeddings | `02_semantic_embeddings.ipynb` | `np.save` | matriz `embeddings` | `float32` | `embeddings.npy` |
| Indexacion | `03_semantic_index.ipynb` | `build_index` | `embeddings.npy` | `metric cosine`, `algorithm brute` | indice `NearestNeighbors` |
| Serializacion indice | `03_semantic_index.ipynb` | `joblib.dump` | indice ajustado | ruta destino | `semantic_index.joblib` |
| Busqueda | `04_semantic_search.ipynb` | `search_related` | query, indice, documents | `limit`, `MODEL_NAME` | resultados con similitud |
| Evaluacion | `05_multilingual_evaluation.ipynb` | `evaluate_parallel_documents` | documents, embeddings | `original_url` como relacion | scores por pares |
| Estadisticas | `src/techmind/evaluation/multilingual.py` | `descriptive_statistics` | scores | agrupacion por par de idiomas | estadisticas descriptivas |
| Persistencia de reportes | `05_multilingual_evaluation.ipynb` | `to_csv` | scores y estadisticas | rutas de reports | archivos CSV |
| Configuracion final | `06_persistence_config.ipynb` | `save_model_config` | documents, embeddings | modelo, normalizacion, metrica | `model_config.json` |

## Artefactos finales

```mermaid
graph TD
    AF["Artefactos finales"] --> A1["models dataset_procesado json"]
    AF --> A2["models documents json"]
    AF --> A3["models embeddings npy"]
    AF --> A4["models semantic_index joblib"]
    AF --> A5["models model_config json"]
    AF --> A6["reports evaluation multilingual_scores csv"]
    AF --> A7["reports evaluation multilingual_statistics csv"]

    A1 --> U1["Entrada para generacion de embeddings"]
    A2 --> U2["Entrada para busqueda y API futura"]
    A3 --> U3["Entrada para indice evaluacion y configuracion"]
    A4 --> U4["Indice cargable para busqueda semantica"]
    A5 --> U5["Contrato tecnico del modelo y configuracion"]
    A6 --> U6["Trazabilidad de similitudes multilingues"]
    A7 --> U7["Resumen estadistico de rendimiento semantico"]
```


## Flujo previsto para API REST futura

```mermaid
graph TD
    C1["Cliente HTTP"] --> C2["POST procesar contenido"]
    C2 --> C3["JSON entrada titulo texto"]

    C3 --> C4["prep_to_Api validate_payload"]
    C4 --> C5["normalize_text"]
    C5 --> C6["build_content_text"]

    C6 --> C7["process_content"]
    C7 --> C8["infer_category"]
    C7 --> C9["extract_additional_information"]

    C8 --> C10["categoria probabilidad"]
    C9 --> C11["informacion_adicional"]

    C10 --> C12["Respuesta JSON"]
    C11 --> C12

    C12 --> C13["categoria"]
    C12 --> C14["probabilidad"]
    C12 --> C15["informacion_adicional"]

    C4 --> E1["Error de validacion"]
    E1 --> E2["safe_process_content"]
    E2 --> E3["Respuesta error JSON"]
```


## Notas arquitectonicas

- Los notebooks actuan como orquestadores reproducibles de cada fase del pipeline.
- La logica reutilizable vive en `src/techmind`, lo que permite migrar progresivamente hacia una API REST sin duplicar codigo.
- El pipeline no entrena un clasificador supervisado. Usa un modelo preentrenado de embeddings y un indice de vecinos con distancia coseno.
- `semantic_index.joblib` es el artefacto serializado principal para busqueda.
- `model_config.json` registra el contrato tecnico necesario para que una API futura cargue los artefactos de forma consistente.
- `prep_to_Api.py` representa una capa preliminar de contrato JSON para la futura API REST.
</archivo_diagrama>
