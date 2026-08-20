# Plan de Trabajo del Agente — Prototipo TechMind

## Objetivo

Construir un prototipo funcional en **Python + Flask** que permita validar la idea central del proyecto:

**Ingresar contenido técnico → analizarlo → clasificarlo → mostrar nivel de confianza y palabras clave.**

---

## Fase 1. Preparar el proyecto

### Tareas del agente

- Crear la estructura base del proyecto.
- Configurar entorno virtual.
- Crear `requirements.txt`.
- Configurar `.gitignore`.
- Crear README inicial.

### Estructura propuesta

```text
techmind-prototype/
├── app.py
├── data/
├── notebooks/
├── models/
├── services/
├── templates/
├── static/
├── requirements.txt
└── README.md
```

### Resultado esperado

Proyecto Flask ejecutándose localmente.

---

## Fase 2. Preparar el dataset

### Dataset seleccionado

**ArXiv CS Papers Multi-Label Classification (200K) — Kaggle**

### Tareas del agente

- Descargar y revisar el dataset.
- Identificar columnas útiles:
  - título;
  - resumen/contenido;
  - categoría.
- Eliminar registros incompletos.
- Seleccionar únicamente categorías relacionadas con informática.
- Crear una muestra balanceada para el prototipo.

### Alcance inicial

```text
10,000 – 20,000 registros
5 – 8 categorías
```

### Categorías sugeridas

```text
Artificial Intelligence
Software Engineering
Machine Learning
Computer Vision
Information Security
Databases
Networks
```

### Resultado esperado

```text
data/arxiv_cs_clean.csv
```

---

## Fase 3. Crear el Notebook de Ciencia de Datos

Crear:

```text
notebooks/01_entrenamiento_modelo.ipynb
```

### Flujo de trabajo

```text
Dataset
   ↓
Exploración
   ↓
Limpieza
   ↓
Preparación del texto
   ↓
TF-IDF
   ↓
Entrenamiento
   ↓
Evaluación
   ↓
Exportación
```

### Tecnologías

```text
Pandas
Scikit-learn
TF-IDF
Logistic Regression
```

### Métricas de evaluación

```text
Accuracy
Precision
Recall
F1-score
Matriz de confusión
```

### Resultado esperado

```text
models/
├── modelo.joblib
└── vectorizador.joblib
```

---

## Fase 4. Crear el servicio de clasificación

Crear:

```text
services/classifier.py
```

### Responsabilidades

```text
Cargar modelo
      ↓
Cargar vectorizador
      ↓
Recibir título + texto
      ↓
Transformar texto
      ↓
Predecir categoría
      ↓
Calcular confianza
```

### Respuesta esperada

```python
{
    "categoria": "Software Engineering",
    "probabilidad": 0.89
}
```

### Resultado esperado

Clasificación funcional de contenido técnico de forma independiente de Flask.

---

## Fase 5. Implementar palabras clave

Crear:

```text
services/keywords.py
```

### Estrategia inicial

Utilizar los términos más relevantes obtenidos mediante **TF-IDF**.

### Flujo

```text
Texto
   ↓
Vectorización TF-IDF
   ↓
Términos con mayor peso
   ↓
Top palabras clave
```

### Resultado esperado

```json
[
  "spring boot",
  "java",
  "rest",
  "backend",
  "api"
]
```

No incorporar modelos NLP adicionales en esta primera versión.

---

## Fase 6. Construir la aplicación Flask

### Rutas mínimas

```text
GET  /
POST /analizar
```

### Flujo

```text
Formulario
    ↓
Título + contenido
    ↓
POST /analizar
    ↓
classifier.py
    ↓
keywords.py
    ↓
Resultado
```

### Información que debe mostrar

```text
Categoría
Nivel de confianza
Palabras clave
```

---

## Fase 7. Crear la interfaz del prototipo

Crear:

```text
templates/
├── index.html
└── resultado.html
```

La interfaz debe ser sencilla y orientada únicamente a demostrar la funcionalidad del prototipo.

---

## Fase 8. Incorporar API JSON

Crear:

```text
POST /api/contenido
```

### Entrada

```json
{
  "titulo": "Introducción a Spring Boot",
  "texto": "Desarrollo de APIs REST utilizando Java..."
}
```

### Salida

```json
{
  "categoria": "Software Engineering",
  "probabilidad": 0.89,
  "palabras_clave": [
    "java",
    "spring boot",
    "api rest"
  ]
}
```

---

## Fase 9. Validar el prototipo

Preparar al menos tres casos de prueba:

```text
Caso 1
Inteligencia Artificial

Caso 2
Desarrollo de Software

Caso 3
Ciberseguridad
```

### Validar en cada caso

```text
Entrada
↓
Categoría esperada
↓
Categoría obtenida
↓
Confianza
↓
Palabras clave
```

---

## Orden exacto de ejecución del agente

```text
1. Crear proyecto
        ↓
2. Preparar dataset Kaggle
        ↓
3. Crear Notebook
        ↓
4. Entrenar y evaluar modelo
        ↓
5. Exportar modelo
        ↓
6. Crear classifier.py
        ↓
7. Crear keywords.py
        ↓
8. Crear Flask
        ↓
9. Crear interfaz
        ↓
10. Crear endpoint JSON
        ↓
11. Realizar pruebas
        ↓
12. Documentar README
```

---

## Criterio de finalización del prototipo

El prototipo se considerará terminado cuando sea posible ejecutar:

```bash
python app.py
```

Ingresar contenido técnico y obtener:

```text
Categoría
Confianza
Palabras clave
```

Además, la misma funcionalidad deberá estar disponible mediante:

```text
POST /api/contenido
```

con respuesta en formato JSON.

---

## Alcance de la versión 0.1

La primera versión **no incluirá todavía**:

- autenticación;
- persistencia en base de datos;
- Spring Boot;
- OCI;
- Docker;
- recomendación de contenidos;
- búsqueda semántica.

El objetivo de esta versión es validar el núcleo funcional:

**Contenido técnico → Modelo → Categoría + Confianza + Palabras clave**
