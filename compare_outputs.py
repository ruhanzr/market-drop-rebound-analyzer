"""Compare CSV outputs from the original and refactored project versions.

This script does not run the analysis and does not overwrite result files.
It only reads CSVs from:

    comparison_outputs/original/
    comparison_outputs/refactored/

Then it prints and saves a simple comparison report.
"""

from pathlib import Path

import pandas as pd


ORIGINAL_DIR = Path("comparison_outputs/original")
REFACTORED_DIR = Path("comparison_outputs/refactored")
REPORT_PATH = Path("comparison_outputs/comparison_report.txt")


# These are the output files we expect to compare when they are available.
FILES_TO_COMPARE = [
    "combined_summary_2010-2014.csv",
    "combined_summary_2015-2019.csv",
    "combined_summary_2020-2024.csv",
    "long_format_summary_2010-2014.csv",
    "long_format_summary_2015-2019.csv",
    "long_format_summary_2020-2024.csv",
    "ranked_setups_2010-2014.csv",
    "ranked_setups_2015-2019.csv",
    "ranked_setups_2020-2024.csv",
    "transaction_cost_sensitivity_2010-2014.csv",
    "transaction_cost_sensitivity_2015-2019.csv",
    "transaction_cost_sensitivity_2020-2024.csv",
    "ranked_after_cost_sensitivity_2010-2014.csv",
    "ranked_after_cost_sensitivity_2015-2019.csv",
    "ranked_after_cost_sensitivity_2020-2024.csv",
    "transaction_cost_survival_summary.csv",
    "selected_setup_drawdowns.csv",
    "selected_setup_drawdown_summary.csv",
    "selected_setup_bootstrap_summary.csv",
]


def sort_for_comparison(df):
    """Sort rows so row order alone does not create a false mismatch."""
    try:
        return df.sort_values(by=list(df.columns)).reset_index(drop=True)
    except Exception:
        # Some mixed-type columns can be hard for pandas to sort.
        # In that case, compare the same rows in their existing order.
        return df.reset_index(drop=True)


def compare_file(file_name):
    """Compare one CSV file and return a status line plus a status category."""
    original_path = ORIGINAL_DIR / file_name
    refactored_path = REFACTORED_DIR / file_name

    original_exists = original_path.exists()
    refactored_exists = refactored_path.exists()

    if not original_exists and not refactored_exists:
        return f"MISSING: {file_name} missing from both folders", "missing"

    if not original_exists:
        return f"MISSING: {file_name} missing from original folder", "missing"

    if not refactored_exists:
        return f"MISSING: {file_name} missing from refactored folder", "missing"

    original_df = pd.read_csv(original_path)
    refactored_df = pd.read_csv(refactored_path)

    if original_df.shape != refactored_df.shape:
        return (
            f"MISMATCH: {file_name}\n"
            f"  Reason: shapes differ "
            f"(original {original_df.shape}, refactored {refactored_df.shape})",
            "mismatch",
        )

    if list(original_df.columns) != list(refactored_df.columns):
        return (
            f"MISMATCH: {file_name}\n"
            "  Reason: column names differ",
            "mismatch",
        )

    original_df = sort_for_comparison(original_df)
    refactored_df = sort_for_comparison(refactored_df)

    try:
        pd.testing.assert_frame_equal(
            original_df,
            refactored_df,
            check_dtype=False,
            atol=1e-6,
            rtol=1e-6,
        )
    except AssertionError as error:
        first_line = str(error).splitlines()[0]
        return (
            f"MISMATCH: {file_name}\n"
            f"  Reason: values differ ({first_line})",
            "mismatch",
        )

    return f"MATCH: {file_name}", "match"


def main():
    """Compare all configured files and write the text report."""
    report_lines = []
    matched_count = 0
    mismatched_count = 0
    missing_count = 0

    for file_name in FILES_TO_COMPARE:
        message, status = compare_file(file_name)
        report_lines.append(message)

        if status == "match":
            matched_count += 1
        elif status == "mismatch":
            mismatched_count += 1
        else:
            missing_count += 1

    summary_lines = [
        "",
        "Comparison complete.",
        f"Files matched: {matched_count}",
        f"Files mismatched: {mismatched_count}",
        f"Files missing: {missing_count}",
    ]

    report_lines.extend(summary_lines)
    report_text = "\n".join(report_lines)

    print(report_text)

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    main()
