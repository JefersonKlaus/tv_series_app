import asyncio

from core.entities import Series
from core.use_cases import (
    GenerateInsightUseCase,
    GetSeriesDetailsUseCase,
    SearchSeriesUseCase,
)


class SuccessfulAIProvider:
    async def generate_insight(self, summary, genres, comments):
        return "Insight gerado"


class FailingAIProvider:
    async def generate_insight(self, summary, genres, comments):
        raise RuntimeError("servico indisponivel")


class SeriesProvider:
    def __init__(self):
        self.queries = []

    async def search_series(self, query):
        self.queries.append(query)
        return [Series(id=1, name="Breaking Bad", genres=["Drama"])]

    async def get_series_details(self, series_id):
        return Series(id=series_id, name="Breaking Bad", genres=["Drama"])


def test_returns_message_when_summary_is_missing():
    use_case = GenerateInsightUseCase(SuccessfulAIProvider())

    result = asyncio.run(use_case.execute("", ["Drama"], []))

    assert result == "Resumo não disponível para gerar insights."


def test_returns_provider_insight():
    use_case = GenerateInsightUseCase(SuccessfulAIProvider())

    result = asyncio.run(use_case.execute("Resumo", ["Drama"], ["Ótimo episódio"]))

    assert result == "Insight gerado"


def test_returns_fallback_when_provider_fails():
    use_case = GenerateInsightUseCase(FailingAIProvider())

    result = asyncio.run(use_case.execute("Resumo", ["Drama"], []))

    assert result.startswith("Insight indisponível no momento.")


def test_search_series_use_case_delegates_to_injected_provider():
    provider = SeriesProvider()
    use_case = SearchSeriesUseCase(provider)

    result = asyncio.run(use_case.execute("  Breaking Bad  "))

    assert result[0].name == "Breaking Bad"
    assert provider.queries == ["Breaking Bad"]


def test_search_series_use_case_ignores_empty_query():
    provider = SeriesProvider()
    use_case = SearchSeriesUseCase(provider)

    assert asyncio.run(use_case.execute("   ")) == []
    assert provider.queries == []


def test_get_series_details_use_case_awaits_injected_provider():
    use_case = GetSeriesDetailsUseCase(SeriesProvider())

    result = asyncio.run(use_case.execute(1))

    assert result is not None
    assert result.name == "Breaking Bad"
