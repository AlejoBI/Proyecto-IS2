# Estrategia de migración de ChromaDB

La instancia actual usa `PersistentClient` sobre el volumen `chroma_data`. Para
una migración segura:

1. Detener escrituras y ejecutar el export de la colección.
2. Verificar que el archivo exportado contiene IDs, documentos, metadatos y
   embeddings.
3. Importar en una colección nueva del destino usando IDs deterministas.
4. Comparar el número de vectores y realizar una consulta de humo por sesión.
5. Cambiar `CHROMA_PATH` o el adaptador y conservar el volumen anterior hasta
   completar la validación.

El export se ejecuta con:

```bash
poetry run python -m server.scripts.export_chroma backup/chroma.json
```

En producción con varias réplicas se recomienda sustituir el almacenamiento
local por un servicio vectorial administrado y mantener `session_id`,
`document_id`, `checksum` y `expires_at` como metadatos obligatorios.
