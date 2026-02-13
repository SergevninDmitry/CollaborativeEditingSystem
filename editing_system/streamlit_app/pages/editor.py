import streamlit as st
from streamlit_autorefresh import st_autorefresh
from editing_system.streamlit_app.utils.api_client import api_client
from editing_system.streamlit_app.utils.auth import require_auth

import html


def render_colored_diff(diff_text: str):
    lines = diff_text.splitlines()
    html_lines = []

    for line in lines:
        escaped = html.escape(line)

        if line.startswith("+") and not line.startswith("+++"):
            html_lines.append(
                f"<div style='background-color:#d4f8d4;'>{escaped}</div>"
            )
        elif line.startswith("-") and not line.startswith("---"):
            html_lines.append(
                f"<div style='background-color:#f8d4d4;'>{escaped}</div>"
            )
        else:
            html_lines.append(f"<div>{escaped}</div>")

    st.markdown(
        "<div style='font-family:monospace'>" +
        "".join(html_lines) +
        "</div>",
        unsafe_allow_html=True
    )

require_auth()

# -----------------------------
# Document selection check
# -----------------------------
if "selected_document_id" not in st.session_state:
    st.warning("No document selected")
    st.switch_page("pages/documents.py")

document_id = st.session_state.selected_document_id

st.title("📝 Document Editor")

# -----------------------------
# Auto refresh (polling)
# -----------------------------
st_autorefresh(interval=10000, key="doc_poll")

# -----------------------------
# Fetch versions
# -----------------------------
versions = api_client.get_versions(document_id, limit=8)

if not versions:
    st.error("No versions found")
    st.stop()

latest_version = versions[0]
latest_version_id = latest_version["id"]
latest_content = latest_version["content"]

# -----------------------------
# Apply pending revert BEFORE widget creation
# -----------------------------
if "pending_revert_content" in st.session_state:
    st.session_state.editor_content = st.session_state.pending_revert_content
    st.session_state.editing_base_content = st.session_state.pending_revert_content
    st.session_state.editing_base_version_id = st.session_state.pending_revert_version_id

    del st.session_state.pending_revert_content
    del st.session_state.pending_revert_version_id

# -----------------------------
# Initialize session state
# -----------------------------
if "editor_initialized_for_doc" not in st.session_state or \
        st.session_state.editor_initialized_for_doc != document_id:

    st.session_state.editor_initialized_for_doc = document_id
    st.session_state.editing_base_version_id = latest_version_id
    st.session_state.editing_base_content = latest_content
    st.session_state.editor_content = latest_content

# Ensure keys always exist
if "editor_content" not in st.session_state:
    st.session_state.editor_content = latest_content

if "editing_base_content" not in st.session_state:
    st.session_state.editing_base_content = latest_content

if "editing_base_version_id" not in st.session_state:
    st.session_state.editing_base_version_id = latest_version_id

# -----------------------------
# Auto update if no local edits
# -----------------------------
if (
    latest_version_id != st.session_state.editing_base_version_id
    and st.session_state.editor_content == st.session_state.editing_base_content
):
    st.session_state.editing_base_version_id = latest_version_id
    st.session_state.editing_base_content = latest_content
    st.session_state.editor_content = latest_content
    st.rerun()



# -----------------------------
# Editor widget
# -----------------------------
content = st.text_area(
    "Content",
    height=400,
    key="editor_content"
)

col1, col2, col3 = st.columns([3, 3, 3])
# -----------------------------
# Save new version
# -----------------------------
with col1:
    if st.button("Save New Version"):
        try:
            new_version = api_client.add_version(
                document_id,
                content,
                st.session_state.editing_base_version_id
            )

            # update base after successful save
            st.session_state.editing_base_version_id = new_version["id"]
            st.session_state.editing_base_content = content

            st.success("Version saved")
            st.rerun()

        except Exception:
            st.error("Conflict detected! Document was modified by another user.")

with col2:
    if latest_version_id != st.session_state.editing_base_version_id:
        st.warning("New version available!")
with col3:
    if st.button("Load Latest Version"):
        st.session_state.pending_revert_content = latest_content
        st.session_state.pending_revert_version_id = latest_version_id
        st.rerun()

# -----------------------------
# Version history
# -----------------------------
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
        if version["id"] == latest_version_id:
            st.write("Latest")
        else:
            if st.button("Revert", key=f"revert_{version['id']}"):
                new_version = api_client.revert_version(
                    document_id,
                    version["id"]
                )

                st.session_state.pending_revert_content = new_version["content"]
                st.session_state.pending_revert_version_id = new_version["id"]

                st.success("Reverted")
                st.rerun()

if "current_diff" in st.session_state:
    st.subheader("Changes")
    render_colored_diff(st.session_state.current_diff)


# -----------------------------
# Back button
# -----------------------------
if st.button("⬅ Back to Documents"):
    st.switch_page("pages/documents.py")
