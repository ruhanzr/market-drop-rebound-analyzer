"""Expanded ETF universe comparison summaries."""

from pathlib import Path

import pandas as pd

from config import CORE_TICKERS, ETF_CATEGORIES, MIN_EVENTS_BY_PERIOD, MIN_WIN_RATE

FILTERED_RESULTS_DIR = Path("filtered_results")


LONG_FORMAT_PATTERN = "long_format_summary_*.csv"


def load_long_format_summaries(results_dir=FILTERED_RESULTS_DIR):
    """Load existing long-format setup summaries from filtered_results."""
    summary_files = sorted(Path(results_dir).glob(LONG_FORMAT_PATTERN))

    if not summary_files:
        return pd.DataFrame()

    summaries = [pd.read_csv(summary_file) for summary_file in summary_files]
    summary = pd.concat(summaries, ignore_index=True)

    if "Category" not in summary.columns:
        summary["Category"] = summary["Ticker"].map(ETF_CATEGORIES)
    if "Universe" not in summary.columns:
        summary["Universe"] = summary["Ticker"].apply(
            lambda ticker: "Core" if ticker in CORE_TICKERS else "Expanded Addition"
        )

    return summary


def passing_setups(summary):
    """Apply the same basic pass rule used by ranking."""
    return summary[
        (summary["Number of big drop days"] >= MIN_EVENTS_BY_PERIOD)
        & (summary["Edge vs benchmark (%)"] > 0)
        & (summary["Win rate (%)"] >= MIN_WIN_RATE)
    ].copy()


def summarize_group(group_name, group_data):
    """Create one comparison row for a universe or category group."""
    passing = passing_setups(group_data)
    best_pool = passing if not passing.empty else group_data
    best_row = best_pool.sort_values("Risk-adjusted score", ascending=False).iloc[0]

    return {
        "Group": group_name,
        "Number_of_ETFs": group_data["Ticker"].nunique(),
        "Number_of_Setups": len(group_data),
        "Number_of_Passing_Setups": len(passing),
        "Average_Edge_vs_Benchmark": round(group_data["Edge vs benchmark (%)"].mean(), 2),
        "Average_Win_Rate": round(group_data["Win rate (%)"].mean(), 2),
        "Best_Ticker": best_row["Ticker"],
        "Best_Drop_Threshold": best_row["Drop threshold (%)"],
        "Best_Holding_Period": best_row["Holding period"],
        "Best_Edge_vs_Benchmark": best_row["Edge vs benchmark (%)"],
        "Best_Risk_Adjusted_Score": best_row["Risk-adjusted score"],
    }


def create_comparison(summary, group_column):
    """Summarize setup behavior by one grouping column."""
    rows = [
        summarize_group(group_name, group_data)
        for group_name, group_data in summary.groupby(group_column)
    ]

    return pd.DataFrame(rows).sort_values(
        by=["Number_of_Passing_Setups", "Average_Edge_vs_Benchmark"],
        ascending=[False, False],
    )


def run_universe_comparison(results_dir=FILTERED_RESULTS_DIR):
    """Create universe and category comparison CSVs from long-format summaries."""
    results_dir = Path(results_dir)
    summary = load_long_format_summaries(results_dir)

    if summary.empty:
        print("No long-format summaries found for universe comparison.")
        return pd.DataFrame(), pd.DataFrame()

    universe_comparison = create_comparison(summary, "Universe")
    category_comparison = create_comparison(summary, "Category")

    universe_comparison.to_csv(results_dir / "universe_comparison.csv", index=False)
    category_comparison.to_csv(results_dir / "category_comparison.csv", index=False)

    return universe_comparison, category_comparison
