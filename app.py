import streamlit as st

from adapters.tvmaze_client import TVMazeClient
from core.use_cases import GetSeriesDetailsUseCase, SearchSeriesUseCase


st.set_page_config(page_title="TV Series Explorer", layout="wide")


@st.cache_resource
def get_use_cases():
    """Compose the concrete TVMaze adapter at the application boundary."""
    tvmaze_client = TVMazeClient()
    return SearchSeriesUseCase(tvmaze_client), GetSeriesDetailsUseCase(tvmaze_client)


search_series_uc, get_series_details_uc = get_use_cases()


def render_series_details(series_id):
    with st.spinner("Carregando detalhes..."):
        series = get_series_details_uc.execute(series_id)

    if series is None:
        st.error("Não foi possível carregar os detalhes da série.")
        return

    if st.button("Voltar para resultados"):
        st.session_state.pop("selected_series_id")
        st.rerun()

    st.header(series.name)
    if series.poster_url:
        st.image(series.poster_url, width=240)
    st.markdown(series.summary or "Resumo não disponível.", unsafe_allow_html=True)
    if series.genres:
        st.write(f"Gêneros: {', '.join(series.genres)}")

    if series.episodes:
        st.subheader("Episódios")
        episodes_by_season = {}
        for episode in series.episodes:
            episodes_by_season.setdefault(episode.season, []).append(episode)

        for season, episodes in sorted(episodes_by_season.items()):
            with st.expander(f"Temporada {season}"):
                for episode in sorted(episodes, key=lambda item: item.number):
                    st.write(f"{episode.number}. {episode.name}")
                    if episode.summary:
                        st.markdown(episode.summary, unsafe_allow_html=True)


st.title("TV Series Explorer")

if "selected_series_id" in st.session_state:
    render_series_details(st.session_state["selected_series_id"])
    st.stop()

query = st.text_input(
    "Busque por uma série",
    placeholder="Ex.: Breaking Bad",
    key="search_query_input",
)

normalized_query = query.strip()
if normalized_query:
    if st.session_state.get("search_query") != normalized_query:
        with st.spinner("Buscando séries..."):
            st.session_state["search_results"] = search_series_uc.execute(query)
        st.session_state["search_query"] = normalized_query

series_results = st.session_state.get("search_results", [])

if series_results:
    st.subheader("Resultados")
    for index, series in enumerate(series_results):
        poster_column, details_column = st.columns([1, 4])
        with poster_column:
            if series.poster_url:
                st.image(series.poster_url, width=120)
        with details_column:
            year = f" ({series.premiered_year})" if series.premiered_year else ""
            st.markdown(f"### {series.name}{year}")
            if series.genres:
                st.write(f"Gêneros: {', '.join(series.genres)}")
            if st.button("Ver detalhes", key=f"series-{series.id}-{index}"):
                st.session_state["selected_series_id"] = series.id
                st.rerun()
elif normalized_query:
    st.info("Nenhuma série encontrada.")
