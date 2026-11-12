# Estado del proyecto

## Alcance actual

El proyecto es una plataforma RAG monolítica modular. Permite cargar PDF, DOCX
y TXT, indexarlos por proveedor, hacer preguntas con fuentes y administrar
usuarios desde rutas protegidas.

## Capacidades implementadas

- Sesiones anónimas temporales y sesiones de usuarios autenticados.
- Registro, login, logout y autorización administrativa.
- BYOK por solicitud para OpenAI y Gemini.
- Embeddings separados por proveedor; no se mezclan espacios vectoriales.
- Reindexación de un documento existente para otro proveedor.
- Estados de documento: `pending`, `processing`, `completed` y `failed`.
- Fuentes en las respuestas y persistencia del historial autenticado.
- Límites de archivos, preguntas, almacenamiento y solicitudes.
- Limpieza automática de sesiones expiradas.
- Healthchecks `/health` y `/ready`.
- Rate limiting local o distribuido con Redis.
- Logs por etapa con `request_id`, sin claves ni contexto privado.
- Pruebas backend, linting, formato y build frontend.

## Decisiones vigentes

- MongoDB conserva metadatos y contenido necesario para reindexar.
- ChromaDB conserva los fragmentos vectorizados por sesión y proveedor.
- El backend es un despliegue único modular; no se introducen microservicios,
  agentes autónomos, MCP ni n8n.
- Las API keys no se persisten ni se incluyen en logs.

## Trabajo futuro

- Evaluación formal con un conjunto de preguntas y respuestas de referencia.
- Métricas operativas centralizadas para latencia, costo y calidad de fuentes.
- Sustitución de ChromaDB local por un servicio administrado si se requieren
  varias réplicas.
