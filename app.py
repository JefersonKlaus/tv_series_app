import streamlit as st

from view.config.dependencies import get_dependencies
from view.presentation.pages.search_page import render_search_page
from view.presentation.pages.series_details_page import render_series_details_page
from view.presentation.state.session import SessionState


st.set_page_config(
    page_title="TV Series Explorer",
    layout="wide",
)


def main():
    dependencies = get_dependencies()

    session = SessionState()

    if session.has_selected_series():
        render_series_details_page(
            dependencies=dependencies,
            session=session,
        )
        return

    render_search_page(
        dependencies=dependencies,
        session=session,
    )


if __name__ == "__main__":
    main()
