import pytest

from adapters.repository import PostgresRepository


def test_repository_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL environment variable is required"):
        PostgresRepository()
def repository(monkeypatch, tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    return PostgresRepository()


def test_repository_persists_status_and_comments(repository, sample_series):
    series = sample_series

    repository.sync_series(series)
    repository.save_series_comment(series.id, "Series comment")
    repository.save_episode_comment(200, "Episode comment")
    repository.mark_episode_as_watched(series.id, 200, True)

    restored = repository.sync_series(series)

    assert restored.comment == "Series comment"
    assert restored.status == "watching"
    assert restored.episodes[0].watched is True
    assert restored.episodes[0].comment == "Episode comment"
    assert restored.episodes[1].watched is False

    repository.mark_episode_as_watched(series.id, 201, True)
    completed = repository.sync_series(series)

    assert completed.status == "watched"


def test_repository_persists_movie_status(repository, sample_movie):
    movie = sample_movie
    repository.sync_series(movie)
    repository.mark_series_as_watched(movie.id, True)

    restored = repository.sync_series(movie)

    assert restored.status == "watched"

    repository.mark_series_as_watched(movie.id, False)
    restored = repository.sync_series(movie)

    assert restored.status == "not_started"
