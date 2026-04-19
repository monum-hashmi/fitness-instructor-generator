# nlp/ml_helper.py
from nlp.ml_intent_model import predict_goal as ml_predict

# simple keyword fallback mapping
KEYWORD_FALLBACK = {
    "weight_loss": ["weight loss", "fat burn", "lose weight", "slim", "cardio"],
    "muscle_gain": ["muscle", "strength", "gain weight", "bulk", "biceps", "dumbbell"],
    "flexibility": ["flexibility", "stretch", "yoga", "mobility", "hamstring", "plank"],
    "endurance": ["endurance", "stamina", "aerobic", "conditioning", "cardio"],
    "core_strength": ["core", "abs", "plank", "midsection", "stability"],
    "balance": ["balance", "stability", "coordination", "proprioception", "single leg"]
}

def predict_goal(user_input: str) -> str:
    """
    Predict goal using ML first.
    If input is empty or ML fails, fallback to keywords.
    """
    text = user_input.lower().strip()
    
    # If empty input, default to weight_loss
    if not text:
        return "weight_loss"

    try:
        predicted_goal = ml_predict(user_input)
    except Exception:
        predicted_goal = ""

    # If ML prediction is empty, fallback to keywords
    if not predicted_goal:
        for goal, keywords in KEYWORD_FALLBACK.items():
            if any(k in text for k in keywords):
                return goal
        # default fallback
        return "weight_loss"

    return predicted_goal
