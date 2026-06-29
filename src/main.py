"""Main execution script for the ETF selloff rebound project."""

from pathlib import Path

import pandas as pd

from analysis import analyze_ticker, download_data, get_big_drop_days_and_metrics
from bootstrap import create_bootstrap_summary
from config import (
    DROP_THRESHOLDS,
    FULL_END_DATE,
    FULL_START_DATE,
    HOLDING_PERIODS,
    MIN_EVENTS_BY_PERIOD,
    MIN_WIN_RATE,
    PERIODS,
    SELECTED_SETUP_TRANSACTION_COST,
    SELECTED_SETUPS,
    TICKERS,
    TRANSACTION_COSTS,
)
from drawdown import analyze_selected_setup, summarize_drawdowns
from ranking import rank_setups
from transaction_costs import calculate_transaction_cost_rows, rank_after_cost_sensitivity
from out_of_sample import run_out_of_sample_test

RESULTS_DIR = Path("results")
FILTERED_RESULTS_DIR = Path("filtered_results")


def year_label(start_date, end_date):
    """Convert date strings into the output label used in file names."""
    start_year = start_date[:4]
    end_year = str(int(end_date[:4]) - 1)
    return start_year, end_year


def main():
    # 1. Load settings
    RESULTS_DIR.mkdir(exist_ok=True)
    FILTERED_RESULTS_DIR.mkdir(exist_ok=True)

    survival_summary_rows = []

    # 2. Run period-based analysis
    # This outer loop runs the analysis separately for each market period.
    for start_date, end_date in PERIODS:
        start_year, end_year = year_label(start_date, end_date)

        combined_rows = []
        long_format_rows = []
        transaction_rows_for_period = []

        # Inside each period, the code loops through each ticker and each drop threshold.
        for ticker in TICKERS:
            data = download_data(ticker, start_date=start_date, end_date=end_date)

            for threshold in DROP_THRESHOLDS:
                combined_row, long_rows = analyze_ticker(
                    ticker,
                    threshold,
                    data,
                    HOLDING_PERIODS,
                    start_year,
                    end_year,
                )

                combined_rows.append(combined_row)
                long_format_rows.extend(long_rows)

                big_drop_days, metrics = get_big_drop_days_and_metrics(
                    ticker,
                    threshold,
                    data,
                    HOLDING_PERIODS,
                )
                transaction_rows = calculate_transaction_cost_rows(
                    ticker,
                    threshold,
                    big_drop_days,
                    metrics,
                    HOLDING_PERIODS,
                    start_year,
                    end_year,
                    TRANSACTION_COSTS,
                )
                transaction_rows_for_period.extend(transaction_rows)
                print()

        combined_summary = pd.DataFrame(combined_rows)
        long_format_summary = pd.DataFrame(long_format_rows)
        transaction_summary = pd.DataFrame(transaction_rows_for_period)

        # 3. Save combined summaries
        # The combined summary is wide and easy to read one ticker/threshold at a time.
        combined_summary.to_csv(
            FILTERED_RESULTS_DIR / f"combined_summary_{start_year}-{end_year}.csv",
            index=False,
        )

        # 4. Save long-format summaries
        # Long format is better for ranking because each row is one setup.
        long_format_summary.to_csv(
            FILTERED_RESULTS_DIR / f"long_format_summary_{start_year}-{end_year}.csv",
            index=False,
        )

        # 5. Rank setups
        ranked_setups = rank_setups(
            long_format_summary,
            min_events=MIN_EVENTS_BY_PERIOD,
            min_win_rate=MIN_WIN_RATE,
        )
        ranked_setups.to_csv(
            FILTERED_RESULTS_DIR / f"ranked_setups_{start_year}-{end_year}.csv",
            index=False,
        )

        # 6. Run transaction-cost sensitivity
        # Transaction costs were already applied to individual trades before recalculating metrics.
        transaction_summary.to_csv(
            FILTERED_RESULTS_DIR / f"transaction_cost_sensitivity_{start_year}-{end_year}.csv",
            index=False,
        )
        ranked_after_cost_sensitivity = rank_after_cost_sensitivity(
            transaction_summary,
            min_events=MIN_EVENTS_BY_PERIOD,
        )
        ranked_after_cost_sensitivity.to_csv(
            FILTERED_RESULTS_DIR / f"ranked_after_cost_sensitivity_{start_year}-{end_year}.csv",
            index=False,
        )

        survival_counts = (
            ranked_after_cost_sensitivity.groupby("Transaction cost (%)")
            .size()
            .reset_index(name="Number of surviving setups")
        )

        for index, row in survival_counts.iterrows():
            survival_summary_rows.append(
                {
                    "Period": f"{start_year}-{end_year}",
                    "Transaction cost (%)": row["Transaction cost (%)"],
                    "Number of surviving setups": row["Number of surviving setups"],
                }
            )

        print("Saved results for combined summary, long format summary, & ranked-setups")

    # 7. Save transaction-cost survival summary
    survival_summary = pd.DataFrame(survival_summary_rows)
    survival_summary.to_csv(
        FILTERED_RESULTS_DIR / "transaction_cost_survival_summary.csv",
        index=False,
    )
    print("Saved transaction cost survival summary")

    # 8. Run selected setup drawdown analysis
    # Drawdown is different from average return because it tracks the path from peak to loss.
    drawdown_rows = []

    for ticker, threshold, holding_period in SELECTED_SETUPS:
        data = download_data(ticker, start_date=FULL_START_DATE, end_date=FULL_END_DATE)
        setup_trades = analyze_selected_setup(
            ticker,
            threshold,
            holding_period,
            data,
            transaction_cost=SELECTED_SETUP_TRANSACTION_COST,
        )
        drawdown_rows.append(setup_trades)

    drawdown_summary = pd.concat(drawdown_rows, ignore_index=True)
    drawdown_results = summarize_drawdowns(drawdown_summary)

    # 9. Save drawdown event file and drawdown summary
    drawdown_summary.to_csv(
        FILTERED_RESULTS_DIR / "selected_setup_drawdowns.csv",
        index=False,
    )
    drawdown_results.to_csv(
        FILTERED_RESULTS_DIR / "selected_setup_drawdown_summary.csv",
        index=False,
    )
    print("Saved selected setup drawdown analysis")
    print("Saved selected setup drawdown summary")

    # 10. Run bootstrap confidence interval analysis
    # Bootstrap intervals help show whether selected setup averages look stable or noisy.
    bootstrap_summary = create_bootstrap_summary(drawdown_summary)

    # 11. Save bootstrap summary
    bootstrap_summary.to_csv(
        FILTERED_RESULTS_DIR / "selected_setup_bootstrap_summary.csv",
        index=False,
    )
    print("Saved selected setup bootstrap summary")

    # 11. Run out-of-sample validation
    out_of_sample_summary = run_out_of_sample_test()

    out_of_sample_summary.to_csv(
        "filtered_results/out_of_sample_test_summary.csv",
        index=False
    )

    print("Saved out-of-sample test summary")

if __name__ == "__main__":
    main()
