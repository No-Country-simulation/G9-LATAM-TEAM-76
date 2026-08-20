# G9-LATAM-TEAM-76
# TechMind – Organización Inteligente del Conocimiento Técnico

## Descripción

**TechMind** es una propuesta orientada a la organización inteligente de contenido técnico mediante técnicas de Ciencia de Datos y procesamiento de texto.

El objetivo del proyecto es facilitar la clasificación, consulta y reutilización de información técnica proveniente de diferentes fuentes, como documentación, artículos, materiales educativos, anotaciones, tutoriales y otros recursos relacionados con tecnología.

La solución busca transformar contenido textual en información estructurada que pueda ser utilizada por otras aplicaciones a través de servicios API.

---

## Objetivo general

Desarrollar una solución capaz de recibir contenido técnico, procesarlo mediante técnicas de Ciencia de Datos y generar información relevante que facilite su organización y posterior consulta.

Entre los posibles resultados generados por la solución se contemplan:

- Clasificación temática del contenido.
- Identificación de palabras clave.
- Organización automática de documentos.
- Identificación de contenidos relacionados.
- Búsqueda y recuperación de conocimiento técnico.
- Exposición de resultados mediante una API en formato JSON.

---

## Arquitectura prevista

La arquitectura final del proyecto contempla la separación entre los componentes de Ciencia de Datos, backend e infraestructura.

```text
Cliente / Aplicación
        │
        ▼
API Backend
Java + Spring Boot
        │
        ▼
Servicio de Ciencia de Datos
Python
        │
        ├── Procesamiento de texto
        ├── Modelo de clasificación
        └── Extracción de información
        │
        ▼
Oracle Cloud Infrastructure
```

### Tecnologías previstas

| Componente | Tecnología |
|---|---|
| Ciencia de Datos | Python |
| Análisis y entrenamiento | Jupyter Notebook / Google Colab |
| Procesamiento de datos | Pandas |
| Machine Learning | Scikit-learn |
| Procesamiento de texto | TF-IDF |
| Backend final | Java + Spring Boot |
| API | REST / JSON |
| Infraestructura | Oracle Cloud Infrastructure – OCI |
| Control de versiones | Git / GitHub |

---

## Prototipo inicial

Actualmente se encuentra en desarrollo una primera **prueba de concepto de TechMind**, cuyo objetivo es validar el funcionamiento básico de la solución antes de avanzar hacia la arquitectura definitiva.

El prototipo se encuentra en la rama:

```text
feature/techmind-prototype
```

### Tecnologías del prototipo

La primera versión utiliza una arquitectura simplificada basada en:

```text
Python
Flask
Pandas
Scikit-learn
TF-IDF
Logistic Regression
Joblib
HTML / CSS
```

### Flujo del prototipo

```text
Contenido técnico
       │
       ▼
Título + Texto
       │
       ▼
Procesamiento TF-IDF
       │
       ▼
Modelo de clasificación
       │
       ├── Categoría
       ├── Nivel de confianza
       └── Palabras clave
       │
       ▼
Interfaz Flask / API JSON
```

El propósito de esta versión es validar el núcleo funcional:

```text
Contenido técnico
        ↓
Procesamiento
        ↓
Clasificación
        ↓
Categoría + Confianza + Palabras clave
```

Este prototipo no representa todavía la arquitectura final del proyecto.

---

## Estrategia de desarrollo

El proyecto se desarrollará progresivamente.

### Etapa 1 – Prototipo funcional

Rama:

```text
feature/techmind-prototype
```

Objetivos:

- Preparación del dataset.
- Análisis exploratorio de datos.
- Procesamiento de texto.
- Entrenamiento de un modelo inicial.
- Clasificación de contenido técnico.
- Extracción de palabras clave.
- Interfaz básica con Flask.
- Endpoint REST con respuesta JSON.

### Etapa 2 – Evolución de la solución

Una vez validado el prototipo se podrá avanzar hacia:

- Separación del componente de Ciencia de Datos.
- Desarrollo del backend principal con Java y Spring Boot.
- Integración entre backend y modelo de Ciencia de Datos.
- Persistencia de información.
- Mejora de los mecanismos de búsqueda y organización del conocimiento.

### Etapa 3 – Integración con OCI

La solución final contempla la integración con servicios de **Oracle Cloud Infrastructure (OCI)** para aspectos como:

- Despliegue de servicios.
- Almacenamiento de modelos.
- Almacenamiento de documentos.
- Persistencia de información.
- Ejecución de la solución en infraestructura cloud.

---

## Estructura de ramas

Actualmente el repositorio utiliza la siguiente organización:

```text
main
│
└── feature/techmind-prototype
```

### `main`

Contiene la versión principal y estable del proyecto, así como la documentación general.

### `feature/techmind-prototype`

Contiene el desarrollo de la primera prueba de concepto de TechMind utilizando **Python y Flask**.

Para consultar el prototipo:

```bash
git checkout feature/techmind-prototype
```

---

## Estado del proyecto

```text
Estado actual: Prototipo inicial en desarrollo
```

La fase actual está orientada a validar el procesamiento y clasificación de contenido técnico antes de avanzar hacia la arquitectura completa de la solución.

---

## Proyecto

**Proyecto 1: TechMind – Organización Inteligente del Conocimiento Técnico**

Repositorio desarrollado como parte de la propuesta de solución para la organización y enriquecimiento inteligente de contenidos técnicos.

