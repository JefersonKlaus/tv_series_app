import streamlit as st

from view.infrastructure.async_runner import run_async
from view.presentation.components.series_card import (
    render_series_card,
)


def render_search_page(
    dependencies,
    session,
):
    st.title("TV Series Explorer")

    query = st.text_input(
        "Busque por uma série",
        placeholder="Ex.: Breaking Bad",
        key="search_query_input",
    )

    normalized_query = query.strip()

    if normalized_query:
        _handle_search(
            normalized_query,
            dependencies,
            session,
        )

    results = session.get_search_results()

    if results:
        _render_results(
            results,
            session,
        )

    elif normalized_query:
        st.info("Nenhuma série encontrada.")


def _handle_search(
    query,
    dependencies,
    session,
):
    if session.get_search_query() == query:
        return

    with st.spinner("Buscando séries..."):
        results = run_async(dependencies.search_series.execute(query))

    session.set_search_results(results)

    session.set_search_query(query)


def _render_results(
    results,
    session,
):
    st.subheader("Resultados")

    for index, series in enumerate(results):
        clicked = render_series_card(
            series,
            index,
        )

        if clicked:
            session.select_series(series)

            st.rerun()
