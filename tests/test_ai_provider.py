import asyncio

import httpx
import pytest

from adapters.ai_provider import HuggingFaceProvider


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    @property
    def is_error(self):
        return self.status_code >= 400

    @property
    def text(self):
        return str(self.payload)

    def raise_for_status(self):
        if self.is_error:
            raise httpx.HTTPStatusError(
                "HTTP error",
                request=httpx.Request(
                    "POST",
                    "https://router.huggingface.co/v1/chat/completions",
                ),
                response=httpx.Response(
                    self.status_code,
                    request=httpx.Request(
                        "POST",
                        "https://router.huggingface.co/v1/chat/completions",
                    ),
                ),
            )

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    async def post(
        self,
        url,
        headers=None,
        json=None,
        timeout=None,
    ):
        self.requests.append((url, headers, json, timeout))

        return self.response


class FailingHttpClient:
    async def post(
        self,
        url,
        headers=None,
        json=None,
        timeout=None,
    ):
        raise httpx.HTTPError("Hugging Face indisponível")


def test_provider_generates_insight_from_content_and_comments(
    monkeypatch,
):
    monkeypatch.setenv(
        "HF_TOKEN",
        "fake-token",
    )

    client = FakeHttpClient(
        FakeResponse(
            {
                "id": "test-id",
                "object": "chat.completion",
                "model": "openai/gpt-oss-20b",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Insight gerado.",
                        },
                    }
                ],
            }
        )
    )

    provider = HuggingFaceProvider(client)

    result = asyncio.run(
        provider.generate_insight(
            "Resumo do episódio",
            ["Drama", "Crime"],
            ["Excelente episódio"],
        )
    )

    assert result == "Insight gerado."

    url, headers, payload, timeout = client.requests[0]

    assert url == "https://router.huggingface.co/v1/chat/completions"

    assert headers["Authorization"] == "Bearer fake-token"

    assert payload["model"] == "openai/gpt-oss-20b"

    assert payload["stream"] is False

    assert payload["max_tokens"] == 150

    messages = payload["messages"]

    user_message = next(message for message in messages if message["role"] == "user")

    prompt = user_message["content"]

    assert "Resumo do episódio" in prompt
    assert "Drama, Crime" in prompt
    assert "Excelente episódio" in prompt


def test_provider_propagates_http_failure_to_use_case_boundary(
    monkeypatch,
):
    monkeypatch.setenv(
        "HF_TOKEN",
        "fake-token",
    )

    provider = HuggingFaceProvider(FailingHttpClient())

    with pytest.raises(httpx.HTTPError):
        asyncio.run(
            provider.generate_insight(
                "Resumo",
                [],
                [],
            )
        )


def test_provider_raises_when_token_is_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "HF_TOKEN",
        raising=False,
    )

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [],
            }
        )
    )

    provider = HuggingFaceProvider(client)

    with pytest.raises(
        RuntimeError,
        match="HF_TOKEN environment variable is not set",
    ):
        asyncio.run(
            provider.generate_insight(
                "Resumo",
                [],
                [],
            )
        )


def test_provider_extracts_reasoning_content_as_fallback(
    monkeypatch,
):
    monkeypatch.setenv(
        "HF_TOKEN",
        "fake-token",
    )

    client = FakeHttpClient(
        FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "reasoning_content": ("Insight alternativo."),
                        }
                    }
                ]
            }
        )
    )

    provider = HuggingFaceProvider(client)

    result = asyncio.run(
        provider.generate_insight(
            "Resumo",
            [],
            [],
        )
    )

    assert result == "Insight alternativo."
