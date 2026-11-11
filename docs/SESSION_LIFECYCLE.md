# Ciclo de vida de las sesiones

## Creación

`GET /session` crea una sesión anónima identificada por un UUID aleatorio y
la entrega en una cookie `HttpOnly` llamada `rag_session_id`. La cookie no
contiene la API key.

MongoDB guarda solamente metadatos:

```text
id, created_at, last_activity, expires_at,
document_count, storage_used, question_count
```

## Expiración

La sesión expira después de 30 minutos sin actividad o, como máximo, después
de 2 horas desde su creación. Los valores son configurables en `.env`.

Cada documento guarda `session_id` y una fecha de expiración. ChromaDB guarda
el mismo `session_id` en los metadatos de cada fragmento. Las consultas solo
buscan fragmentos de la sesión actual.

## Limpieza

El worker de `server/main.py` se ejecuta cada 10 minutos y elimina:

1. documentos vencidos de MongoDB;
2. vectores relacionados en ChromaDB;
3. archivos físicos de `media/sessions/`;
4. sesiones vencidas;
5. entradas antiguas del rate limiter.

MongoDB usa un índice TTL para limpiar los metadatos de sesión. La eliminación
de documentos y archivos la hace el worker porque MongoDB no puede borrar un
archivo almacenado en el volumen de la aplicación.

Un reinicio del servidor no conserva las claves, porque nunca se persisten.
Los documentos pueden sobrevivir si los volúmenes son persistentes, pero sus
sesiones continuarán expirando y el worker los eliminará.
