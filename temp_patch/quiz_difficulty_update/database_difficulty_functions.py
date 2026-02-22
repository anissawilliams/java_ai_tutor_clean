# Add this to your database.py file

def save_quiz_responses(user_id: str, session_id: str, responses: Dict, 
                       score: int, total: int, results: List = None):
    """
    Save quiz responses, score, and difficulty breakdown.
    
    Args:
        user_id: User ID
        session_id: Session ID (arraylist or recursion)
        responses: Dict of question index -> user answer
        score: Number correct
        total: Total questions
        results: List of result dicts from score_quiz (includes difficulty)
    """
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        
        # Basic quiz data
        quiz_data = {
            'quiz_responses': responses,
            'quiz_score': score,
            'quiz_total': total,
            'quiz_percentage': round((score / total) * 100, 1) if total > 0 else 0,
            'quiz_completed_time': time.time()
        }
        
        # Add difficulty breakdown if results provided
        if results:
            difficulty_breakdown = calculate_difficulty_breakdown(results)
            quiz_data['difficulty_breakdown'] = difficulty_breakdown
            
            # Also save individual question details
            quiz_data['question_details'] = []
            for i, result in enumerate(results):
                quiz_data['question_details'].append({
                    'question_number': i,
                    'difficulty': result.get('difficulty', 0),
                    'is_correct': result.get('is_correct', False),
                    'user_answer': result.get('user_answer', ''),
                })
        
        ref.update(quiz_data)
        
    except Exception as e:
        st.error(f"Error saving quiz responses: {e}")


def calculate_difficulty_breakdown(results: List[Dict]) -> Dict:
    """
    Calculate performance by difficulty level.
    
    Returns:
        {
            'by_level': {
                1: {'correct': 2, 'total': 2, 'percentage': 100},
                2: {'correct': 1, 'total': 2, 'percentage': 50},
                ...
            },
            'average_difficulty_correct': 2.3,  # Avg difficulty of correct answers
            'average_difficulty_incorrect': 3.8  # Avg difficulty of incorrect answers
        }
    """
    breakdown = {
        'by_level': {},
        'average_difficulty_correct': 0,
        'average_difficulty_incorrect': 0
    }
    
    # Count by difficulty level
    difficulty_stats = {}
    correct_difficulties = []
    incorrect_difficulties = []
    
    for result in results:
        diff = result.get('difficulty', 0)
        is_correct = result.get('is_correct', False)
        
        # Track by level
        if diff not in difficulty_stats:
            difficulty_stats[diff] = {'correct': 0, 'total': 0}
        
        difficulty_stats[diff]['total'] += 1
        if is_correct:
            difficulty_stats[diff]['correct'] += 1
            correct_difficulties.append(diff)
        else:
            incorrect_difficulties.append(diff)
    
    # Convert to percentages
    for level, stats in difficulty_stats.items():
        breakdown['by_level'][level] = {
            'correct': stats['correct'],
            'total': stats['total'],
            'percentage': round((stats['correct'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0
        }
    
    # Calculate averages
    if correct_difficulties:
        breakdown['average_difficulty_correct'] = round(sum(correct_difficulties) / len(correct_difficulties), 2)
    
    if incorrect_difficulties:
        breakdown['average_difficulty_incorrect'] = round(sum(incorrect_difficulties) / len(incorrect_difficulties), 2)
    
    return breakdown


# ============================================================================
# QUERY FUNCTIONS FOR DIFFICULTY ANALYSIS
# ============================================================================

def get_difficulty_stats_by_condition(topic: str, difficulty_level: int) -> Dict:
    """
    Query: How many students answered a specific difficulty level correctly, by condition?
    
    Args:
        topic: 'arraylist' or 'recursion'
        difficulty_level: 1-5
    
    Returns:
        {
            'condition_1': {'correct': 15, 'total': 20, 'percentage': 75},
            'condition_2': {'correct': 12, 'total': 20, 'percentage': 60},
            'condition_3': {'correct': 10, 'total': 20, 'percentage': 50}
        }
    """
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}
        
        stats = {
            'condition_1': {'correct': 0, 'total': 0},
            'condition_2': {'correct': 0, 'total': 0},
            'condition_3': {'correct': 0, 'total': 0}
        }
        
        for user_id, user_data in all_users.items():
            condition = user_data.get('condition', 0)
            if condition not in [1, 2, 3]:
                continue
            
            session_data = user_data.get('sessions', {}).get(topic, {})
            question_details = session_data.get('question_details', [])
            
            for q in question_details:
                if q.get('difficulty') == difficulty_level:
                    stats[f'condition_{condition}']['total'] += 1
                    if q.get('is_correct'):
                        stats[f'condition_{condition}']['correct'] += 1
        
        # Add percentages
        for condition_key in stats:
            total = stats[condition_key]['total']
            if total > 0:
                stats[condition_key]['percentage'] = round(
                    (stats[condition_key]['correct'] / total) * 100, 1
                )
            else:
                stats[condition_key]['percentage'] = 0
        
        return stats
        
    except Exception as e:
        print(f"Error getting difficulty stats: {e}")
        return {}


def get_all_difficulty_stats(topic: str) -> Dict:
    """
    Get comprehensive difficulty statistics for a topic.
    
    Returns:
        {
            'by_difficulty': {
                1: {'condition_1': {...}, 'condition_2': {...}, 'condition_3': {...}},
                2: {...},
                ...
            },
            'overall': {
                'condition_1': {'avg_difficulty_correct': 2.3, 'avg_difficulty_incorrect': 3.8},
                'condition_2': {...},
                'condition_3': {...}
            }
        }
    """
    result = {
        'by_difficulty': {},
        'overall': {}
    }
    
    # Get stats for each difficulty level
    for difficulty in range(1, 6):  # 1-5
        result['by_difficulty'][difficulty] = get_difficulty_stats_by_condition(topic, difficulty)
    
    # Get overall averages
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}
        
        condition_avgs = {
            'condition_1': {'correct': [], 'incorrect': []},
            'condition_2': {'correct': [], 'incorrect': []},
            'condition_3': {'correct': [], 'incorrect': []}
        }
        
        for user_id, user_data in all_users.items():
            condition = user_data.get('condition', 0)
            if condition not in [1, 2, 3]:
                continue
            
            session_data = user_data.get('sessions', {}).get(topic, {})
            breakdown = session_data.get('difficulty_breakdown', {})
            
            avg_correct = breakdown.get('average_difficulty_correct', 0)
            avg_incorrect = breakdown.get('average_difficulty_incorrect', 0)
            
            if avg_correct > 0:
                condition_avgs[f'condition_{condition}']['correct'].append(avg_correct)
            if avg_incorrect > 0:
                condition_avgs[f'condition_{condition}']['incorrect'].append(avg_incorrect)
        
        # Calculate overall averages
        for condition_key, avgs in condition_avgs.items():
            result['overall'][condition_key] = {
                'avg_difficulty_correct': round(sum(avgs['correct']) / len(avgs['correct']), 2) if avgs['correct'] else 0,
                'avg_difficulty_incorrect': round(sum(avgs['incorrect']) / len(avgs['incorrect']), 2) if avgs['incorrect'] else 0,
                'n_students': len(avgs['correct'])
            }
    
    except Exception as e:
        print(f"Error calculating overall stats: {e}")
    
    return result


def export_difficulty_data_csv(topic: str, output_file: str = None):
    """
    Export difficulty data to CSV for analysis.
    
    Columns: user_id, email, condition, question_number, difficulty, is_correct, user_answer
    """
    import pandas as pd
    
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}
        
        rows = []
        
        for user_id, user_data in all_users.items():
            email = user_data.get('email', '')
            condition = user_data.get('condition', 0)
            
            session_data = user_data.get('sessions', {}).get(topic, {})
            question_details = session_data.get('question_details', [])
            
            for q in question_details:
                rows.append({
                    'user_id': user_id,
                    'email': email,
                    'condition': condition,
                    'question_number': q.get('question_number', 0),
                    'difficulty': q.get('difficulty', 0),
                    'is_correct': q.get('is_correct', False),
                    'user_answer': q.get('user_answer', '')
                })
        
        df = pd.DataFrame(rows)
        
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Exported to {output_file}")
        
        return df
        
    except Exception as e:
        print(f"Error exporting difficulty data: {e}")
        return None
