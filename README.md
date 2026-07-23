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
