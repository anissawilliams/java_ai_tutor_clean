import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. DATA LOADING (Mock vs Real)
# ==========================================

# ---------------- OPTION A: MOCK DATA (For testing right now) ----------------
# This mirrors the "One Lesson" structure you described.
data = {
    "user_001": {
        "sessions": {
            "Arraylists": {  # Single lesson
                "status": "complete",
                "quiz_percentage": 0.8,
                "total_messages": 37,  # High engagement example
                "duration_seconds": 1200,
                "messages": [
                    {"role": "user", "content": "What is an ArrayList?", "timestamp": 100},
                    {"role": "assistant", "content": "It is a resizable array...", "timestamp": 101},
                    {"role": "user", "content": "Why not use a normal array?", "timestamp": 102},
                    # ... imagine 34 more messages here ...
                ],
                "question_details": [
                    {"difficulty": 1, "is_correct": True},
                    {"difficulty": 4, "is_correct": False},
                    {"difficulty": 2, "is_correct": True}
                ]
            }
        }
    },
    "user_002": {
        "sessions": {
            "Arraylists": {
                "status": "complete",
                "quiz_percentage": 1.0,
                "total_messages": 12,  # Low engagement example
                "duration_seconds": 600,
                "messages": [
                    {"role": "user", "content": "Start quiz", "timestamp": 200},
                    {"role": "assistant", "content": "Here is question 1...", "timestamp": 201}
                ],
                "question_details": [
                    {"difficulty": 1, "is_correct": True},
                    {"difficulty": 4, "is_correct": True},  # Smart user
                    {"difficulty": 2, "is_correct": True}
                ]
            }
        }
    }
}
# -----------------------------------------------------------------------------

# ---------------- OPTION B: REAL DATA (Uncomment when ready) -----------------
# data = raw_data
# -----------------------------------------------------------------------------


# ==========================================
# 2. THE PROCESSING ENGINE
# ==========================================
print("Processing data...")

rows = []

# This loop works even if there is only 1 lesson per user
for user_id, user_data in data.items():
    sessions = user_data.get("sessions", {})

    # Loop through the lessons (even if it's just one)
    for topic, s in sessions.items():
        # Calculate extra text metrics on the fly
        messages = s.get("messages", [])
        user_msgs = [m for m in messages if m.get('role') == 'user']
        # Count how many times the user asked "Why" or used a question mark
        question_count = sum(1 for m in user_msgs if "?" in m.get('content', ''))

        rows.append({
            "user_id": user_id,
            "lesson_name": topic,
            "score_pct": s.get("quiz_percentage", 0),
            "engagement_turns": s.get("total_messages", 0),
            "duration_mins": s.get("duration_seconds", 0) / 60,
            "questions_asked": question_count,  # Curiosity metric
            "is_high_engagement": s.get("total_messages", 0) > 30  # Flag for your 37-msg insight
        })

df = pd.DataFrame(rows)

# ==========================================
# 3. VISUALIZATIONS
# ==========================================
plt.style.use('ggplot')
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Engagement vs Learning
# Does talking more lead to higher scores?
sns.scatterplot(
    data=df,
    x="engagement_turns",
    y="score_pct",
    hue="is_high_engagement",
    s=150,
    palette={True: "green", False: "gray"},
    ax=ax[0]
)
ax[0].set_title("Engagement vs. Quiz Score")
ax[0].set_xlabel("Total Chat Messages")
ax[0].set_ylabel("Quiz Score (0-1.0)")

# Plot 2: Time vs. Learning
# Are they spending quality time?
sns.regplot(data=df, x="duration_mins", y="score_pct", ax=ax[1], color="teal")
ax[1].set_title("Time Spent vs. Quiz Score")
ax[1].set_xlabel("Duration (Minutes)")

plt.tight_layout()
plt.show()

# ==========================================
# 4. INSTANT INSIGHTS
# ==========================================
print("\n--- INSTANT REPORT ---")
print(f"Total Students Processed: {len(df)}")
print(f"Average Score: {df['score_pct'].mean():.2%}")
print(f"Avg Messages per Session: {df['engagement_turns'].mean():.1f}")
if not df[df['is_high_engagement']].empty:
    high_eng_score = df[df['is_high_engagement']]['score_pct'].mean()
    print(f"Score for High Engagement Users (>30 msgs): {high_eng_score:.2%}")
else:
    print("No high engagement users found in this batch.")