# 📊 Quiz Difficulty Tracking - Implementation Guide

## What's Been Added

### 1. Difficulty Levels in Questions
Each quiz question now has a difficulty rating (1-5):
- **1** = Easy (basic concepts)
- **2** = Medium (requires understanding)
- **3** = Medium-Hard (requires analysis)
- **4** = Hard (requires deep understanding)
- **5** = Very Hard (synthesis/advanced)

### 2. Database Structure

**Saved in Firebase under:** `users/{user_id}/sessions/{topic}/`

```json
{
  "quiz_score": 4,
  "quiz_total": 5,
  "quiz_percentage": 80,
  "difficulty_breakdown": {
    "by_level": {
      "1": {"correct": 1, "total": 1, "percentage": 100},
      "2": {"correct": 2, "total": 2, "percentage": 100},
      "3": {"correct": 1, "total": 1, "percentage": 100},
      "4": {"correct": 0, "total": 1, "percentage": 0}
    },
    "average_difficulty_correct": 2.0,
    "average_difficulty_incorrect": 4.0
  },
  "question_details": [
    {
      "question_number": 0,
      "difficulty": 1,
      "is_correct": true,
      "user_answer": "ArrayList can change size dynamically"
    },
    ...
  ]
}
```

## Files to Update

### 1. Replace `content/static_quiz.py`
Use: `static_quiz_with_difficulty.py`

**Changes:**
- Added `difficulty: int` to QuizQuestion dataclass
- Assigned difficulty (1-5) to each question
- Results now include difficulty in returned dict

### 2. Update `utils/database.py`
Add functions from: `database_difficulty_functions.py`

**New functions:**
- `save_quiz_responses()` - Updated to save difficulty data
- `calculate_difficulty_breakdown()` - Computes stats
- `get_difficulty_stats_by_condition()` - Query by difficulty
- `get_all_difficulty_stats()` - Comprehensive stats
- `export_difficulty_data_csv()` - Export for analysis

### 3. Update `views/quiz.py`
Use: `quiz_with_difficulty.py`

**Changes:**
- Pass `results` to `save_quiz_responses()`
- Show difficulty stars in feedback (⭐⭐⭐)

## Example Queries

### Query 1: How many answered difficulty 4?
```python
from database_difficulty_functions import get_difficulty_stats_by_condition

stats = get_difficulty_stats_by_condition('arraylist', 4)
print(stats)
# Output:
# {
#   'condition_1': {'correct': 15, 'total': 20, 'percentage': 75},
#   'condition_2': {'correct': 12, 'total': 20, 'percentage': 60},
#   'condition_3': {'correct': 10, 'total': 20, 'percentage': 50}
# }
```

### Query 2: Get all difficulty stats
```python
from database_difficulty_functions import get_all_difficulty_stats

stats = get_all_difficulty_stats('arraylist')

# See performance on each difficulty level by condition
print(stats['by_difficulty'][4])  # Difficulty 4 stats

# See average difficulty of correct/incorrect answers
print(stats['overall']['condition_1'])
```

### Query 3: Export to CSV
```python
from database_difficulty_functions import export_difficulty_data_csv

df = export_difficulty_data_csv('arraylist', 'arraylist_data.csv')

# Analyze in pandas
print(df.groupby(['condition', 'difficulty'])['is_correct'].mean())
```

## Quick Deployment

1. **Update quiz questions:**
```bash
cp static_quiz_with_difficulty.py content/static_quiz.py
```

2. **Add database functions:**
```bash
# Copy functions from database_difficulty_functions.py
# into your utils/database.py
```

3. **Update quiz view:**
```bash
cp quiz_with_difficulty.py views/quiz.py
```

4. **Restart app:**
```bash
streamlit run app.py
```

## Analysis Examples

### See who struggled with hard questions:
```python
df = export_difficulty_data_csv('arraylist')
hard = df[df['difficulty'] >= 4]
struggling = hard.groupby('condition')['is_correct'].mean()
print(struggling)
```

### Compare conditions on easy vs hard:
```python
df = export_difficulty_data_csv('arraylist')

easy = df[df['difficulty'] <= 2].groupby('condition')['is_correct'].mean()
hard = df[df['difficulty'] >= 4].groupby('condition')['is_correct'].mean()

print("Easy questions:")
print(easy)
print("\nHard questions:")
print(hard)
```

### Find students who got hard questions right:
```python
df = export_difficulty_data_csv('arraylist')
hard_correct = df[(df['difficulty'] >= 4) & (df['is_correct'] == True)]
print(hard_correct['email'].unique())
```

## Current Difficulty Ratings

### ArrayList Quiz:
1. Main advantage (Diff 1) ⭐
2. Runs out of capacity (Diff 2) ⭐⭐
3. O(1) operation (Diff 3) ⭐⭐⭐
4. Initial capacity (Diff 2) ⭐⭐
5. Most expensive (Diff 4) ⭐⭐⭐⭐

### Recursion Quiz:
1. Essential element (Diff 1) ⭐
2. No base case (Diff 2) ⭐⭐
3. Call stack (Diff 3) ⭐⭐⭐
4. factorial(3) (Diff 2) ⭐⭐
5. fibonacci base case (Diff 3) ⭐⭐⭐
6. Memory usage (Diff 4) ⭐⭐⭐⭐
7. Natural recursion (Diff 3) ⭐⭐⭐

## Benefits

✅ Track which difficulty levels students struggle with
✅ Compare conditions on hard vs easy questions  
✅ Identify if scaffolding helps with complex concepts
✅ See if character-based learning improves on harder material
✅ Export granular data for statistical analysis
✅ Query specific difficulty levels easily

## Ready to Deploy! 🚀
