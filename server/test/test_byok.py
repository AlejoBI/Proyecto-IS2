from types import SimpleNamespace

import openai

from server.adapters.openai_adapter import OpenAIAdapter


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
    OpenAIAdapter(
        "gemini-key", "gemini-model", "gemini-embedding", 100, 0.2,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        provider="gemini",
    )

    assert captured["api_key"] == "gemini-key"
    assert captured["base_url"] == "https://generativelanguage.googleapis.com/v1beta/openai/"
