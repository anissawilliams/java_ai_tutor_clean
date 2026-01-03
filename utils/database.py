"""
Database Operations
Handle all data storage and retrieval for the research study
"""

import time
from firebase_admin import db
import streamlit as st
from typing import Optional, Dict, List


def save_session_start(user_id: str, session_id: str, condition: int):
    """Record that a session has started."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'status': 'in_progress',
            'start_time': time.time(),
            'condition': condition,
            'messages': [],
            'scaffold_progress': []
        })
    except Exception as e:
        st.error(f"Error saving session start: {e}")


def save_message(user_id: str, session_id: str, role: str, content: str, 
                 step: Optional[str] = None):
    """Save a conversation message."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}/messages')
        
        message_data = {
            'role': role,
            'content': content,
            'timestamp': time.time()
        }
        
        if step:
            message_data['step'] = step
        
        # Get current messages
        messages = ref.get() or []
        messages.append(message_data)
        
        # Save back
        ref.set(messages)
        
    except Exception as e:
        st.error(f"Error saving message: {e}")


def save_scaffold_progress(user_id: str, session_id: str, step: str):
    """Record scaffold step progression."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}/scaffold_progress')
        
        progress_data = {
            'step': step,
            'timestamp': time.time()
        }
        
        # Get current progress
        progress = ref.get() or []
        progress.append(progress_data)
        
        # Save back
        ref.set(progress)
        
    except Exception as e:
        st.error(f"Error saving scaffold progress: {e}")


def save_quiz_responses(user_id: str, session_id: str, responses: Dict, score: int, total: int):
    """Save quiz responses and score."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'quiz_responses': responses,
            'quiz_score': score,
            'quiz_total': total,
            'quiz_completed_time': time.time()
        })
    except Exception as e:
        st.error(f"Error saving quiz responses: {e}")


def save_survey_responses(user_id: str, session_id: str, responses: Dict):
    """Save survey responses."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'survey_responses': responses,
            'survey_completed_time': time.time()
        })
    except Exception as e:
        st.error(f"Error saving survey responses: {e}")


def complete_session(user_id: str, session_id: str):
    """Mark a session as complete."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        
        # Get session data
        session_data = ref.get()
        
        if session_data:
            start_time = session_data.get('start_time', time.time())
            duration = time.time() - start_time
            
            # Count messages
            messages = session_data.get('messages', [])
            user_messages = sum(1 for m in messages if m['role'] == 'user')
            assistant_messages = sum(1 for m in messages if m['role'] == 'assistant')
            
            ref.update({
                'status': 'completed',
                'end_time': time.time(),
                'duration_seconds': duration,
                'total_messages': len(messages),
                'user_messages': user_messages,
                'assistant_messages': assistant_messages
            })
    except Exception as e:
        st.error(f"Error completing session: {e}")


def get_session_status(user_id: str, session_id: str) -> str:
    """
    Get the status of a session.
    
    Returns: 'not_started', 'in_progress', 'completed'
    """
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        session_data = ref.get()
        
        if not session_data:
            return 'not_started'
        
        return session_data.get('status', 'not_started')
        
    except Exception as e:
        st.error(f"Error getting session status: {e}")
        return 'not_started'


def get_next_session(user_id: str) -> Optional[str]:
    """
    Determine which session the user should do next.
    
    Returns: 'arraylist', 'recursion', or None if all complete
    """
    try:
        # Check ArrayList
        arraylist_status = get_session_status(user_id, 'arraylist')
        if arraylist_status != 'completed':
            return 'arraylist'
        
        # Check Recursion
        recursion_status = get_session_status(user_id, 'recursion')
        if recursion_status != 'completed':
            return 'recursion'
        
        # Both complete
        return None
        
    except Exception as e:
        st.error(f"Error getting next session: {e}")
        return 'arraylist'  # Default to first session


def get_all_users() -> Dict:
    """Get all user data (admin only)."""
    try:
        ref = db.reference('users')
        return ref.get() or {}
    except Exception as e:
        st.error(f"Error getting all users: {e}")
        return {}


def get_user_condition(user_id: str) -> int:
    """Get the condition assigned to a user."""
    try:
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get()
        
        if user_data and 'condition' in user_data:
            return user_data['condition']
        
        # If no condition, something went wrong
        return 1
        
    except Exception as e:
        st.error(f"Error getting user condition: {e}")
        return 1


def export_data_to_dict() -> List[Dict]:
    """
    Export all data for analysis.
    
    Returns list of dicts, one per session completion.
    """
    try:
        all_users = get_all_users()
        export_data = []
        
        for user_id, user_data in all_users.items():
            email = user_data.get('email', '')
            condition = user_data.get('condition', 0)
            condition_name = user_data.get('condition_name', '')
            
            sessions = user_data.get('sessions', {})
            
            for session_id, session_data in sessions.items():
                if session_data.get('status') == 'completed':
                    messages = session_data.get('messages', [])
                    
                    row = {
                        'user_id': user_id,
                        'email': email,
                        'condition': condition,
                        'condition_name': condition_name,
                        'topic': session_id,
                        'session_start': session_data.get('start_time', ''),
                        'session_end': session_data.get('end_time', ''),
                        'duration_seconds': session_data.get('duration_seconds', 0),
                        'duration_minutes': round(session_data.get('duration_seconds', 0) / 60, 2),
                        'total_messages': session_data.get('total_messages', 0),
                        'user_messages': session_data.get('user_messages', 0),
                        'assistant_messages': session_data.get('assistant_messages', 0),
                        'scaffold_steps_completed': len(session_data.get('scaffold_progress', [])),
                        'quiz_score': session_data.get('quiz_score', 0),
                        'quiz_total': session_data.get('quiz_total', 0),
                        'quiz_percentage': round((session_data.get('quiz_score', 0) / session_data.get('quiz_total', 1)) * 100, 1),
                        'survey_responses': str(session_data.get('survey_responses', {})),
                        'completed': True
                    }
                    
                    export_data.append(row)
        
        return export_data
        
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return []
