"""Interpret baseline Version 2 models with coefficients and feature importances."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from train_model import CATEGORICAL_FEATURES, load_dataset, make_model_pipeline, split_train_test

ML_DIR = Path(__file__).resolve().parent
LOGISTIC_OUTPUT_FILE = ML_DIR / "logistic_regression_coefficients.csv"
FOREST_OUTPUT_FILE = ML_DIR / "random_forest_feature_importance.csv"


def get_feature_names(fitted_pipeline):
    """Return transformed feature names from the fitted preprocessing step."""
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    return preprocessor.get_feature_names_out()


def clean_feature_name(feature_name):
    """Make ColumnTransformer feature names easier to read in CSV outputs."""
    for prefix in ["numeric__", "categorical__"]:
        if feature_name.startswith(prefix):
            return feature_name.replace(prefix, "", 1)

    return feature_name


def export_logistic_coefficients(model):
    """Save logistic regression coefficients ordered by absolute effect size."""
    feature_names = [clean_feature_name(name) for name in get_feature_names(model)]
    coefficients = model.named_steps["model"].coef_[0]

    coefficient_table = pd.DataFrame(
        {
            "Feature": feature_names,
            "Coefficient": coefficients,
            "Absolute_Coefficient": abs(coefficients),
        }
    ).sort_values("Absolute_Coefficient", ascending=False)

    coefficient_table.to_csv(LOGISTIC_OUTPUT_FILE, index=False)
    return coefficient_table


def export_random_forest_importance(model):
    """Save random forest feature importances ordered from strongest to weakest."""
    feature_names = [clean_feature_name(name) for name in get_feature_names(model)]
    importances = model.named_steps["model"].feature_importances_

    importance_table = pd.DataFrame(
        {
            "Feature": feature_names,
            "Importance": importances,
        }
    ).sort_values("Importance", ascending=False)

    importance_table.to_csv(FOREST_OUTPUT_FILE, index=False)
    return importance_table


def main():
    dataset = load_dataset()
    x_train, x_test, y_train, y_test = split_train_test(dataset)

    print(f"Training rows: {len(x_train)}")
    print(f"Test rows: {len(x_test)}")
    print(f"Categorical features one-hot encoded: {', '.join(CATEGORICAL_FEATURES)}")

    logistic_model = make_model_pipeline(LogisticRegression(max_iter=1000, random_state=42))
    forest_model = make_model_pipeline(RandomForestClassifier(n_estimators=200, random_state=42))

    print("Training Logistic Regression...")
    logistic_model.fit(x_train, y_train)
    logistic_coefficients = export_logistic_coefficients(logistic_model)

    print("Training Random Forest...")
    forest_model.fit(x_train, y_train)
    forest_importance = export_random_forest_importance(forest_model)

    print("\nTop 15 Logistic Regression features by absolute coefficient:")
    print(logistic_coefficients.head(15).to_string(index=False))
    print(f"\nSaved logistic regression coefficients to {LOGISTIC_OUTPUT_FILE}")

    print("\nTop 15 Random Forest features by importance:")
    print(forest_importance.head(15).to_string(index=False))
    print(f"\nSaved random forest feature importances to {FOREST_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
