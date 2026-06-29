import pandas as pd
import yfinance as yf

from analysis import analyze_ticker
from ranking import rank_setups
from config import TICKERS, DROP_THRESHOLDS, HOLDING_PERIODS

def build_period_results(start_date, end_date):
    """
    Runs the normal ticker/threshold analysis for one time period.

    This function creates the same kind of long-format table that the main
    project already uses for ranking setups.
    """

    start_year = start_date[:4]
    end_year = str(int(end_date[:4]) - 1)

    long_format_rows = []

    # Loop through each ETF.
    for ticker in TICKERS:
        print(f"Downloading {ticker} from {start_date} to {end_date}...")

        data = yf.download(ticker, start=start_date, end=end_date)

        # For each ETF, test each drop threshold.
        for threshold in DROP_THRESHOLDS:
            combined_row, long_rows = analyze_ticker(
                ticker,
                threshold,
                data,
                HOLDING_PERIODS,
                start_year,
                end_year
            )

            # We only need long-format rows because those are best for ranking.
            long_format_rows.extend(long_rows)

    period_results = pd.DataFrame(long_format_rows)

    return period_results

def select_training_setups(training_results):

    ranked_training_setups = rank_setups(training_results, min_events=25, min_win_rate=55)
    top_training_setups = ranked_training_setups.head(10)
    return top_training_setups

def match_training_to_test(top_training_setups, test_results):
    out_of_sample_rows = []

    for index, training_row in top_training_setups.iterrows():
        ticker = training_row["Ticker"]
        threshold = training_row["Drop threshold (%)"]
        holding_period = training_row["Holding period"]

        matching_test_row = test_results[
            (test_results["Ticker"] == ticker) &
            (test_results["Drop threshold (%)"] == threshold) &
            (test_results["Holding period"] == holding_period)
        ]

        if matching_test_row.empty:
            continue

        test_row = matching_test_row.iloc[0]

        passed_test = (
            test_row["Edge vs benchmark (%)"] > 0 and
            test_row["Win rate (%)"] >= 55
        )

        out_of_sample_rows.append({
            "Ticker": ticker,
            "Drop threshold (%)": threshold,
            "Holding period": holding_period,

            "Training number of big drop days": training_row["Number of big drop days"],
            "Training average return (%)": training_row["Average return (%)"],
            "Training edge vs benchmark (%)": training_row["Edge vs benchmark (%)"],
            "Training win rate (%)": training_row["Win rate (%)"],
            "Training risk-adjusted score": training_row["Risk-adjusted score"],

            "Test number of big drop days": test_row["Number of big drop days"],
            "Test average return (%)": test_row["Average return (%)"],
            "Test edge vs benchmark (%)": test_row["Edge vs benchmark (%)"],
            "Test win rate (%)": test_row["Win rate (%)"],
            "Test risk-adjusted score": test_row["Risk-adjusted score"],

            "Passed out-of-sample test": "Yes" if passed_test else "No"
        })

    return pd.DataFrame(out_of_sample_rows)

def run_out_of_sample_test():
    """
    Runs a basic out-of-sample test.

    Training period:
    2010-2019

    Test period:
    2020-2024

    The training period chooses the top setups.
    The test period only tests those exact same setups.
    """

    training_results = build_period_results("2010-01-01", "2020-01-01")

    top_training_setups = select_training_setups(training_results)

    test_results = build_period_results("2020-01-01", "2025-01-01")

    out_of_sample_summary = match_training_to_test(
        top_training_setups,
        test_results
    )

    return out_of_sample_summary