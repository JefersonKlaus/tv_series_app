from abc import ABC, abstractmethod
from typing import List

from core.entities import Series


class IAProvider(ABC):
    @abstractmethod
    async def generate_insight(
        self, summary: str, genres: List[str], comments: List[str]
    ) -> str:
        pass


class TVMazeClient(ABC):
    @abstractmethod
    async def search_series(self, query: str) -> List[Series]:
        pass

    @abstractmethod
    async def get_series_details(self, series_id: int) -> Series | None:
        pass


class PersistenceRepository(ABC):
    @abstractmethod
    def sync_series(self, series: Series) -> Series:
        pass

    @abstractmethod
    def list_with_state(self, series_list: List[Series]) -> List[Series]:
        pass

    @abstractmethod
    def mark_episode_as_watched(
        self, series_external_id: int, episode_external_id: int, watched: bool
    ) -> None:
        pass

    @abstractmethod
    def mark_series_as_watched(self, series_external_id: int, watched: bool) -> None:
        pass

    @abstractmethod
    def save_series_comment(self, series_external_id: int, comment: str) -> None:
        pass

    @abstractmethod
    def save_episode_comment(self, episode_external_id: int, comment: str) -> None:
        pass
