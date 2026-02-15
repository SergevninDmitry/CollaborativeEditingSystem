import streamlit as st
from utils.api_client import api_client
from utils.auth import require_auth

require_auth()

st.title("👤 User Profile")

user = api_client.get_current_user()

st.subheader("Profile Information")

full_name = st.text_input("Full Name", value=user.get("full_name") or "")
about_user = st.text_area(
    "About You",
    value=user.get("about_user") or "",
    height=150
)

if st.button("Save Profile"):
    try:
        api_client.update_profile(full_name, about_user)
        st.success("Profile updated")
        st.rerun()
    except Exception:
        st.error("Failed to update profile")


st.subheader("Change Password")

old_password = st.text_input("Old Password", type="password")
new_password = st.text_input("New Password", type="password")

if st.button("Change Password"):
    try:
        api_client.change_password(old_password, new_password)
        st.success("Password changed successfully")
    except Exception:
        st.error("Wrong password")
