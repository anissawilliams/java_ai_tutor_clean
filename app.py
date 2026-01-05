# app.py

import streamlit as st
from session.state import init_session_state
from session.auth_handler import expose_handlers
from routing.router import route


def main():
    st.set_page_config(
        page_title="Java Learning Study",
        page_icon="🎓",
        layout="wide"
    )

    init_session_state()
    expose_handlers()

    route()


if __name__ == "__main__":
    main()