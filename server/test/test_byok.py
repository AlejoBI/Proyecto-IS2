from types import SimpleNamespace

import openai
import pytest

from server.adapters import openai_adapter
from server.adapters.openai_adapter import OpenAIAdapter, ProviderError


class FakeOpenAIClient:
    def __init__(self, **kwargs):
        self.received_key = kwargs["api_key"]
        self.embeddings = SimpleNamespace(create=lambda **_: SimpleNamespace(
            data=[SimpleNamespace(embedding=[0.1, 0.2])]
        ))
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **_: SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))]
        )))


def test_byok_adapter_uses_the_request_key(monkeypatch):
    client = None

    def create_client(**kwargs):
        nonlocal client
        client = FakeOpenAIClient(**kwargs)
        return client

    monkeypatch.setattr(openai, "OpenAI", create_client)
    adapter = OpenAIAdapter("user-key", "model", "embedding", 100, 0.2)

    assert adapter.get_embedding("text") == [0.1, 0.2]
    assert adapter.generate_text("question", "context") == "answer"
    assert client.received_key == "user-key"


def test_gemini_adapter_uses_its_compatibility_base_url(monkeypatch):
    captured = {}

    def create_client(**kwargs):
        captured.update(kwargs)
        return FakeOpenAIClient(**kwargs)

    monkeypatch.setattr(openai, "OpenAI", create_client)
    adapter = OpenAIAdapter(
        "gemini-key", "gemini-model", "gemini-embedding", 100, 0.2,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        provider="gemini",
    )

    assert captured["api_key"] == "gemini-key"
    assert captured["base_url"] == "https://generativelanguage.googleapis.com/v1beta/openai/"

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"embedding":{"values":[0.3,0.4]}}'

    monkeypatch.setattr(openai_adapter, "urlopen", lambda *_args, **_kwargs: FakeResponse())
    assert adapter.get_embedding("text") == [0.3, 0.4]


def test_gemini_adapter_rejects_empty_embedding(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"embedding":{"values":[]}}'

    monkeypatch.setattr(openai_adapter, "urlopen", lambda *_args, **_kwargs: FakeResponse())
    adapter = OpenAIAdapter(
        "gemini-key", "gemini-model", "gemini-embedding", 100, 0.2,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        provider="gemini",
    )

    with pytest.raises(ProviderError, match="empty or invalid embedding"):
        adapter.get_embedding("text")


def test_gemini_adapter_generates_with_native_endpoint(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"candidates":[{"content":{"parts":[{"text":"answer"}]}}]}'

    monkeypatch.setattr(openai_adapter, "urlopen", lambda *_args, **_kwargs: FakeResponse())
    adapter = OpenAIAdapter(
        "gemini-key", "gemini-3.8-flash", "gemini-embedding-001", 100, 0.2,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        provider="gemini",
    )

    assert adapter.generate_text("question", "context") == "answer"


def test_openai_quota_error_is_actionable():
    adapter = OpenAIAdapter("openai-key", "model", "embedding", 100, 0.2)
    error = SimpleNamespace(
        status_code=429,
        body={"code": "insufficient_quota"},
    )

    provider_error = adapter._openai_provider_error("generation", error)

    assert provider_error.status_code == 429
    assert "no remaining credits" in str(provider_error)
    assert "switch to Gemini" in str(provider_error)
