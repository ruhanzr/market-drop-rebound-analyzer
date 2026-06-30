# Market Drop Rebound Analyzer

## Overview

Market Drop Rebound Analyzer is a Python research/backtesting project that tests whether major ETF selloffs are followed by short-term rebounds.

The main research question is:

**After an ETF drops by a certain percentage in one day, does it tend to rebound over the next 1, 3, or 5 trading days?**

The project should be viewed as a market research pipeline, not a finished trading strategy. The goal was to test a market idea, validate it across different conditions, and avoid overstating results.

## Project Versions

**Version 1: Rules-Based Rebound Analysis**

Tested ETF drop/rebound behavior across multiple tickers, drop thresholds, holding periods, and market regimes. The pipeline calculates average return, benchmark return, edge vs benchmark, win rate, best/worst return, average winning/losing trade, and a simple risk-adjusted score.

**Version 1.1: Expanded ETF Universe Test**

Expanded the ETF universe from 8 ETFs to 23 ETFs, adding more sectors, semiconductors, software, bonds, and commodities. The broader test found some stronger individual raw-edge setups, but the original core ETF universe remained stronger on average and on a risk-adjusted basis.

**Version 2: Machine Learning Rebound Prediction**

Converted the rules-based analysis into an event-level ML dataset and tested whether simple models could predict which big-drop events would rebound over the next 5 trading days. Logistic regression, decision tree, and random forest models did not meaningfully beat the majority-class baseline, and probability-threshold filtering did not reveal a strong hidden signal.

## Key Findings

- The strongest raw edges mostly appeared after 2% to 3% ETF drops with 5-day holding periods.
- Average edge was strongest around the -2.5% drop threshold.
- The best-looking ETFs by average edge included XLV, DIA, and XLK.
- Risk-adjusted ranking changed the interpretation because some high-edge setups also had large downside.
- Results were regime-dependent: 2015-2019 looked strongest, while 2020-2024 looked weaker and more fragile.
- No setup appeared in the top 10 across all three tested periods.
- The expanded ETF universe found more total passing setups, but did not fully solve the stability problem.
- The ML extension showed that the simple event-level features were not enough to create a strong out-of-sample predictive model.

## Final Conclusion

The drop-rebound effect was historically present, especially in equity-based ETFs and 5-day holding periods after larger selloffs. However, the effect was regime-dependent, weakened under stricter validation, and was difficult to convert into a stable predictive strategy.

The final result of this project is not a trading strategy. It is a research pipeline that tests a market hypothesis using rules-based analysis, robustness checks, out-of-sample validation, expanded-universe comparison, and simple ML baselines.

## Repository Structure

```text
src/
  main.py
  config.py
  analysis.py
  ranking.py
  transaction_costs.py
  drawdown.py
  bootstrap.py
  out_of_sample.py
  universe_comparison.py

ml/
  feature_engineering.py
  train_model.py
  model_interpretation.py
  probability_threshold_analysis.py
  ml_event_dataset.csv
  model_results.csv
  logistic_regression_coefficients.csv
  random_forest_feature_importance.csv
  probability_threshold_results.csv

docs/
  methodology.md
  results.md
  ml_extension.md

filtered_results/
  universe_comparison.csv
  category_comparison.csv

data/
  chart images
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the rules-based pipeline:

```bash
python src/main.py
```

Build the ML event dataset:

```bash
python ml/feature_engineering.py
```

Train baseline ML models:

```bash
python ml/train_model.py
```

Run ML interpretation and probability-threshold analysis:

```bash
python ml/model_interpretation.py
python ml/probability_threshold_analysis.py
```

## Full Documentation

More detailed explanations are in the `docs/` folder:

- [Methodology](docs/methodology.md): calculations, metrics, validation steps, and pipeline logic.
- [Results](docs/results.md): Version 1 and Version 1.1 findings, charts, expanded ETF universe comparison, and final rules-based conclusion.
- [ML Extension](docs/ml_extension.md): ML dataset, leakage rules, train/test split, baseline model results, feature interpretation, and ML conclusion.

## Development Note

I used OpenAI Codex as an AI coding assistant when adding the ML extension for implementation support, refactoring, and debugging. I directed the research question, project structure, validation approach, interpretation of results, and final conclusions.
