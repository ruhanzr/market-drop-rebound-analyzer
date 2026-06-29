"""Drawdown analysis for selected setups."""

import pandas as pd

from config import CORE_TICKERS, ETF_CATEGORIES


def analyze_selected_setup(ticker, threshold, holding_period, data, transaction_cost):
    """Create event-level drawdown rows for one selected setup."""
    data = data.copy()
    data["Daily_Return"] = data["Close"].pct_change()

    return_column = f"Return_{holding_period}_Day_Later"
    data[return_column] = (data["Close"].shift(-holding_period) / data["Close"]) - 1

    setup_trades = data[data["Daily_Return"] <= threshold].copy()
    setup_trades = setup_trades.reset_index()
    setup_trades = setup_trades.rename(columns={"index": "Date"})
    setup_trades["Ticker"] = ticker
    setup_trades["Category"] = ETF_CATEGORIES[ticker]
    setup_trades["Universe"] = "Core" if ticker in CORE_TICKERS else "Expanded Addition"
    setup_trades["Drop threshold (%)"] = threshold * 100
    setup_trades["Holding period"] = holding_period

    setup_trades["Trade return"] = setup_trades[return_column]
    setup_trades["Trade return after costs"] = setup_trades["Trade return"] - transaction_cost

    setup_trades["Cumulative return"] = (1 + setup_trades["Trade return after costs"]).cumprod() - 1
    setup_trades["Running peak"] = setup_trades["Cumulative return"].cummax()

    # Drawdown measures how far the cumulative return has fallen from its
    # previous high. It shows the path of losses, not just the average trade.
    setup_trades["Drawdown"] = (
        (1 + setup_trades["Cumulative return"]) / (1 + setup_trades["Running peak"])
    ) - 1

    return setup_trades[
        [
            "Date",
            "Ticker",
            "Category",
            "Universe",
            "Drop threshold (%)",
            "Holding period",
            "Daily_Return",
            return_column,
            "Trade return",
            "Trade return after costs",
            "Cumulative return",
            "Running peak",
            "Drawdown",
        ]
    ]


def summarize_drawdowns(drawdown_summary):
    """Summarize the event-level drawdown rows by selected setup."""
    drawdown_result_rows = []

    for setup, group in drawdown_summary.groupby(["Ticker", "Drop threshold (%)", "Holding period"]):
        ticker, threshold, holding_period = setup

        final_cumulative_return = group["Cumulative return"].iloc[-1]
        max_drawdown = group["Drawdown"].min()
        average_trade_return = group["Trade return after costs"].mean()
        win_rate = (group["Trade return after costs"] > 0).mean()
        best_trade = group["Trade return after costs"].max()
        worst_trade = group["Trade return after costs"].min()

        drawdown_result_rows.append(
            {
                "Ticker": ticker,
                "Category": ETF_CATEGORIES[ticker],
                "Universe": "Core" if ticker in CORE_TICKERS else "Expanded Addition",
                "Drop threshold (%)": threshold,
                "Holding period": holding_period,
                "Number of trades": len(group),
                "Final cumulative return (%)": round(final_cumulative_return * 100, 2),
                "Maximum drawdown (%)": round(max_drawdown * 100, 2),
                "Average trade return after costs (%)": round(average_trade_return * 100, 2),
                "Win rate after costs (%)": round(win_rate * 100, 2),
                "Best trade after costs (%)": round(best_trade * 100, 2),
                "Worst trade after costs (%)": round(worst_trade * 100, 2),
            }
        )

    return pd.DataFrame(drawdown_result_rows)
