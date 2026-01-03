"""
Firebase Configuration
Uses Streamlit secrets for secure credential management
"""

import streamlit as st
import json

try:
    FIREBASE_CONFIG = {
        "apiKey": st.secrets["firebase"]["apiKey"],
        "authDomain": st.secrets["firebase"]["authDomain"],
        "projectId": st.secrets["firebase"]["projectId"],
        "storageBucket": st.secrets["firebase"]["storageBucket"],
        "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
        "appId": st.secrets["firebase"]["appId"],
        "databaseURL": st.secrets["firebase"]["databaseURL"]
    }
    
    SERVICE_ACCOUNT_KEY = dict(st.secrets["firebase"]["serviceAccount"])
    
except Exception as e:
    st.error(f"""
    Firebase credentials not found in secrets!
    
    Please set up your secrets:
    
    **Local Development:**
    1. Create `.streamlit/secrets.toml` file
    2. Copy the template from `.streamlit/secrets.toml.example`
    3. Fill in your Firebase credentials
    
    **Streamlit Cloud:**
    1. Go to App Settings > Secrets
    2. Add your Firebase credentials in TOML format
    
    Error: {e}
    """)
    
    # Provide fallback empty config to prevent crashes
    FIREBASE_CONFIG = {
        "apiKey": "NOT_CONFIGURED",
        "authDomain": "",
        "projectId": "",
        "storageBucket": "",
        "messagingSenderId": "",
        "appId": "",
        "databaseURL": ""
    }
    SERVICE_ACCOUNT_KEY = {}

"""
SECRETS.TOML FORMAT:

[firebase]
apiKey = "YOUR_API_KEY"
authDomain = "YOUR_PROJECT_ID.firebaseapp.com"
projectId = "YOUR_PROJECT_ID"
storageBucket = "YOUR_PROJECT_ID.appspot.com"
messagingSenderId = "YOUR_MESSAGING_SENDER_ID"
appId = "YOUR_APP_ID"
databaseURL = "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com"

[firebase.serviceAccount]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = '''-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----'''
client_email = "YOUR_CLIENT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
"""

# Database Rules (add these to Firebase Realtime Database Rules)
DATABASE_RULES = """
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "admin": {
      ".read": "auth != null && root.child('admins').child(auth.uid).exists()",
      ".write": "auth != null && root.child('admins').child(auth.uid).exists()"
    }
  }
}
"""

