import streamlit as st
from streamlit_autorefresh import st_autorefresh
from editing_system.streamlit_app.utils.api_client import api_client
from editing_system.streamlit_app.utils.auth import require_auth

require_auth()

if "selected_document_id" not in st.session_state:
    st.warning("No document selected")
    st.switch_page("pages/documents.py")


document_id = st.session_state.selected_document_id

st.title("📝 Document Editor")

# Poll every 3 seconds
st_autorefresh(interval=10000, key="doc_poll")

versions = api_client.get_versions(document_id)

latest_version = versions[0] if versions else None

if not latest_version:
    st.error("No versions found")
    st.stop()

latest_version_id = latest_version["id"]
latest_content = latest_version["content"]

if "editing_base_version_id" not in st.session_state:
    st.session_state.editing_base_version_id = latest_version_id

if "editing_base_content" not in st.session_state:
    st.session_state.editing_base_content = latest_content

if "editor_content" not in st.session_state:
    st.session_state.editor_content = latest_content

# Initialize editing state
if "editing_base_version_id" not in st.session_state:
    st.session_state.editing_base_version_id = latest_version_id
    st.session_state.editing_base_content = latest_content
    st.session_state.editor_content = latest_content

# Auto update only if no local changes
if (
    latest_version_id != st.session_state.editing_base_version_id
    and st.session_state.editor_content == st.session_state.editing_base_content
):
    st.session_state.editing_base_version_id = latest_version_id
    st.session_state.editing_base_content = latest_content
    st.session_state.editor_content = latest_content
    st.rerun()

content = st.text_area(
    "Content",
    height=400,
    key="editor_content"
)

if st.button("Save New Version"):
    try:
        new_version = api_client.add_version(
            document_id,
            content,
            st.session_state.editing_base_version_id
        )

        st.session_state.editing_base_version_id = new_version["id"]
        st.session_state.editing_base_content = content

        st.write("Base version after Save:", st.session_state.editing_base_version_id)
        st.write("Latest version after Save:", latest_version_id)
        st.success("Version saved")
        st.rerun()

    except Exception:
        st.error("Conflict detected! Document was modified by another user.")

st.subheader("Version History")

for i, version in enumerate(versions):
    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(version["created_at"])

    with col2:
        if i == 0:
            st.write("Current")
        else:
            if st.button("Revert", key=f"revert_{version['id']}"):
                api_client.revert_version(document_id, version["id"])
                st.success("Reverted")
                st.rerun()

if st.button("⬅ Back to Documents"):
    st.switch_page("pages/documents.py")
