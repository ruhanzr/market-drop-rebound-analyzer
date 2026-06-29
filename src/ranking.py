"""Ranking helpers for setup summaries."""


def rank_setups(long_format_summary, min_events, min_win_rate):
    """Filter and sort setups using the long-format summary table.

    Long format is easier for ranking because each row is one complete setup:
    ticker, threshold, holding period, and its metrics.
    """
    ranked_setups = long_format_summary[
        (long_format_summary["Number of big drop days"] >= min_events)
        & (long_format_summary["Edge vs benchmark (%)"] > 0)
        & (long_format_summary["Win rate (%)"] >= min_win_rate)
    ].copy()

    return ranked_setups.sort_values(
        by="Risk-adjusted score",
        ascending=False,
    )
