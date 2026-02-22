# views/quiz.py

import streamlit as st
from content.research_topics import get_research_topic
from content.static_quiz import get_quiz, score_quiz
from utils.database import save_quiz_responses
from utils.database import complete_session


def render_quiz():
    """Render the quiz for the current session."""

    session_id = st.session_state.current_session_id
    topic = get_research_topic(session_id)

    st.title(f"📝 Quiz: {topic.name}")
    st.write("Please answer these questions based on what you learned.")
    st.write("---")

    quiz_questions = get_quiz(session_id)

    # Initialize quiz state
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    # ---------------------------------------------------------
    # QUIZ NOT SUBMITTED YET
    # ---------------------------------------------------------
    if not st.session_state.quiz_submitted:

        for i, q in enumerate(quiz_questions):
            st.subheader(f"Question {i + 1}")
            st.write(q.question)

            answer = st.radio(
                "Select your answer:",
                options=q.options,
                key=f"quiz_q_{i}",
                index=None,
            )

            if answer:
                st.session_state.quiz_answers[i] = answer

            st.write("")

        # Check if all answered
        all_answered = len(st.session_state.quiz_answers) == len(quiz_questions)

        if st.button("Submit Quiz", type="primary", disabled=not all_answered):

            # Score quiz - now returns results with difficulty
            score, total, results = score_quiz(
                session_id, st.session_state.quiz_answers
            )

            # Save with results (includes difficulty tracking)
            save_quiz_responses(
                st.session_state.user_id,
                session_id,
                st.session_state.quiz_answers,
                score,
                total,
                results  # ✅ NEW: Pass results to save difficulty data
            )

            # Store results
            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            st.session_state.quiz_total = total
            st.session_state.quiz_results = results

            st.rerun()

        if not all_answered:
            st.info(
                f"Please answer all questions "
                f"({len(st.session_state.quiz_answers)}/{len(quiz_questions)} complete)"
            )

        return

    # ---------------------------------------------------------
    # QUIZ SUBMITTED — SHOW RESULTS
    # ---------------------------------------------------------
    st.success("✅ Quiz Complete!")
    st.metric(
        "Your Score",
        f"{st.session_state.quiz_score}/{st.session_state.quiz_total}",
    )

    st.write("---")

    # Show detailed feedback
    for i, result in enumerate(st.session_state.quiz_results):
        # Show difficulty level in feedback
        difficulty_stars = "⭐" * result.get('difficulty', 1)
        
        with st.expander(
            f"Question {i + 1} ({difficulty_stars}) — "
            f"{'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"
        ):
            st.write(f"**Q:** {result['question']}")
            st.write(f"**Your answer:** {result['user_answer']}")

            if not result["is_correct"]:
                st.write(f"**Correct answer:** {result['correct_answer']}")

            st.info(f"**Explanation:** {result['explanation']}")

    st.write("---")

    if st.button("Continue to Survey", type="primary"):
        st.session_state.phase = "survey"
        st.rerun()
