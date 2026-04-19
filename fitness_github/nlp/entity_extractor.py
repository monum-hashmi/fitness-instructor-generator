"""
Entity extractor.

Parses a user's free-text input and returns a dict of recognised fitness
entities: fitness_level, goal, equipment, and duration (minutes).
"""


def extract_entities(text: str) -> dict:
    """
    Extract fitness-related entities from raw user input.

    Parameters
    ----------
    text : str
        Raw user input string.

    Returns
    -------
    dict
        Keys: ``fitness_level``, ``goal``, ``equipment``, ``duration``.
    """
    text = text.lower()

    entities = {
        "fitness_level": "beginner",
        "goal": "weight_loss",
        "equipment": "none",
        "duration": 20,
    }

    if "intermediate" in text:
        entities["fitness_level"] = "intermediate"

    if "muscle" in text:
        entities["goal"] = "muscle_gain"

    if "flexibility" in text or "stretch" in text:
        entities["goal"] = "flexibility"

    if "dumbbell" in text:
        entities["equipment"] = "dumbbells"

    if "gym" in text:
        entities["equipment"] = "gym"

    for d in [10, 20, 30]:
        if str(d) in text:
            entities["duration"] = d

    return entities
