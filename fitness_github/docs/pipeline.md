# Fitness Instructor Generator - Pipeline Overview

This document explains the end-to-end workflow, with emphasis on NLP/ML.

## 1) Entry Point (UI)
File: app.py

- Collects user input:
  - Goal selection (radio button).
  - Optional free-text preference.
- If free-text is provided, ML prediction is used.
- If free-text is empty, the selected goal is used.

## 2) NLP Preprocessing (Rule-Based Intent Path)
File: nlp/preprocess.py

- Lowercase text.
- Remove punctuation.
- Split into tokens.
- Remove NLTK stopwords.
- Lemmatize tokens.
- Return cleaned string.

## 3) Rule-Based Intent Classifier
File: nlp/intent_classifier.py

- Checks keyword sets in cleaned text.
- Returns an intent label (e.g., weight_loss_request).
- Currently computed in app.py but not used downstream.

## 4) ML Goal Prediction (Core NLP/ML)
File: nlp/ml_intent_model.py

Training:
- Load labeled data from data/training_data.csv (text, label).
- Convert text to TF-IDF vectors.
- Train Linear SVM (LinearSVC).
- Save model + vectorizer to nlp/ml_goal_model.pkl.
- Retrain automatically when CSV is newer than the model file.

Prediction:
- Load model + vectorizer.
- Transform input to TF-IDF vector.
- Predict goal label.

## 5) ML Wrapper + Fallback
File: nlp/ml_helper.py

- Calls ML prediction.
- If ML fails/empty, uses keyword fallbacks.
- Guarantees a goal for workout generation.

## 6) Workout Generation
File: workout_engine/generator.py

- Filter exercises by goal from nlp/exercise_metadata.py.
- Apply preset sets/reps/rest (PREDEFINED_EXERCISES).
- If user text exists:
  - TF-IDF on exercise descriptions + user text.
  - Rank by cosine similarity.
- Return top 3 exercises.

## 7) Media + Timers
File: app.py

- Try to load exercise video from assets/.
- If missing: show "No video available."
- Run per-set timers (time-based or rep-based).
- Optional TTS via audio/tts.py.

## Flow Summary (Text)
1) app.py collects input
2) ml_helper.py -> ml_intent_model.py predicts goal
3) generator.py selects and ranks exercises
4) app.py renders video/timers/voice
