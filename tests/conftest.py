import pytest

from adapters.repository import PostgresRepository
from core.entities import Episode, Series


@pytest.fixture
def repository(monkeypatch, tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    return PostgresRepository()


@pytest.fixture
def sample_series():
    return Series(
        id=100,
        name="Test Series",
        genres=["Drama"],
        episodes=[
            Episode(id=200, name="Pilot", season=1, number=1),
            Episode(id=201, name="Finale", season=1, number=2),
        ],
    )


@pytest.fixture
def sample_movie():
    return Series(id=300, name="Test Movie", genres=[])
