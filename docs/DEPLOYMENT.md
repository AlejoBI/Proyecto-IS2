# Despliegue de la demo RAG

## Variables mínimas

1. Copiar `.env.example` a `.env`.
2. Definir `SECRET_ACCESS_TOKEN` con un secreto aleatorio.
3. Definir `MONGODB_URI` con una instancia persistente y autenticada.
4. Mantener `OPENAI_API_KEY` vacío en modo BYOK.
5. Configurar `REACT_VITE_CONNECTION` con el origen real del frontend.

## Local

```powershell
docker compose up --build -d
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
```

El backend queda en el puerto 8000 y MongoDB en el 27017. Los volúmenes
`mongodb_data` y `chroma_data` son persistentes.

## Frontend

El frontend usa Tailwind CSS 4 integrado mediante el plugin oficial de Vite.
Los comandos de calidad son:

```bash
npm run lint
npm run format:check
npm run build
```

Crear `client/.env`:

```env
VITE_API_URL=http://localhost:8000
```

El frontend debe servirse con HTTPS en producción. No se debe compilar una
API key dentro de `VITE_*`: esas variables son públicas.

## Proveedores de IA

El formulario permite elegir OpenAI o Google Gemini por solicitud. La clave se
envía únicamente en el encabezado de esa solicitud y no se almacena. Para
Gemini, define en el entorno del backend:

```env
GEMINI_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

La misma conversación puede mezclar proveedores: cada respuesta conserva el
proveedor usado en el historial. Los documentos se reindexan bajo demanda en
la colección vectorial del proveedor seleccionado para evitar mezclar espacios
de embeddings incompatibles.

Los usuarios autenticados conservan sus documentos en MongoDB y pueden
recuperar su historial mediante `/me/documents` y `/me/history`. Las sesiones
anónimas siguen siendo temporales y sus datos se limpian automáticamente.

## Operación

Los índices de MongoDB se crean de forma idempotente al iniciar el adaptador.
También pueden prepararse explícitamente con:

```bash
poetry run python -m server.scripts.ensure_indexes
```

Antes de publicar:

- configurar un dominio y HTTPS;
- restringir CORS al dominio del frontend;
- usar MongoDB Atlas o MongoDB administrado;
- conservar ChromaDB en un volumen persistente o migrarlo a un servicio
  vectorial administrado;
- reemplazar el limiter local por Redis si se usan varias réplicas;
- configurar `REDIS_URL` para activar el limiter distribuido;
- configurar límites de CPU, memoria, tamaño de disco y ancho de banda;
- revisar periódicamente los logs sin registrar encabezados sensibles.

## Backups y retención

El backup incluye MongoDB y el volumen local de ChromaDB. Debe ejecutarse con
la herramienta `mongodump` disponible y programarse mediante Task Scheduler,
cron o el orquestador:

```bash
poetry run python -m server.scripts.backup
poetry run python -m server.scripts.backup --prune-only
```

`BACKUP_RETENTION_DAYS` controla la limpieza automática. En producción, los
directorios generados deben copiarse a almacenamiento externo u object
storage antes de aplicar la retención local.
