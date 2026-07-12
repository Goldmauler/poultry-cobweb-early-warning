"""Feature/panel builder stub.

STATUS
------
Proposal-stage stub. No working code implemented yet.

WHAT THIS WILL DO
-----------------
Join the per-series raw tables (broiler, chick, egg, feed) into a single
region-day panel, then engineer the modelling features and the forecast
target. All series are aligned on (region, date).

INPUTS
------
data/raw/broiler_rates_*.csv
data/raw/chick_rates_*.csv
data/raw/egg_rates_*.csv
data/raw/feed_prices_*.csv
Plus join sources: DAHD/WOAH avian-influenza dates, Open-Meteo weather,
a public festival/fasting calendar.

ENGINEERED COLUMNS (see README Section 7 for the full 20-attribute table)
-------------------------------------------------------------------------
chick_price_ma7, chick_price_yoy,
feed_cost_index, gross_margin (broiler - feed cost),
broiler_price_lag_1, broiler_price_lag_7, broiler_price_lag_42,
heat_stress_index, rainfall,
birdflu_flag (region, 30-day window),
festival_flag, day_of_week, month, season,
target = broiler_price at t+42

OUTPUT
------
data/processed/panel.parquet  -- one row per (region, date), model-ready
"""
