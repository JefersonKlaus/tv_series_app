import logging
import os
from contextlib import asynccontextmanager

import httpx

from core.interfaces import IAProvider


logger = logging.getLogger(__name__)


class HuggingFaceProvider(IAProvider):
    """Adapter for generating short insights through Hugging Face."""

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    MODEL = "openai/gpt-oss-20b"
    TIMEOUT = 30

    def __init__(
        self,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.http_client = http_client

    async def generate_insight(
        self,
        summary: str,
        genres: list[str],
        comments: list[str],
    ) -> str:
        prompt = self._build_prompt(
            summary=summary,
            genres=genres,
            comments=comments,
        )

        async with self._client_context() as client:
            response = await client.post(
                self.API_URL,
                headers=self._headers(),
                json={
                    "model": self.MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You generate short TV series insights in Portuguese."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "max_tokens": 150,
                    "temperature": 0.3,
                    "stream": False,
                },
                timeout=self.TIMEOUT,
            )

            if response.is_error:
                logger.error(
                    "Hugging Face error [%s]: %s",
                    response.status_code,
                    response.text,
                )

                response.raise_for_status()

            payload = response.json()

        logger.info(
            "Hugging Face response - model=%s choices=%s",
            payload.get("model"),
            len(payload.get("choices", [])),
        )

        return self._extract_content(payload)

    @staticmethod
    def _build_prompt(
        summary: str,
        genres: list[str],
        comments: list[str],
    ) -> str:
        comment_text = (
            "; ".join(
                comment.strip() for comment in comments if comment and comment.strip()
            )
            or "None"
        )

        return (
            "Write exactly one short insight sentence in Portuguese "
            "about this TV series.\n"
            "Do not add a preamble.\n"
            "Do not use bullet points.\n"
            "Do not mention that you are an AI.\n"
            "Return only the insight sentence.\n\n"
            f"Summary: {summary or 'None'}\n"
            f"Genres: {', '.join(genres) or 'None'}\n"
            f"User comments: {comment_text}"
        )

    @staticmethod
    def _headers() -> dict[str, str]:
        token = os.getenv("HF_TOKEN")

        if not token:
            raise RuntimeError("HF_TOKEN environment variable is not set")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _extract_content(payload: dict) -> str:
        """
        Extract generated text from the Hugging Face response.
        """

        logger.info(
            "Hugging Face raw response: %s",
            payload,
        )

        try:
            choices = payload.get("choices")

            if not choices:
                raise ValueError("Hugging Face returned no choices")

            message = choices[0].get("message", {})

            logger.info(
                "Hugging Face message: %s",
                message,
            )

            content = message.get("content")

            if isinstance(content, str) and content.strip():
                return content.strip()

            reasoning_content = message.get("reasoning_content")

            if isinstance(reasoning_content, str) and reasoning_content.strip():
                logger.warning("Hugging Face returned reasoning_content but no content")

                return reasoning_content.strip()

        except (IndexError, TypeError, AttributeError) as exc:
            logger.exception("Unexpected Hugging Face response structure")

            raise ValueError("Unexpected Hugging Face response") from exc

        logger.error(
            "Hugging Face returned no usable content: %s",
            payload,
        )

        raise ValueError("Hugging Face returned no insight")

    @asynccontextmanager
    async def _client_context(self):
        """
        Use the injected HTTP client when available.
        Otherwise create and close one locally.
        """

        if self.http_client is not None:
            yield self.http_client
            return

        async with httpx.AsyncClient() as client:
            yield client
