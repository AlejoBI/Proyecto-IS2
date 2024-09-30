import chromadb
import numpy as np
from typing import List
from server.core import ports
from server.core import models
from server.helpers.vectorize_document import document_to_vectors, get_openai_embeddings

class ChromaDBAdapter(ports.DocumentRepositoryPort):
    def __init__(self, number_of_vectorial_results: int) -> None:
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("documents")
        self._number_of_vectorial_results = number_of_vectorial_results

    # Guardar un documento con embeddings generados por OpenAI
    async def save_document(self, document: models.Document, content: str, openai_client) -> None:
        embeddings_document = await document_to_vectors(content, openai_client)

        # Si hay más de un embedding, combinarlo promediando
        if len(embeddings_document) > 1:
            combined_embedding = np.mean(embeddings_document, axis=0).tolist()
        else:
            combined_embedding = embeddings_document[0]

        # Agregar el documento a ChromaDB con su embedding
        self.collection.add(
            ids=[document.document_id],
            embeddings=[combined_embedding],  # Aseguramos que sea una lista de embeddings
            documents=[content]
        )

    # Obtener documentos usando embeddings generados para la query
    def get_documents(self, query: str, openai_client, n_results: int | None = None) -> List[models.Document]:
        if not n_results:
            n_results = self._number_of_vectorial_results

        # Generar embedding para la query usando OpenAI
        query_embedding = get_openai_embeddings(query, openai_client)

        # Hacer la consulta usando los embeddings de la query
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)

        # Procesar los resultados y devolver documentos
        documents = []
        for i, doc_id_list in enumerate(results['ids']):
            for doc_id in doc_id_list:
                documents.append(models.Document(id=doc_id, content=results['documents'][i][0]))
        return documents

    # Obtener vectores almacenados en la colección
    def get_vectors(self):
        return self.collection.get(include=['embeddings', 'documents', 'metadatas'])