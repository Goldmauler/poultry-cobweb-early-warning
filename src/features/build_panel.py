"""Build the modelling panel: egg price + feed cost + engineered features.

Joins the daily NECC egg panel (data/processed/egg_panel.csv) with the monthly
FRED feed series (data/raw/feed_fred.csv), and engineers lag, moving-average,
feed-cost and calendar features plus the forecast target.

The chick->broiler leading-indicator study is motivated in the README but is
not modellable (chick/broiler prices are published only as images). This panel
therefore powers the executable core: forecasting the NECC egg price, which is
the one dense, structured Indian poultry price series and exhibits its own
feed-driven cyclical dynamics.

Inputs
------
data/processed/egg_panel.csv   (zone, date, egg_price, ...)
data/raw/feed_fred.csv         (date[m], maize_usd_mt, soy_usd_mt)

Output
------
data/processed/analysis_panel.csv   one row per (zone, date), model-ready

Usage
-----
python src/features/build_panel.py --horizon 30
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

EGG = os.path.join("data", "processed", "egg_panel.csv")
FEED = os.path.join("data", "raw", "feed_fred.csv")
OUT = os.path.join("data", "processed", "analysis_panel.csv")

# Feed-cost index weights (maize dominates poultry feed; soy meal is the protein).
W_MAIZE, W_SOY = 0.70, 0.30


def load_egg() -> pd.DataFrame:
    df = pd.read_csv(EGG, parse_dates=["date"])
    df = df[["zone", "date", "egg_price"]].dropna()
    df = df[(df["egg_price"] > 0) & (df["egg_price"] < 2000)]  # paise sanity bound
    return df.sort_values(["zone", "date"]).reset_index(drop=True)


def load_feed() -> pd.DataFrame:
    f = pd.read_csv(FEED, parse_dates=["date"])
    f = f[["date", "maize_usd_mt", "soy_usd_mt"]].dropna()
    # Normalise each series to its own long-run mean, then weight into an index.
    f["feed_cost_index"] = (
        W_MAIZE * f["maize_usd_mt"] / f["maize_usd_mt"].mean()
        + W_SOY * f["soy_usd_mt"] / f["soy_usd_mt"].mean()
    )
    f["ym"] = f["date"].dt.to_period("M")
    return f[["ym", "maize_usd_mt", "soy_usd_mt", "feed_cost_index"]]


def build(horizon: int) -> pd.DataFrame:
    egg = load_egg()
    feed = load_feed()

    # Monthly feed joined onto daily egg by year-month.
    egg["ym"] = egg["date"].dt.to_period("M")
    df = egg.merge(feed, on="ym", how="left").drop(columns="ym")

    # Per-zone time-series features (data sorted by zone,date).
    g = df.groupby("zone", group_keys=False)
    df["egg_ma7"] = g["egg_price"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["egg_ma30"] = g["egg_price"].transform(lambda s: s.rolling(30, min_periods=1).mean())
    df["egg_lag1"] = g["egg_price"].shift(1)
    df["egg_lag7"] = g["egg_price"].shift(7)
    df["egg_lag30"] = g["egg_price"].shift(30)
    df["egg_yoy"] = g["egg_price"].shift(365)
    df["egg_ret30"] = df["egg_price"] / df["egg_lag30"] - 1.0

    # Calendar / seasonality.
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["doy"] = df["date"].dt.dayofyear
    df["sin_doy"] = np.sin(2 * np.pi * df["doy"] / 365.25)
    df["cos_doy"] = np.cos(2 * np.pi * df["doy"] / 365.25)

    # Forecast target: egg price `horizon` days ahead, per zone.
    df["target"] = g["egg_price"].shift(-horizon)

    return df.sort_values(["zone", "date"]).reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build egg+feed modelling panel.")
    ap.add_argument("--horizon", type=int, default=30, help="forecast horizon in days")
    args = ap.parse_args()

    for path in (EGG, FEED):
        if not os.path.exists(path):
            print(f"missing input: {path} (run the scrapers first)", file=sys.stderr)
            return 1

    df = build(args.horizon)
    df.to_csv(OUT, index=False)
    modelled = df.dropna(subset=["target", "egg_lag30", "feed_cost_index"])
    print(f"panel rows        : {len(df):,}  (modelable: {len(modelled):,})")
    print(f"zones             : {df['zone'].nunique()}")
    print(f"date range        : {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"features          : {[c for c in df.columns if c not in ('zone','date','target')]}")
    print(f"feed coverage     : {df['feed_cost_index'].notna().mean():.1%} of rows")
    print(f"written           : {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
