import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import openai
from server.core import ports


logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Error seguro y específico de un proveedor de modelos."""


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
        self._timeout = timeout
        self._base_url = base_url
        self._api_key = api_key

    def get_embedding(self, text: str) -> list[float]:
        if not text.strip():
            raise ProviderError(f"{self.provider.capitalize()} cannot embed empty text")

        if self.provider == "gemini":
            return self._get_gemini_embedding(text)

        response = self._openai_client.embeddings.create(
            input=text,
            model=self._embedding_model,
        )
        embedding = response.data[0].embedding
        self._validate_embedding(embedding)
        return embedding

    def _get_gemini_embedding(self, text: str) -> list[float]:
        base_url = (self._base_url or
                    "https://generativelanguage.googleapis.com/v1beta/openai/")
        native_base_url = base_url.removesuffix("openai/").removesuffix("openai")
        endpoint = (f"{native_base_url}models/{quote(self._embedding_model, safe='')}:"
                    f"embedContent?key={quote(self._api_key, safe='')}")
        payload = {
            "model": f"models/{self._embedding_model}",
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT",
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            logger.warning("Gemini embedding request failed status=%s", error.code)
            raise ProviderError("Gemini embedding request failed") from None
        except (URLError, TimeoutError, json.JSONDecodeError):
            logger.warning("Gemini embedding request could not be completed")
            raise ProviderError("Gemini embedding request failed") from None

        embedding = body.get("embedding", {}).get("values", [])
        self._validate_embedding(embedding)
        return embedding

    def _validate_embedding(self, embedding: object) -> None:
        if not isinstance(embedding, list) or not embedding or not all(
            isinstance(value, (int, float)) for value in embedding
        ):
            raise ProviderError(
                f"{self.provider.capitalize()} returned an empty or invalid embedding"
            )

    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        logger.info("llm.generation.started provider=%s model=%s", self.provider, self._model)
        try:
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
        except Exception as error:
            logger.warning(
                "llm.generation.failed provider=%s model=%s error_type=%s status_code=%s",
                self.provider,
                self._model,
                type(error).__name__,
                getattr(error, "status_code", None),
            )
            raise
        logger.info("llm.generation.completed provider=%s model=%s", self.provider, self._model)
        return response.choices[0].message.content
