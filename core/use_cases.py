import logging
import asyncio

from core.entities import Series
from core.interfaces import IAProvider, PersistenceRepository, TVMazeClient

logger = logging.getLogger(__name__)


class SearchSeriesUseCase:
    """Searches TV series through the injected provider."""

    def __init__(
        self,
        series_provider: TVMazeClient,
        persistence: PersistenceRepository | None = None,
    ):
        self.series_provider = series_provider
        self.persistence = persistence

    async def execute(self, query: str) -> list[Series]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        series_list = await self.series_provider.search_series(normalized_query)
        if self.persistence:
            return await asyncio.to_thread(
                self.persistence.list_with_state, series_list
            )
        return series_list


class GetSeriesDetailsUseCase:
    """Loads the selected series details through the injected provider."""

    def __init__(
        self,
        series_provider: TVMazeClient,
        persistence: PersistenceRepository | None = None,
    ):
        self.series_provider = series_provider
        self.persistence = persistence

    async def execute(self, series_id: int) -> Series | None:
        series = await self.series_provider.get_series_details(series_id)
        if series and self.persistence:
            return await asyncio.to_thread(self.persistence.sync_series, series)
        return series


class MarkEpisodeWatchedUseCase:
    def __init__(self, persistence: PersistenceRepository):
        self.persistence = persistence

    async def execute(self, series_id: int, episode_id: int, watched: bool) -> None:
        await asyncio.to_thread(
            self.persistence.mark_episode_as_watched,
            series_id,
            episode_id,
            watched,
        )


class MarkSeriesWatchedUseCase:
    def __init__(self, persistence: PersistenceRepository):
        self.persistence = persistence

    async def execute(self, series_id: int, watched: bool) -> None:
        await asyncio.to_thread(
            self.persistence.mark_series_as_watched, series_id, watched
        )


class SaveSeriesCommentUseCase:
    def __init__(self, persistence: PersistenceRepository):
        self.persistence = persistence

    async def execute(self, series_id: int, comment: str) -> None:
        await asyncio.to_thread(
            self.persistence.save_series_comment, series_id, comment
        )


class SaveEpisodeCommentUseCase:
    def __init__(self, persistence: PersistenceRepository):
        self.persistence = persistence

    async def execute(self, episode_id: int, comment: str) -> None:
        await asyncio.to_thread(
            self.persistence.save_episode_comment, episode_id, comment
        )


class GenerateInsightUseCase:
    def __init__(self, ai_provider: IAProvider):
        self.ai_provider = ai_provider

    async def execute(
        self, summary: str, genres: list[str], comments: list[str] | None = None
    ) -> str:
        if not summary:
            return "Resumo não disponível para gerar insights."

        try:
            return await self.ai_provider.generate_insight(
                summary, genres, comments or []
            )
        except Exception as e:
            logger.error(f"Erro na API de IA: {e}")
            return "Insight indisponível no momento. Tente novamente mais tarde."
