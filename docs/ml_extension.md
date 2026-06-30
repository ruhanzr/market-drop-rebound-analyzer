# Version 2: Machine Learning Rebound Prediction

This document explains the ML phase of the project, including the event-level dataset, train/test split, baseline models, feature interpretation, probability-threshold analysis, and final ML conclusion.

After completing the rules-based analysis and expanded ETF robustness test, I added a machine learning phase to test whether event-level features could better predict which big-drop events were likely to rebound.

The motivation for this phase came from the Version 1 and Version 1.1 results. The rules-based analysis found that rebound behavior after large ETF selloffs was historically present, especially around 5-day holding periods, but the effect was regime-dependent and did not fully survive out-of-sample validation. The expanded ETF universe test found some stronger individual setups, but it did not fully solve the stability problem.

For the ML phase, I converted the project into an event-level prediction problem. Each row in the ML dataset represents one ETF, one drop threshold, and one big-drop date.

The ML dataset was created in:

```text
ml/feature_engineering.py
```

The dataset output was:

```text
ml/ml_event_dataset.csv
```

The final dataset contained:

```text
28,255 event rows
23 ETFs
18 columns
No missing values
Date range: 2010-03-18 to 2024-12-19
```

The target variable for the first baseline model was:

```text
Target_Positive_5D = 1 if the ETF had a positive 5-day forward return after the drop, otherwise 0
```

I started with this target because the rules-based phase showed that the 5-day holding period had the strongest rebound behavior.

The model features only used information available on or before the drop day, including:

```text
Drop threshold
Daily return
Previous 5-day return
Previous 10-day return
Previous 20-day volatility
Volume change
Distance from 20-day moving average
Distance from 50-day moving average
Ticker
ETF category
Universe group
```

Future return columns were not used as model inputs because that would create data leakage. Columns such as `Forward_5D_Return`, `Benchmark_5D_Return`, `Edge_vs_Benchmark_5D`, and the target columns were treated as labels or result columns, not features.

The train/test split was time-based:

```text
Training period: 2010-2019
Test period: 2020-2024
```

I used a time-based split instead of a random split because market regimes matter. A random split would mix events from the same market environments across training and testing, which could make the model look more reliable than it actually is.

### ML Dataset Class Balance

For `Target_Positive_5D`, the dataset had:

```text
0: 11,928 rows | 42.22%
1: 16,327 rows | 57.78%
```

For `Target_Beat_Benchmark_5D`, the dataset had:

```text
0: 12,609 rows | 44.63%
1: 15,646 rows | 55.37%
```

This showed that rebounds were more common than non-rebounds, but the dataset was not extremely imbalanced.

Rows by period:

```text
2010-2014: 7,971
2015-2019: 7,489
2020-2024: 12,795
```

Rows by category:

```text
Sector: 11,132
Commodities: 5,725
Broad Index: 4,400
Semiconductors: 4,245
Software: 1,695
Bonds: 1,058
```

### Baseline ML Models

The baseline models were trained in:

```text
ml/train_model.py
```

The models tested were:

```text
Majority-class baseline
Logistic regression
Decision tree
Random forest
```

The majority-class baseline predicted the most common training class for every test event. This was included to check whether the ML models actually added predictive value beyond simply guessing the most common outcome.

The results were saved to:

```text
ml/model_results.csv
```

The baseline model results were:

```text
Majority-class baseline:
Accuracy: 55.66%
F1 score: 0.715
ROC AUC: 0.500

Logistic regression:
Accuracy: 55.13%
F1 score: 0.698
ROC AUC: 0.498

Decision tree:
Accuracy: 52.08%
F1 score: 0.591
ROC AUC: 0.508

Random forest:
Accuracy: 52.65%
F1 score: 0.639
ROC AUC: 0.493
```

Logistic regression had the strongest F1 score among the actual ML models, but it still did not beat the majority-class baseline. The decision tree had the highest ROC AUC, but its ROC AUC was only 0.508, which is very close to random guessing.

The important result is that the simple ML models did not find a strong out-of-sample predictive signal beyond the broad historical tendency for big-drop events to rebound.

### Feature Interpretation

After training the baseline models, I added a model interpretation layer to understand what the models were relying on.

The interpretation scripts and outputs were:

```text
ml/model_interpretation.py
ml/logistic_regression_coefficients.csv
ml/random_forest_feature_importance.csv
```

For logistic regression, the strongest coefficient by absolute value was `Distance_From_20D_MA`. This means the model leaned heavily on how far the ETF was from its 20-day moving average on the drop day. The coefficient was negative, which suggests that being more extended relative to the 20-day moving average was associated with a lower predicted probability of a positive 5-day rebound.

Other large logistic regression coefficients were tied to ETF identity or category, including tickers and groups such as USO, bonds, HYG, commodities, LQD, TLT, XLE, XLV, and XLP. This suggests that the model was also picking up cross-ETF and cross-category differences.

For random forest, the most important features were mostly numeric event-level features:

```text
Daily_Return
Previous_5D_Return
Previous_20D_Volatility
Distance_From_20D_MA
Distance_From_50D_MA
Previous_10D_Return
Volume_Change
```

This was useful because it showed that the random forest was not only memorizing ticker labels. However, since the model performance remained weak, these features were not strong enough to produce a reliable out-of-sample predictor.

### Probability-Threshold Analysis

I also tested whether the models became more useful when filtering for higher-confidence predictions.

The script was:

```text
ml/probability_threshold_analysis.py
```

The output was:

```text
ml/probability_threshold_results.csv
```

The idea was to ask:

**Even if the models do not beat the baseline overall, do the highest-confidence model predictions produce better rebound events?**

The answer was not strongly.

For logistic regression:

```text
Threshold 0.50:
Selected events: 11,867
Average 5D return: 0.326%
Average edge vs benchmark: 0.057%
Win rate: 55.82%

Threshold 0.70:
Selected events: 2,238
Average 5D return: 0.446%
Average edge vs benchmark: 0.165%
Win rate: 55.27%
```

The 0.70 threshold had a higher average return and edge, but the win rate did not improve. The result was also not smooth across thresholds because the 0.65 threshold had negative edge. Because of that, I would not call this a reliable high-confidence signal.

For random forest:

```text
Threshold 0.50:
Average edge vs benchmark: 0.048%
Win rate: 55.46%

Threshold 0.55:
Average edge vs benchmark: 0.090%
Win rate: 55.61%

Threshold 0.70:
Average edge vs benchmark: -0.055%
Win rate: 54.47%
```

Random forest also did not show a strong confidence pattern. The best threshold was around 0.55, but the improvement was small, and performance got worse at 0.70.

The probability-threshold analysis did not reveal a strong hidden ML signal. Higher model confidence did not consistently produce better events.

### Version 2 Conclusion

The ML extension converted the rules-based rebound analysis into an event-level prediction problem and tested whether simple features could identify which big-drop events were likely to rebound.

The models did not beat the majority-class baseline, ROC AUC stayed near random, and probability-threshold filtering did not reveal a reliable high-confidence signal. Feature interpretation showed that the models relied mainly on moving-average distance, recent returns, volatility, daily return, and volume change, but those features were not strong enough to produce stable out-of-sample predictive power.

This supports the broader project conclusion: ETF rebound behavior after major selloffs was historically present, but it was regime-dependent and difficult to convert into a stable predictive strategy using simple rules or baseline ML models.
