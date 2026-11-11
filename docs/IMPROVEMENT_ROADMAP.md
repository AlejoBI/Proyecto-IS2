# Roadmap de modernización

Este documento es el checklist vivo del proyecto. Una tarea solo se marca como
completada cuando existe implementación y una validación correspondiente.

## Fase 1 — Seguridad y límites

- [x] BYOK: API key por solicitud, sin persistencia.
- [x] Sesiones anónimas con expiración y limpieza automática.
- [x] Límites de archivos, almacenamiento, preguntas y solicitudes.
- [x] Aislamiento de documentos y vectores por sesión.
- [x] Autorización de rol administrativo en el backend.
- [x] Eliminar información sensible de las respuestas de autenticación.
- [x] Impedir que el registro público cree administradores.
- [x] Evitar exponer hashes de contraseñas en el panel.
- [x] Separar rutas públicas, autenticación, RAG y administración.
- [x] Configurar CORS y cookies para producción.

## Fase 2 — Backend y dominio

- [x] Separar `AuthService`, `RAGService` y `AdminService`.
- [x] Mantener `SessionService` y `CleanupService` independientes.
- [x] Separar routers por contexto (`auth`, `rag`, `admin`, `public`).
- [x] Sustituir strings de estado públicos por respuestas y errores tipados.
- [x] Centralizar parcialmente respuestas de error y logging sin credenciales.
- [x] Validar extensión y tamaño de archivos.
- [x] Detectar documentos duplicados por checksum.
- [x] Limpiar archivos cuando falla el procesamiento.
- [x] Añadir estados de procesamiento de documentos (`pending`, `processing`, `completed`, `failed`).
- [x] Limitar lecturas y procesar el trabajo pesado fuera del ciclo de validación de la solicitud.

## Fase 3 — RAG

- [x] Devolver fuentes y fragmentos usados en cada respuesta.
- [x] Evitar documentos duplicados.
- [x] Añadir reintentos y timeouts controlados para el proveedor LLM.
- [x] Mejorar la configuración de chunking y recuperación.
- [x] Añadir evaluación reproducible con preguntas y respuestas de referencia.
- [x] Definir estrategia y herramienta de exportación/migración de ChromaDB.

## Fase 4 — Frontend

- [x] Separar visualmente la interfaz pública y el panel administrativo.
- [x] Crear hooks especializados para sesión, documentos y consultas.
- [x] Mostrar cuotas y expiración de la sesión.
- [x] Mostrar fuentes del RAG.
- [x] Centralizar errores y estados de carga principales.
- [x] Eliminar estado duplicado de autenticación y cookies.
- [x] Persistir documentos e historial para usuarios registrados.
- [x] Aislar documentos registrados por usuario en MongoDB y ChromaDB.

## Fase 5 — Datos y operación

- [x] Definir índices y migración idempotente de MongoDB.
- [x] Añadir auditoría administrativa mínima.
- [x] Reemplazar el rate limiter local por Redis cuando `REDIS_URL` está configurado.
- [x] Configurar backups de MongoDB/ChromaDB y políticas de retención.
- [x] Healthchecks de MongoDB y backend (`/health` y `/ready`).

## Fase 6 — Calidad

- [x] Compilación Python validada.
- [x] Build del frontend validado.
- [x] 22 pruebas unitarias pasan (18 existentes + 4 nuevas).
- [x] Tests de autorización administrativa.
- [x] Test unitario del rate limiter.
- [x] Test unitario de fuentes y aislamiento de sesión en respuestas RAG.
- [x] Test unitario de limpieza y expiración de sesiones.
- [x] Test del flujo BYOK con OpenAI simulado.
- [x] CI para pruebas backend, compilación Python y build frontend.
- [x] Linting y formateo automático con ESLint y Prettier.
- [x] Migrar Bootstrap/React-Bootstrap a Tailwind CSS.

## Registro de trabajo

### 2026-11-11

- Se creó este roadmap.
- Se inició la Fase 1 con autorización backend y saneamiento del login.
- Se completaron servicios y routers separados, fuentes RAG, validación de
  duplicados, auditoría administrativa, readiness probe y CI.
- Se completaron estados tipados de documentos, evaluación reproducible del
  RAG, exportación de ChromaDB, limiter Redis y backups con retención.
