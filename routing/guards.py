# routing/guards.py

import streamlit as st
from views.admin import is_admin


def login_required() -> bool:
    """Return True if the user is logged in."""
    return bool(st.session_state.get("logged_in"))


def admin_only() -> bool:
    """Return True if the logged-in user is an admin."""
    email = st.session_state.get("email")
    return email is not None and is_admin(email)