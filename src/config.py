"""Project settings for the ETF rebound analysis."""

# ETFs tested by the analysis.
TICKERS = ["SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV"]

# Daily return cutoffs that define a selloff day.
DROP_THRESHOLDS = [-0.01, -0.015, -0.02, -0.025, -0.03]

# Number of trading days to hold after a selloff day.
HOLDING_PERIODS = [1, 3, 5]

# Separate market periods used to see whether results are stable over time.
PERIODS = [
    ("2010-01-01", "2015-01-01"),
    ("2015-01-01", "2020-01-01"),
    ("2020-01-01", "2025-01-01"),
]

# Cost assumptions tested against each setup.
TRANSACTION_COSTS = [0.0, 0.001, 0.0025, 0.005]

# Setups chosen for the deeper drawdown and bootstrap checks.
SELECTED_SETUPS = [
    ("SPY", -0.02, 5),
    ("QQQ", -0.025, 5),
    ("XLF", -0.025, 5),
]

# Full date range used for selected setup drawdown and bootstrap analysis.
FULL_START_DATE = "2010-01-01"
FULL_END_DATE = "2025-01-01"

# Ranking filters keep very small samples and weak win rates out of the top lists.
MIN_EVENTS_BY_PERIOD = 25
MIN_WIN_RATE = 55

# Transaction cost used for the selected setup drawdown and bootstrap checks.
SELECTED_SETUP_TRANSACTION_COST = 0.001
