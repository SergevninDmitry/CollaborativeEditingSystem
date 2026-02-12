import streamlit as st
from editing_system.streamlit_app.utils.api_client import api_client


def logout():
    keys = ["access_token", "authenticated", "user_email"]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


def require_auth():
    if "access_token" not in st.session_state:
        st.error("You must login first.")
        st.stop()

    try:
        user = api_client.get_current_user()
        st.session_state.user_email = user["email"]

    except Exception:
        logout()
