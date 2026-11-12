# Despliegue de la demo RAG

## Variables mínimas

1. Copiar `.env.example` a `.env`.
2. Definir `SECRET_ACCESS_TOKEN` con un secreto aleatorio.
3. Definir `MONGODB_URI` con una instancia persistente y autenticada.
4. Mantener `OPENAI_API_KEY` vacío en modo BYOK; las claves llegan por solicitud.
5. Configurar `REACT_VITE_CONNECTION` con el origen real del frontend.

## Entornos y plantillas de variables

El repositorio incluye plantillas seguras, sin credenciales reales:

| Entorno | Backend | Frontend | Uso |
|---|---|---|---|
| `develop` | `.env.develop.example` | `client/.env.develop.example` | Desarrollo local o staging. |
| `production` | `.env.production.example` | `client/.env.production.example` | Render + Cloudflare Pages. |
| local genérico | `.env.example` | `client/.env` | Configuración base local. |

Para trabajar localmente, copiar la plantilla correspondiente a `.env` en la
raíz y la plantilla del frontend a `client/.env`:

```powershell
Copy-Item .env.develop.example .env
Copy-Item client/.env.develop.example client/.env
```

No se deben subir `.env`, API keys, contraseñas ni secretos. En Render y
Cloudflare las variables se configuran desde sus respectivos paneles; las
plantillas solo sirven como referencia y checklist.

Las diferencias importantes son:

- `develop` usa localhost, cookies `lax` y almacenamiento local.
- `production` usa HTTPS, cookies `none` + `secure`, MongoDB Atlas y el backend
  de Render.
- El frontend de Cloudflare solo necesita `VITE_API_URL`; nunca debe recibir
  `OPENAI_API_KEY` ni `GEMINI_API_KEY`.

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

Para OpenAI se configuran `MODEL` y `EMBEDDING_MODEL`. El modelo de generación
puede cambiarse desde `.env` sin modificar el código; las API keys de usuario
no deben ponerse en variables `VITE_*` ni versionarse.

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

## Despliegue recomendado: Cloudflare Pages + Render

Esta sección describe el despliegue de producción recomendado para este
repositorio:

```text
Cloudflare Pages (React/Vite) --> Render (FastAPI/Docker) --> MongoDB Atlas
                                             |
                                             +--> Redis administrado (opcional)
```

### 1. MongoDB Atlas

1. Crear un cluster y una base de datos.
2. Crear un usuario de base de datos con permisos sobre `proyecto_is2`.
3. En **Network Access**, autorizar las conexiones del servicio de Render.
   Para una prueba temporal puede usarse `0.0.0.0/0`, pero en producción se
   recomienda restringir la red según la estrategia de acceso elegida.
4. Copiar la URI SRV, por ejemplo:

```text
mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

La contraseña debe estar URL-encoded si contiene caracteres especiales.

### 2. Backend en Render

Crear **New → Web Service**, conectar el repositorio y seleccionar el runtime
Docker. Render utilizará el `Dockerfile` del repositorio. El contenedor escucha
el `PORT` proporcionado por Render y usa `8000` como fallback local.

Configurar el health check como:

```text
/ready
```

No usar `/health` como única comprobación de producción: `/health` confirma que
el proceso vive, mientras `/ready` verifica la conexión con MongoDB.

#### Disco persistente en un plan pago

ChromaDB y los archivos cargados deben escribirse en un disco persistente de
Render. Crear un disk con:

```text
Mount path: /var/data
```

Usar un plan de Render que soporte persistent disks. Los planes gratuitos no
conservan ChromaDB ni archivos entre despliegues.

#### Despliegue gratuito sin Persistent Disk

Para una demo con Render Free y MongoDB Atlas Free no es necesario bloquear el
despliegue por no tener disco. Usar en Render:

```env
CHROMA_PATH=/tmp/chroma_data
MEDIA_PATH=/tmp/media
BACKUP_DIR=/tmp/backups
```

MongoDB conserva los usuarios, el texto extraído, metadatos e historial. El
filesystem de Render es efímero, por lo que ChromaDB y los archivos locales se
pueden perder al reiniciar o redeployar. Cuando el backend recibe una pregunta,
puede volver a generar los embeddings usando el contenido almacenado en
MongoDB; la primera consulta después de un reinicio puede ser más lenta y
consumir embeddings nuevamente.

Esta modalidad es adecuada para una demo o portafolio, no para producción con
garantías de persistencia. Para producción real, agregar el disk en `/var/data`
y cambiar las rutas a:

```env
CHROMA_PATH=/var/data/chroma_data
MEDIA_PATH=/var/data/media
BACKUP_DIR=/var/data/backups
```

#### Variables de entorno del backend

Configurar estas variables en **Render → Environment**. No subirlas al
repositorio:

```env
APP_HOST=0.0.0.0
APP_PORT=8000

REACT_VITE_CONNECTION=https://tu-proyecto.pages.dev
ALLOWED_ORIGINS=https://tu-proyecto.pages.dev
COOKIE_SECURE=true
COOKIE_SAMESITE=none

ALGORITHM=HS256
SECRET_ACCESS_TOKEN=<secreto-largo-aleatorio>

MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=proyecto_is2
MONGODB_COLLECTION_USERS=users
MONGODB_COLLECTION_DOCUMENTS=documents

OPENAI_API_KEY=
MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

GEMINI_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

MAX_TOKENS=500
TEMPERATURE=0.2
NUMBER_OF_VECTORIAL_RESULTS=3
CHROMA_PATH=/var/data/chroma_data
MEDIA_PATH=/var/data/media

SESSION_IDLE_MINUTES=30
SESSION_MAX_HOURS=2
MAX_FILE_SIZE_BYTES=10485760
MAX_DOCUMENTS_PER_SESSION=5
MAX_STORAGE_BYTES_PER_SESSION=52428800
MAX_QUESTIONS_PER_SESSION=20
MAX_QUERY_LENGTH=2000
CHUNK_SIZE_TOKENS=2048

OPENAI_TIMEOUT_SECONDS=30
OPENAI_MAX_RETRIES=2
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=60
REDIS_URL=
REDIS_RATE_LIMIT_PREFIX=proyecto-is2:rate
CLEANUP_INTERVAL_SECONDS=600
BACKUP_DIR=/var/data/backups
BACKUP_RETENTION_DAYS=7
ALLOWED_FILE_EXTENSIONS=.pdf,.docx,.txt
```

`OPENAI_API_KEY` debe permanecer vacío en modo BYOK. La clave de OpenAI o
Gemini la introduce cada usuario en el frontend y se envía en
`X-LLM-API-Key`. Nunca colocar una clave en una variable `VITE_*`.

Si se configura Redis administrado, asignar su URL a `REDIS_URL`; si se deja
vacío, el backend utiliza un limiter en memoria válido para una sola instancia.

### 3. Frontend en Cloudflare Pages

Crear un proyecto Pages conectado al repositorio. Como el repositorio contiene
backend y frontend, configurar:

```text
Root directory: client
Build command: npm run build
Build output directory: dist
```

En **Settings → Environment variables**, agregar para Production:

```env
VITE_API_URL=https://tu-backend.onrender.com
```

Después del primer despliegue, copiar el dominio real de Cloudflare Pages y
actualizar en Render:

```env
REACT_VITE_CONNECTION=https://tu-proyecto.pages.dev
ALLOWED_ORIGINS=https://tu-proyecto.pages.dev
```

Si se agrega un dominio personalizado, usar ese dominio exacto y no dejar el
valor de ejemplo. Si se mantienen frontend y backend en dominios distintos,
`COOKIE_SAMESITE=none` y `COOKIE_SECURE=true` son necesarios para que las
cookies HttpOnly funcionen en solicitudes cross-site con `withCredentials`.

### 4. Orden de validación

1. Abrir `https://tu-backend.onrender.com/health`.
2. Abrir `https://tu-backend.onrender.com/ready` y verificar MongoDB Atlas.
3. Abrir el frontend de Cloudflare Pages.
4. Confirmar en el navegador que `GET /session` responde sin error CORS.
5. Registrar un usuario, cerrar sesión y volver a iniciar sesión.
6. Cargar un TXT pequeño con OpenAI o Gemini.
7. Hacer una pregunta y confirmar que devuelve fuentes.
8. Cambiar de proveedor y usar `Index for Gemini` o `Index for OpenAI`.

### 5. Errores frecuentes

- **CORS:** `ALLOWED_ORIGINS` debe contener únicamente el origen exacto del
  frontend, incluyendo `https://` y sin una barra final.
- **Sesión no persistente:** comprobar `COOKIE_SECURE=true`,
  `COOKIE_SAMESITE=none`, HTTPS y que Axios use `withCredentials`.
- **Archivos o vectores desaparecen:** comprobar que `/var/data` sea un disk
  persistente y que `CHROMA_PATH` y `MEDIA_PATH` estén debajo de ese path.
- **Render no está listo:** revisar `/ready`, `MONGODB_URI`, credenciales y
  reglas de red de Atlas.
- **Frontend apunta a localhost:** revisar `VITE_API_URL` y volver a desplegar
  Pages; las variables `VITE_*` se incorporan durante el build.
