# Proyecto - IS2

El frontend utiliza React, Vite y Tailwind CSS; el backend utiliza FastAPI,
MongoDB y ChromaDB.
*Miembros:*
- Ludy Astrid Agudelo - 2221008
- Juan Diego Cortes - 2215750
- Juan David Borrero - 2215284
- Alejandro Bravo Isajar - 2220332

# Configuración
*Configurar el ambiente virtual:*

Dentro del directorio Server ejecutar el siguiente comando:
`conda create --name myenvPS2(Este nombre es el que quiera) python=3.12`

Luego activar el ambiente virtual con el siguiente comando:
`conda activate myenvPS2` (Este nombre es el que se puso al crearlo)

Una vez ya activo el ambiente virtual, instalar las dependencias con el siguiente comando:
`poetry install`

Listo 👍👍

# Dependencias 
*Poetry add dependencie:*

- `python=3.12`: Es la versión del lenguaje de programación Python que se está utilizando. Python es conocido por su simplicidad y legibilidad.
- `pydantic`: Es una biblioteca de validación de datos y configuración en Python. Permite definir modelos de datos con validación automática y conversión de tipos.
- `fastapi`: Es un framework web moderno y de alto rendimiento para construir APIs con Python 3.6+ basado en las anotaciones de tipo estándar de Python.
- `uvicorn`: Es un servidor ASGI (Asynchronous Server Gateway Interface) rápido y ligero, utilizado para ejecutar aplicaciones web asíncronas en Python, como las construidas con FastAPI.
- `openai`: Es una biblioteca de Python que permite interactuar con la API de OpenAI. Esta API proporciona acceso a modelos avanzados de inteligencia artificial para tareas como generación de texto, traducción, resumen, y más.
- `chromadb`: Es una biblioteca de Python para trabajar con bases de datos de series temporales y datos de series temporales. Facilita el almacenamiento, consulta y análisis de grandes volúmenes de datos temporales.
- `pydantic_settings`: Es una configuración o instancia de un modelo de Pydantic. Pydantic es una biblioteca de validación de datos y configuración en Python que permite definir modelos de datos con validación automática y conversión de tipos.

## RAG implementado

El proyecto incluye un flujo RAG funcional compuesto por:

1. Carga de archivos PDF, DOCX y TXT mediante FastAPI.
2. Extracción y limpieza del texto.
3. Fragmentación por tokens con `tiktoken`.
4. Generación de embeddings mediante OpenAI.
5. Persistencia y búsqueda semántica de fragmentos en ChromaDB.
6. Recuperación de contexto y generación de respuestas mediante OpenAI.
7. Persistencia de documentos y metadatos en MongoDB.

La colección de ChromaDB se guarda localmente en `./chroma_data`. Para iniciar el backend, define las variables del archivo `.env` y ejecuta:

```bash
poetry install
poetry run uvicorn server.main:app --reload
```

Endpoints principales:

- `POST /save-document`: carga y vectoriza un documento.
- `GET /generate-answer?query=...`: recupera los fragmentos más relevantes y genera una respuesta con fuentes.
- `GET /get-vectors`: consulta los vectores almacenados (solo administración).
- `GET /session`: crea o recupera una sesión temporal y devuelve sus límites.

## Demo pública BYOK

La demo usa el modelo **Bring Your Own Key**: cada visitante proporciona su
propia clave de OpenAI desde el frontend. La clave viaja únicamente en
`X-OpenAI-API-Key` durante la solicitud y no se almacena.

Las sesiones son anónimas y temporales. Los documentos, vectores y archivos se
asocian a una sesión, tienen límites de tamaño/cantidad y se eliminan
automáticamente cuando la sesión vence. Consulta la documentación detallada:

- [Seguridad y límites](docs/SECURITY.md)
- [Ciclo de vida y limpieza](docs/SESSION_LIFECYCLE.md)
- [Despliegue](docs/DEPLOYMENT.md)
