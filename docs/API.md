# API

La API se sirve desde el origen configurado en `VITE_API_URL`. Las rutas usan
cookies de sesión/autenticación cuando corresponde. Las operaciones RAG reciben
la clave del proveedor en `X-LLM-API-Key` y el proveedor en `X-LLM-Provider`.

## Sesión y autenticación

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/session` | Crear o recuperar sesión anónima y límites. |
| `POST` | `/register` | Registrar usuario. |
| `POST` | `/login` | Iniciar sesión y emitir cookie `access_token`. |
| `GET` | `/checkauth` | Consultar autenticación; anónimo devuelve `200`. |
| `POST` | `/logout` | Eliminar cookie de autenticación. |

## Documentos y preguntas

| Método | Ruta | Uso |
|---|---|---|
| `POST` | `/save-document` | Cargar, extraer, vectorizar y guardar documento. |
| `GET` | `/session/documents` | Listar documentos de la sesión. |
| `DELETE` | `/session/documents/{document_id}` | Eliminar documento y vectores. |
| `POST` | `/session/documents/{document_id}/index` | Indexar documento existente para el proveedor actual. |
| `GET` | `/generate-answer?query=...` | Recuperar contexto y generar respuesta con fuentes. |
| `GET` | `/me/documents` | Listar documentos del usuario autenticado. |
| `GET` | `/me/history` | Listar historial del usuario autenticado. |

## Administración

Estas rutas requieren un usuario autenticado con rol `admin`:

`GET /admin/get-users`, `POST /admin/save-user`, `PUT /admin/update-user`,
`DELETE /admin/delete-user`, `GET /admin/get-documents` y
`DELETE /admin/delete-document`.

También requieren administración `GET /get-document` y `GET /get-vectors`.

## Respuestas y errores

Una respuesta exitosa de pregunta contiene `answer`, `sources` y, cuando aplica,
`provider`. Las respuestas de error usan `detail`. Los fallos del proveedor
pueden devolver `401/403` (clave), `429` (cuota o rate limit), `502` (fallo de
upstream) o `503` (indisponibilidad). En preguntas se incluye `X-Request-ID`
para diagnóstico.

Ejemplo:

```bash
curl -G http://localhost:8000/generate-answer \
  --data-urlencode "query=¿Cuál es el objetivo del documento?" \
  -H "X-LLM-Provider: openai" \
  -H "X-LLM-API-Key: $OPENAI_API_KEY"
```
