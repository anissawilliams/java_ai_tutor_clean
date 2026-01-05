# views/login.py

import streamlit as st

def render_login_page():
    st.title("Java Learning Research Study")
    st.write("Please log in to continue.")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if email and password:
            st.session_state.handle_login(email, password)
        else:
            st.error("Please enter both email and password.")