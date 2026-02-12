import streamlit as st
from editing_system.streamlit_app.utils.api_client import api_client
from editing_system.streamlit_app.utils.auth import require_auth

require_auth()

st.title("📝 Document Editor")

documents = api_client.get_documents()

doc_titles = [doc["title"] for doc in documents]
doc_map = {doc["title"]: doc for doc in documents}

selected_title = st.selectbox(
    "Select Document",
    options=["-- Create New --"] + doc_titles
)

if selected_title == "-- Create New --":
    st.subheader("Create New Document")

    new_title = st.text_input("Document Title")
    new_content = st.text_area("Content", height=300)

    if st.button("Create Document"):
        if new_title.strip() == "":
            st.error("Title cannot be empty")
        else:
            api_client.create_document(new_title, new_content)
            st.success("Document created")
            st.rerun()
else:
    document = doc_map[selected_title]
    document_id = document["id"]
    versions = api_client.get_versions(document_id)

    latest_version_id = versions[0]["id"] if versions else None
    latest_content = versions[0]["content"] if versions else ""

    st.subheader(f"Editing: {selected_title}")

    if (
            "current_document_id" not in st.session_state
            or st.session_state.current_document_id != document_id
            or st.session_state.get("latest_version_id") != latest_version_id
    ):
        st.session_state.current_document_id = document_id
        st.session_state.latest_version_id = latest_version_id
        st.session_state.editor_content = latest_content

    content = st.text_area(
        "Content",
        height=400,
        key="editor_content"
    )

    if st.button("Save New Version"):
        api_client.add_version(document_id, content)
        st.success("Version saved")
        st.rerun()

    st.subheader("Version History")

    for i, version in enumerate(versions):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"{version['created_at']}")

        with col2:
            if i != 0:
                if st.button(
                        "Revert",
                        key=f"revert_{version['id']}"
                ):
                    api_client.revert_version(document_id, version["id"])
                    st.success("Reverted successfully")
                    st.rerun()
            else:
                st.write("Current")
