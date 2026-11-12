# Proyecto IS2 — Plataforma RAG

Plataforma web para cargar documentos PDF, DOCX o TXT y hacer preguntas sobre
su contenido con respuestas acompañadas de fuentes. El usuario puede elegir
OpenAI o Google Gemini por solicitud; las claves se entregan mediante BYOK
(Bring Your Own Key) y no se almacenan.

## Equipo

- Ludy Astrid Agudelo — 2221008
- Juan Diego Cortes — 2215750
- Juan David Borrero — 2215284
- Alejandro Bravo Isajar — 2220332

## Stack

- **Frontend:** React, Vite, Axios y Tailwind CSS.
- **Backend:** Python 3.12, FastAPI, Pydantic y Uvicorn.
- **Persistencia:** MongoDB para usuarios, documentos, sesiones e historial.
- **Búsqueda semántica:** ChromaDB para embeddings y recuperación vectorial.
- **Límites distribuidos opcionales:** Redis.
- **Proveedores LLM:** OpenAI y Gemini, seleccionables por solicitud.

## Inicio rápido

```powershell
copy .env.example .env
docker compose up --build -d
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
```

Para desarrollo local:

```powershell
poetry install
poetry run uvicorn server.main:app --reload
cd client
npm install
npm run dev
```

La configuración completa está en [Despliegue](docs/DEPLOYMENT.md).

## Cómo funciona

1. El navegador crea una sesión y carga un documento.
2. El backend valida el archivo, extrae el texto, lo divide en fragmentos y
   genera embeddings con el proveedor seleccionado.
3. Los fragmentos se guardan en ChromaDB y los metadatos en MongoDB.
4. Una pregunta recupera fragmentos de la sesión y proveedor actuales y envía
   ese contexto al modelo generativo.
5. La respuesta vuelve con sus fuentes y, para usuarios autenticados, se guarda
   en el historial.

Cada proveedor usa su propio espacio vectorial. Un documento procesado para
OpenAI puede reindexarse para Gemini sin volver a cargar el archivo.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Flujo RAG](docs/RAG_FLOW.md)
- [Componentes](docs/COMPONENTS.md)
- [Patrones de diseño](docs/DESIGN_PATTERNS.md)
- [Prácticas de ingeniería](docs/ENGINEERING_PRACTICES.md)
- [API](docs/API.md)
- [Observabilidad y diagnóstico](docs/OBSERVABILITY.md)
- [Seguridad](docs/SECURITY.md)
- [Ciclo de vida de sesiones](docs/SESSION_LIFECYCLE.md)
- [Evaluación](docs/RAG_EVALUATION.md)
- [Despliegue](docs/DEPLOYMENT.md)
- [Migración de ChromaDB](docs/CHROMA_MIGRATION.md)
- [Estado del proyecto](docs/PROJECT_STATUS.md)

## Calidad

```powershell
python -m compileall -q server
poetry run pytest -q
cd client
npm run lint
npm run format:check
npm run build
```
