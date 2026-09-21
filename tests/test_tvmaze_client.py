import asyncio

import httpx

from adapters.tvmaze_client import TVMazeClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    async def get(self, url, params=None, timeout=None):
        self.requests.append((url, params, timeout))
        return FakeResponse(self.responses.pop(0))


class FailingHttpClient:
    async def get(self, url, params=None, timeout=None):
        raise httpx.HTTPError("TVMaze indisponível")


def test_search_series_maps_title_year_and_poster():
    http_client = FakeHttpClient(
        [
            [
                {
                    "show": {
                        "id": 1,
                        "name": "Breaking Bad",
                        "premiered": "2008-01-20",
                        "genres": ["Drama"],
                        "image": {"medium": "poster.jpg"},
                    }
                }
            ]
        ]
    )

    results = asyncio.run(TVMazeClient(http_client).search_series("Breaking Bad"))

    assert results[0].name == "Breaking Bad"
    assert results[0].premiered_year == 2008
    assert results[0].poster_url == "poster.jpg"
    assert http_client.requests[0][1] == {"q": "Breaking Bad"}


def test_get_series_details_maps_episodes():
    http_client = FakeHttpClient(
        [
            {
                "id": 1,
                "name": "Breaking Bad",
                "genres": ["Drama"],
                "image": None,
            },
            [
                {"id": 10, "name": "Pilot", "season": 1, "number": 1},
                {"id": 11, "name": "Cat's in the Bag...", "season": 1, "number": 2},
            ],
        ]
    )

    series = asyncio.run(TVMazeClient(http_client).get_series_details(1))

    assert series is not None
    assert [episode.name for episode in series.episodes] == [
        "Pilot",
        "Cat's in the Bag...",
    ]
    assert http_client.requests[1][0].startswith("https://api.tvmaze.com")
    assert http_client.requests[1][0].endswith("/shows/1/episodes")


def test_search_series_returns_empty_for_blank_query():
    http_client = FakeHttpClient([])

    results = asyncio.run(TVMazeClient(http_client).search_series("   "))

    assert results == []
    assert http_client.requests == []


def test_search_series_returns_empty_when_request_fails():
    results = asyncio.run(
        TVMazeClient(FailingHttpClient()).search_series("Breaking Bad")
    )

    assert results == []
