"""Train baseline Version 2 models for positive 5-day rebound prediction."""

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

ML_DIR = Path(__file__).resolve().parent
DATASET_FILE = ML_DIR / "ml_event_dataset.csv"
RESULTS_FILE = ML_DIR / "model_results.csv"
TARGET_COLUMN = "Target_Positive_5D"

TRAIN_PERIODS = ["2010-2014", "2015-2019"]
TEST_PERIOD = "2020-2024"

NUMERIC_FEATURES = [
    "Drop_Threshold",
    "Daily_Return",
    "Previous_5D_Return",
    "Previous_10D_Return",
    "Previous_20D_Volatility",
    "Volume_Change",
    "Distance_From_20D_MA",
    "Distance_From_50D_MA",
]
CATEGORICAL_FEATURES = ["Ticker", "Category", "Universe"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_dataset():
    """Load the ML event dataset created by feature_engineering.py."""
    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {DATASET_FILE}. Run python ml/feature_engineering.py first."
        )

    return pd.read_csv(DATASET_FILE)


def split_train_test(dataset):
    """Split events by historical period, preserving the out-of-sample test window."""
    train_data = dataset[dataset["Period"].isin(TRAIN_PERIODS)].copy()
    test_data = dataset[dataset["Period"] == TEST_PERIOD].copy()

    if train_data.empty:
        raise ValueError("Training set is empty. Expected rows for 2010-2014 and 2015-2019.")
    if test_data.empty:
        raise ValueError("Test set is empty. Expected rows for 2020-2024.")

    x_train = train_data[FEATURE_COLUMNS]
    y_train = train_data[TARGET_COLUMN]
    x_test = test_data[FEATURE_COLUMNS]
    y_test = test_data[TARGET_COLUMN]

    return x_train, x_test, y_train, y_test


def make_preprocessor():
    """Create preprocessing for numeric and categorical features."""
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def make_model_pipeline(model):
    """Attach shared preprocessing to one classifier."""
    return Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            ("model", model),
        ]
    )


def get_positive_class_scores(model, x_test):
    """Return scores suitable for ROC AUC when the classifier supports them."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x_test)[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(x_test)

    return None


def evaluate_model(model_name, model, x_test, y_test):
    """Calculate the common classification metrics for one fitted model."""
    predictions = model.predict(x_test)
    scores = get_positive_class_scores(model, x_test)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()

    roc_auc = None
    if scores is not None and y_test.nunique() == 2:
        roc_auc = roc_auc_score(y_test, scores)

    return {
        "Model": model_name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, zero_division=0),
        "Recall": recall_score(y_test, predictions, zero_division=0),
        "F1 score": f1_score(y_test, predictions, zero_division=0),
        "ROC AUC": roc_auc,
        "True Negatives": tn,
        "False Positives": fp,
        "False Negatives": fn,
        "True Positives": tp,
    }


def train_and_evaluate_models(x_train, x_test, y_train, y_test):
    """Fit the baseline models and return their evaluation rows."""
    models = {
        "Majority Class Baseline": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": make_model_pipeline(
            LogisticRegression(max_iter=1000, random_state=42)
        ),
        "Decision Tree": make_model_pipeline(
            DecisionTreeClassifier(random_state=42)
        ),
        "Random Forest": make_model_pipeline(
            RandomForestClassifier(n_estimators=200, random_state=42)
        ),
    }

    result_rows = []

    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model.fit(x_train, y_train)
        result_rows.append(evaluate_model(model_name, model, x_test, y_test))

    return pd.DataFrame(result_rows)


def add_baseline_comparison(results):
    """Add metric deltas versus the majority-class baseline."""
    baseline = results[results["Model"] == "Majority Class Baseline"].iloc[0]
    comparison_metrics = ["Accuracy", "Precision", "Recall", "F1 score", "ROC AUC"]

    for metric in comparison_metrics:
        results[f"{metric} vs Baseline"] = results[metric] - baseline[metric]

    return results


def print_summary(results):
    """Print the headline winners among the trained models."""
    model_results = results[results["Model"] != "Majority Class Baseline"].copy()
    best_f1 = model_results.sort_values("F1 score", ascending=False).iloc[0]
    best_auc = model_results.sort_values("ROC AUC", ascending=False).iloc[0]

    print("\nBest model by F1 score:")
    print(f"{best_f1['Model']} with F1 score {best_f1['F1 score']:.3f}")
    print("Best model by ROC AUC:")
    print(f"{best_auc['Model']} with ROC AUC {best_auc['ROC AUC']:.3f}")


def main():
    dataset = load_dataset()
    x_train, x_test, y_train, y_test = split_train_test(dataset)

    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")
    print("Training target balance:")
    print(y_train.value_counts(normalize=True).sort_index())
    print("Test target balance:")
    print(y_test.value_counts(normalize=True).sort_index())

    results = train_and_evaluate_models(x_train, x_test, y_train, y_test)
    results = add_baseline_comparison(results)
    results.to_csv(RESULTS_FILE, index=False)

    print("\nModel results:")
    print(results.to_string(index=False))
    print(f"\nSaved model results to {RESULTS_FILE}")
    print_summary(results)


if __name__ == "__main__":
    main()
