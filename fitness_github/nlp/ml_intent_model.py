# nlp/ml_intent_model.py
import csv
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_goal_model.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "training_data.csv")
BEST_MODEL_NAME = "LinearSVC"
BEST_VECTORIZER_KWARGS = {
    "analyzer": "char_wb",
    "ngram_range": (3, 5),
    "sublinear_tf": True,
    "min_df": 1,
}

# Train model once
def _load_training_data():
    texts = []
    labels = []
    if not os.path.exists(DATA_PATH):
        return texts, labels
    with open(DATA_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if text and label:
                texts.append(text)
                labels.append(label)
    return texts, labels


def train_model():
    texts, labels = _load_training_data()
    if not texts:
        raise RuntimeError("No training data found. Check data/training_data.csv.")
    vectorizer = TfidfVectorizer(**BEST_VECTORIZER_KWARGS)
    X = vectorizer.fit_transform(texts)
    # Use the current best-performing model for training/prediction.
    clf = LinearSVC()
    clf.fit(X, labels)
    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "model": clf}, f)
    print("ML Goal model trained and saved.")

# Compare multiple models using cross-validation
def evaluate_models(cv_folds=5, random_state=42):
    texts, labels = _load_training_data()
    if not texts:
        raise RuntimeError("No training data found. Check data/training_data.csv.")
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    candidates = {
        "LinearSVC(word_1_2)": {
            "vectorizer": TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
            "model": LinearSVC(),
        },
        "LinearSVC(char_3_5)": {
            "vectorizer": TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True),
            "model": LinearSVC(),
        },
        "LogReg(word_1_2)": {
            "vectorizer": TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
            "model": LogisticRegression(max_iter=2000, solver="liblinear"),
        },
    }
    results = {}
    for name, cfg in candidates.items():
        pipeline = make_pipeline(cfg["vectorizer"], cfg["model"])
        scores = cross_val_score(pipeline, texts, labels, cv=skf, scoring="accuracy")
        results[name] = {"mean_accuracy": scores.mean(), "std_accuracy": scores.std()}
    return results

# Predict goal from user input
def predict_goal(user_text):
    if not os.path.exists(MODEL_PATH):
        train_model()
    elif os.path.exists(DATA_PATH):
        data_mtime = os.path.getmtime(DATA_PATH)
        model_mtime = os.path.getmtime(MODEL_PATH)
        if data_mtime > model_mtime:
            train_model()
    with open(MODEL_PATH, "rb") as f:
        data = pickle.load(f)
    vectorizer = data["vectorizer"]
    model = data["model"]
    X = vectorizer.transform([user_text])
    return model.predict(X)[0]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate", action="store_true", help="Evaluate models with cross-validation")
    args = parser.parse_args()

    if args.evaluate:
        results = evaluate_models()
        for name, stats in results.items():
            mean_acc = stats["mean_accuracy"]
            std_acc = stats["std_accuracy"]
            print(f"{name}: accuracy={mean_acc:.3f} (+/-{std_acc:.3f})")
