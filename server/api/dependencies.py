from server.adapters.openai_adapter import OpenAIAdapter
from server.adapters.chromadb_adapter import ChromaDBAdapter
from server.adapters.mongodb_adapter import MongoDBAdapter
from server.app import usecases, configurations


class RAGServiceSingleton:
    _instance = None

    @classmethod
    def get_instance(cls) -> usecases.RAGService:
        if cls._instance is None:
            configs = configurations.Settings()
            openai_adapter = OpenAIAdapter(api_key=configs.OPENAI_API_KEY, model=configs.MODEL,
                                           max_tokens=configs.MAX_TOKENS, temperature=configs.TEMPERATURE)
            document_repo = ChromaDBAdapter(number_of_vectorial_results=configs.NUMBER_OF_VECTORIAL_RESULTS)
            mongo_repo = MongoDBAdapter(uri=configs.MONGODB_URI, database=configs.MONGODB_DATABASE, users_collection=configs.MONGODB_COLLECTION_USERS,
                                        documents_collection=configs.MONGODB_COLLECTION_DOCUMENTS)
            cls._instance = usecases.RAGService(document_repo=document_repo, mongo_repo=mongo_repo, openai_adapter=openai_adapter)
        return cls._instance