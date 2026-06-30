# Methodology

This document explains the calculations, metrics, and validation steps used in the Market Drop Rebound Analyzer project.

## How the Project Works

The project follows this general process:

1. Load project settings from `config.py`.
2. Download historical ETF price data.
3. Calculate daily returns.
4. Calculate future returns for 1-day, 3-day, and 5-day holding periods.
5. Identify big-drop days based on each threshold.
6. Calculate performance metrics after those drops.
7. Compare those returns to benchmark average returns.
8. Calculate edge vs benchmark.
9. Calculate a simple risk-adjusted score.
10. Save event-level and summary CSV files.
11. Create long-format summary files for filtering and ranking.
12. Rank setups using sample size, edge, win rate, and risk-adjusted score.
13. Repeat the analysis across separate market periods.
14. Apply transaction-cost assumptions.
15. Compare setup survival under different cost levels.
16. Analyze cumulative return and drawdown for selected repeated setups.
17. Run bootstrap confidence intervals for selected setups.
18. Run out-of-sample validation using 2010-2019 as training data and 2020-2024 as test data.
19. Compare the original core ETF universe against the expanded ETF universe.
20. Build an event-level ML dataset from the big-drop events.
21. Train baseline ML models using a time-based train/test split.
22. Interpret model features and test probability-threshold filtering.

---

## Main Calculations

### Daily Return

The first important calculation is the ETF’s daily return:

```python
data["Daily_Return"] = data["Close"].pct_change()
```

This calculates the percentage change from one closing price to the next. It is what allows the program to identify days where an ETF dropped by a certain amount.

For example, if SPY dropped by 2.3% in one day, then that day would qualify under the `-2.0%` threshold because the daily return is less than or equal to `-0.02`.

---

### Future Return

The project then calculates future returns for different holding periods:

```text
1 trading day
3 trading days
5 trading days
```

The idea is to ask:

**If I bought at the close of a big-drop day, what would my return be after 1, 3, or 5 trading days?**

Conceptually:

```text
Future return = future close / current close - 1
```

---

### Drop Thresholds

The project tests multiple definitions of a big drop:

```text
-1.0%
-1.5%
-2.0%
-2.5%
-3.0%
```

This matters because a 1% drop and a 3% drop are not the same type of event. A 1% drop happens more often, but it may not create a strong rebound. A 3% drop happens less often, but it may either create a stronger rebound or signal a more dangerous market environment.

Testing multiple thresholds lets the project answer a better question:

**Do larger drops lead to stronger rebounds, or do they just create more risk?**

---

## Metrics Calculated

For each ticker, threshold, and holding period, the project calculates:

```text
Number of big drop days
Average return
Benchmark average return
Edge vs benchmark
Win rate
Best return
Worst return
Average winning trade
Average losing trade
Risk-adjusted score
```

### Number of Big Drop Days

This is the number of times the ETF dropped by at least the selected threshold.

This matters because a setup with very few events may not be reliable. A setup with a small sample size could look strong mostly because of randomness.

---

### Average Return

This is the average return after a big-drop day for a given holding period.

For example:

```text
Average 5-day return after a -2.0% drop
```

This shows what happened after the specific condition being tested.

---

### Benchmark Average Return

This is the ETF’s normal average future return over the same holding period, using all days instead of only big-drop days.

This matters because an average return after a big drop does not mean much by itself. If SPY returns 0.78% after a big drop, I need to know whether that is actually better than SPY’s normal 5-day return.

---

### Edge vs Benchmark

This is the difference between the big-drop return and the normal benchmark return.

Conceptually:

```text
Edge = average return after big drop - benchmark average return
```

A positive edge means the big-drop setup performed better than normal. A negative edge means the setup performed worse than normal. An edge near zero means the setup was probably not very special.

This became one of the most important metrics in the project because it tells me whether the big-drop condition actually added value.

---

### Win Rate

This is the percentage of big-drop events where the future return was positive.

For example, a 60% win rate means that 60% of the time, the ETF was positive after the selected holding period.

Win rate matters because average return alone can be misleading. A setup could have a high average return because of a few huge winners, even if it loses often.

---

### Best and Worst Return

The best return shows the strongest future return after a big drop.

The worst return shows the largest loss after a big drop.

This matters because a setup can have a positive average return but still have large downside risk.

---

### Average Winning and Losing Trade

Average winning trade measures the average return among only positive-return events.

Average losing trade measures the average return among only negative-return events.

This matters because win rate by itself is not enough. A setup could win often but lose too much when it loses.

---

### Risk-Adjusted Score

After comparing setups by raw edge, I added a simple risk-adjusted score:

```text
Risk-adjusted score = edge vs benchmark / abs(average losing trade)
```

This is not meant to be a professional risk metric. It is a simple way to compare how much extra return a setup produced relative to the size of its average loss.

This helped because sorting only by edge favored some high-volatility setups. For example, XLE had some strong raw edges, but it also had large downside. The risk-adjusted score helped separate high-rebound setups from cleaner setups with more reasonable losses.

---

## Validation Steps Added

Version 1 includes several validation steps beyond the basic full-period analysis.

### 1. Full-Period Analysis

The first step tested all tickers, thresholds, and holding periods across the full 2010-2024 period.

This showed the strongest raw edges and helped identify the general pattern that 5-day holding periods after larger drops tended to produce the strongest rebound results.

---

### 2. Period-by-Period Testing

I split the data into:

```text
2010-2014
2015-2019
2020-2024
```

This tested whether the strongest setups were stable across different market environments.

The results showed that the best setups were not identical across periods. The 2015-2019 period looked strongest, while the 2020-2024 period looked weaker and more fragile.

---

### 3. Stability Comparison

After ranking setups within each period, I compared the top 10 setups from each period.

No setup appeared in the top 10 across all three periods.

Three setups appeared in the top 10 in two out of three periods:

```text
SPY | -2.0% threshold | 5-day hold
QQQ | -2.5% threshold | 5-day hold
XLF | -2.5% threshold | 5-day hold
```

This was an important result because it showed that the rebound effect existed historically, but the strongest setups were not perfectly stable across all regimes.

---

### 4. Transaction-Cost Sensitivity

I tested several transaction-cost assumptions:

```text
0.00%
0.10%
0.25%
0.50%
```

For each cost level, the project adjusted individual trade returns first and then recalculated the metrics.

This matters because transaction costs do not only reduce average return. They can also turn small winners into losers, reduce win rate, and change the average winning and losing trade.

The results showed that the number of surviving setups declined as costs increased. The 2020-2024 period was especially sensitive to transaction costs.

---

### 5. Selected Setup Drawdown Analysis

After the stability and transaction-cost analysis, I selected repeated setups for deeper path analysis:

```text
SPY | -2.0% threshold | 5-day hold
QQQ | -2.5% threshold | 5-day hold
XLF | -2.5% threshold | 5-day hold
```

For these setups, I calculated:

```text
Cumulative return
Running peak
Drawdown
Maximum drawdown
Final cumulative return
```

This helped move the analysis beyond summary statistics. A setup can have a positive average return but still have a painful or unrealistic return path.

The drawdown analysis showed that QQQ -2.5% 5D had the strongest selected setup path. SPY -2.0% 5D was also positive but had deeper drawdown. XLF -2.5% 5D looked much weaker after path and drawdown analysis.

---

### 6. Bootstrap Confidence Intervals

I added a bootstrap confidence interval test for the selected setups.

The goal was to check whether the average after-cost trade return looked statistically reliable or whether it could plausibly be random noise.

Conceptually:

```text
Repeatedly resample trade returns
Calculate the average return for each sample
Use the simulated averages to estimate a 95% confidence interval
```

The bootstrap results showed that QQQ -2.5% 5D was the strongest statistically among the selected setups. Its confidence interval stayed slightly positive, while SPY and XLF had intervals that crossed zero.

---

### 7. Out-of-Sample Validation

Finally, I added an out-of-sample test.

The setup was:

```text
Training period: 2010-2019
Test period: 2020-2024
```

The top 10 setups were selected using only the training period. Then those exact setups were tested on the later test period.

None of the top 10 training setups passed the out-of-sample rule in 2020-2024.

The passing rule required:

```text
Positive test-period edge
Test-period win rate of at least 55%
```

XLV -2.5% 5D had the best test-period edge, but its win rate was below the passing threshold.

This suggests that the rebound effect was historically present, but not stable enough to treat as a finished trading strategy.

---

## Files Created

The project creates several types of output files.

### Event-Level Files

These contain the actual big-drop dates for each ticker, threshold, and period, along with future return columns.

Example:

```text
SPY_2p0_big_drop_days2010-2014.csv
QQQ_2p5_big_drop_days2015-2019.csv
XLE_3p0_big_drop_days2020-2024.csv
```

These files are useful because they allow inspection of the actual events behind the summary statistics.

---

### Summary Files

These summarize the metrics for each ticker, threshold, and holding period.

Example:

```text
SPY_2p0_summary2010-2014.csv
QQQ_2p5_summary2015-2019.csv
```

---

### Combined Summary Files

These combine results across tickers and thresholds.

Example:

```text
combined_summary_2010-2014.csv
combined_summary_2015-2019.csv
combined_summary_2020-2024.csv
```

---

### Long-Format Summary Files

These are the most useful files for ranking and filtering.

Each row represents:

```text
One period
One ticker
One drop threshold
One holding period
```

This format makes it easier to sort, filter, rank, and compare setups directly.

---

### Ranked Setup Files

The ranked setup files apply rules such as:

```text
Minimum number of big-drop days
Edge vs benchmark > 0
Win rate >= 55%
Sort by risk-adjusted score
```

These files turn the project from raw data output into a system that can automatically identify the best-looking setups under defined rules.

---

### Transaction-Cost Files

These files show which setups survive under different transaction-cost assumptions.

Example:

```text
ranked_after_cost_sensitivity_2010-2014.csv
ranked_after_cost_sensitivity_2015-2019.csv
ranked_after_cost_sensitivity_2020-2024.csv
transaction_cost_survival_summary.csv
```

---

### Drawdown Files

These files analyze selected repeated setups over time.

Example:

```text
selected_setup_drawdowns.csv
selected_setup_drawdown_summary.csv
```

They include cumulative return, running peak, and drawdown for selected setups.

---

### Bootstrap Files

These files summarize the bootstrap confidence interval results for selected setups.

Example:

```text
selected_setup_bootstrap_summary.csv
```

---

### Stability Comparison Files

These files compare whether the same setups appeared repeatedly in top-ranked results across periods.

Example:

```text
stability_top10_comparison.csv
top10_by_period_combined.csv
```

---
