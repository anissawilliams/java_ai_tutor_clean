"""
Bulk Firebase User Creation Script
Creates users from CSV/Excel file with email, password, and condition assignment
"""
import os

import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, db
import sys

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


def create_users_from_csv(csv_file, default_password="Cougars2026"):
    """
    Create Firebase users from CSV file.
    
    CSV format:
    email,condition
    student1@cofc.edu,1
    student2@cofc.edu,2
    student3@cofc.edu,3
    """
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    results = {
        'created': [],
        'failed': [],
        'already_exist': []
    }
    
    for index, row in df.iterrows():
        email = row['email'].strip()
        condition = int(row['condition'])
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=default_password,
                email_verified=False
            )
            
            print(f"✅ Created user: {email} (UID: {user.uid})")
            
            # Add user to Realtime Database with condition
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'email': email,
                'condition': condition,
                'condition_name': get_condition_name(condition),
                'assigned_date': pd.Timestamp.now().isoformat(),
                'sessions': {
                    'arraylist': {'status': 'not_started'},
                    'recursion': {'status': 'not_started'}
                }
            })
            
            results['created'].append({
                'email': email,
                'uid': user.uid,
                'condition': condition,
                'password': default_password
            })
            
        except auth.EmailAlreadyExistsError:
            print(f"⚠️  User already exists: {email}")
            # Update their condition anyway
            try:
                existing_user = auth.get_user_by_email(email)
                user_ref = db.reference(f'users/{existing_user.uid}')
                user_ref.update({
                    'condition': condition,
                    'condition_name': get_condition_name(condition)
                })
                results['already_exist'].append(email)
            except Exception as e:
                print(f"❌ Error updating existing user {email}: {e}")
                results['failed'].append({'email': email, 'error': str(e)})
                
        except Exception as e:
            print(f"❌ Error creating user {email}: {e}")
            results['failed'].append({'email': email, 'error': str(e)})
    
    return results


def create_users_from_excel(excel_file, sheet_name=0, default_password="JavaStudy2025"):
    """
    Create Firebase users from Excel file.
    
    Excel format (Sheet 1):
    | email              | condition |
    |--------------------|-----------|
    | student1@cofc.edu  | 1         |
    | student2@cofc.edu  | 2         |
    | student3@cofc.edu  | 3         |
    """
    
    # Read Excel
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Use same logic as CSV
    return create_users_from_dataframe(df, default_password)


def create_users_from_dataframe(df, default_password="Cougars2026"):
    """Create users from pandas DataFrame"""
    
    results = {
        'created': [],
        'failed': [],
        'already_exist': []
    }
    
    for index, row in df.iterrows():
        email = row['email'].strip()
        condition = int(row['condition'])
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=default_password,
                email_verified=False
            )
            
            print(f"✅ Created: {email} → Condition {condition} (UID: {user.uid})")
            
            # Add to database with condition
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'email': email,
                'condition': condition,
                'condition_name': get_condition_name(condition),
                'assigned_date': pd.Timestamp.now().isoformat(),
                'sessions': {
                    'arraylist': {'status': 'not_started'},
                    'recursion': {'status': 'not_started'}
                }
            })
            
            results['created'].append({
                'email': email,
                'uid': user.uid,
                'condition': condition,
                'password': default_password
            })
            
        except auth.EmailAlreadyExistsError:
            print(f"⚠️  Already exists: {email} - Updating condition to {condition}")
            try:
                existing_user = auth.get_user_by_email(email)
                user_ref = db.reference(f'users/{existing_user.uid}')
                user_ref.update({
                    'condition': condition,
                    'condition_name': get_condition_name(condition)
                })
                results['already_exist'].append({
                    'email': email,
                    'condition': condition
                })
            except Exception as e:
                print(f"❌ Error updating {email}: {e}")
                results['failed'].append({'email': email, 'error': str(e)})
                
        except Exception as e:
            print(f"❌ Error creating {email}: {e}")
            results['failed'].append({'email': email, 'error': str(e)})
    
    return results


def get_condition_name(condition):
    """Get readable condition name"""
    conditions = {
        1: "character_scaffolded",
        2: "non_character_scaffolded",
        3: "direct_chat"
    }
    return conditions.get(condition, "unknown")


def print_summary(results):
    """Print summary of user creation"""
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Created: {len(results['created'])} users")
    print(f"⚠️  Already existed: {len(results['already_exist'])} users")
    print(f"❌ Failed: {len(results['failed'])} users")
    print("="*60)
    
    if results['created']:
        print("\n📋 CREATED USERS:")
        for user in results['created']:
            print(f"  {user['email']} → Condition {user['condition']} (Password: {user['password']})")
    
    if results['failed']:
        print("\n❌ FAILED:")
        for failure in results['failed']:
            print(f"  {failure['email']}: {failure['error']}")


def export_credentials(results, output_file='user_credentials.csv'):
    """Export created user credentials to CSV"""
    if results['created']:
        df = pd.DataFrame(results['created'])
        df.to_csv(output_file, index=False)
        print(f"\n💾 Credentials exported to: {output_file}")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    # Initialize Firebase
    init_firebase()
    
    # OPTION 1: From CSV file
    #csv_file = sys.argv[1] if len(sys.argv) > 1 else 'test_user_load.csv'
    csv_file = 'section2_cleaned.csv'
    results = create_users_from_csv(csv_file, default_password='Cougars2026')
    
    # OPTION 2: From Excel file
    # results = create_users_from_excel('students.xlsx', default_password='JavaStudy2025')
    
    # Print summary
    print_summary(results)
    
    # Export credentials
    export_credentials(results, 'created_users_section_2.csv')
    
    print("\n✅ Done! Users can now login with their email and password: Cougars2026")
