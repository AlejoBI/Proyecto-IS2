# Seguridad del modo demo

## Bring Your Own Key (BYOK)

La demo pública no usa una clave de proveedor del servidor. El usuario escribe
su propia clave en el navegador y el cliente la envía en `X-LLM-API-Key`, junto
con `X-LLM-Provider`, únicamente en carga, consulta e indexación.

La API:

- no guarda la clave en MongoDB, ChromaDB, cookies ni archivos;
- no la imprime en logs;
    - crea un cliente del proveedor seleccionado para cada solicitud;
- devuelve los errores del proveedor sin incluir la clave completa.

Las rutas administrativas requieren una cookie JWT válida cuyo token incluya
el rol `admin`. El registro público siempre crea usuarios con rol `user`.

La clave permanece en el estado de React y se pierde al recargar la página.
El usuario debe asumir el costo y los permisos de su cuenta del proveedor.

## Límites de abuso

Cada solicitud RAG necesita una sesión temporal y está protegida por:

- límite de solicitudes por IP y sesión;
- máximo de 5 documentos y 50 MB por sesión;
- máximo de 10 MB por archivo;
- máximo de 20 preguntas por sesión;
- máximo de 2.000 caracteres por pregunta;
- aislamiento de los vectores por `session_id`.

El rate limiter incluido es local al proceso. Para varias réplicas debe
reemplazarse por Redis o por un rate limiter administrado por el proveedor.

## Producción

El despliegue público debe usar HTTPS, secretos del proveedor, CORS limitado
al dominio del frontend, MongoDB con autenticación y backups. Nunca se debe
cometer `.env` ni colocar una clave real en el frontend.
