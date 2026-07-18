"""Forecast the NECC egg price `horizon` days ahead, with honest validation.

WHAT THIS RUNS ON
-----------------
The executable core of the project: the egg + feed panel built by
`src/features/build_panel.py`. The chick -> broiler leading-indicator study
(H1/H2 in the README) is motivated there but cannot be run at submission,
because the chick and broiler rate pages were never densely archived. This
module therefore tests the same *structure* of hypothesis on the series that
does have dense history:

    H1' : feed cost Granger-causes the egg price.
    H2' : the cross-correlation of feed cost against egg price peaks at a
          positive lag -- i.e. feed cost moves first.

That is the same claim shape as the chick->broiler test (an upstream input
price leading a downstream output price), run on data that actually exists.

MODELS
------
naive_persist  : predict price[t+h] = price[t].  The number a farmer already
                 has for free. Any model that cannot beat this is worthless.
naive_seasonal : predict price[t+h] = price[t+h-365].  Last year, same day.
ridge          : linear model on the lag/MA/feed/calendar feature panel.
xgboost        : gradient-boosted trees on the same panel.

VALIDATION
----------
Walk-forward (rolling-origin) only. Each fold trains strictly on dates before
its test window, so no future observation ever reaches the training past.
Random k-fold is never used: it leaks the future and produces a meaningless
score on time-series data.

Usage
-----
python src/models/forecast.py --horizon 30 --folds 5
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PANEL = os.path.join("data", "processed", "analysis_panel.csv")
OUT_DIR = os.path.join("reports")
OUT_METRICS = os.path.join(OUT_DIR, "metrics.json")
OUT_PREDS = os.path.join("data", "processed", "predictions.csv")

FEATURES = [
    "egg_ma7", "egg_ma30", "egg_lag1", "egg_lag7", "egg_lag30",
    "egg_yoy", "egg_ret30", "maize_usd_mt", "soy_usd_mt", "feed_cost_index",
    "day_of_week", "month", "sin_doy", "cos_doy",
]


# ---------------------------------------------------------------- metrics

def mae(y, p):
    return float(np.mean(np.abs(y - p)))


def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))


def mape(y, p):
    m = y != 0
    return float(np.mean(np.abs((y[m] - p[m]) / y[m])) * 100)


def score(y, p) -> dict:
    return {"MAE": mae(y, p), "RMSE": rmse(y, p), "MAPE": mape(y, p)}


# ---------------------------------------------------------------- data

def load_panel(horizon: int) -> pd.DataFrame:
    df = pd.read_csv(PANEL, parse_dates=["date"])
    need = ["target", "egg_price"] + FEATURES
    df = df.dropna(subset=need).sort_values("date").reset_index(drop=True)
    # `naive_seasonal` needs egg_yoy, already required above.
    return df


def walk_forward_splits(dates: pd.Series, folds: int):
    """Rolling-origin splits: fold k trains on everything before its test block."""
    uniq = np.sort(dates.unique())
    # Hold out the last 50% of the timeline, cut into `folds` equal test blocks.
    start = len(uniq) // 2
    edges = np.linspace(start, len(uniq), folds + 1).astype(int)
    for k in range(folds):
        tr_end, te_end = uniq[edges[k]], uniq[edges[k + 1] - 1]
        yield k, (dates < tr_end), (dates >= tr_end) & (dates <= te_end)


# ---------------------------------------------------------------- models

def fit_predict(name, Xtr, ytr, Xte):
    if name == "ridge":
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        m = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    elif name == "xgboost":
        from xgboost import XGBRegressor
        m = XGBRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, n_jobs=4,
            random_state=0, tree_method="hist",
        )
    else:
        raise ValueError(name)
    m.fit(Xtr, ytr)
    return m, m.predict(Xte)


# ---------------------------------------------------------------- causality

def causality_tests(df: pd.DataFrame, maxlag: int = 12) -> dict:
    """H1'/H2' on a national monthly mean series (feed is monthly)."""
    from statsmodels.tsa.stattools import adfuller, grangercausalitytests

    s = (df.set_index("date")
           .groupby(pd.Grouper(freq="ME"))[["egg_price", "feed_cost_index"]]
           .mean().dropna())
    # Granger requires stationarity -> difference both series.
    d = s.diff().dropna()

    out = {"n_months": int(len(d))}
    for col in ("egg_price", "feed_cost_index"):
        out[f"adf_p_{col}_diff"] = float(adfuller(d[col])[1])

    # Does feed cost Granger-cause egg price? Column order: [effect, cause].
    # The test prints a full report per lag; silence it and keep the p-values.
    with contextlib.redirect_stdout(io.StringIO()):
        g = grangercausalitytests(d[["egg_price", "feed_cost_index"]], maxlag=maxlag)
    pvals = {int(lag): float(r[0]["ssr_ftest"][1]) for lag, r in g.items()}
    best = min(pvals, key=pvals.get)
    out["granger_feed_to_egg"] = {
        "p_by_lag": pvals, "best_lag_months": int(best), "best_p": pvals[best],
        "significant_5pct": bool(pvals[best] < 0.05),
    }

    # H2': cross-correlation, feed leading egg.
    a = (d["feed_cost_index"] - d["feed_cost_index"].mean()).values
    b = (d["egg_price"] - d["egg_price"].mean()).values
    ccf = {}
    for lag in range(0, 25):
        if lag >= len(a):
            break
        x, y = a[: len(a) - lag], b[lag:]
        denom = np.sqrt((x**2).sum() * (y**2).sum())
        ccf[int(lag)] = float((x * y).sum() / denom) if denom else 0.0
    peak = max(ccf, key=lambda k: abs(ccf[k]))
    out["crosscorr_feed_leads_egg"] = {
        "by_lag_months": ccf, "peak_lag_months": int(peak), "peak_r": ccf[peak],
    }
    return out


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Forecast egg price h days ahead.")
    ap.add_argument("--horizon", type=int, default=30)
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()

    if not os.path.exists(PANEL):
        print(f"missing {PANEL}; run src/features/build_panel.py first", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_panel(args.horizon)
    print(f"panel: {len(df):,} rows | {df['zone'].nunique()} zones | "
          f"{df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"walk-forward: {args.folds} rolling-origin folds, horizon={args.horizon}d\n")

    rows, preds = [], []
    for k, tr, te in walk_forward_splits(df["date"], args.folds):
        Xtr, ytr = df.loc[tr, FEATURES].values, df.loc[tr, "target"].values
        Xte, yte = df.loc[te, FEATURES].values, df.loc[te, "target"].values
        if len(Xtr) < 1000 or len(Xte) == 0:
            continue

        fold_pred = {
            "naive_persist": df.loc[te, "egg_price"].values,
            "naive_seasonal": df.loc[te, "egg_yoy"].values,
        }
        for name in ("ridge", "xgboost"):
            _, p = fit_predict(name, Xtr, ytr, Xte)
            fold_pred[name] = p

        span = f"{df.loc[te,'date'].min().date()}..{df.loc[te,'date'].max().date()}"
        print(f"fold {k+1}  train={len(Xtr):>7,}  test={len(Xte):>6,}  {span}")
        for name, p in fold_pred.items():
            s = score(yte, p)
            s.update(fold=k + 1, model=name, n_test=len(yte), test_span=span)
            rows.append(s)
            print(f"    {name:<15} MAE={s['MAE']:7.2f}  RMSE={s['RMSE']:7.2f}  "
                  f"MAPE={s['MAPE']:5.2f}%")

        preds.append(pd.DataFrame({
            "fold": k + 1,
            "zone": df.loc[te, "zone"].values,
            "date": df.loc[te, "date"].values,
            "actual": yte,
            **fold_pred,
        }))
        print()

    per_fold = pd.DataFrame(rows)
    summary = per_fold.groupby("model")[["MAE", "RMSE", "MAPE"]].mean()

    # Skill score vs the free baseline a farmer already has.
    base = summary.loc["naive_persist", "MAE"]
    summary["skill_vs_persist"] = 1 - summary["MAE"] / base

    print("=" * 62)
    print(f"MEAN ACROSS {per_fold['fold'].nunique()} WALK-FORWARD FOLDS")
    print("=" * 62)
    print(summary.round(3).to_string())

    best = summary.drop(index=["naive_persist", "naive_seasonal"])["MAE"].idxmin()
    print(f"\nbest model: {best}  "
          f"({summary.loc[best,'skill_vs_persist']:.1%} MAE reduction vs persistence)")

    print("\nCausality (H1'/H2' on monthly national means)")
    print("-" * 62)
    c = causality_tests(df)
    g, x = c["granger_feed_to_egg"], c["crosscorr_feed_leads_egg"]
    print(f"  Granger feed -> egg : best lag {g['best_lag_months']} months, "
          f"p={g['best_p']:.4g} "
          f"({'SIGNIFICANT' if g['significant_5pct'] else 'not significant'} at 5%)")
    print(f"  Cross-correlation   : peak at lag {x['peak_lag_months']} months, "
          f"r={x['peak_r']:.3f}")

    pd.concat(preds).to_csv(OUT_PREDS, index=False)
    with open(OUT_METRICS, "w") as fh:
        json.dump({
            "horizon_days": args.horizon,
            "folds": int(per_fold["fold"].nunique()),
            "per_fold": rows,
            "summary": summary.reset_index().to_dict("records"),
            "best_model": best,
            "causality": c,
        }, fh, indent=2)
    print(f"\nwritten: {OUT_METRICS}\nwritten: {OUT_PREDS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
