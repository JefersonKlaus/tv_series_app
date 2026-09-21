import streamlit as st


def render_series_basic_info(series):
    st.header(series.name)

    if series.poster_url:
        st.image(
            series.poster_url,
            width=240,
        )

    st.markdown(
        series.summary or "Resumo não disponível.",
        unsafe_allow_html=True,
    )

    if series.genres:
        st.write(f"Gêneros: {', '.join(series.genres)}")
