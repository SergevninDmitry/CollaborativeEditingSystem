import streamlit as st
from editing_system.streamlit_app.utils.api_client import api_client
from editing_system.streamlit_app.utils.auth import require_auth

require_auth()

st.title("📄 Your Documents")

documents = api_client.get_documents()

doc_titles = [doc["title"] for doc in documents]
doc_map = {doc["title"]: doc for doc in documents}


st.subheader("Create New Document")

new_title = st.text_input("Document Title")
new_content = st.text_area("Initial Content", height=200)

if st.button("Create Document"):
    if not new_title.strip():
        st.error("Title cannot be empty")
    else:
        doc = api_client.create_document(new_title, new_content)
        st.session_state.selected_document_id = doc["id"]

st.divider()

st.subheader("Open Existing Document")

if doc_titles:
    selected = st.selectbox("Select Document", doc_titles)

    if st.button("Open Document"):
        st.session_state.selected_document_id = doc_map[selected]["id"]
else:
    st.info("No documents yet.")

st.subheader("Share Document")

if "selected_document_id" in st.session_state:

    share_email = st.text_input("User email to share with")

    if st.button("Share"):
        try:
            api_client.share_document(
                st.session_state.selected_document_id,
                share_email
            )
            st.success("Document shared successfully")
        except Exception:
            st.error("Failed to share document")

if st.button("Go to Editor"):
    st.switch_page("pages/editor.py")
