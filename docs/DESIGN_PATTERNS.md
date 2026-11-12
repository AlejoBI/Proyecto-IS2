# Patrones de diseño

## Ports and Adapters (arquitectura hexagonal)

Las interfaces de `server/core/ports.py` separan los casos de uso de MongoDB,
ChromaDB y los proveedores LLM. Los adaptadores concretos pueden probarse o
reemplazarse sin cambiar el flujo de aplicación.

## Repository

`MongoDBAdapter` y `ChromaDBAdapter` encapsulan persistencia, consultas y
borrado. El servicio no construye consultas de infraestructura directamente
para las operaciones normales.

## Service Layer / Use Cases

`RAGService` coordina indexación, recuperación, generación e historial.
`AuthService`, `AdminService` y los servicios de sesión mantienen separadas las
reglas de sus respectivos contextos.

## Strategy

`FileReader` selecciona el lector adecuado para PDF, DOCX o TXT. Cada lector
implementa la misma operación de lectura y limpieza de contenido.

## Adapter

`OpenAIAdapter` ofrece una interfaz común para OpenAI y Gemini. El proveedor y
el modelo cambian por solicitud, pero el caso de uso recibe el mismo puerto.

## Dependency Injection

FastAPI inyecta sesiones, usuarios, servicios y autorización mediante
`Depends`. Esto centraliza la construcción y facilita las pruebas.

## DTO y estado tipado

Pydantic valida entradas y salidas. `DocumentStatus` representa explícitamente
el ciclo de procesamiento en lugar de depender de strings arbitrarios.

## Decisiones no adoptadas

El sistema no usa microservicios, agentes autónomos, MCP, n8n ni una malla de
servicios. La modularidad está dentro de un único backend para mantener simple
el despliegue y hacer explícitos los límites del proyecto.
