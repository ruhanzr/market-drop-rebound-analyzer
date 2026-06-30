"""Build the event-level ML dataset for Version 2 rebound prediction."""

from pathlib import Path
import sys

import pandas as pd
import yfinance as yf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import (  # noqa: E402
    CORE_TICKERS,
    DROP_THRESHOLDS,
    ETF_CATEGORIES,
    FULL_END_DATE,
    FULL_START_DATE,
    TICKERS,
)

THRESHOLDS = DROP_THRESHOLDS
START_DATE = FULL_START_DATE
END_DATE = FULL_END_DATE
OUTPUT_FILE = Path(__file__).resolve().parent / "ml_event_dataset.csv"
FORWARD_DAYS = 5
DATASET_COLUMNS = [
    "Date",
    "Ticker",
    "Category",
    "Universe",
    "Drop_Threshold",
    "Daily_Return",
    "Forward_5D_Return",
    "Benchmark_5D_Return",
    "Edge_vs_Benchmark_5D",
    "Target_Positive_5D",
    "Target_Beat_Benchmark_5D",
    "Previous_5D_Return",
    "Previous_10D_Return",
    "Previous_20D_Volatility",
    "Volume_Change",
    "Distance_From_20D_MA",
    "Distance_From_50D_MA",
    "Period",
]


def download_ticker_data(ticker):
    """Download one ticker and normalize yfinance's occasional MultiIndex columns."""
    data = yf.download(ticker, start=START_DATE, end=END_DATE)

    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs(ticker, axis=1, level=-1)

    return data


def assign_period(date):
    """Map an event date to the Version 1 market-period labels."""
    year = date.year

    if 2010 <= year <= 2014:
        return "2010-2014"
    if 2015 <= year <= 2019:
        return "2015-2019"
    if 2020 <= year <= 2024:
        return "2020-2024"

    return None


def add_features(data):
    """Create event features using only data available on or before each day."""
    data = data.copy()
    data["Daily_Return"] = data["Close"].pct_change()
    data["Forward_5D_Return"] = (data["Close"].shift(-FORWARD_DAYS) / data["Close"]) - 1
    data["Previous_5D_Return"] = (data["Close"] / data["Close"].shift(5)) - 1
    data["Previous_10D_Return"] = (data["Close"] / data["Close"].shift(10)) - 1
    data["Previous_20D_Volatility"] = data["Daily_Return"].shift(1).rolling(20).std()
    data["Volume_Change"] = (data["Volume"] / data["Volume"].rolling(20).mean()) - 1
    data["Distance_From_20D_MA"] = (data["Close"] / data["Close"].rolling(20).mean()) - 1
    data["Distance_From_50D_MA"] = (data["Close"] / data["Close"].rolling(50).mean()) - 1

    return data


def build_rows_for_ticker(ticker):
    """Build one ML row per ticker, threshold, and big-drop date."""
    data = download_ticker_data(ticker)

    if data.empty:
        print(f"No data returned for {ticker}; skipping.")
        return []

    data = add_features(data)
    benchmark_5d_return = data["Forward_5D_Return"].mean()
    category = ETF_CATEGORIES[ticker]
    universe = "Core" if ticker in CORE_TICKERS else "Expanded Addition"
    rows = []

    for threshold in THRESHOLDS:
        big_drop_days = data[data["Daily_Return"] <= threshold].copy()

        for event_date, row in big_drop_days.iterrows():
            rows.append(
                {
                    "Date": event_date.date().isoformat(),
                    "Ticker": ticker,
                    "Category": category,
                    "Universe": universe,
                    "Drop_Threshold": threshold,
                    "Daily_Return": row["Daily_Return"],
                    "Forward_5D_Return": row["Forward_5D_Return"],
                    "Benchmark_5D_Return": benchmark_5d_return,
                    "Edge_vs_Benchmark_5D": row["Forward_5D_Return"] - benchmark_5d_return,
                    "Target_Positive_5D": 1 if row["Forward_5D_Return"] > 0 else 0,
                    "Target_Beat_Benchmark_5D": 1
                    if row["Forward_5D_Return"] > benchmark_5d_return
                    else 0,
                    "Previous_5D_Return": row["Previous_5D_Return"],
                    "Previous_10D_Return": row["Previous_10D_Return"],
                    "Previous_20D_Volatility": row["Previous_20D_Volatility"],
                    "Volume_Change": row["Volume_Change"],
                    "Distance_From_20D_MA": row["Distance_From_20D_MA"],
                    "Distance_From_50D_MA": row["Distance_From_50D_MA"],
                    "Period": assign_period(event_date),
                }
            )

    return rows


def build_ml_event_dataset():
    """Create and save the full Version 2 event-level ML dataset."""
    all_rows = []
    processed_tickers = 0

    for ticker in TICKERS:
        print(f"Processing {ticker}...")
        ticker_rows = build_rows_for_ticker(ticker)
        all_rows.extend(ticker_rows)
        processed_tickers += 1

    dataset = pd.DataFrame(all_rows, columns=DATASET_COLUMNS)

    required_columns = [
        "Daily_Return",
        "Forward_5D_Return",
        "Benchmark_5D_Return",
        "Edge_vs_Benchmark_5D",
        "Previous_5D_Return",
        "Previous_10D_Return",
        "Previous_20D_Volatility",
        "Volume_Change",
        "Distance_From_20D_MA",
        "Distance_From_50D_MA",
        "Period",
    ]
    dataset = dataset.dropna(subset=required_columns).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    dataset.to_csv(OUTPUT_FILE, index=False)

    print(f"Number of rows created: {len(dataset)}")
    print(f"Number of tickers processed: {processed_tickers}")
    print("Class balance for Target_Positive_5D:")
    print(dataset["Target_Positive_5D"].value_counts(normalize=True).sort_index())
    print("Class balance for Target_Beat_Benchmark_5D:")
    print(dataset["Target_Beat_Benchmark_5D"].value_counts(normalize=True).sort_index())
    print("Rows by Period:")
    print(dataset["Period"].value_counts().sort_index())
    print("Rows by Category:")
    print(dataset["Category"].value_counts().sort_index())

    return dataset


if __name__ == "__main__":
    build_ml_event_dataset()


