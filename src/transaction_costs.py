"""Transaction-cost sensitivity functions."""

from config import CORE_TICKERS, ETF_CATEGORIES


def calculate_transaction_cost_rows(
    ticker,
    threshold,
    big_drop_days,
    metrics,
    holding_periods,
    start_year,
    end_year,
    transaction_costs,
):
    """Recalculate setup metrics after applying each transaction-cost assumption."""
    transaction_rows = []

    for transaction_cost in transaction_costs:
        for days in holding_periods:
            return_column = f"Return_{days}_Day_Later"

            # Costs are applied to each trade first because they can change
            # which trades count as winners and losers.
            after_cost_returns = big_drop_days[return_column] - transaction_cost

            after_cost_avg_return = after_cost_returns.mean()
            after_cost_benchmark = metrics[days]["benchmark_avg_return"]
            after_cost_edge = after_cost_avg_return - after_cost_benchmark
            after_cost_win_rate = (after_cost_returns > 0).mean()
            after_cost_best = after_cost_returns.max()
            after_cost_worst = after_cost_returns.min()
            after_cost_winning_trades = after_cost_returns[after_cost_returns > 0]
            after_cost_losing_trades = after_cost_returns[after_cost_returns <= 0]
            after_cost_avg_win = after_cost_winning_trades.mean()
            after_cost_avg_loss = after_cost_losing_trades.mean()
            after_cost_score = after_cost_edge / abs(after_cost_avg_loss)

            transaction_rows.append(
                {
                    "Period": f"{start_year}-{end_year}",
                    "Transaction cost (%)": round(transaction_cost * 100, 2),
                    "Ticker": ticker,
                    "Category": ETF_CATEGORIES[ticker],
                    "Universe": "Core" if ticker in CORE_TICKERS else "Expanded Addition",
                    "Drop threshold (%)": round(threshold * 100, 1),
                    "Holding period": days,
                    "Number of big drop days": len(big_drop_days),
                    "Average return after costs (%)": round(after_cost_avg_return * 100, 2),
                    "Benchmark average return (%)": round(after_cost_benchmark * 100, 2),
                    "Edge vs benchmark after costs (%)": round(after_cost_edge * 100, 2),
                    "Win rate after costs (%)": round(after_cost_win_rate * 100, 2),
                    "Best return after costs (%)": round(after_cost_best * 100, 2),
                    "Worst return after costs (%)": round(after_cost_worst * 100, 2),
                    "Average winning trade after costs (%)": round(after_cost_avg_win * 100, 2),
                    "Average losing trade after costs (%)": round(after_cost_avg_loss * 100, 2),
                    "Risk-adjusted score after costs": round(after_cost_score, 3),
                }
            )

    return transaction_rows


def rank_after_cost_sensitivity(transaction_summary, min_events):
    """Find setups that still pass the filters after transaction costs."""
    ranked_after_cost_sensitivity = transaction_summary[
        (transaction_summary["Number of big drop days"] >= min_events)
        & (transaction_summary["Edge vs benchmark after costs (%)"] > 0)
        & (transaction_summary["Win rate after costs (%)"] >= 55)
    ].copy()

    return ranked_after_cost_sensitivity.sort_values(
        by=["Transaction cost (%)", "Risk-adjusted score after costs"],
        ascending=[True, False],
    )
