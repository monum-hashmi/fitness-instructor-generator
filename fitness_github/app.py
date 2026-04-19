import os
import time

import streamlit as st

from audio.tts import speak
from nlp.entity_extractor import extract_entities
from nlp.ml_helper import predict_goal
from workout_engine.generator import generate_workout

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fitness Instructor Generator",
    page_icon="🏋️",
    layout="wide",
)

VOICE_DELAY_SECONDS = 2

GOAL_OPTIONS = {
    "Weight Loss": "weight_loss",
    "Muscle Gain": "muscle_gain",
    "Flexibility": "flexibility",
    "Endurance": "endurance",
    "Core Strength": "core_strength",
    "Balance": "balance",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXERCISE_VIDEOS = {
    "Child Pose":        os.path.join(BASE_DIR, "assets", "child_pose.mp4"),
    "Hamstring Stretch": os.path.join(BASE_DIR, "assets", "hamstring_stretch.mp4"),
    "Jumping Jacks":     os.path.join(BASE_DIR, "assets", "jumping_jacks.mp4"),
    "Dumbbell Curls":    os.path.join(BASE_DIR, "assets", "dumbbell_curls.mp4"),
    "Neck Stretch":      os.path.join(BASE_DIR, "assets", "neck_stretch.mp4"),
    "Plank":             os.path.join(BASE_DIR, "assets", "plank_exercise.mp4"),
    "Push-ups":          os.path.join(BASE_DIR, "assets", "push_ups.mp4"),
    "Squats":            os.path.join(BASE_DIR, "assets", "squats.mp4"),
    "Lunges":            os.path.join(BASE_DIR, "assets", "lunges.mp4"),
}

if "autoplayed_exercises" not in st.session_state:
    st.session_state.autoplayed_exercises = set()

st.title("🏋️ Fitness Instructor Generator")
st.write("Get a personalised workout plan with live timers and exercise videos.")

goal_label = st.radio("Select your fitness goal:", tuple(GOAL_OPTIONS.keys()))
goal_selected = GOAL_OPTIONS[goal_label]

user_input = st.text_input(
    "Describe your preference (optional):",
    placeholder="e.g. 20 minute home workout",
)

enable_voice = st.checkbox("Enable voice instructions", value=False)

if st.button("Generate Workout"):
    entities = extract_entities(user_input)

    if user_input.strip():
        entities["goal"] = predict_goal(user_input)
        st.info(f"🎯 Predicted goal: **{entities['goal'].replace('_', ' ').title()}**")
    else:
        entities["goal"] = goal_selected
        st.info(f"🎯 Selected goal: **{entities['goal'].replace('_', ' ').title()}**")

    entities["preference_text"] = user_input
    workout_plan = generate_workout(entities)

    st.divider()
    st.header("Your Personalised Workout Plan")

    for exercise in workout_plan:
        st.subheader(exercise["name"])
        if "description" in exercise:
            st.markdown(f"*{exercise['description']}*")

        video_col, timer_col = st.columns([1, 1])

        video_placeholder = video_col.empty()
        no_video_text = video_col.empty()
        video_path = EXERCISE_VIDEOS.get(exercise["name"])
        video_bytes = None
        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as f:
                video_bytes = f.read()
        else:
            no_video_text.info("No video available for this exercise.")

        set_text = timer_col.empty()
        timer_text = timer_col.empty()
        progress_bar = timer_col.progress(0)
        rest_text = timer_col.empty()
        rest_bar = timer_col.empty()

        if enable_voice and exercise["name"] not in st.session_state.autoplayed_exercises:
            speak(f"Starting {exercise['name']}")
            time.sleep(VOICE_DELAY_SECONDS)
            st.session_state.autoplayed_exercises.add(exercise["name"])

        for set_no in range(1, exercise["sets"] + 1):
            rest_text.empty()
            rest_bar.empty()
            set_text.markdown(f"### Set {set_no} of {exercise['sets']}")

            if video_bytes:
                video_placeholder.video(video_bytes, format="video/mp4", start_time=0)

            duration = (
                exercise["value"]
                if exercise["type"] == "time"
                else exercise["value"] * 2
            )

            if exercise["type"] == "reps":
                timer_text.markdown(f"🔁 *Do {exercise['value']} reps*")

            for sec in range(duration, 0, -1):
                timer_text.markdown(f"⏱️ *Time remaining:* **{sec}s**")
                progress_bar.progress((duration - sec + 1) / duration)
                time.sleep(1)

            video_placeholder.empty()

            if exercise["rest"] > 0:
                for sec in range(exercise["rest"], 0, -1):
                    rest_text.markdown(f"⏱️ Rest remaining: **{sec}s**")
                    rest_bar.progress((exercise["rest"] - sec + 1) / exercise["rest"])
                    time.sleep(1)
                rest_bar.progress(1.0)

        st.divider()

    st.success("🎉 Workout Complete!")
