import json
import logging
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import openai
from server.core import ports


logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Error seguro y específico de un proveedor de modelos."""

    def __init__(self, message: str, status_code: int | None = None,
                 request_id: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id


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
        self._request_id = "-"

    def get_embedding(self, text: str) -> list[float]:
        if not text.strip():
            raise ProviderError(f"{self.provider.capitalize()} cannot embed empty text")

        if self.provider == "gemini":
            return self._get_gemini_embedding(text)

        try:
            response = self._openai_client.embeddings.create(
                input=text,
                model=self._embedding_model,
            )
        except Exception as error:
            raise self._openai_provider_error("embedding", error) from None
        embedding = response.data[0].embedding
        self._validate_embedding(embedding)
        return embedding

    def _get_gemini_embedding(self, text: str) -> list[float]:
        endpoint = self._gemini_endpoint(self._embedding_model, "embedContent")
        payload = {
            "model": f"models/{self._embedding_model}",
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT",
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._gemini_headers(),
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            logger.warning("Gemini embedding request failed status=%s", error.code)
            detail = self._read_upstream_error(error)
            logger.warning(
                "Gemini embedding upstream_error request_id=%s status=%s detail=%s",
                self._request_id,
                error.code,
                detail,
            )
            raise ProviderError(
                self._gemini_http_error("embedding", error.code),
                error.code,
                self._request_id,
            ) from None
        except (URLError, TimeoutError, json.JSONDecodeError):
            logger.warning("Gemini embedding request could not be completed")
            raise ProviderError("Gemini embedding request failed") from None

        embedding = body.get("embedding", {}).get("values", [])
        self._validate_embedding(embedding)
        return embedding

    def _gemini_endpoint(self, model: str, action: str) -> str:
        base_url = (self._base_url or
                    "https://generativelanguage.googleapis.com/v1beta/openai/")
        native_base_url = base_url.removesuffix("openai/").removesuffix("openai")
        return (f"{native_base_url}models/{quote(model, safe='')}:{action}"
                f"?key={quote(self._api_key, safe='')}")

    @staticmethod
    def _gemini_http_error(operation: str, status_code: int) -> str:
        if status_code in {401, 403}:
            return f"Gemini rejected the API key during {operation}"
        if status_code == 404:
            return f"Gemini model was not found during {operation}"
        if status_code == 429:
            return "Gemini rate limit reached. Try again shortly"
        if status_code >= 500:
            return "Gemini is temporarily unavailable. Try again shortly"
        return f"Gemini {operation} request failed"

    def _validate_embedding(self, embedding: object) -> None:
        if not isinstance(embedding, list) or not embedding or not all(
            isinstance(value, (int, float)) for value in embedding
        ):
            raise ProviderError(
                f"{self.provider.capitalize()} returned an empty or invalid embedding"
            )

    def generate_text(self, prompt: str, retrieval_context: str) -> str:
        logger.info("llm.generation.started provider=%s model=%s", self.provider, self._model)
        if self.provider == "gemini":
            return self._generate_gemini_text(prompt, retrieval_context)

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
            raise self._openai_provider_error("generation", error) from None
        logger.info("llm.generation.completed provider=%s model=%s", self.provider, self._model)
        return response.choices[0].message.content

    def _openai_provider_error(self, operation: str, error: Exception) -> ProviderError:
        status_code = getattr(error, "status_code", None)
        body = getattr(error, "body", None)
        error_code = body.get("code") if isinstance(body, dict) else None
        raw_error = str(error).lower()

        if status_code == 429 and (
            error_code in {"insufficient_quota", "credit_balance_exhausted"}
            or "insufficient_quota" in raw_error
            or "credit_balance_exhausted" in raw_error
        ):
            return ProviderError(
                "OpenAI has no remaining credits. Add credits at "
                "https://platform.openai.com/settings/organization/billing/ "
                "or switch to Gemini.",
                429,
            )
        if status_code == 429:
            return ProviderError("OpenAI rate limit reached. Try again shortly.", 429)
        if status_code in {401, 403}:
            return ProviderError("OpenAI rejected the API key. Verify it and try again.", status_code)
        if status_code and status_code >= 500:
            return ProviderError("OpenAI is temporarily unavailable. Try again shortly.", status_code)
        return ProviderError(f"OpenAI {operation} request failed. Verify your key and try again.", status_code)

    def _generate_gemini_text(self, prompt: str, retrieval_context: str) -> str:
        endpoint = self._gemini_endpoint(self._model, "generateContent")
        payload = {
            "systemInstruction": {
                "parts": [{
                    "text": "Answer using the following retrieved context. "
                    f"If the answer is not present, say so clearly.\n\nContext:\n{retrieval_context}"
                }]
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": self._max_tokens,
                "temperature": self._temperature,
            },
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._gemini_headers(),
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            logger.warning(
                "Gemini generation request failed status=%s model=%s",
                error.code,
                self._model,
            )
            detail = self._read_upstream_error(error)
            logger.warning(
                "Gemini generation upstream_error request_id=%s status=%s detail=%s",
                self._request_id,
                error.code,
                detail,
            )
            raise ProviderError(
                self._gemini_http_error("generation", error.code),
                error.code,
                self._request_id,
            ) from None
        except (URLError, TimeoutError, json.JSONDecodeError):
            logger.warning("Gemini generation request could not be completed model=%s", self._model)
            raise ProviderError("Gemini generation request failed") from None

        try:
            text = "".join(
                part.get("text", "")
                for candidate in body.get("candidates", [])
                for part in candidate.get("content", {}).get("parts", [])
            ).strip()
        except AttributeError:
            text = ""
        if not text:
            logger.warning(
                "Gemini generation empty_response request_id=%s model=%s candidates=%d",
                self._request_id,
                self._model,
                len(body.get("candidates", [])) if isinstance(body, dict) else 0,
            )
            raise ProviderError("Gemini returned an empty generation", request_id=self._request_id)
        logger.info(
            "llm.generation.completed provider=%s model=%s request_id=%s",
            self.provider,
            self._model,
            self._request_id,
        )
        return text

    def _gemini_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Client-Request-ID": self._request_id,
        }

    def _read_upstream_error(self, error: HTTPError) -> str:
        try:
            raw_body = error.read().decode("utf-8", errors="replace")
            body = json.loads(raw_body)
            message = body.get("error", {}).get("message", "")
            if not message:
                message = body.get("message", "")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            message = ""
        if not message:
            message = str(error.reason or "No upstream detail")
        return re.sub(r"(AIza|sk-)[A-Za-z0-9_-]+", "[REDACTED]", message)[:300]
