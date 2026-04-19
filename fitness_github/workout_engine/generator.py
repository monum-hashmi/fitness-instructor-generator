"""
Workout generator.

Filters exercises from the metadata catalogue by goal, then optionally
re-ranks them by cosine similarity to the user's free-text preference.
Returns the top 3 exercises for the session.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.exercise_metadata import EXERCISES


def generate_workout(entities: dict) -> list:
    """
    Build a personalised workout plan.

    Parameters
    ----------
    entities : dict
        Must contain ``"goal"`` (str).
        Optionally contains ``"preference_text"`` (str) for similarity ranking.

    Returns
    -------
    list[dict]
        Up to 3 exercise dicts from the metadata catalogue.
    """
    goal = entities["goal"]
    user_text = entities.get("preference_text", "").strip()

    filtered = [ex for ex in EXERCISES if ex["goal"] == goal]

    if not filtered:
        # Graceful fallback: return first 3 exercises regardless of goal
        return EXERCISES[:3]

    if user_text:
        descriptions = [ex["description"] for ex in filtered]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(descriptions + [user_text])
        similarities = cosine_similarity(X[-1], X[:-1]).flatten()
        filtered = [
            ex
            for _, ex in sorted(
                zip(similarities, filtered), key=lambda pair: pair[0], reverse=True
            )
        ]

    return filtered[:3]
