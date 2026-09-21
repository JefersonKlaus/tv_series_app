import streamlit as st

from adapters.repository import PostgresRepository
from adapters.tvmaze_client import TVMazeClient
from core.use_cases import (
    GetSeriesDetailsUseCase,
    MarkEpisodeWatchedUseCase,
    MarkSeriesWatchedUseCase,
    SaveEpisodeCommentUseCase,
    SaveSeriesCommentUseCase,
    SearchSeriesUseCase,
)


class Dependencies:
    def __init__(
        self,
        search_series,
        get_series_details,
        mark_episode_watched,
        mark_series_watched,
        save_series_comment,
        save_episode_comment,
    ):
        self.search_series = search_series
        self.get_series_details = get_series_details
        self.mark_episode_watched = mark_episode_watched
        self.mark_series_watched = mark_series_watched
        self.save_series_comment = save_series_comment
        self.save_episode_comment = save_episode_comment


@st.cache_resource
def get_dependencies() -> Dependencies:
    tvmaze_client = TVMazeClient()
    repository = PostgresRepository()

    return Dependencies(
        search_series=SearchSeriesUseCase(
            tvmaze_client,
            repository,
        ),
        get_series_details=GetSeriesDetailsUseCase(
            tvmaze_client,
            repository,
        ),
        mark_episode_watched=MarkEpisodeWatchedUseCase(
            repository,
        ),
        mark_series_watched=MarkSeriesWatchedUseCase(
            repository,
        ),
        save_series_comment=SaveSeriesCommentUseCase(
            repository,
        ),
        save_episode_comment=SaveEpisodeCommentUseCase(
            repository,
        ),
    )
