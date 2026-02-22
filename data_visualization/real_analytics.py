import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. DATA LOADING (Mock vs Real)
# ==========================================


# ---------------- OPTION B: REAL DATA (Uncomment when ready) -----------------
file = "array_list_session_data.json"
print(f"Loading data from {file}...")
data = pd.read_json(file)
print(data.head())
print(data.columns)
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