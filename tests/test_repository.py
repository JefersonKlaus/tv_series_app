from adapters.repository import PostgresRepository
from core.entities import Episode, Series


def test_repository_persists_status_and_comments(monkeypatch, tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    repository = PostgresRepository()
    series = Series(
        id=100,
        name="Test Series",
        genres=["Drama"],
        episodes=[
            Episode(id=200, name="Pilot", season=1, number=1),
            Episode(id=201, name="Finale", season=1, number=2),
        ],
    )

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


def test_repository_persists_movie_status(monkeypatch, tmp_path):
    database_url = f"sqlite:///{tmp_path / 'movie.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    repository = PostgresRepository()
    movie = Series(id=300, name="Test Movie", genres=[])

    repository.sync_series(movie)
    repository.mark_series_as_watched(movie.id, True)

    restored = repository.sync_series(movie)

    assert restored.status == "watched"

    repository.mark_series_as_watched(movie.id, False)
    restored = repository.sync_series(movie)

    assert restored.status == "not_started"
