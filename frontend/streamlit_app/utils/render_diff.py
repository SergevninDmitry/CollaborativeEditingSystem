import html
import streamlit as st


def render_colored_diff(diff_text: str):
    lines = diff_text.splitlines()
    html_lines = []

    for line in lines:
        escaped = html.escape(line)

        # diff headers
        if line.startswith("---") or line.startswith("+++"):
            html_lines.append(
                f'<div style="color:#666;font-weight:bold;padding:2px 6px;">{escaped}</div>'
            )

        # added lines
        elif line.startswith("+"):
            html_lines.append(
                f'<div style="background:#d4f8d4;color:#000;padding:2px 6px;white-space:pre;">{escaped}</div>'
            )

        # removed lines
        elif line.startswith("-"):
            html_lines.append(
                f'<div style="background:#f8d4d4;color:#000;padding:2px 6px;white-space:pre;">{escaped}</div>'
            )

        # context lines
        else:
            html_lines.append(
                f'<div style="color:#000;padding:2px 6px;white-space:pre;">{escaped}</div>'
            )

    container = (
            '<div style="'
            'font-family:monospace;'
            'font-size:14px;'
            'line-height:1.4;'
            'border:1px solid #ddd;'
            'border-radius:6px;'
            'overflow-x:auto;'
            'background:#fafafa;'
            '">'
            + "".join(html_lines)
            + "</div>"
    )

    st.markdown(container, unsafe_allow_html=True)
