"""Forecasting and causality-test stub.

STATUS
------
Proposal-stage stub. No working code implemented yet.

WHAT THIS WILL DO
-----------------
Test whether the day-old-chick price carries predictive information about the
broiler price 42 days ahead, and forecast that price, always benchmarked
against a baseline that only sees broiler price history.

MODELS
------
baseline : ARIMA / SARIMA on broiler price alone. Structurally blind to
           placements -- it can only chase the cycle. The proposed model must
           beat this to matter.
proposed : SARIMAX with chick_price as an exogenous regressor;
           XGBoost / Ridge on the lag-feature panel.

CAUSALITY / LAG
---------------
- Granger causality: chick_price -> broiler_price at t+42 (H1).
- Cross-correlation of chick_price vs broiler_price; expect a peak near a
  40-45 day lag, recovering the biological grow-out cycle from price alone (H2).

VALIDATION
----------
Walk-forward (rolling-origin) cross-validation ONLY. Never random k-fold:
a random split leaks future observations into the training past and produces
a meaningless score on time-series data.

METRICS
-------
MAE, RMSE, MAPE, and skill score versus a seasonal-naive baseline.
Interpretability via SHAP.
"""
