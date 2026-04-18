"""
Migration Script: Add Queue Session to All Existing Users
Run once to ensure all users have the queue session in Firebase.
Does NOT touch existing arraylist or recursion progress.

Usage:
    python add_queue_migration.py
"""

import os
import sys
import toml
import firebase_admin
from firebase_admin import credentials, db


def init_firebase():
    """Initialize Firebase from .streamlit/secrets.toml"""
    secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')

    if not os.path.exists(secrets_path):
        print(f"❌ Could not find secrets file at: {secrets_path}")
        print("Make sure you run this from your project root directory.")
        sys.exit(1)

    secrets = toml.load(secrets_path)
    firebase_cfg = secrets["firebase"]

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
        'databaseURL': firebase_cfg["databaseURL"]
    })
    print("✅ Firebase initialized.\n")


def add_queue_session_all_users():
    """Add queue session to all existing users without touching other sessions"""
    admins_emails = [
        "anissaewilliams@gmail.com",
        "anissawilliamschs@gmail.com",
        "hashemin@cofc.edu",
        "rashidp@cofc.edu",
        "tiwaria@cofc.edu"
    ]

    users = db.reference('users').get() or {}
    updated = 0
    skipped = 0
    already_has = 0

    print(f"Found {len(users)} total users.\n")

    for uid, data in users.items():
        email = data.get('email', 'unknown')
        sessions = data.get('sessions', {})

        if 'queue' in sessions:
            print(f"⏭️  Already has queue: {email}")
            already_has += 1
        else:
            db.reference(f'users/{uid}/sessions/queue').set({'status': 'not_started'})
            print(f"✅ Added queue session: {email}")
            updated += 1

    print(f"\n{'='*50}")
    print(f"MIGRATION COMPLETE")
    print(f"{'='*50}")
    print(f"✅ Updated:      {updated} users")
    print(f"⏭️  Already had:   {already_has} users")
    print(f"📊 Total users:   {len(users)}")


def reset_single_user(email):
    """Reset all sessions for a specific user"""
    users = db.reference('users').get() or {}
    for uid, data in users.items():
        if data.get('email') == email:
            print(f"Found: {email} (UID: {uid})")
            print(f"Current sessions: {data.get('sessions', {})}")
            db.reference(f'users/{uid}/sessions').set({
                'arraylist': {'status': 'not_started'},
                'recursion': {'status': 'not_started'},
                'queue': {'status': 'not_started'}
            })
            print("✅ All sessions reset!")
            return uid
    print(f"❌ User not found: {email}")
    return None


if __name__ == "__main__":
    init_firebase()

    if len(sys.argv) >= 2 and sys.argv[1] == "--reset":
        # Usage: python add_queue_migration.py --reset email@example.com
        if len(sys.argv) >= 3:
            reset_single_user(sys.argv[2])
        else:
            print("Usage: python add_queue_migration.py --reset email@example.com")
    else:
        # Default: run migration for all users
        add_queue_session_all_users()
