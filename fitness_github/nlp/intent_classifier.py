from nlp.preprocess import preprocess_text

INTENT_KEYWORDS = {
    "weight_loss_request": ["lose", "fat", "slim"],
    "muscle_gain_request": ["muscle", "strength", "bulk"],
    "flexibility_request": ["flexibility", "stretch", "yoga"],
    "workout_request": ["workout", "exercise", "training"]
}

def classify_intent(text: str) -> str:
    processed = preprocess_text(text)

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in processed:
                return intent

    return "workout_request"
