from abc import ABC, abstractmethod
from typing import List
from core.entities import Series


class IAProvider(ABC):
    @abstractmethod
    def generate_insight(
        self, summary: str, genres: List[str], comments: List[str]
    ) -> str:
        pass


class TVMazeClient(ABC):
    @abstractmethod
    def search_series(self, query: str) -> List[Series]:
        pass

    @abstractmethod
    def get_series_details(self, series_id: int) -> Series:
        pass


class PersistenceRepository(ABC):
    @abstractmethod
    def mark_as_watched(self, episode_id: int) -> None:
        pass
