import streamlit as st

from adapters.tvmaze_client import TVMazeClient
from core.use_cases import SearchSeriesUseCase


st.set_page_config(page_title="TV Series Explorer", layout="wide")


@st.cache_resource
def get_search_series_use_case():
    """Compose the concrete TVMaze adapter at the application boundary."""
    return SearchSeriesUseCase(TVMazeClient())


search_series_uc = get_search_series_use_case()

st.title("TV Series Explorer")
query = st.text_input("Busque por uma série", placeholder="Ex.: Breaking Bad")

if query:
    with st.spinner("Buscando séries..."):
        series_results = search_series_uc.execute(query)

    if not series_results:
        st.info("Nenhuma série encontrada.")
    else:
        st.subheader("Resultados")
        for series in series_results:
            poster_column, details_column = st.columns([1, 4])
            with poster_column:
                if series.poster_url:
                    st.image(series.poster_url, width=120)
            with details_column:
                year = f" ({series.premiered_year})" if series.premiered_year else ""
                st.markdown(f"### {series.name}{year}")
                if series.genres:
                    st.write(f"Gêneros: {', '.join(series.genres)}")
