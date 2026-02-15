import streamlit as st
from config import setup_logging


def main():
    setup_logging()

    st.set_page_config(
        page_title="Collaborative Editing System",
        page_icon="✏️",
        layout="centered"
    )

    # st.title("📝 Collaborative Editing System")

    st.sidebar.success("Select an option.")

    welcome_page = st.Page(
        "pages/welcome_page.py",
        title="Welcome",
        icon="🏠",
        url_path="/"
    )

    login_page = st.Page(
        "pages/login.py",
        title="Login",
        icon="🔐",
        url_path="login"
    )

    editor_page = st.Page(
        "pages/editor.py",
        title="Editor",
        icon="📝",
        url_path="editor"
    )

    documents_page = st.Page(
        "pages/documents.py",
        title="Documents",
        icon="📝",
        url_path="documents"
    )

    profile_page = st.Page(
        "pages/profile.py",
        title="Profile",
        icon="👤",
        url_path="profile"
    )

    pg = st.navigation([welcome_page,
                        login_page,
                        profile_page,
                        documents_page,
                        editor_page
    ])

    pg.run()


if __name__ == "__main__":
    main()
