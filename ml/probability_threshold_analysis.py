"""Evaluate high-confidence rebound predictions by probability threshold."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from train_model import FEATURE_COLUMNS, load_dataset, make_model_pipeline, split_train_test

ML_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = ML_DIR / "probability_threshold_results.csv"
PROBABILITY_THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70]


def get_test_rows(dataset):
    """Return test-period rows aligned to split_train_test output."""
    return dataset[dataset["Period"] == "2020-2024"].copy().reset_index(drop=True)


def summarize_threshold(model_name, threshold, test_rows, probabilities):
    """Summarize realized returns for selected high-probability test events."""
    selected = test_rows[probabilities >= threshold]
    total_events = len(test_rows)

    row = {
        "Model": model_name,
        "Probability_Threshold": threshold,
        "Number_of_Selected_Events": len(selected),
        "Selection_Rate": len(selected) / total_events if total_events else 0,
        "Average_Forward_5D_Return": selected["Forward_5D_Return"].mean(),
        "Average_Edge_vs_Benchmark_5D": selected["Edge_vs_Benchmark_5D"].mean(),
        "Win_Rate": selected["Target_Positive_5D"].mean(),
        "Beat_Benchmark_Rate": selected["Target_Beat_Benchmark_5D"].mean(),
    }

    return row


def analyze_model(model_name, model, x_train, y_train, x_test, test_rows):
    """Train one model and evaluate selected events across probability thresholds."""
    print(f"Training {model_name}...")
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]

    return [
        summarize_threshold(model_name, threshold, test_rows, probabilities)
        for threshold in PROBABILITY_THRESHOLDS
    ]


def main():
    dataset = load_dataset()
    x_train, x_test, y_train, y_test = split_train_test(dataset)
    test_rows = get_test_rows(dataset)

    # Keep the test rows aligned with x_test from split_train_test.
    test_rows = test_rows.reset_index(drop=True)
    x_test = x_test.reset_index(drop=True)
    test_rows = test_rows.loc[x_test.index]

    models = {
        "Logistic Regression": make_model_pipeline(LogisticRegression(max_iter=1000, random_state=42)),
        "Random Forest": make_model_pipeline(RandomForestClassifier(n_estimators=200, random_state=42)),
    }

    result_rows = []
    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")
    print(f"Features used: {', '.join(FEATURE_COLUMNS)}")

    for model_name, model in models.items():
        result_rows.extend(analyze_model(model_name, model, x_train, y_train, x_test, test_rows))

    results = pd.DataFrame(result_rows)
    results.to_csv(OUTPUT_FILE, index=False)

    print("\nProbability threshold results:")
    print(results.to_string(index=False))
    print(f"\nSaved probability threshold results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
