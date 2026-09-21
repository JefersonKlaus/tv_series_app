import os

from adapters.model import Base, EpisodeModel, SeriesModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.entities import Episode, Series
from core.interfaces import PersistenceRepository


class PostgresRepository(PersistenceRepository):
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable is required")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def sync_series(self, series: Series) -> Series:
        with self.Session() as session:
            model = self._get_or_create_series(session, series)
            for episode in series.episodes:
                self._get_or_create_episode(session, model, episode)
            self._update_series_status(model)
            session.commit()
            series.comment = model.comment
            series.status = model.status
            state_by_id = {episode.external_id: episode for episode in model.episodes}
            for episode in series.episodes:
                state = state_by_id.get(episode.id)
                if state:
                    episode.watched = state.watched
                    episode.comment = state.comment
            return series

    def list_with_state(self, series_list: list[Series]) -> list[Series]:
        with self.Session() as session:
            for series in series_list:
                model = (
                    session.query(SeriesModel).filter_by(external_id=series.id).first()
                )
                if model:
                    series.comment = model.comment
                    series.status = model.status
            return series_list

    def mark_episode_as_watched(
        self, series_external_id: int, episode_external_id: int, watched: bool
    ) -> None:
        with self.Session() as session:
            episode = (
                session.query(EpisodeModel)
                .join(EpisodeModel.series)
                .filter(
                    EpisodeModel.external_id == episode_external_id,
                    SeriesModel.external_id == series_external_id,
                )
                .first()
            )
            if episode is None:
                return
            episode.watched = watched
            self._update_series_status(episode.series)
            session.commit()

    def mark_series_as_watched(self, series_external_id: int, watched: bool) -> None:
        with self.Session() as session:
            series = (
                session.query(SeriesModel)
                .filter_by(external_id=series_external_id)
                .first()
            )
            if series is None or series.episodes:
                return
            series.status = "watched" if watched else "not_started"
            session.commit()

    def save_series_comment(self, series_external_id: int, comment: str) -> None:
        with self.Session() as session:
            series = (
                session.query(SeriesModel)
                .filter_by(external_id=series_external_id)
                .first()
            )
            if series:
                series.comment = comment.strip() or None
                session.commit()

    def save_episode_comment(self, episode_external_id: int, comment: str) -> None:
        with self.Session() as session:
            episode = (
                session.query(EpisodeModel)
                .filter_by(external_id=episode_external_id)
                .first()
            )
            if episode:
                episode.comment = comment.strip() or None
                session.commit()

    @staticmethod
    def _get_or_create_series(session, series: Series) -> SeriesModel:
        model = session.query(SeriesModel).filter_by(external_id=series.id).first()
        if model is None:
            model = SeriesModel(external_id=series.id, name=series.name)
            session.add(model)
        else:
            model.name = series.name
        return model

    @staticmethod
    def _get_or_create_episode(session, series_model, episode: Episode):
        model = session.query(EpisodeModel).filter_by(external_id=episode.id).first()
        if model is None:
            model = EpisodeModel(
                external_id=episode.id,
                series=series_model,
                name=episode.name,
                season=episode.season,
                number=episode.number,
            )
            session.add(model)
        else:
            model.name = episode.name
            model.season = episode.season
            model.number = episode.number
        return model

    @staticmethod
    def _update_series_status(series_model):
        episodes = series_model.episodes
        if not episodes:
            return
        if not any(episode.watched for episode in episodes):
            series_model.status = "not_started"
        elif all(episode.watched for episode in episodes):
            series_model.status = "watched"
        else:
            series_model.status = "watching"
