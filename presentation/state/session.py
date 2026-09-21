import streamlit as st


class SessionState:
    SELECTED_SERIES_ID = "selected_series_id"
    SELECTED_SERIES = "selected_series"
    LOADING_DETAILS = "loading_details"
    UPDATING_DETAILS = "updating_details"
    SEARCH_RESULTS = "search_results"
    SEARCH_QUERY = "search_query"
    SEARCH_QUERY_INPUT = "search_query_input"
    EDITING_SERIES_ID = "editing_series_id"
    EDITING_EPISODE_ID = "editing_episode_id"

    # SELECT SERIE
    def get_selected_series(self):
        return st.session_state.get(self.SELECTED_SERIES)

    def set_selected_series(self, series):
        st.session_state[self.SELECTED_SERIES] = series

    def get_selected_series_id(self):
        return st.session_state.get(self.SELECTED_SERIES_ID)

    def select_series(self, series):
        st.session_state[self.SELECTED_SERIES_ID] = series.id

        st.session_state[self.SELECTED_SERIES] = series

        st.session_state[self.LOADING_DETAILS] = True

        st.session_state[self.UPDATING_DETAILS] = False

    def has_selected_series(self):
        return self.get_selected_series_id() is not None

    def clear_selected_series(self):
        st.session_state.pop(
            self.SELECTED_SERIES_ID,
            None,
        )

        st.session_state.pop(
            self.SELECTED_SERIES,
            None,
        )

        st.session_state.pop(
            self.LOADING_DETAILS,
            None,
        )

        st.session_state.pop(
            self.UPDATING_DETAILS,
            None,
        )

    # SYNC WITH SEARCH RESULTS
    def update_series_in_search_results(self, series):
        results = self.get_search_results()

        for index, result in enumerate(results):
            if result.id == series.id:
                results[index] = series
                break

        st.session_state[self.SEARCH_RESULTS] = results

    # LOADING
    def is_loading_details(self):
        return st.session_state.get(
            self.LOADING_DETAILS,
            False,
        )

    def set_loading_details(self, value: bool):
        st.session_state[self.LOADING_DETAILS] = value

    # UPDATING
    def is_updating_details(self):
        return st.session_state.get(
            self.UPDATING_DETAILS,
            False,
        )

    def set_updating_details(self, value: bool):
        st.session_state[self.UPDATING_DETAILS] = value

    # SEARCH
    def get_search_results(self):
        return st.session_state.get(
            self.SEARCH_RESULTS,
            [],
        )

    def set_search_results(self, results):
        st.session_state[self.SEARCH_RESULTS] = results

    def get_search_query(self):
        return st.session_state.get(
            self.SEARCH_QUERY,
            "",
        )

    def set_search_query(self, query):
        st.session_state[self.SEARCH_QUERY] = query

    # EDITING
    def set_editing_series(self, series_id):
        st.session_state[self.EDITING_SERIES_ID] = series_id

    def get_editing_series_id(self):
        return st.session_state.get(self.EDITING_SERIES_ID)

    def clear_editing_series(self):
        st.session_state.pop(
            self.EDITING_SERIES_ID,
            None,
        )

    def set_editing_episode(self, episode_id):
        st.session_state[self.EDITING_EPISODE_ID] = episode_id

    def get_editing_episode_id(self):
        return st.session_state.get(self.EDITING_EPISODE_ID)

    def clear_editing_episode(self):
        st.session_state.pop(
            self.EDITING_EPISODE_ID,
            None,
        )
