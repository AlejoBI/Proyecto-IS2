# Componentes del sistema

| Componente | Responsabilidad |
|---|---|
| `server/main.py` | Aplicación, healthchecks, CORS y limpieza periódica. |
| `server/api/*_routes.py` | HTTP, autenticación, autorización y códigos de respuesta. |
| `server/api/dependencies.py` | Construcción de servicios y adaptadores compartidos. |
| `server/api/schemas.py` | DTOs y validación de entradas y respuestas. |
| `server/app/usecases.py` | Casos de uso de RAG, indexación, recuperación e historial. |
| `server/core/models.py` | Modelos de dominio y estados de documentos. |
| `server/core/ports.py` | Interfaces para repositorios y proveedores LLM. |
| `server/adapters/mongodb_adapter.py` | Usuarios, documentos, sesiones e historial. |
| `server/adapters/chromadb_adapter.py` | Colecciones, embeddings, búsqueda y borrado vectorial. |
| `server/adapters/openai_adapter.py` | Cliente común para OpenAI y Gemini y errores del proveedor. |
| `server/helpers/strategies.py` | Lectura y extracción de PDF, DOCX y TXT. |
| `server/services/sessions.py` | Creación, límites, expiración y limpieza de sesiones. |
| `client/src/components/QuestionForm.jsx` | Interfaz de proveedor, documentos, preguntas y fuentes. |
| `client/src/hooks/useRag.js` | Estado de carga, consulta, eliminación y reindexación. |
| `client/src/api/auth.js` | Cliente HTTP para autenticación y operaciones RAG. |
