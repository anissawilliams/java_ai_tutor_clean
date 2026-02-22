"""
Difficulty Analysis Script
Query and analyze quiz performance by difficulty level
"""

import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from database_difficulty_functions import (
    get_difficulty_stats_by_condition,
    get_all_difficulty_stats,
    export_difficulty_data_csv
)


# Initialize Firebase
def init_firebase():
    cred = credentials.Certificate('.streamlit/secrets.toml')  # Update path
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'YOUR_DATABASE_URL'  # Update this
    })


# ============================================================================
# EXAMPLE QUERIES
# ============================================================================

def example_query_1():
    """How many students in each condition answered difficulty level 4 correctly?"""
    
    print("="*60)
    print("QUERY: Performance on Difficulty Level 4 (Hard)")
    print("="*60)
    
    # ArrayList
    print("\n📚 ArrayList - Difficulty 4:")
    stats = get_difficulty_stats_by_condition('arraylist', 4)
    for condition, data in stats.items():
        print(f"  {condition}: {data['correct']}/{data['total']} correct ({data['percentage']}%)")
    
    # Recursion
    print("\n🔄 Recursion - Difficulty 4:")
    stats = get_difficulty_stats_by_condition('recursion', 4)
    for condition, data in stats.items():
        print(f"  {condition}: {data['correct']}/{data['total']} correct ({data['percentage']}%)")


def example_query_2():
    """Get comprehensive stats for all difficulty levels"""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE DIFFICULTY ANALYSIS - ArrayList")
    print("="*60)
    
    stats = get_all_difficulty_stats('arraylist')
    
    # Print by difficulty level
    print("\n📊 Performance by Difficulty Level:")
    for difficulty in range(1, 6):
        print(f"\n  Difficulty {difficulty}:")
        level_stats = stats['by_difficulty'].get(difficulty, {})
        for condition, data in level_stats.items():
            print(f"    {condition}: {data['correct']}/{data['total']} ({data['percentage']}%)")
    
    # Print overall averages
    print("\n📈 Average Difficulty of Correct/Incorrect Answers:")
    for condition, data in stats['overall'].items():
        print(f"  {condition} (n={data['n_students']}):")
        print(f"    Correct answers avg difficulty: {data['avg_difficulty_correct']}")
        print(f"    Incorrect answers avg difficulty: {data['avg_difficulty_incorrect']}")


def example_query_3():
    """Export all data to CSV for deeper analysis"""
    
    print("\n" + "="*60)
    print("EXPORTING DATA TO CSV")
    print("="*60)
    
    # Export ArrayList data
    df_arraylist = export_difficulty_data_csv('arraylist', 'arraylist_difficulty_data.csv')
    print(f"\n✅ ArrayList data exported: {len(df_arraylist)} rows")
    
    # Export Recursion data  
    df_recursion = export_difficulty_data_csv('recursion', 'recursion_difficulty_data.csv')
    print(f"✅ Recursion data exported: {len(df_recursion)} rows")
    
    # Quick analysis
    print("\n📊 Quick Analysis:")
    print(f"\nArrayList - Accuracy by difficulty:")
    print(df_arraylist.groupby('difficulty')['is_correct'].mean().round(3))
    
    print(f"\nRecursion - Accuracy by difficulty:")
    print(df_recursion.groupby('difficulty')['is_correct'].mean().round(3))


def example_query_4():
    """Compare conditions on hard questions only"""
    
    print("\n" + "="*60)
    print("PERFORMANCE ON HARD QUESTIONS (Difficulty 4-5)")
    print("="*60)
    
    # Get all data
    df = export_difficulty_data_csv('arraylist')
    
    # Filter to hard questions
    hard_questions = df[df['difficulty'] >= 4]
    
    # Group by condition
    print("\n📚 ArrayList - Hard Questions Performance:")
    for condition in [1, 2, 3]:
        condition_data = hard_questions[hard_questions['condition'] == condition]
        accuracy = condition_data['is_correct'].mean() * 100
        n_students = len(condition_data['user_id'].unique())
        print(f"  Condition {condition}: {accuracy:.1f}% accuracy (n={n_students} students)")


# ============================================================================
# CUSTOM QUERIES
# ============================================================================

def custom_query_difficulty_progression():
    """Did students get harder questions right more often in certain conditions?"""
    
    df = export_difficulty_data_csv('arraylist')
    
    print("\n" + "="*60)
    print("DIFFICULTY PROGRESSION ANALYSIS")
    print("="*60)
    
    # Calculate accuracy by difficulty for each condition
    for condition in [1, 2, 3]:
        condition_data = df[df['condition'] == condition]
        print(f"\nCondition {condition}:")
        
        for diff in range(1, 6):
            diff_data = condition_data[condition_data['difficulty'] == diff]
            if len(diff_data) > 0:
                accuracy = diff_data['is_correct'].mean() * 100
                n = len(diff_data)
                print(f"  Difficulty {diff}: {accuracy:.1f}% (n={n})")


def custom_query_by_email(email: str):
    """Get difficulty breakdown for a specific student"""
    
    df_arraylist = export_difficulty_data_csv('arraylist')
    df_recursion = export_difficulty_data_csv('recursion')
    
    print(f"\n{'='*60}")
    print(f"STUDENT PERFORMANCE: {email}")
    print(f"{'='*60}")
    
    # ArrayList
    student_arraylist = df_arraylist[df_arraylist['email'] == email]
    if len(student_arraylist) > 0:
        print("\n📚 ArrayList:")
        for _, row in student_arraylist.iterrows():
            status = "✅" if row['is_correct'] else "❌"
            print(f"  Q{row['question_number']+1} (Difficulty {row['difficulty']}): {status}")
        
        avg_diff_correct = student_arraylist[student_arraylist['is_correct']]['difficulty'].mean()
        avg_diff_incorrect = student_arraylist[~student_arraylist['is_correct']]['difficulty'].mean()
        print(f"  Avg difficulty of correct: {avg_diff_correct:.1f}")
        print(f"  Avg difficulty of incorrect: {avg_diff_incorrect:.1f}")
    
    # Recursion
    student_recursion = df_recursion[df_recursion['email'] == email]
    if len(student_recursion) > 0:
        print("\n🔄 Recursion:")
        for _, row in student_recursion.iterrows():
            status = "✅" if row['is_correct'] else "❌"
            print(f"  Q{row['question_number']+1} (Difficulty {row['difficulty']}): {status}")
        
        avg_diff_correct = student_recursion[student_recursion['is_correct']]['difficulty'].mean()
        avg_diff_incorrect = student_recursion[~student_recursion['is_correct']]['difficulty'].mean()
        print(f"  Avg difficulty of correct: {avg_diff_correct:.1f}")
        print(f"  Avg difficulty of incorrect: {avg_diff_incorrect:.1f}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Initialize Firebase
    init_firebase()
    
    # Run example queries
    print("\n🔍 RUNNING DIFFICULTY ANALYSIS QUERIES\n")
    
    example_query_1()  # Difficulty 4 performance
    example_query_2()  # Comprehensive stats
    example_query_3()  # Export to CSV
    example_query_4()  # Hard questions comparison
    
    # Custom queries
    custom_query_difficulty_progression()
    
    # Query specific student
    # custom_query_by_email('student1@cofc.edu')
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
