import os
import firebase_admin
from firebase_admin import credentials, firestore, db

# Initialize Firebase Admin SDK

def init_firebase():
    """Initialize Firebase - update path to your service account key"""
    try:
        path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
        cred = credentials.Certificate(path)
    except:
        # Alternative: use secrets dict
        import streamlit as st
        firebase_cfg = st.secrets["firebase"]
        service_account_info = {
            "type": firebase_cfg["type"],
            "project_id": firebase_cfg["project_id"],
            "private_key_id": firebase_cfg["private_key_id"],
            "private_key": firebase_cfg["private_key"],
            "client_email": firebase_cfg["client_email"],
            "client_id": firebase_cfg["client_id"],
            "auth_uri": firebase_cfg["auth_uri"],
            "token_uri": firebase_cfg["token_uri"],
            "auth_provider_x509_cert_url": firebase_cfg["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_cfg["client_x509_cert_url"],
        }
        cred = credentials.Certificate(service_account_info)

    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_cfg["databaseURL"]  # Update this
    })


if __name__ == "__main__":
        # Initialize Firebase
    init_firebase()




