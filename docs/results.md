# Results and Findings

This document contains the detailed rules-based and expanded-universe results for the project.

## Key Findings

The strongest raw edges mostly appeared in 5-day holding periods after 2% to 3% drops.

Average edge was strongest around the -2.5% drop threshold.

The best-looking ETFs by average edge included:

```text
XLV
DIA
XLK
```

However, risk-adjusted ranking changed the interpretation. Some high-edge setups also had large downside, especially in more volatile ETFs such as XLE.

The results were regime-dependent:

```text
2015-2019 looked strongest.
2020-2024 looked weaker and more fragile.
```

The stability comparison found no setup that appeared in the top 10 across all three periods.

The three most repeated setups were:

```text
SPY | -2.0% | 5-day
QQQ | -2.5% | 5-day
XLF | -2.5% | 5-day
```

After drawdown and bootstrap testing, QQQ -2.5% 5D was the strongest selected setup.

The out-of-sample test showed that the strongest training-period setups did not pass the validation rule in 2020-2024.

The final conclusion is that the drop-rebound effect was real historically, but it was regime-dependent and not stable enough to call a finished trading strategy.

---

## Results and Visualizations

The project includes chart images summarizing the main findings.

### Average Edge by Holding Period

![Average edge vs benchmark by holding period](data/avgEvB_HP.png)

The average edge vs benchmark was highest for the 5-day holding period. This supports one of the main findings of the project: the rebound effect was stronger over several trading days than immediately the next day.

---

### Average Edge by Drop Threshold

![Average edge vs benchmark by drop threshold](data/avgEvB_DT.png)

The average edge was strongest around the -2.5% threshold. This suggests that larger one-day drops generally created stronger rebound opportunities than smaller drops, but the relationship was not perfectly linear.

---

### Average Edge by ETF

![Average edge vs benchmark by ETF](data/avgEvB_ETF.png)

The ETFs with the strongest average edge were XLV, DIA, and XLK. This showed that the rebound effect was not equally strong across all ETFs.

---

### Top Setups by Risk-Adjusted Score

![Top setups by risk-adjusted score](data/setup_RAS.png)

The strongest individual setups by risk-adjusted score were mostly concentrated in earlier periods, especially 2010-2014 and 2015-2019.

---

### Average Top-10 Risk-Adjusted Score by Period

![Average top-10 risk-adjusted score by period](data/avgT10RAS_P.png)

The 2015-2019 period had the strongest average top-10 risk-adjusted score. The 2020-2024 period was much weaker, which supports the idea that the rebound effect depended heavily on market regime.

---

### Most Stable Ranked Setups

![Most stable ranked setups across time periods](data/stable_ranked.png)

No setup appeared in the top 10 across all three periods. The most stable setups appeared in two out of three periods.

---

### Transaction Cost Sensitivity

![Surviving setups by transaction cost and period](data/survivingSetups_C\&P.png)

The number of surviving setups declined as transaction costs increased. The 2020-2024 period was much more fragile than the earlier periods.

---

### Selected Setup Cumulative Return

![Cumulative return of selected stable setups](data/cumulativeReturnSSS.png)

QQQ -2.5% 5D had the strongest cumulative return path among the selected repeated setups.

---

### Selected Setup Drawdown

![Drawdown of selected stable setups](data/drawdownSSS.png)

The drawdown chart showed that QQQ had the strongest selected path, SPY had positive performance with deeper drawdown, and XLF had the weakest path.

---

### Bootstrap Confidence Intervals

![Bootstrap confidence interval by setup](data/bootstrapConfidence_S.png)

QQQ -2.5% 5D was the only selected setup whose bootstrap confidence interval stayed above zero.

---

## Current Conclusion

Version 1 found historical rebound behavior after large ETF selloffs, especially over 5-day holding periods and around the -2.5% threshold.

However, the stricter validation steps changed the interpretation.

The strongest raw setups were not always the best after accounting for downside risk. The best setups changed across market periods. Transaction costs weakened the results. Drawdown analysis showed that some repeated setups had poor return paths. Bootstrap confidence intervals showed that only QQQ -2.5% 5D was statistically stronger among the selected setups. The out-of-sample test showed that the best training-period setups did not pass the validation rule in 2020-2024.

The final conclusion is:

**The drop-rebound effect was historically present, but it was regime-dependent and not stable enough to treat as a finished trading strategy.**

This makes Version 1 a completed rules-based research/backtesting project, while still leaving room for future extensions.

---

## Version 1.1: Expanded ETF Universe Test

After completing the original Version 1 analysis, I added a broader ETF robustness test to see whether the rebound effect became stronger or more stable when tested across a larger universe.

The original core universe contained 8 ETFs:

```text
SPY, QQQ, IWM, DIA, XLK, XLF, XLE, XLV
```

The expanded universe added 15 more ETFs across sectors, semiconductors, software, bonds, and commodities:

```text
XLI, XLY, XLP, XLU, XLB, XLRE, SMH, SOXX, IGV, TLT, HYG, LQD, GLD, SLV, USO
```

The goal of this extension was not just to add more tickers, but to test whether the same drop-rebound framework found stronger or more stable setups outside the original ETF group.

The expanded additions produced more total passing setups because there were more ETFs tested, but the original core universe remained stronger on average.

```text
Core universe:
Average edge vs benchmark: 0.33%
Average win rate: 58.63%
Best setup: QQQ | -2.5% threshold | 5-day hold
Best risk-adjusted score: 1.525

Expanded additions:
Average edge vs benchmark: 0.23%
Average win rate: 56.56%
Best setup: XLY | -2.5% threshold | 5-day hold
Best risk-adjusted score: 1.013
```

The broader test found some strong individual raw-edge setups, especially XLY -2.5% 5D, but the original core ETFs still performed better on average and on a risk-adjusted basis.

When grouped by ETF category, broad index and sector ETFs had the strongest overall results. Broad index ETFs had an average edge of 0.34% and an average win rate of 59.12%, while sector ETFs had an average edge of 0.32% and an average win rate of 57.65%.

Software also showed strong average results, but that category only included one ETF, IGV, so the result should not be overinterpreted. Commodities were weak overall, and bonds produced relatively few passing setups.

This extension supports the original conclusion: the drop-rebound effect was historically present, especially in equity-based ETFs, but expanding the universe did not fully solve the stability problem.

## Limitations

This project has several limitations.

The analysis only uses historical ETF data. It does not include macroeconomic variables, volatility indexes, market breadth, interest rates, or news.

The strategy rules are simple and based only on one-day drop thresholds.

The transaction-cost model is basic and does not include slippage, liquidity constraints, bid-ask spread changes, or position sizing.

The bootstrap test helps estimate uncertainty, but it does not prove that a setup will continue working in the future.

The out-of-sample test showed that the strongest training-period setups did not pass the validation rule in 2020-2024.

Because of these limitations, this project should not be viewed as a complete trading system. It is a market research pipeline that tests whether a historical rebound effect exists and how stable that effect is under stricter validation.

---
