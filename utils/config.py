"""
Research Study Configuration
Core settings for the Java learning research study
"""

# Session Configuration
SESSION_DURATION = 15 * 60  # 10 minutes for learning
QUIZ_TIME_ESTIMATE = 10 * 60  # ~5 minutes for quiz (no hard limit)
SURVEY_TIME_ESTIMATE = 5 * 60  # ~3 minutes for survey

# Session Available Dates
SESSION_1_START = '2026-01-22'
SESSION_2_START = '2026-01-29'


# Study Configuration
TOTAL_PARTICIPANTS = 60
PARTICIPANTS_PER_CONDITION = 20

# Conditions
CONDITIONS = {
    1: "character_scaffolded",      # Treatment 1: Character + Scaffolding
    2: "non_character_scaffolded",  # Treatment 2: No Character + Scaffolding
    3: "direct_chat"                # Control: No Character, No Scaffolding
}

# Manual Condition Assignments
# Add student emails here with their assigned condition
MANUAL_CONDITION_ASSIGNMENTS = {
    # Example:
    # "student1@cofc.edu": 1,
    # "student2@cofc.edu": 2,
    # "student3@cofc.edu": 3,
    
    # Researcher/testing accounts (you can delete these from Firebase later)
    "anissawilliamschs@gmail.com": 1,
    "anissaewilliams@gmail.com": 2,
    "hashemi@cofc.edu": 1,
}

# Session Sequence
SESSIONS = {
    'session_1': {
        'id': 'arraylist',
        'name': 'Dynamic ArrayList',
        'start_date': SESSION_1_START,
        'topic_key': 'arraylist',
        'difficulty': 'easy',
        'order': 1,
        'description': 'Learn about dynamically sizing ArrayLists in Java'
    },
    'session_2': {
        'id': 'recursion',
        'name': 'Recursion',
        'start_date': SESSION_2_START,
        'topic_key': 'recursion',
        'difficulty': 'hard',
        'order': 2,
        'description': 'Learn about recursive functions in Java',
        'requires_completion': 'session_1'  # Must complete ArrayList first
    }
}

# Data Collection
COLLECT_DATA = {
    'messages': True,           # All conversation messages
    'timestamps': True,         # Timestamp every interaction
    'scaffold_progress': True,  # Step progression (conditions 1 & 2)
    'quiz_responses': True,     # Quiz answers
    'survey_responses': True,   # Survey answers
    'session_duration': True,   # Time spent
    'interaction_count': True   # Number of messages
}

# Export Settings
EXPORT_FORMAT = 'csv'
EXPORT_INCLUDE = [
    'user_id',
    'email',
    'condition',
    'topic',
    'session_start',
    'session_end',
    'duration_minutes',
    'message_count',
    'user_message_count',
    'assistant_message_count',
    'scaffold_steps_completed',
    'quiz_score',
    'quiz_total',
    'survey_responses',
    'completed'
]

# UI Settings
SHOW_DEBUG_INFO = False  # Set to True for testing, False for production
SHOW_SKIP_BUTTONS = True  # Set to True to enable "Skip to Quiz" button
REQUIRE_EMAIL_VERIFICATION = False  # Set to True if using email verification
ALLOW_MULTIPLE_ATTEMPTS = False  # Students can only do each session once

# Study Information (shown to students)
STUDY_INFO = {
    'title': 'Java Learning Research Study',
    'description': 'Help us understand how different teaching methods affect learning!',
    'institution': 'College of Charleston',
    'estimated_time': '~18 minutes per session (2 sessions total)',
    'contact': 'researcher@cofc.edu'
}