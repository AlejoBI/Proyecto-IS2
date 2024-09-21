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
            configs = configurations.Configs()
            openai_adapter = OpenAIAdapter(api_key=configs.openai_api_key, model=configs.model,
                                           max_tokens=configs.max_tokens, temperature=configs.temperature)
            document_repo = ChromaDBAdapter(number_of_vectorial_results=configs.number_of_vectorial_results)
            user_repo = FirebaseUserAdapter(configs.firebase_uri)
            cls._instance = usecases.RAGService(document_repo=document_repo, openai_adapter=openai_adapter, user_repo=user_repo)
        return cls._instance