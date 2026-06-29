import yfinance as yf
import pandas as pd
import numpy as np
def analyze_ticker(ticker, threshold, data, holding_periods, startYear, endYear, transaction_costs):
    print(f"Analyzing {ticker} at {threshold * 100:.1f}% threshold...")
    data = data.copy()
    data["Daily_Return"] = data["Close"].pct_change()
    metrics = {}
    threshold_label = f"{abs(threshold) * 100:.1f}".replace(".", "p")
    for days in holding_periods:
        data[f"Return_{days}_Day_Later"] = (data["Close"].shift(-days) / data["Close"]) - 1

    big_drop_days = data[data["Daily_Return"] <= threshold]
    big_drop_days = big_drop_days.copy()

    big_drop_days["Ticker"] = ticker
    big_drop_days["Drop_Threshold"] = threshold

    big_drop_days = big_drop_days.reset_index()

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
            "avg_loss": big_drop_days[big_drop_days[return_column] <= 0][return_column].mean()
        }

    summary_rows = []

    summary_rows.append({
        "Metric": "Drop threshold",
        "Value": f"{threshold * 100:.1f}%"
    })    

    summary_rows.append({
        "Metric": "Number of big drop days",
        "Value": len(big_drop_days)
    })

    for days in holding_periods:
        summary_rows.append({
            "Metric": f"Average {days}-day return",
            "Value": f"{metrics[days]['avg_return'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Benchmark average {days}-day return",
            "Value": f"{metrics[days]['benchmark_avg_return'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Edge vs benchmark {days}-day return",
            "Value": f"{metrics[days]['edge_vs_benchmark'] * 100:.2f}%"
        })        
        summary_rows.append({
            "Metric": f"{days}-day win rate",
            "Value": f"{metrics[days]['win_rate'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Best {days}-day return",
            "Value": f"{metrics[days]['best_return'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Worst {days}-day return",
            "Value": f"{metrics[days]['worst_return'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Average {days}-day winning trade",
            "Value": f"{metrics[days]['avg_win'] * 100:.2f}%"
        })
        summary_rows.append({
            "Metric": f"Average {days}-day losing trade",
            "Value": f"{metrics[days]['avg_loss'] * 100:.2f}%"
        })
    summary = pd.DataFrame(summary_rows)

    print(f"Finished analysis for {ticker}")

    big_drop_days.to_csv(f"results/{ticker}_{threshold_label}_big_drop_days_{startYear}-{endYear}.csv", index=False)
    summary.to_csv(f"results/{ticker}_{threshold_label}_summary_{startYear}-{endYear}.csv", index=False)
    print(f"Saved results for {ticker} at {threshold * 100:.1f}% threshold")

    combined_row = {
        "Period": f"{startYear}-{endYear}",
        "Ticker": ticker,
        "Drop threshold": f"{threshold * 100:.1f}%",
        "Number of big drop days": len(big_drop_days)
    }

    for days in holding_periods:
        combined_row[f"Average {days}-day return"] = f"{metrics[days]['avg_return'] * 100:.2f}%"
        combined_row[f"Benchmark average {days}-day return"] = f"{metrics[days]['benchmark_avg_return'] * 100:.2f}%"
        combined_row[f"Edge vs benchmark {days}-day return"] = f"{metrics[days]['edge_vs_benchmark'] * 100:.2f}%"
        combined_row[f"{days}-day win rate"] = f"{metrics[days]['win_rate'] * 100:.2f}%"
        combined_row[f"Best {days}-day return"] = f"{metrics[days]['best_return'] * 100:.2f}%"
        combined_row[f"Worst {days}-day return"] = f"{metrics[days]['worst_return'] * 100:.2f}%"
        combined_row[f"Average {days}-day winning trade"] = f"{metrics[days]['avg_win'] * 100:.2f}%"
        combined_row[f"Average {days}-day losing trade"] = f"{metrics[days]['avg_loss'] * 100:.2f}%"
        
    long_rows = []

    for days in holding_periods:
        long_rows.append({
            "Period": f"{startYear}-{endYear}",
            "Ticker": ticker,
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
            "Risk-adjusted score": round(metrics[days]["edge_vs_benchmark"] / abs(metrics[days]["avg_loss"]), 3)
        })

    transaction_rows = []

    for transaction_cost in transaction_costs:
        for days in holding_periods:
            return_column = f"Return_{days}_Day_Later"
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

            transaction_rows.append({
                "Period": f"{startYear}-{endYear}",
                "Transaction cost (%)": round(transaction_cost * 100, 2),
                "Ticker": ticker,
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

                "Risk-adjusted score after costs": round(after_cost_score, 3)
            })
    return combined_row, long_rows, transaction_rows

def analyze_selected_setup(ticker, threshold, holding_period, data, transaction_cost):
    data = data.copy()

    data["Daily_Return"] = data["Close"].pct_change()

    return_column = f"Return_{holding_period}_Day_Later"
    data[return_column] = (data["Close"].shift(-holding_period) / data["Close"]) - 1

    setup_trades = data[data["Daily_Return"] <= threshold].copy()
    setup_trades = setup_trades.reset_index()
    setup_trades = setup_trades.rename(columns={"index": "Date"})
    setup_trades["Ticker"] = ticker
    setup_trades["Drop threshold (%)"] = threshold * 100
    setup_trades["Holding period"] = holding_period

    setup_trades["Trade return"] = setup_trades[return_column]
    setup_trades["Trade return after costs"] = setup_trades["Trade return"] - transaction_cost

    setup_trades["Cumulative return"] = (1 + setup_trades["Trade return after costs"]).cumprod() - 1

    setup_trades["Running peak"] = setup_trades["Cumulative return"].cummax()

    setup_trades["Drawdown"] = (
        (1 + setup_trades["Cumulative return"]) /
        (1 + setup_trades["Running peak"])
    ) - 1

    setup_trades = setup_trades[[
    "Date",
    "Ticker",
    "Drop threshold (%)",
    "Holding period",
    "Daily_Return",
    return_column,
    "Trade return",
    "Trade return after costs",
    "Cumulative return",
    "Running peak",
    "Drawdown"
    ]]

    return setup_trades

def bootstrap_average_return(trade_returns, num_simulations=10000):
    bootstrap_means = []

    for simulation in range(num_simulations):
        sample = trade_returns.sample(
            n=len(trade_returns),
            replace=True
        )

        bootstrap_means.append(sample.mean())

    lower_bound = np.percentile(bootstrap_means, 2.5)
    upper_bound = np.percentile(bootstrap_means, 97.5)

    return lower_bound, upper_bound

tickers = ["SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV"]
drop_thresholds = [-0.01, -0.015, -0.02, -0.025, -0.03]
holding_periods = [1, 3, 5]
periods = [
    ("2010-01-01", "2015-01-01"),
    ("2015-01-01", "2020-01-01"),
    ("2020-01-01", "2025-01-01")
]
transaction_costs = [0.0, 0.001, 0.0025, 0.005]
survival_summary_rows = []
for start_date, end_date in periods:
    startYear = start_date[:4]
    endYear = str(int(end_date[:4]) - 1)
    combined_rows = []
    long_format_rows = []
    transaction_row = []
    for ticker in tickers:
        data = yf.download(ticker, start=start_date, end=end_date)
        for threshold in drop_thresholds:
            combined_row, long_rows, transaction_rows = analyze_ticker(ticker, threshold, data, holding_periods, startYear, endYear, transaction_costs)
            combined_rows.append(combined_row)
            long_format_rows.extend(long_rows)
            transaction_row.extend(transaction_rows)
            print()

    combined_summary = pd.DataFrame(combined_rows)
    long_format_summary = pd.DataFrame(long_format_rows)
    transaction_summary = pd.DataFrame(transaction_row)

    ranked_setups = long_format_summary[
        (long_format_summary["Number of big drop days"] >= 25) & (long_format_summary["Edge vs benchmark (%)"] > 0) & (long_format_summary["Win rate (%)"] >= 55)                                 
    ]
    ranked_setups = ranked_setups.sort_values(
        by="Risk-adjusted score",
        ascending=False
    )

    ranked_after_cost_sensitivity = transaction_summary[
        (transaction_summary["Number of big drop days"] >= 25) & (transaction_summary["Edge vs benchmark after costs (%)"] > 0) & (transaction_summary["Win rate after costs (%)"] >= 55)
    ]

    ranked_after_cost_sensitivity = ranked_after_cost_sensitivity.sort_values(
        by=["Transaction cost (%)", "Risk-adjusted score after costs"],
        ascending=[True, False]
    )

    survival_counts = (
    ranked_after_cost_sensitivity
    .groupby("Transaction cost (%)")
    .size()
    .reset_index(name="Number of surviving setups")
    )

    for index, row in survival_counts.iterrows():
        survival_summary_rows.append({
            "Period": f"{startYear}-{endYear}",
            "Transaction cost (%)": row["Transaction cost (%)"],
            "Number of surviving setups": row["Number of surviving setups"]
    })

    transaction_summary.to_csv(f"filtered_results/transaction_cost_sensitivity_{startYear}-{endYear}.csv", index=False)
    ranked_after_cost_sensitivity.to_csv(f"filtered_results/ranked_after_cost_sensitivity_{startYear}-{endYear}.csv", index=False)
    ranked_setups.to_csv(f"filtered_results/ranked_setups_{startYear}-{endYear}.csv", index=False)
    combined_summary.to_csv(f"filtered_results/combined_summary_{startYear}-{endYear}.csv", index=False)
    long_format_summary.to_csv(f"filtered_results/long_format_summary_{startYear}-{endYear}.csv", index=False)
    print("Saved results for combined summary, long format summary, & ranked-setups")
    survival_summary = pd.DataFrame(survival_summary_rows)

    survival_summary.to_csv(
        "filtered_results/transaction_cost_survival_summary.csv",
        index=False
    )

    print("Saved transaction cost survival summary")

selected_setups = [
    ("SPY", -0.02, 5),
    ("QQQ", -0.025, 5),
    ("XLF", -0.025, 5)
]

drawdown_rows = []

for ticker, threshold, holding_period in selected_setups:
    data = yf.download(ticker, start="2010-01-01", end="2025-01-01")

    setup_trades = analyze_selected_setup(
        ticker,
        threshold,
        holding_period,
        data,
        transaction_cost=0.001
    )

    drawdown_rows.append(setup_trades)

drawdown_summary = pd.concat(drawdown_rows, ignore_index=True)

drawdown_result_rows = []

for setup, group in drawdown_summary.groupby(["Ticker", "Drop threshold (%)", "Holding period"]):
    ticker, threshold, holding_period = setup

    final_cumulative_return = group["Cumulative return"].iloc[-1]
    max_drawdown = group["Drawdown"].min()
    average_trade_return = group["Trade return after costs"].mean()
    win_rate = (group["Trade return after costs"] > 0).mean()
    best_trade = group["Trade return after costs"].max()
    worst_trade = group["Trade return after costs"].min()

    drawdown_result_rows.append({
        "Ticker": ticker,
        "Drop threshold (%)": threshold,
        "Holding period": holding_period,
        "Number of trades": len(group),
        "Final cumulative return (%)": round(final_cumulative_return * 100, 2),
        "Maximum drawdown (%)": round(max_drawdown * 100, 2),
        "Average trade return after costs (%)": round(average_trade_return * 100, 2),
        "Win rate after costs (%)": round(win_rate * 100, 2),
        "Best trade after costs (%)": round(best_trade * 100, 2),
        "Worst trade after costs (%)": round(worst_trade * 100, 2)
    })

drawdown_results = pd.DataFrame(drawdown_result_rows)

drawdown_results.to_csv(
    "filtered_results/selected_setup_drawdown_summary.csv",
    index=False
)

print("Saved selected setup drawdown summary")

drawdown_summary.to_csv(
    "filtered_results/selected_setup_drawdowns.csv",
    index=False
)

print("Saved selected setup drawdown analysis")

bootstrap_rows = []

for setup, group in drawdown_summary.groupby(["Ticker", "Drop threshold (%)", "Holding period"]):
    ticker, threshold, holding_period = setup

    trade_returns = group["Trade return after costs"].dropna()

    lower_bound, upper_bound = bootstrap_average_return(trade_returns)

    bootstrap_rows.append({
        "Ticker": ticker,
        "Drop threshold (%)": threshold,
        "Holding period": holding_period,
        "Number of trades": len(trade_returns),
        "Average trade return after costs (%)": round(trade_returns.mean() * 100, 2),
        "Bootstrap 95% lower bound (%)": round(lower_bound * 100, 2),
        "Bootstrap 95% upper bound (%)": round(upper_bound * 100, 2)
    })

bootstrap_summary = pd.DataFrame(bootstrap_rows)

bootstrap_summary.to_csv(
    "filtered_results/selected_setup_bootstrap_summary.csv",
    index=False
)

print("Saved selected setup bootstrap summary")