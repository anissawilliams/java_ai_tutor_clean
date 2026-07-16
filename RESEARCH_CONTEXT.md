# Research Context

This document captures the study design, findings, and paper status for whoever inherits this project. The code is secondary — this is the context that only exists in people's heads if not written down.

---

## The Study

**Institution:** College of Charleston — Intelligent Tutoring Systems (ITS) Lab  
**PI:** [Lab PI name]  
**Engineering lead:** Anissa Williams  
**IRB status:** Approved. Survey responses excluded from analysis per IRB requirements — only chat interaction data is in scope.

**Research question:** Does scaffolded AI tutoring produce better learning outcomes than unstructured AI chat? Does a character/persona add further benefit?

### Participants
- ~104 students total across two semesters
- CS 221 (Intro Java) students at CofC
- Spring 2026 was the most recent data collection

### Sessions
Students completed up to 3 sessions on different Java topics:

| Session | Topic | Difficulty | Notes |
|---|---|---|---|
| 1 | ArrayList | Easy | All students, required first |
| 2 | Recursion | Hard | Requires Session 1 completion |
| 3 | Queue | Medium | Requires Session 1; Recursion optional |

Each session: ~15 min learning + quiz + survey. Estimated total: ~18 min/session.

---

## Experimental Conditions

Students were randomly assigned to one of three conditions at registration. Assignment persists across all sessions.

| Condition | Name | Description |
|---|---|---|
| 1 | `character_scaffolded` | AI tutor has a character/persona + structured 7-step scaffold |
| 2 | `non_character_scaffolded` | Structured 7-step scaffold, no persona |
| 3 | `direct_chat` | Free-form AI chat, no scaffold, no persona (control) |

~20 students per condition was the target.

### The Scaffold (Conditions 1 & 2)
Seven sequential steps managed by `TutorFlow` in `tutor_flow/flow_manager.py`:

1. **INITIAL_METAPHOR** — AI presents a metaphor for the concept
2. **STUDENT_METAPHOR** — Student generates their own metaphor
3. **VISUAL_DIAGRAM** — ASCII diagram shown, student confirms understanding
4. **CODE_STRUCTURE** — AI shows code structure, asks question
5. **CODE_USAGE** — AI shows usage example, student engages
6. **PRACTICE** — Student solves a problem
7. **REFLECTION** — Student summarizes what they learned

Step advancement is signal-based — the `should_advance_step()` method in `flow_manager.py` listens for readiness signals ("got it", "makes sense", etc.) and blocks advancement on confusion signals ("confused", "don't get it", etc.).

---

## Key Findings (Paper 1)

**The headline result:** Statistically significant quiz score improvement from Session 1 → Session 3 for both scaffolded conditions.

- Condition 1 (character + scaffold): p = 0.004
- Condition 2 (scaffold only): p = 0.006
- Condition 3 (direct chat): not significant

**The counterintuitive finding:** Short student responses ("yes", "okay", "got it") in scaffolded sessions *predicted high performance* — breaking the assumption that message length = engagement quality. Scaffolded students said less and scored more.

**Temporal pattern:** Lag-1 autocorrelation in student response timing deepened monotonically across sessions for scaffolded students only. This was strongest during Recursion (the hardest topic) — interpreted as scaffold-mediated cognitive resilience.

**Target venue:** SIGCSE (CS education research conference)

---

## Paper 2 — Status and Directions

The team has one more data exploration week, then 3–4 weeks of writing. Two primary directions are being developed:

### Direction A: Behavioral Footprint / CEI Framework
Extending ICAP theory (Chi & Wylie, 2014 — 4,500+ citations) into a continuous behavioral engagement metric for GenAI tutoring systems.

**ICAP background:** Interactive > Constructive > Active > Passive in terms of learning depth. Published 2014, predates generative AI, well-established foundation.

**CEI (Cognitive Engagement Index)** — proposed formula:
```
CEI = w1(Z_ponder) + w2(Z_density) - w3(Z_velocity)
```
Where:
- `Z_ponder` = normalized time between student messages (think time)
- `Z_density` = normalized message character count
- `Z_velocity` = normalized response speed (inverse engagement signal)

The key tension: velocity and density often trade off. A student who responds instantly with "yes" may be more engaged (ready signal) or less engaged (not reading). The CEI framework tries to resolve this using the scaffolded vs. direct chat contrast as ground truth.

**This paper must diverge significantly from Paper 1** — different analytic approach, not just more of the same.

### Direction B: Efficiency Analysis
Token cost-effectiveness: scaffolded conditions use fewer tokens while achieving better outcomes.

Key data points:
- Direct chat (Condition 3): higher character counts, lower scores (~55%)
- Scaffolded (Conditions 1 & 2): lower character counts, higher scores (~76%)
- Scaffolded students spend 10–20% less think time while maintaining or improving performance

**Paper angle:** "Quality over quantity" — efficient learning interactions vs. verbose ones.

---

## Data

### What's collected
Per session, per user, stored in Firebase under `users/{user_id}/sessions/{topic}`:

- Full chat transcript (`messages[]` — role, content, timestamp, scaffold step)
- Quiz responses + score + difficulty breakdown per question
- Survey responses (Likert + free text) — **excluded from analysis per IRB**
- Scaffold step progression log
- Session timing (start, end, duration, message counts)

### Where the data lives
- **Firebase Realtime Database:** `java-learning-study-d2e9b-default-rtdb.firebaseio.com`
- **Local exports:** `data_visualization/all_data_array_list_session.json` (ArrayList sessions), `trimmed_data.json` (redacted sample)
- **Export tool:** Run the app and navigate to `/?export=true` for CSV

### Data schema (Firebase)
```
users/
  {user_id}/
    email
    condition          (1, 2, or 3)
    condition_name     ("character_scaffolded", etc.)
    sessions/
      arraylist/
        status         ("completed" | "in_progress")
        condition
        start_time     (Unix timestamp)
        end_time
        duration_seconds
        total_messages
        user_messages
        assistant_messages
        messages[]
          role         ("user" | "assistant")
          content
          timestamp
          step         (scaffold step name, conditions 1&2 only)
        scaffold_progress[]
          step
          timestamp
        quiz_score
        quiz_total
        quiz_percentage
        question_details[]
          question_number
          difficulty    (1–5)
          is_correct
          user_answer
        difficulty_breakdown
          by_level: {1: {correct, total, percentage}, ...}
          average_difficulty_correct
          average_difficulty_incorrect
      recursion/       (same structure)
      queue/           (same structure)
```

### Analysis starting point
`data_visualization/real_analytics.py` is the most developed analysis script. Start there. The JSON exports are the cleanest way to work locally without hitting Firebase on every run — use `retrieve_session_data.py` to refresh them.

---

## People

| Person | Role | Contact |
|---|---|---|
| Anissa Williams | Engineering lead, co-author | williamsa17@g.cofc.edu |
| [Lab PI] | Research PI | [email] |
| Navid Hashemi Tonekaboni | Prior work on multi-agent Socratic AI; potential EU collaboration | [contact if available] |

---

## What "Done" Looks Like

- [ ] Paper 1 submitted to SIGCSE
- [ ] Paper 2 direction finalized and drafted
- [ ] Firebase data exported and archived locally (don't rely solely on cloud)
- [ ] Analysis notebooks cleaned up and reproducible
