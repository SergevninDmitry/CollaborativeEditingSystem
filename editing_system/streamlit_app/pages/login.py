import streamlit as st
import re
from editing_system.streamlit_app.utils.api_client import api_client
from editing_system.streamlit_app.utils.auth import logout

# if "access_token" not in st.session_state:
#     st.error("You must login first")
#     st.stop()


st.title("Collaborative Editing System")

mode = st.radio(
    "Choose action",
    ["Login", "Register"]
)


if mode == "Login":
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            value=st.session_state.get("user_email", ""),
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submit = st.form_submit_button("Login")
if mode == "Register":
    st.subheader("Register")
    with st.form("register_form"):
        email = st.text_input(
            "Email",
            value=st.session_state.get("user_email", ""),
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submit = st.form_submit_button("Register")

if submit:
    try:
        if mode == "Register":
            api_client.register(email, password)
            st.success("Account created successfully. Logging you in...")

        result = api_client.login(email, password)

        st.session_state.access_token = result["access_token"]
        user_data = api_client.get_current_user()
        st.session_state.user_email = user_data["email"]
        st.session_state.authenticated = True

        st.success("Login successful")
        st.rerun()


    except Exception as e:
        st.error(str(e))


if st.session_state.get("access_token"):
    st.sidebar.markdown("---")
    st.sidebar.write(f"Logged in as: {st.session_state.get('user_email')}")

    if st.sidebar.button("Logout"):
        logout()
