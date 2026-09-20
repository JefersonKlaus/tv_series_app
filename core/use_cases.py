import logging

from core.entities import Series
from core.interfaces import IAProvider, TVMazeClient

logger = logging.getLogger(__name__)


class SearchSeriesUseCase:
    """Searches TV series through the injected provider."""

    def __init__(self, series_provider: TVMazeClient):
        self.series_provider = series_provider

    def execute(self, query: str) -> list[Series]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        return self.series_provider.search_series(normalized_query)


class GenerateInsightUseCase:
    def __init__(self, ai_provider: IAProvider):
        self.ai_provider = ai_provider

    def execute(self, summary: str, genres: list[str], comments: list[str]) -> str:
        if not summary:
            return "Resumo não disponível para gerar insights."

        try:
            return self.ai_provider.generate_insight(summary, genres, comments)
        except Exception as e:
            logger.error(f"Erro na API de IA: {e}")
            return "Insight indisponível no momento. Nossa IA está descansando, mas este episódio promete focar em temas centrais da série!"
