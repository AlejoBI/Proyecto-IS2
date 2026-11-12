# Observabilidad y diagnóstico

## Identificación de solicitudes

Cada pregunta genera un `request_id` corto. Se devuelve en el header
`X-Request-ID` y se incluye en los logs relacionados. Debe compartirse para
diagnosticar un error sin compartir la API key, el prompt o el documento.

## Eventos principales

```text
rag.answer.request.started
rag.answer.indexing.started / completed
rag.answer.retrieval.completed
rag.answer.generation.started / completed
rag.answer.history.started / completed
rag.answer.request.completed
rag.answer.provider_failed
rag.answer.failed
```

Los eventos incluyen proveedor, cantidad de fuentes, duración y tipo de error;
no incluyen contenido privado.

## Diagnóstico rápido

| Código | Interpretación | Acción |
|---|---|---|
| `400` | No hay índice para el proveedor o solicitud inválida. | Reindexar el documento o corregir la entrada. |
| `401/403` | El proveedor rechazó la API key. | Verificar key, proyecto y permisos. |
| `429` | Cuota agotada o límite de solicitudes. | Revisar billing/cuota o esperar; también puede cambiarse de proveedor. |
| `502` | Fallo inesperado de upstream. | Buscar el `request_id` y revisar disponibilidad del proveedor. |
| `503` | Servicio temporalmente no disponible. | Reintentar más tarde. |

Los endpoints locales `/health` y `/ready` permiten distinguir un proceso vivo
de una API lista para acceder a MongoDB.
