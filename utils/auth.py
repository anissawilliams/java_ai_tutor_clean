import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, auth as admin_auth

# ---------------------------------------------------------
# Firebase Initialization (Admin SDK)
# ---------------------------------------------------------

def init_firebase():
    """Initialize Firebase Admin SDK once."""
    if not firebase_admin._apps:
        # Extract only the service account fields
        firebase_cfg = st.secrets["firebase"]
        service_account_keys = {
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri",
            "auth_provider_x509_cert_url",
            "client_x509_cert_url",
        }

        service_account_info = {
            k: firebase_cfg[k] for k in service_account_keys if k in firebase_cfg
        }

        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, {
            "databaseURL": firebase_cfg["databaseURL"]
        })

init_firebase()


# ---------------------------------------------------------
# Firebase REST API Login (Email/Password)
# ---------------------------------------------------------

FIREBASE_API_KEY = st.secrets["firebase"]["apiKey"]

def firebase_login(email: str, password: str):
    """
    Authenticate a user using Firebase's REST API.
    Returns a dict containing idToken, refreshToken, localId, etc.
    Raises ValueError on failure.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        return data
    else:
        error_msg = data.get("error", {}).get("message", "Login failed")
        raise ValueError(error_msg)


# ---------------------------------------------------------
# Session Helpers
# ---------------------------------------------------------

def set_session(user_data: dict):
    """Store user login info in Streamlit session_state."""
    st.session_state["logged_in"] = True
    st.session_state["id_token"] = user_data["idToken"]
    st.session_state["refresh_token"] = user_data["refreshToken"]
    st.session_state["user_id"] = user_data["localId"]
    st.session_state["email"] = user_data.get("email")


def logout_user():
    """Clear session state."""
    for key in ["logged_in", "id_token", "refresh_token", "uid", "email"]:
        st.session_state.pop(key, None)


def require_auth():
    """Simple guard for protected pages."""
    if not st.session_state.get("logged_in"):
        st.error("You must log in to access this page.")
        st.stop()


# ---------------------------------------------------------
# User Data via Admin SDK
# ---------------------------------------------------------

def get_user_data(uid: str):
    """
    Fetch user info from Firebase Authentication using Admin SDK.
    """
    try:
        user = admin_auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "disabled": user.disabled,
            "email_verified": user.email_verified,
        }
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return None


