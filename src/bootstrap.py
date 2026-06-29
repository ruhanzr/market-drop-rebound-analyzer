"""Bootstrap confidence intervals for selected setup returns."""

import numpy as np
import pandas as pd

from config import CORE_TICKERS, ETF_CATEGORIES


def bootstrap_average_return(trade_returns, num_simulations=10000):
    """Estimate a confidence interval for average return by resampling trades.

    Bootstrapping resamples the selected trades with replacement. This gives a
    simple estimate of how stable the average trade return is.
    """
    bootstrap_means = []

    for simulation in range(num_simulations):
        sample = trade_returns.sample(
            n=len(trade_returns),
            replace=True,
        )

        bootstrap_means.append(sample.mean())

    lower_bound = np.percentile(bootstrap_means, 2.5)
    upper_bound = np.percentile(bootstrap_means, 97.5)

    return lower_bound, upper_bound


def create_bootstrap_summary(drawdown_summary):
    """Create bootstrap confidence interval rows for each selected setup."""
    bootstrap_rows = []

    for setup, group in drawdown_summary.groupby(["Ticker", "Drop threshold (%)", "Holding period"]):
        ticker, threshold, holding_period = setup
        trade_returns = group["Trade return after costs"].dropna()

        lower_bound, upper_bound = bootstrap_average_return(trade_returns)

        bootstrap_rows.append(
            {
                "Ticker": ticker,
                "Category": ETF_CATEGORIES[ticker],
                "Universe": "Core" if ticker in CORE_TICKERS else "Expanded Addition",
                "Drop threshold (%)": threshold,
                "Holding period": holding_period,
                "Number of trades": len(trade_returns),
                "Average trade return after costs (%)": round(trade_returns.mean() * 100, 2),
                "Bootstrap 95% lower bound (%)": round(lower_bound * 100, 2),
                "Bootstrap 95% upper bound (%)": round(upper_bound * 100, 2),
            }
        )

    return pd.DataFrame(bootstrap_rows)
