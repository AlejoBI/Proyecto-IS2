# Evaluación del RAG

La evaluación automática contra proveedores reales no se ejecuta en CI para no
consumir créditos ni exponer credenciales. El flujo de CI usa adaptadores
simulados para comprobar:

- que la API key del usuario se inyecta por solicitud;
- que la búsqueda recibe el `session_id` correcto;
- que la respuesta incluye fuentes;
- que los errores del proveedor no se exponen al cliente.
- que OpenAI y Gemini mantienen índices vectoriales separados.
- que un documento puede reindexarse sin volver a cargar el archivo.

## Evaluación manual con una clave propia

1. Iniciar el backend y frontend.
2. Crear una sesión desde la pantalla pública.
3. Subir un TXT, PDF o DOCX con hechos conocidos.
4. Hacer preguntas cuya respuesta esté y no esté en el documento.
5. Verificar que las fuentes correspondan al documento cargado.
6. Repetir con una segunda sesión y confirmar que no recupera los vectores de
   la primera.

## Métricas recomendadas para una futura evaluación formal

- Recall@k de fragmentos relevantes.
- Precisión de las fuentes citadas.
- Exactitud de la respuesta contra respuestas de referencia.
- Latencia de embeddings y generación.
- Tasa de errores del proveedor.
- Costo promedio por documento y pregunta.
