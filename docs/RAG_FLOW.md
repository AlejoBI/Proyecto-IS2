# Flujo RAG

## Indexación

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as React
    participant API as FastAPI
    participant DB as MongoDB
    participant LLM as OpenAI/Gemini
    participant V as ChromaDB
    U->>UI: Selecciona proveedor y archivo
    UI->>API: POST /save-document + BYOK
    API->>API: Valida extensión, tamaño y checksum
    API->>API: Extrae texto y divide en chunks
    API->>LLM: Solicita embeddings
    LLM-->>API: Vectores
    API->>V: Guarda chunks y metadatos
    API->>DB: Guarda documento y estado
    API-->>UI: Documento completado
```

## Consulta

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as React
    participant API as FastAPI
    participant V as ChromaDB
    participant LLM as OpenAI/Gemini
    participant DB as MongoDB
    U->>UI: Escribe una pregunta
    UI->>API: GET /generate-answer + proveedor
    API->>LLM: Embedding de la pregunta
    LLM-->>API: Vector de consulta
    API->>V: Busca por sesión y proveedor
    V-->>API: Fragmentos relevantes
    API->>LLM: Pregunta + contexto recuperado
    LLM-->>API: Respuesta
    API->>DB: Guarda historial si está autenticado
    API-->>UI: Respuesta + fuentes + X-Request-ID
```

## Reindexación

Si el documento está `completed` pero no tiene índice para el proveedor actual,
la interfaz muestra `Index for Gemini` o `Index for OpenAI`. `POST
/session/documents/{document_id}/index` reutiliza el contenido guardado, genera
los embeddings del proveedor seleccionado y actualiza `indexed_providers`.

## Aislamiento

La recuperación nunca cruza sesiones ni proveedores. Un documento puede tener,
por ejemplo, `indexed_providers: ["openai", "gemini"]`, pero cada índice vive
en su colección vectorial correspondiente.
