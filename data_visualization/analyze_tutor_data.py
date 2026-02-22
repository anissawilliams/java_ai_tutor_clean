#  """"
# Java Tutor Study Data Analysis Script
# =====================================
# Extracts and analyzes data from the Java tutor session JSON file.
# Outputs statistics that can be used in the React dashboard.
#
# Usage:
#     python analyze_tutor_data.py <path_to_json_file>
#
# Example:
#     python analyze_tutor_data.py array_list_session_data.json
# """""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Any
import statistics


def load_data(filepath: str) -> dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_completed_sessions(data: dict) -> List[Dict[str, Any]]:
    """Extract all completed arraylist sessions with their metadata."""
    completed = []
    
    for uid, user_data in data.get('users', {}).items():
        arraylist = user_data.get('sessions', {}).get('arraylist', {})
        
        if arraylist.get('status') == 'completed':
            session = {
                'uid': uid,
                'email': user_data.get('email'),
                'condition': user_data.get('condition'),
                'condition_name': user_data.get('condition_name'),
                'quiz_score': arraylist.get('quiz_score'),
                'quiz_total': arraylist.get('quiz_total'),
                'quiz_percentage': arraylist.get('quiz_percentage'),
                'duration_seconds': arraylist.get('duration_seconds'),
                'duration_minutes': arraylist.get('duration_seconds', 0) / 60,
                'total_messages': arraylist.get('total_messages'),
                'user_messages': arraylist.get('user_messages'),
                'assistant_messages': arraylist.get('assistant_messages'),
                'question_details': arraylist.get('question_details', []),
                'survey_responses': arraylist.get('survey_responses', {}),
            }
            completed.append(session)
    
    return completed


def compute_condition_stats(sessions: List[Dict]) -> Dict[str, Dict]:
    """Compute statistics grouped by condition."""
    conditions = defaultdict(lambda: {
        'scores': [],
        'durations': [],
        'messages': [],
        'surveys': [],
        'question_details': []
    })
    
    for s in sessions:
        cond = s['condition_name']
        conditions[cond]['scores'].append(s['quiz_percentage'])
        conditions[cond]['durations'].append(s['duration_minutes'])
        conditions[cond]['messages'].append(s['total_messages'])
        conditions[cond]['surveys'].append(s['survey_responses'])
        conditions[cond]['question_details'].extend(s['question_details'])
    
    # Compute aggregates
    stats = {}
    for cond, data in conditions.items():
        n = len(data['scores'])
        stats[cond] = {
            'n': n,
            'avg_score': round(sum(data['scores']) / n, 1) if n else 0,
            'score_sd': round(statistics.stdev(data['scores']), 1) if n > 1 else 0,
            'avg_duration': round(sum(data['durations']) / n, 1) if n else 0,
            'duration_sd': round(statistics.stdev(data['durations']), 1) if n > 1 else 0,
            'avg_messages': round(sum(data['messages']) / n, 1) if n else 0,
            'scores_list': data['scores'],
            'durations_list': data['durations'],
            'surveys': data['surveys'],
            'question_details': data['question_details']
        }
    
    return stats


def compute_question_stats(sessions: List[Dict]) -> Dict[int, Dict]:
    """Compute per-question statistics."""
    questions = defaultdict(lambda: defaultdict(list))
    
    for s in sessions:
        cond = s['condition_name']
        for q in s['question_details']:
            qnum = q.get('question_number')
            questions[qnum][cond].append({
                'correct': q.get('is_correct', False),
                'difficulty': q.get('difficulty')
            })
    
    stats = {}
    for qnum in sorted(questions.keys()):
        stats[qnum] = {
            'difficulty': questions[qnum][list(questions[qnum].keys())[0]][0]['difficulty'],
            'by_condition': {}
        }
        total_correct = 0
        total_count = 0
        
        for cond, answers in questions[qnum].items():
            correct = sum(1 for a in answers if a['correct'])
            total = len(answers)
            pct = round(correct / total * 100) if total else 0
            stats[qnum]['by_condition'][cond] = {
                'correct': correct,
                'total': total,
                'percentage': pct
            }
            total_correct += correct
            total_count += total
        
        stats[qnum]['overall'] = {
            'correct': total_correct,
            'total': total_count,
            'percentage': round(total_correct / total_count * 100) if total_count else 0
        }
    
    return stats


def compute_survey_stats(condition_stats: Dict) -> Dict[str, Dict]:
    """Compute survey response statistics by condition."""
    survey_scale = {
        'Strongly Disagree': 1, 
        'Disagree': 2, 
        'Neutral': 3, 
        'Agree': 4, 
        'Strongly Agree': 5,
        'Yes': 1, 
        'No': 0
    }
    
    metrics = ['engagement', 'learning_helpfulness', 'understanding', 'vs_other_ai', 'would_use_again']
    
    results = {}
    for cond, stats in condition_stats.items():
        results[cond] = {}
        for metric in metrics:
            values = []
            for survey in stats['surveys']:
                if survey and metric in survey:
                    val = survey[metric]
                    if val in survey_scale:
                        values.append(survey_scale[val])
            if values:
                results[cond][metric] = round(sum(values) / len(values), 2)
    
    return results


def compute_score_distribution(condition_stats: Dict) -> Dict[str, List[int]]:
    """Compute score distribution by ranges for each condition."""
    ranges = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
    
    def get_range(score):
        if score <= 20: return 0
        elif score <= 40: return 1
        elif score <= 60: return 2
        elif score <= 80: return 3
        else: return 4
    
    distributions = {}
    for cond, stats in condition_stats.items():
        dist = [0, 0, 0, 0, 0]
        for score in stats['scores_list']:
            dist[get_range(score)] += 1
        distributions[cond] = dist
    
    return distributions


def generate_scatter_data(sessions: List[Dict]) -> Dict[str, List[tuple]]:
    """Generate duration vs score scatter plot data."""
    scatter = defaultdict(list)
    for s in sessions:
        scatter[s['condition_name']].append(
            (round(s['duration_minutes'], 1), s['quiz_percentage'])
        )
    return dict(scatter)


def print_summary(condition_stats: Dict, question_stats: Dict, survey_stats: Dict):
    """Print a formatted summary of all statistics."""
    print("=" * 60)
    print("JAVA TUTOR STUDY - DATA ANALYSIS SUMMARY")
    print("=" * 60)
    
    total_n = sum(s['n'] for s in condition_stats.values())
    print(f"\nTotal completed sessions: {total_n}")
    
    print("\n" + "-" * 40)
    print("CONDITION STATISTICS")
    print("-" * 40)
    
    for cond, stats in condition_stats.items():
        print(f"\n{cond.upper().replace('_', ' ')} (n={stats['n']})")
        print(f"  Quiz Score:  {stats['avg_score']}% (SD: {stats['score_sd']})")
        print(f"  Duration:    {stats['avg_duration']} min (SD: {stats['duration_sd']})")
        print(f"  Messages:    {stats['avg_messages']} avg")
        print(f"  Efficiency:  {round(stats['avg_score'] / stats['avg_duration'], 1)} pts/min")
    
    print("\n" + "-" * 40)
    print("QUESTION STATISTICS")
    print("-" * 40)
    
    for qnum, qstats in question_stats.items():
        print(f"\nQ{qnum + 1} (Difficulty: {qstats['difficulty']})")
        print(f"  Overall: {qstats['overall']['percentage']}%")
        for cond, cstats in qstats['by_condition'].items():
            short_cond = cond.replace('_scaffolded', '').replace('_', ' ')
            print(f"  {short_cond}: {cstats['percentage']}% ({cstats['correct']}/{cstats['total']})")
    
    print("\n" + "-" * 40)
    print("SURVEY STATISTICS")
    print("-" * 40)
    
    for cond, metrics in survey_stats.items():
        print(f"\n{cond.upper().replace('_', ' ')}")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")


def export_for_react(condition_stats: Dict, question_stats: Dict, 
                      survey_stats: Dict, scatter_data: Dict,
                      score_dist: Dict) -> dict:
    """Export data in a format ready for the React dashboard."""
    
    # Condition data for charts
    condition_data = []
    for cond, stats in condition_stats.items():
        short_name = {
            'character_scaffolded': 'Character',
            'non_character_scaffolded': 'Non-Char',
            'direct_chat': 'Direct'
        }.get(cond, cond)
        
        survey = survey_stats.get(cond, {})
        condition_data.append({
            'name': cond.replace('_', ' ').title(),
            'shortName': short_name,
            'n': stats['n'],
            'score': stats['avg_score'],
            'scoreSD': stats['score_sd'],
            'duration': stats['avg_duration'],
            'messages': stats['avg_messages'],
            'engagement': survey.get('engagement', 0),
            'understanding': survey.get('understanding', 0),
            'wouldUseAgain': round(survey.get('would_use_again', 0) * 100)
        })
    
    # Question data
    question_data = []
    for qnum, qstats in question_stats.items():
        question_data.append({
            'question': f'Q{qnum + 1}',
            'difficulty': qstats['difficulty'],
            'overall': qstats['overall']['percentage'],
            'character': qstats['by_condition'].get('character_scaffolded', {}).get('percentage', 0),
            'nonChar': qstats['by_condition'].get('non_character_scaffolded', {}).get('percentage', 0),
            'direct': qstats['by_condition'].get('direct_chat', {}).get('percentage', 0)
        })
    
    # Survey data for radar chart
    survey_data = [
        {
            'metric': 'Engagement',
            'character': survey_stats.get('character_scaffolded', {}).get('engagement', 0),
            'nonChar': survey_stats.get('non_character_scaffolded', {}).get('engagement', 0),
            'direct': survey_stats.get('direct_chat', {}).get('engagement', 0)
        },
        {
            'metric': 'Helpfulness',
            'character': survey_stats.get('character_scaffolded', {}).get('learning_helpfulness', 0),
            'nonChar': survey_stats.get('non_character_scaffolded', {}).get('learning_helpfulness', 0),
            'direct': survey_stats.get('direct_chat', {}).get('learning_helpfulness', 0)
        },
        {
            'metric': 'Understanding',
            'character': survey_stats.get('character_scaffolded', {}).get('understanding', 0),
            'nonChar': survey_stats.get('non_character_scaffolded', {}).get('understanding', 0),
            'direct': survey_stats.get('direct_chat', {}).get('understanding', 0)
        },
        {
            'metric': 'vs Other AI',
            'character': survey_stats.get('character_scaffolded', {}).get('vs_other_ai', 0),
            'nonChar': survey_stats.get('non_character_scaffolded', {}).get('vs_other_ai', 0),
            'direct': survey_stats.get('direct_chat', {}).get('vs_other_ai', 0)
        }
    ]
    
    # Score distribution
    ranges = ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%']
    score_dist_data = []
    for i, r in enumerate(ranges):
        score_dist_data.append({
            'range': r,
            'character': score_dist.get('character_scaffolded', [0]*5)[i],
            'nonChar': score_dist.get('non_character_scaffolded', [0]*5)[i],
            'direct': score_dist.get('direct_chat', [0]*5)[i]
        })
    
    # Scatter data
    scatter_formatted = []
    cond_map = {
        'character_scaffolded': 'Character',
        'non_character_scaffolded': 'Non-Char',
        'direct_chat': 'Direct'
    }
    for cond, points in scatter_data.items():
        for dur, score in points:
            scatter_formatted.append({
                'duration': dur,
                'score': score,
                'condition': cond_map.get(cond, cond)
            })
    
    return {
        'conditionData': condition_data,
        'questionData': question_data,
        'surveyData': survey_data,
        'scoreDistribution': score_dist_data,
        'scatterData': scatter_formatted
    }


def main():
    # Default filepath or use command line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'array_list_session_data.json'
    
    print(f"Loading data from: {filepath}")
    
    # Load and process data
    data = load_data(filepath)
    sessions = extract_completed_sessions(data)
    
    print(f"Found {len(sessions)} completed sessions")
    
    # Compute all statistics
    condition_stats = compute_condition_stats(sessions)
    question_stats = compute_question_stats(sessions)
    survey_stats = compute_survey_stats(condition_stats)
    score_dist = compute_score_distribution(condition_stats)
    scatter_data = generate_scatter_data(sessions)
    
    # Print summary
    print_summary(condition_stats, question_stats, survey_stats)
    
    # Export for React
    react_data = export_for_react(
        condition_stats, question_stats, survey_stats, 
        scatter_data, score_dist
    )
    
    # Save React-ready data to JSON
    output_file = 'dashboard_data.json'
    with open(output_file, 'w') as f:
        json.dump(react_data, f, indent=2)
    print(f"\n✓ React-ready data saved to: {output_file}")
    
    # Also print the JavaScript-formatted data
    print("\n" + "=" * 60)
    print("REACT DASHBOARD DATA (copy into your component)")
    print("=" * 60)
    print("\nconst conditionData =", json.dumps(react_data['conditionData'], indent=2))
    print("\nconst questionData =", json.dumps(react_data['questionData'], indent=2))
    print("\nconst surveyData =", json.dumps(react_data['surveyData'], indent=2))
    print("\nconst scoreDistData =", json.dumps(react_data['scoreDistribution'], indent=2))
    
    return react_data


if __name__ == '__main__':
    main()
