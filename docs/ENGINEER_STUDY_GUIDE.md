# Guía de estudio para construir sistemas RAG de producción

Este documento explica qué conocimientos necesita un ingeniero para desarrollar
una plataforma como Proyecto IS2. No es una lista de tecnologías para memorizar:
es una ruta para entender las decisiones, los riesgos y las responsabilidades
de cada parte del sistema.

## 1. Qué se está construyendo

El sistema combina una aplicación web, una API, autenticación, persistencia,
procesamiento de archivos, búsqueda semántica, modelos generativos, seguridad
y despliegue cloud.

```text
Usuario
  -> Frontend web
  -> API y autenticación
  -> Procesamiento de documentos
  -> Embeddings y base vectorial
  -> Recuperación de contexto
  -> Modelo generativo
  -> Respuesta con fuentes
```

La dificultad no está únicamente en llamar a una API de IA. Está en conectar
correctamente todos esos componentes, aislar los datos, manejar fallos,
controlar costos y operar el sistema después de publicarlo.

## 2. Competencias generales

### Programación

Debe dominar al menos un lenguaje de backend y uno de frontend, además de:

- tipos, estructuras de datos, funciones y clases;
- programación orientada a objetos y composición;
- excepciones, validación y manejo de errores;
- asincronía, concurrencia y operaciones bloqueantes;
- lectura de documentación y depuración;
- Git, ramas, commits pequeños y revisión de cambios.

En este proyecto Python coordina la API y React maneja la interfaz. No basta
con conocer la sintaxis: hay que entender qué trabajo puede ejecutarse dentro
del event loop y qué trabajo debe enviarse a un threadpool o worker.

### Sistemas web

Conceptos esenciales:

- HTTP, métodos, headers, cookies, status codes y JSON;
- REST y diseño de endpoints;
- CORS y solicitudes con credenciales;
- DNS, HTTPS, dominios y certificados;
- frontend estático versus backend dinámico;
- proxies, timeouts, reintentos y límites de tamaño.

Esto permite entender por qué Cloudflare Pages necesita `VITE_API_URL`, por qué
Render debe permitir el origen del frontend y por qué una cookie cross-site
requiere `Secure` y `SameSite=None`.

## 3. Backend y diseño de APIs

### Qué estudiar

1. FastAPI o un framework equivalente.
2. Validación con modelos tipados.
3. Inyección de dependencias.
4. Separación entre rutas, servicios, dominio y adaptadores.
5. Autenticación y autorización.
6. Manejo centralizado de errores.
7. Logging estructurado.

### Qué debe saber hacer el ingeniero

- Diseñar una ruta que valide la entrada antes de ejecutar trabajo costoso.
- Devolver códigos HTTP coherentes: `400`, `401`, `403`, `404`, `409`, `413`,
  `429`, `502` y `503`.
- Diferenciar autenticación de autorización.
- Evitar que una excepción interna exponga secretos o trazas privadas.
- Inyectar servicios para poder sustituirlos por mocks en pruebas.

En Proyecto IS2, `rag_routes.py` debe ocuparse del protocolo HTTP, mientras
`RAGService` coordina el caso de uso y los adaptadores hablan con MongoDB,
ChromaDB y los proveedores de IA.

## 4. Frontend moderno

### Qué estudiar

- HTML semántico, CSS responsive y accesibilidad;
- JavaScript moderno y módulos ES;
- React, componentes, hooks y estado;
- formularios, estados de carga y errores;
- Axios o `fetch`, cookies y `withCredentials`;
- variables de entorno públicas en Vite;
- build de producción y separación entre desarrollo y producción.

### Aplicación al proyecto

El frontend debe poder representar al menos estos estados:

```text
idle -> uploading -> processing -> completed
                         \-> failed
completed -> indexing-for-provider
question -> retrieving -> generating -> answered
```

Una buena interfaz no muestra solo “error”. Explica si falló la API key, la
cuota, la indexación, la recuperación o el proveedor externo.

## 5. Bases de datos y persistencia

### MongoDB

Debe conocer:

- documentos, colecciones e índices;
- consultas por campos y filtros de autorización;
- índices únicos e idempotencia;
- TTL e identificación de datos expirados;
- consistencia, backups y restauración;
- conexión segura y credenciales.

MongoDB guarda usuarios, sesiones, documentos, contenido extraído e historial.
El contenido extraído es importante porque permite reindexar un documento para
Gemini u OpenAI sin pedir al usuario que lo cargue otra vez.

### Almacenamiento de archivos

Hay que entender la diferencia entre un filesystem efímero y uno persistente.
En Render, ChromaDB y `media/` necesitan un persistent disk o un almacenamiento
externo. Una base de datos persistente no vuelve persistentes automáticamente
los archivos locales.

## 6. RAG, embeddings y modelos generativos

### Conceptos que debe dominar

- tokenización y límites de contexto;
- chunking y solapamiento de fragmentos;
- embeddings como representación vectorial;
- similitud semántica y búsqueda `top-k`;
- grounding y alucinaciones;
- prompt con contexto recuperado;
- fuentes, trazabilidad y evaluación;
- latencia, costo, cuota y reintentos.

### Flujo técnico

```text
Archivo
  -> extracción de texto
  -> limpieza
  -> chunks
  -> embeddings
  -> ChromaDB

Pregunta
  -> embedding de consulta
  -> búsqueda top-k
  -> contexto recuperado
  -> generación
  -> respuesta + fuentes
```

### Regla crítica de proveedores

Los embeddings de proveedores distintos no deben mezclarse en una misma
colección. Cambiar de OpenAI a Gemini exige reindexar el documento con el
embedding del nuevo proveedor. El modelo generativo y el modelo de embeddings
son decisiones separadas.

### Qué debe saber evaluar

- si los fragmentos recuperados realmente responden la pregunta;
- si `k` es demasiado bajo o demasiado alto;
- si la respuesta usa información que no estaba en el contexto;
- cuánto cuesta indexar un documento y responder una pregunta;
- qué hacer cuando no existe evidencia suficiente.

## 7. Procesamiento de documentos

Para PDF, DOCX y TXT debe comprender:

- validación por extensión y tamaño;
- lectura binaria y codificaciones;
- extracción de texto imperfecta;
- documentos vacíos o corruptos;
- sanitización de nombres de archivo;
- checksum para detectar duplicados;
- limpieza de archivos cuando falla el procesamiento.

La extensión del archivo no es una garantía de su contenido. Un sistema serio
valida límites, captura errores de lectura y nunca confía en el nombre recibido
del navegador.

## 8. Seguridad

### Temas indispensables

- hash seguro de contraseñas;
- JWT y cookies `HttpOnly`;
- `Secure`, `SameSite` y CSRF;
- CORS con lista explícita de orígenes;
- control de acceso por usuario y por rol;
- aislamiento por sesión y propietario;
- protección contra subida de archivos maliciosos;
- rate limiting y límites de recursos;
- gestión de secretos;
- redacción de logs.

### Preguntas que debe poder responder

- ¿Puede un usuario consultar vectores de otra sesión?
- ¿Puede un usuario normal llamar una ruta administrativa?
- ¿Se guarda una API key en MongoDB, cookies o logs?
- ¿Qué ocurre si el proveedor responde con un error que contiene datos
  sensibles?
- ¿Qué evita que una sesión suba infinitos archivos o preguntas?

BYOK reduce la responsabilidad de almacenar claves, pero no elimina la
responsabilidad de protegerlas durante el transporte y evitar que aparezcan en
logs, mensajes de error o bundles públicos.

## 9. Arquitectura y patrones

Debe conocer, saber justificar y no aplicar mecánicamente:

- **Ports and Adapters:** aislar el dominio de proveedores concretos.
- **Repository:** encapsular persistencia.
- **Service Layer:** coordinar casos de uso.
- **Strategy:** seleccionar lectores de archivos.
- **Adapter:** ofrecer una interfaz común para OpenAI y Gemini.
- **Dependency Injection:** sustituir dependencias en pruebas.
- **DTO/schema:** validar contratos de entrada y salida.

La pregunta importante no es “¿qué patrón puedo agregar?”, sino “¿qué cambio
sería fácil y seguro si MongoDB, ChromaDB o el proveedor de IA cambia mañana?”.

## 10. Testing y calidad

### Niveles de prueba

1. **Unitarias:** validan servicios, adaptadores simulados y reglas aisladas.
2. **Integración:** verifican MongoDB, ChromaDB o Redis en un entorno controlado.
3. **API:** prueban rutas, headers, cookies y códigos HTTP.
4. **Frontend:** prueban estados y flujos principales.
5. **Evaluación RAG:** compara respuestas, fuentes, recall y latencia.
6. **Smoke test:** confirma `/health`, `/ready`, login, carga y pregunta.

Las pruebas contra OpenAI o Gemini no deben depender de una key real ni
consumir créditos en CI. Para eso se usan mocks y pruebas manuales separadas.

## 11. DevOps y cloud

### Conocimientos necesarios

- Dockerfile, imágenes, volúmenes y healthchecks;
- variables de entorno y secretos;
- CI/CD y despliegue desde Git;
- logs de plataforma y rollback;
- dominios, DNS y HTTPS;
- persistent disks y bases de datos administradas;
- diferencias entre servicios gratuitos y producción.

### Arquitectura de despliegue estudiada

```text
Cloudflare Pages
  VITE_API_URL
        |
        v
Render Web Service
  FastAPI + Docker
        |
        +--> MongoDB Atlas
        +--> Persistent Disk: ChromaDB + media
        +--> Redis opcional
```

El ingeniero debe poder desplegar, leer logs, verificar `/ready`, revisar CORS,
confirmar cookies y restaurar datos antes de considerar el sistema operativo.

## 12. Observabilidad y operación

Debe saber medir:

- duración de extracción, embeddings, retrieval y generación;
- número de fuentes recuperadas;
- errores por proveedor y código HTTP;
- uso de cuota y costo aproximado;
- tamaño de almacenamiento;
- expiración y limpieza de sesiones.

Un `request_id` permite conectar la respuesta del usuario con los eventos del
backend. Los logs deben ser útiles sin registrar prompts completos, documentos,
API keys, cookies ni tokens.

## 13. Ruta de aprendizaje recomendada

### Nivel 1 — Fundamentos

- Python y JavaScript.
- Git y terminal.
- HTTP, JSON y bases de datos básicas.
- HTML, CSS y React básico.

**Ejercicio:** crear un CRUD pequeño con login y una interfaz React.

### Nivel 2 — Backend profesional

- FastAPI, Pydantic y dependencias.
- MongoDB, índices y validación.
- JWT, cookies, CORS y autorización.
- pytest y mocks.

**Ejercicio:** crear una API de documentos con usuarios, roles, límites y
pruebas de autorización.

### Nivel 3 — Datos y archivos

- Uploads, PDF/DOCX/TXT y checksum.
- Procesamiento asíncrono y trabajo bloqueante.
- Estados de procesamiento y limpieza.

**Ejercicio:** cargar un documento, extraerlo, dividirlo y guardar su estado.

### Nivel 4 — IA aplicada

- Tokens, embeddings, vector stores y retrieval.
- Prompting con contexto y fuentes.
- Costos, cuotas, timeouts y errores de proveedores.

**Ejercicio:** construir un RAG local con un solo proveedor y después agregar
un segundo proveedor con colecciones separadas.

### Nivel 5 — Producción

- Docker y CI.
- MongoDB Atlas, Render y Cloudflare Pages.
- Persistent disks, backups, healthchecks y observabilidad.

**Ejercicio:** desplegar el sistema, romper intencionalmente CORS y una
conexión de base de datos, y diagnosticar ambos fallos con logs.

## 14. Lista de preparación profesional

Una persona está preparada para construir un sistema de esta magnitud cuando
puede explicar y demostrar lo siguiente:

- Diseña una API con contratos y errores consistentes.
- Implementa autenticación, autorización y aislamiento de datos.
- Procesa archivos sin confiar en entradas del usuario.
- Explica cómo funcionan embeddings y recuperación semántica.
- Mantiene separados los espacios vectoriales incompatibles.
- Diseña reintentos sin duplicar datos ni multiplicar costos.
- Escribe pruebas sin depender de servicios externos pagos.
- Despliega frontend y backend con variables separadas.
- Configura CORS, cookies seguras, HTTPS y secretos.
- Detecta qué datos son efímeros y cuáles necesitan persistencia.
- Añade logs y `request_id` sin filtrar información privada.
- Puede restaurar una base de datos o explicar el procedimiento de recuperación.
- Sabe justificar por qué una arquitectura es simple, mantenible y suficiente.

## 15. Referencia con Proyecto IS2

Para estudiar el código en orden, se recomienda leer:

1. `README.md` para el alcance.
2. `docs/ARCHITECTURE.md` para las capas.
3. `server/api/rag_routes.py` para el contrato HTTP.
4. `server/app/usecases.py` para el flujo RAG.
5. `server/core/ports.py` y `server/core/models.py` para dominio.
6. `server/adapters/openai_adapter.py` para proveedores y errores.
7. `server/adapters/chromadb_adapter.py` para retrieval.
8. `server/adapters/mongodb_adapter.py` para persistencia.
9. `client/src/components/QuestionForm.jsx` y `client/src/hooks/useRag.js`
   para la experiencia de usuario.
10. `docs/DEPLOYMENT.md`, `docs/SECURITY.md` y `docs/OBSERVABILITY.md` para
    llevarlo a producción.
