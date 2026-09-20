import logging
from typing import Any, Optional

import requests

from core.entities import Episode, Series
from core.interfaces import TVMazeClient as TVMazeClientInterface

logger = logging.getLogger(__name__)


class TVMazeClient(TVMazeClientInterface):
    """HTTP adapter for the public TVMaze API."""

    BASE_URL = "http://api.tvmaze.com"
    TIMEOUT = 10

    def __init__(self, http_client: Optional[requests.Session] = None) -> None:
        self.http_client = http_client or requests.Session()

    def search_series(self, query: str) -> list[Series]:
        """Return matching series with title, year, poster, and basic metadata."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        data = self._get_json("/search/shows", params={"q": normalized_query})
        return [
            self._series_from_payload(item.get("show", {}))
            for item in data
            if item.get("show")
        ]

    def get_series_details(self, series_id: int) -> Optional[Series]:
        """Return a series and its episodes grouped by season by the caller."""
        series_data = self._get_json(f"/shows/{series_id}")
        episodes_data = self._get_json(f"/shows/{series_id}/episodes")

        if not series_data:
            return None

        series = self._series_from_payload(series_data)
        series.episodes = [
            self._episode_from_payload(episode)
            for episode in episodes_data
            if episode.get("id") is not None
        ]
        return series

    def _get_json(self, path: str, params: Optional[dict[str, str]] = None) -> Any:
        try:
            response = self.http_client.get(
                f"{self.BASE_URL}{path}",
                params=params,
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            logger.warning("TVMaze request failed for %s: %s", path, error)
            return []

    @staticmethod
    def _series_from_payload(payload: dict[str, Any]) -> Series:
        premiered = payload.get("premiered") or ""
        return Series(
            id=payload.get("id", 0),
            name=payload.get("name", "Untitled"),
            genres=payload.get("genres") or [],
            poster_url=(payload.get("image") or {}).get("medium"),
            summary=payload.get("summary"),
            premiered_year=int(premiered[:4]) if premiered[:4].isdigit() else None,
        )

    @staticmethod
    def _episode_from_payload(payload: dict[str, Any]) -> Episode:
        return Episode(
            id=payload["id"],
            name=payload.get("name", "Untitled"),
            season=payload.get("season", 0),
            number=payload.get("number", 0),
            summary=payload.get("summary"),
        )
