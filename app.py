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

st.set_page_config(page_title="TV Series Explorer", layout="wide")


@st.cache_resource
def get_use_cases():
    """Compose the concrete TVMaze adapter at the application boundary."""
    tvmaze_client = TVMazeClient()
    persistence = PostgresRepository()
    return (
        SearchSeriesUseCase(tvmaze_client, persistence),
        GetSeriesDetailsUseCase(tvmaze_client, persistence),
        MarkEpisodeWatchedUseCase(persistence),
        MarkSeriesWatchedUseCase(persistence),
        SaveSeriesCommentUseCase(persistence),
        SaveEpisodeCommentUseCase(persistence),
    )


(
    search_series_uc,
    get_series_details_uc,
    mark_episode_watched_uc,
    mark_series_watched_uc,
    save_series_comment_uc,
    save_episode_comment_uc,
) = get_use_cases()


@st.dialog("Editar comentário da série")
def edit_series_comment(series_id, current_comment):
    comment = st.text_area(
        "Comentário",
        value=current_comment or "",
        key=f"series-comment-{series_id}",
    )
    if st.button("Salvar comentário", key=f"save-series-comment-{series_id}"):
        save_series_comment_uc.execute(series_id, comment)
        st.session_state.pop("editing_series_id", None)
        st.rerun()


@st.dialog("Editar comentário do episódio")
def edit_episode_comment(episode_id, current_comment):
    comment = st.text_area(
        "Comentário",
        value=current_comment or "",
        key=f"episode-comment-{episode_id}",
    )
    if st.button("Salvar comentário", key=f"save-episode-comment-{episode_id}"):
        save_episode_comment_uc.execute(episode_id, comment)
        st.session_state.pop("editing_episode_id", None)
        st.rerun()


def render_series_details(series_id):
    with st.spinner("Carregando detalhes..."):
        series = get_series_details_uc.execute(series_id)

    if series is None:
        st.error("Não foi possível carregar os detalhes da série.")
        return

    if st.button("Voltar para resultados"):
        previous_query = st.session_state.get(
            "search_query", st.session_state.get("search_query_input", "")
        )
        st.session_state.pop("selected_series_id")
        st.session_state.pop("search_query", None)
        st.session_state.pop("search_results", None)
        st.session_state["search_query_input"] = previous_query
        st.rerun()

    st.header(series.name)
    if series.poster_url:
        st.image(series.poster_url, width=240)
    st.markdown(series.summary or "Resumo não disponível.", unsafe_allow_html=True)
    if series.genres:
        st.write(f"Gêneros: {', '.join(series.genres)}")

    if not series.episodes:
        movie_watched = st.selectbox(
            "Status do filme",
            options=[False, True],
            index=1 if series.status == "watched" else 0,
            format_func=lambda watched: "Assistido" if watched else "Não iniciado",
            key=f"movie-watched-{series.id}",
        )
        if (movie_watched and series.status != "watched") or (
            not movie_watched and series.status != "not_started"
        ):
            mark_series_watched_uc.execute(series.id, movie_watched)
            st.rerun()

    st.write(f"Status: **{series.status}**")
    st.write(f"Comentário: {series.comment or 'Nenhum comentário'}")
    if st.button("Editar comentário da série"):
        st.session_state["editing_series_id"] = series.id
        st.rerun()

    if st.session_state.get("editing_series_id") == series.id:
        edit_series_comment(series.id, series.comment)

    if series.episodes:
        st.subheader("Episódios")
        episodes_by_season = {}
        for episode in series.episodes:
            episodes_by_season.setdefault(episode.season, []).append(episode)

        for season, episodes in sorted(episodes_by_season.items()):
            with st.expander(f"Temporada {season}"):
                for episode in sorted(episodes, key=lambda item: item.number):
                    watched = st.checkbox(
                        f"{episode.number}. {episode.name}",
                        value=episode.watched,
                        key=f"watched-{series.id}-{episode.id}",
                    )
                    if watched != episode.watched:
                        mark_episode_watched_uc.execute(series.id, episode.id, watched)
                        st.rerun()
                    if episode.summary:
                        st.markdown(episode.summary, unsafe_allow_html=True)
                    if episode.comment:
                        st.write(f"Comentário: {episode.comment}")
                    if st.button(
                        f"Editar comentário - T{episode.season}E{episode.number}",
                        key=f"edit-episode-{episode.id}",
                    ):
                        st.session_state["editing_episode_id"] = episode.id
                        st.rerun()
                    if st.session_state.get("editing_episode_id") == episode.id:
                        edit_episode_comment(episode.id, episode.comment)


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
            st.write(f"Status: **{series.status}**")
            if series.comment:
                st.write(f"Comentário: {series.comment}")
            if st.button("Ver detalhes", key=f"series-{series.id}-{index}"):
                st.session_state["selected_series_id"] = series.id
                st.rerun()
elif normalized_query:
    st.info("Nenhuma série encontrada.")
