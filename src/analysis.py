"""Core ETF selloff analysis functions."""

from pathlib import Path

import pandas as pd
import yfinance as yf

from config import CORE_TICKERS, ETF_CATEGORIES


RESULTS_DIR = Path("results")


def download_data(ticker, start_date, end_date):
    """Download price data for one ETF over one date range."""
    data = yf.download(ticker, start=start_date, end=end_date)

    # Some yfinance versions return two-level columns even for one ticker.
    # Flattening keeps the output CSVs readable without changing the math.
    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs(ticker, axis=1, level=-1)

    return data


def calculate_future_returns(data, holding_periods):
    """Return a copy of the data with daily and forward return columns added."""
    data = data.copy()
    data["Daily_Return"] = data["Close"].pct_change()

    for days in holding_periods:
        data[f"Return_{days}_Day_Later"] = (data["Close"].shift(-days) / data["Close"]) - 1

    return data


def get_big_drop_days_and_metrics(ticker, threshold, data, holding_periods):
    """Find selloff days and calculate the metrics used by the summaries."""
    data = calculate_future_returns(data, holding_periods)

    big_drop_days = data[data["Daily_Return"] <= threshold].copy()
    big_drop_days["Ticker"] = ticker
    big_drop_days["Drop_Threshold"] = threshold
    big_drop_days = big_drop_days.reset_index()

    metrics = {}

    for days in holding_periods:
        return_column = f"Return_{days}_Day_Later"

        metrics[days] = {
            "avg_return": big_drop_days[return_column].mean(),
            "benchmark_avg_return": data[return_column].mean(),
            "edge_vs_benchmark": big_drop_days[return_column].mean() - data[return_column].mean(),
            "win_rate": (big_drop_days[return_column] > 0).mean(),
            "best_return": big_drop_days[return_column].max(),
            "worst_return": big_drop_days[return_column].min(),
            "avg_win": big_drop_days[big_drop_days[return_column] > 0][return_column].mean(),
            "avg_loss": big_drop_days[big_drop_days[return_column] <= 0][return_column].mean(),
        }

    return big_drop_days, metrics


def threshold_label(threshold):
    """Create the threshold text used in per-ticker output file names."""
    return f"{abs(threshold) * 100:.1f}".replace(".", "p")


def create_ticker_summary(ticker, threshold, big_drop_count, metrics, holding_periods):
    """Build the small Metric/Value summary saved for each ticker and threshold."""
    category = ETF_CATEGORIES[ticker]
    universe = "Core" if ticker in CORE_TICKERS else "Expanded Addition"

    summary_rows = [
        {"Category": category, "Universe": universe, "Metric": "Drop threshold", "Value": f"{threshold * 100:.1f}%"},
        {"Category": category, "Universe": universe, "Metric": "Number of big drop days", "Value": big_drop_count},
    ]

    for days in holding_periods:
        summary_rows.extend(
            [
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Average {days}-day return",
                    "Value": f"{metrics[days]['avg_return'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Benchmark average {days}-day return",
                    "Value": f"{metrics[days]['benchmark_avg_return'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Edge vs benchmark {days}-day return",
                    "Value": f"{metrics[days]['edge_vs_benchmark'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"{days}-day win rate",
                    "Value": f"{metrics[days]['win_rate'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Best {days}-day return",
                    "Value": f"{metrics[days]['best_return'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Worst {days}-day return",
                    "Value": f"{metrics[days]['worst_return'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Average {days}-day winning trade",
                    "Value": f"{metrics[days]['avg_win'] * 100:.2f}%",
                },
                {
                    "Category": category,
                    "Universe": universe,
                    "Metric": f"Average {days}-day losing trade",
                    "Value": f"{metrics[days]['avg_loss'] * 100:.2f}%",
                },
            ]
        )

    return pd.DataFrame(summary_rows)


def create_combined_row(ticker, threshold, big_drop_days, metrics, holding_periods, start_year, end_year):
    """Build one wide-format row for the period-level combined summary."""
    combined_row = {
        "Period": f"{start_year}-{end_year}",
        "Ticker": ticker,
        "Category": ETF_CATEGORIES[ticker],
        "Universe": "Core" if ticker in CORE_TICKERS else "Expanded Addition",
        "Drop threshold": f"{threshold * 100:.1f}%",
        "Number of big drop days": len(big_drop_days),
    }

    for days in holding_periods:
        combined_row[f"Average {days}-day return"] = f"{metrics[days]['avg_return'] * 100:.2f}%"
        combined_row[f"Benchmark average {days}-day return"] = (
            f"{metrics[days]['benchmark_avg_return'] * 100:.2f}%"
        )
        combined_row[f"Edge vs benchmark {days}-day return"] = (
            f"{metrics[days]['edge_vs_benchmark'] * 100:.2f}%"
        )
        combined_row[f"{days}-day win rate"] = f"{metrics[days]['win_rate'] * 100:.2f}%"
        combined_row[f"Best {days}-day return"] = f"{metrics[days]['best_return'] * 100:.2f}%"
        combined_row[f"Worst {days}-day return"] = f"{metrics[days]['worst_return'] * 100:.2f}%"
        combined_row[f"Average {days}-day winning trade"] = f"{metrics[days]['avg_win'] * 100:.2f}%"
        combined_row[f"Average {days}-day losing trade"] = f"{metrics[days]['avg_loss'] * 100:.2f}%"

    return combined_row


def create_long_rows(ticker, threshold, big_drop_days, metrics, holding_periods, start_year, end_year):
    """Build one row per ticker, threshold, and holding period for ranking."""
    long_rows = []

    for days in holding_periods:
        long_rows.append(
            {
                "Period": f"{start_year}-{end_year}",
                "Ticker": ticker,
                "Category": ETF_CATEGORIES[ticker],
                "Universe": "Core" if ticker in CORE_TICKERS else "Expanded Addition",
                "Drop threshold (%)": round(threshold * 100, 1),
                "Holding period": days,
                "Number of big drop days": len(big_drop_days),
                "Average return (%)": round(metrics[days]["avg_return"] * 100, 2),
                "Benchmark average return (%)": round(metrics[days]["benchmark_avg_return"] * 100, 2),
                "Edge vs benchmark (%)": round(metrics[days]["edge_vs_benchmark"] * 100, 2),
                "Win rate (%)": round(metrics[days]["win_rate"] * 100, 2),
                "Best return (%)": round(metrics[days]["best_return"] * 100, 2),
                "Worst return (%)": round(metrics[days]["worst_return"] * 100, 2),
                "Average winning trade (%)": round(metrics[days]["avg_win"] * 100, 2),
                "Average losing trade (%)": round(metrics[days]["avg_loss"] * 100, 2),
                "Risk-adjusted score": round(
                    metrics[days]["edge_vs_benchmark"] / abs(metrics[days]["avg_loss"]),
                    3,
                ),
            }
        )

    return long_rows


def save_ticker_outputs(ticker, threshold, big_drop_days, summary, start_year, end_year):
    """Save the per-ticker event file and readable summary file."""
    label = threshold_label(threshold)
    big_drop_days.to_csv(RESULTS_DIR / f"{ticker}_{label}_big_drop_days_{start_year}-{end_year}.csv", index=False)
    summary.to_csv(RESULTS_DIR / f"{ticker}_{label}_summary_{start_year}-{end_year}.csv", index=False)


def analyze_ticker(ticker, threshold, data, holding_periods, start_year, end_year):
    """Run one ticker/threshold analysis and return combined and long-format rows."""
    print(f"Analyzing {ticker} at {threshold * 100:.1f}% threshold...")

    big_drop_days, metrics = get_big_drop_days_and_metrics(ticker, threshold, data, holding_periods)
    summary = create_ticker_summary(ticker, threshold, len(big_drop_days), metrics, holding_periods)

    save_ticker_outputs(ticker, threshold, big_drop_days, summary, start_year, end_year)

    combined_row = create_combined_row(
        ticker,
        threshold,
        big_drop_days,
        metrics,
        holding_periods,
        start_year,
        end_year,
    )
    long_rows = create_long_rows(
        ticker,
        threshold,
        big_drop_days,
        metrics,
        holding_periods,
        start_year,
        end_year,
    )

    print(f"Finished analysis for {ticker}")
    print(f"Saved results for {ticker} at {threshold * 100:.1f}% threshold")

    return combined_row, long_rows
