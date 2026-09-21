import streamlit as st

from infrastructure.async_runner import run_async
from presentation.components.series_basic_info import (
    render_series_basic_info,
)


@st.fragment
def update_series_details(
    dependencies,
    session,
):
    if not session.is_loading_details():
        return

    series = session.get_selected_series()

    if series is None:
        return

    if session.is_updating_details():
        return

    session.set_updating_details(True)

    try:
        updated_series = run_async(dependencies.get_series_details.execute(series.id))

    except Exception as error:
        session.set_loading_details(False)
        session.set_updating_details(False)

        st.error("Não foi possível atualizar os detalhes da série.")

        st.exception(error)

        return

    session.set_selected_series(updated_series)

    session.update_series_in_search_results(updated_series)

    session.set_loading_details(False)
    session.set_updating_details(False)

    st.rerun(scope="app")


def render_series_details_page(
    dependencies,
    session,
):
    series = session.get_selected_series()

    if series is None:
        session.clear_selected_series()
        st.rerun()

    _render_back_button(session)

    if session.is_loading_details():
        render_series_basic_info(series)

        st.info("Atualizando os detalhes...")

        update_series_details(
            dependencies,
            session,
        )

        return

    _render_full_details(
        series,
        dependencies,
        session,
    )


def _render_back_button(session):
    if not st.button("Voltar para resultados"):
        return

    session.clear_selected_series()

    st.rerun()


def _render_full_details(
    series,
    dependencies,
    session,
):
    render_series_basic_info(series)

    _render_status(
        series,
        dependencies,
        session,
    )

    _render_series_comment(
        series,
        dependencies,
        session,
    )

    _render_episodes(
        series,
        dependencies,
        session,
    )


def _render_status(
    series,
    dependencies,
    session,
):
    if not series.episodes:
        movie_watched = st.selectbox(
            "Status do filme",
            options=[
                False,
                True,
            ],
            index=(1 if series.status == "watched" else 0),
            format_func=lambda value: "Assistido" if value else "Não iniciado",
            key=f"movie-watched-{series.id}",
        )

        expected_status = "watched" if movie_watched else "not_started"

        if series.status != expected_status:
            run_async(
                dependencies.mark_series_watched.execute(
                    series.id,
                    movie_watched,
                )
            )

            series.status = expected_status

            st.rerun()

    st.write(f"Status: **{series.status}**")


def _render_series_comment(
    series,
    dependencies,
    session,
):
    st.write("Comentário: " + (series.comment or "Nenhum comentário"))

    if st.button(
        "Editar comentário da série",
        key=f"edit-series-{series.id}",
    ):
        session.set_editing_series(series.id)

    if session.get_editing_series_id() == series.id:
        _render_series_comment_dialog(
            series,
            dependencies,
            session,
        )


@st.dialog("Editar comentário da série")
def _render_series_comment_dialog(
    series,
    dependencies,
    session,
):
    comment = st.text_area(
        "Comentário",
        value=series.comment or "",
        key=f"series-comment-{series.id}",
    )

    if not st.button(
        "Salvar comentário",
        key=f"save-series-comment-{series.id}",
    ):
        return

    run_async(
        dependencies.save_series_comment.execute(
            series.id,
            comment,
        )
    )

    # Atualiza o objeto atualmente selecionado
    series.comment = comment.strip() or None

    session.set_selected_series(series)

    session.update_series_in_search_results(series)

    session.clear_editing_series()

    st.rerun()


def _render_episodes(
    series,
    dependencies,
    session,
):
    if not series.episodes:
        return

    st.subheader("Episódios")

    episodes_by_season = {}

    for episode in series.episodes:
        episodes_by_season.setdefault(
            episode.season,
            [],
        ).append(episode)

    for season, episodes in sorted(episodes_by_season.items()):
        with st.expander(f"Temporada {season}"):
            for episode in sorted(
                episodes,
                key=lambda item: item.number,
            ):
                _render_episode(
                    series,
                    episode,
                    dependencies,
                    session,
                )


def _render_episode(
    series,
    episode,
    dependencies,
    session,
):
    watched = st.checkbox(
        (f"{episode.number}. {episode.name}"),
        value=episode.watched,
        key=(f"watched-{series.id}-{episode.id}"),
    )

    if watched != episode.watched:
        run_async(
            dependencies.mark_episode_watched.execute(
                series.id,
                episode.id,
                watched,
            )
        )

        episode.watched = watched

        _update_series_status(series)

        st.rerun()

    if episode.summary:
        st.markdown(
            episode.summary,
            unsafe_allow_html=True,
        )

    if episode.comment:
        st.write(f"Comentário: {episode.comment}")

    if st.button(
        (f"Editar comentário - T{episode.season}E{episode.number}"),
        key=f"edit-episode-{episode.id}",
    ):
        session.set_editing_episode(episode.id)

    if session.get_editing_episode_id() == episode.id:
        _render_episode_comment(
            series,
            episode,
            dependencies,
            session,
        )


def _render_episode_comment(
    series,
    episode,
    dependencies,
    session,
):
    text_key = f"episode-comment-{episode.id}"

    comment = st.text_area(
        "Comentário",
        value=episode.comment or "",
        key=text_key,
    )

    if not st.button(
        "Salvar comentário",
        key=f"save-episode-comment-{episode.id}",
    ):
        return

    run_async(
        dependencies.save_episode_comment.execute(
            episode.id,
            comment,
        )
    )

    episode.comment = comment.strip() or None

    session.clear_editing_episode()

    st.rerun()


def _update_series_status(series):
    watched = [episode.watched for episode in series.episodes]

    if all(watched):
        series.status = "watched"

    elif any(watched):
        series.status = "watching"

    else:
        series.status = "not_started"
