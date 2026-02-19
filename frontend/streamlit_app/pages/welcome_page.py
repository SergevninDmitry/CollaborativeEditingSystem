import streamlit as st


st.title("📝 Collaborative Editing System")

st.markdown("""
Welcome to the **Collaborative Editing System**.

This project is a microservice-based application that allows:

- 👤 User registration and authentication
- 📄 Collaborative document creation and editing
- 🕓 Version control and document history tracking

---

### 🔧 Technologies Used

- **FastAPI** — Backend REST API
- **Streamlit** — Frontend UI
- **PostgreSQL / SQLite** — Database
- **SQLAlchemy (async)** — ORM
- **JWT Authentication** — Secure login system

---

### 🚀 Project Goals

- Simulate real-time collaborative editing
- Maintain version history
- Track user contributions
- Demonstrate clean service architecture

---

Use the sidebar to navigate to the Login page and start using the system.
""")

st.info("Select a page from the sidebar to continue.")
if st.button("Go to login"):
    st.switch_page("pages/login.py")
