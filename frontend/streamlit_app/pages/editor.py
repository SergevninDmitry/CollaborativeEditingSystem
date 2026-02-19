import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.api_client import api_client
from utils.auth import require_auth
from utils.render_diff import render_colored_diff


require_auth()

if "selected_document_id" not in st.session_state:
    st.warning("No document selected")

    if st.button("⬅ Back to Documents"):
        st.switch_page("pages/documents.py")

document_id = st.session_state.selected_document_id

st.title("📝 Document Editor")

# Auto refresh (polling)
st_autorefresh(interval=5000, key="doc_poll")

versions = api_client.get_versions(document_id, limit=8)

if not versions:
    st.error("No versions found")
    st.stop()

latest = versions[0]
latest_id = latest["id"]
latest_content = latest["content"]

# Initialize session state
if "editing_base_version_id" not in st.session_state:
    st.session_state.editing_base_version_id = latest_id
    st.session_state.editing_base_content = latest_content
    st.session_state.editor_content = latest_content

if latest_id != st.session_state.editing_base_version_id:

    if st.session_state.editor_content != st.session_state.editing_base_content:
        st.warning(
            "⚠ Another user updated the document while you were editing."
        )
    else:
        # safe auto sync
        st.session_state.editor_content = latest_content
        st.session_state.editing_base_content = latest_content
        st.session_state.editing_base_version_id = latest_id
        st.rerun()

if st.session_state.get("load_latest_requested"):
    st.session_state.editor_content = latest_content
    st.session_state.editing_base_content = latest_content
    st.session_state.editing_base_version_id = latest_id

    st.session_state.load_latest_requested = False

st.markdown(f"##### {st.session_state.selected_document_title}")
st.text_area(
    "Content",
    height=400,
    key="editor_content",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([3, 3, 3])
with col1:
    if st.button("💾 Save New Version"):
        base_version_id = st.session_state.editing_base_version_id

        try:
            new_version = api_client.add_version(
                document_id,
                st.session_state.editor_content,
                base_version_id
            )
            # update base after successful save
            st.session_state.editing_base_version_id = new_version["id"]
            st.session_state.editing_base_content = st.session_state.editor_content

            st.success("Version saved")
            st.rerun()

        except Exception:
            st.error("Conflict detected!")

with col2:
    if latest_id != st.session_state.editing_base_version_id:
        st.warning("New version available!")
with col3:
    if st.button("Load Latest Version"):
        st.session_state.load_latest_requested = True
        st.rerun()

st.subheader("Version History")
for version in versions:
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

    with col1:
        st.write(version["created_at"])

    with col2:
        st.write(version["author_email"])

    with col3:
        if st.button("View Changes", key=f"diff_{version['id']}"):
            diff = api_client.get_diff(
                document_id,
                version["id"]
            )
            st.session_state.current_diff = diff

    with col4:
        if version["id"] == st.session_state.editing_base_version_id:
            st.write("Latest")
        else:
            if st.button("Revert", key=f"revert_{version['id']}"):
                new_version = api_client.revert_version(
                    document_id,
                    version["id"]
                )

                st.session_state.load_latest_requested = True

                st.success("Reverted")
                st.rerun()

if "current_diff" in st.session_state:
    st.subheader("Changes")
    render_colored_diff(st.session_state.current_diff)

if st.button("⬅ Back to Documents"):
    st.switch_page("pages/documents.py")
