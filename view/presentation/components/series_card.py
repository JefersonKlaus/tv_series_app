import streamlit as st


def render_series_card(series, index):
    poster_column, details_column = st.columns([1, 4])

    with poster_column:
        if series.poster_url:
            st.image(
                series.poster_url,
                width=120,
            )

    with details_column:
        year = f" ({series.premiered_year})" if series.premiered_year else ""

        st.markdown(f"### {series.name}{year}")

        if series.genres:
            st.write(f"Gêneros: {', '.join(series.genres)}")

        st.write(f"Status: **{series.status}**")

        if series.comment:
            st.write(f"Comentário: {series.comment}")

        return st.button(
            "Ver detalhes",
            key=f"series-{series.id}-{index}",
        )
