from adapters.openai_adapter import OpenAIAdapter
from adapters.chromadb_adapter import ChromaDBAdapter
from adapters.firebase_adapter import FirebaseUserAdapter
from app import usecases
from app import configurations

class RAGServiceSingleton:
    _instance = None

    @classmethod
    def get_instance(cls) -> usecases.RAGService:
        if cls._instance is None:
            configs = configurations.Settings()
            openai_adapter = OpenAIAdapter(api_key=configs.OPENAI_API_KEY, model=configs.MODEL,
                                           max_tokens=configs.MAX_TOKENS, temperature=configs.TEMPERATURE)
            document_repo = ChromaDBAdapter(number_of_vectorial_results=configs.NUMBER_OF_VECTORIAL_RESULTS, uri=configs.CHROMADB_URI)
            user_repo = FirebaseUserAdapter(configs.FIREBASE_URI)
            cls._instance = usecases.RAGService(document_repo=document_repo, user_repo=user_repo, openai_adapter=openai_adapter)
        return cls._instance