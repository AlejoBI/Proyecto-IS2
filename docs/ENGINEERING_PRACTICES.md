# Prácticas de ingeniería

## Seguridad

- BYOK: la clave se recibe por solicitud, no se persiste y no se registra.
- HTTPS, CORS restringido, cookies `HttpOnly` y secretos fuera del repositorio.
- Validación de extensiones, tamaño, checksum, límites de sesión y autorización.
- Los logs registran tipo de error y `request_id`, nunca prompts, contexto ni
  encabezados sensibles.

## Fiabilidad

- Estados explícitos de documento: `pending`, `processing`, `completed`, `failed`.
- Timeouts y reintentos controlados para proveedores externos.
- Reindexación idempotente: si el proveedor ya tiene el índice, no se duplica.
- Trabajo de lectura y vectorización fuera del ciclo bloqueante de validación HTTP.
- `/health`, `/ready`, limpieza periódica y backups configurables.

## Calidad

- Pruebas unitarias con adaptadores simulados; las pruebas no consumen créditos.
- `compileall` y pytest para backend.
- ESLint, Prettier y build de producción para frontend.
- Cambios pequeños y auditables, con documentación de decisiones técnicas.

## Costos y proveedores

El proveedor se selecciona por solicitud. Los documentos solo se reindexan para
el proveedor solicitado y sus embeddings permanecen separados. La aplicación
no oculta los errores de cuota: devuelve un mensaje accionable y un código HTTP
adecuado.
