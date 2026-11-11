import openai
from server.core import ports


class OpenAIAdapter(ports.LlmPort):
    def __init__(self, api_key: str, model: str, embedding_model: str,
                 max_tokens: int, temperature: float,
                 timeout: float = 30.0, max_retries: int = 2,
                 base_url: str | None = None, provider: str = "openai") -> None:
        self._openai_client = openai.OpenAI(api_key=api_key, timeout=timeout,
                                            max_retries=max_retries, base_url=base_url)
        self._model = model
        self._embedding_model = embedding_model
        self._max_tokens = max_tokens
        self._temperature = temperature
        self.provider = provider

    def get_embedding(self, text: str) -> list[float]:
        response = self._openai_client.embeddings.create(
            input=text,
            model=self._embedding_model,
        )
        return response.data[0].embedding

    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        response = self._openai_client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system",
                 "content": f"The context is: {retrieval_context}, please respond to the following question: "},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        return response.choices[0].message.content
