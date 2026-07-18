"""Generate the figure set for the case study.

Reads the model-ready panel and the walk-forward outputs, and writes every
figure used in the README to reports/figures/.

Usage
-----
python src/features/build_panel.py --horizon 30
python src/models/forecast.py --horizon 30 --folds 5
python src/viz/make_figures.py
"""

from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")

# Run as `python src/viz/make_figures.py` from the repo root; make `src.` importable.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator

PANEL = os.path.join("data", "processed", "analysis_panel.csv")
PREDS = os.path.join("data", "processed", "predictions.csv")
METRICS = os.path.join("reports", "metrics.json")
FIGDIR = os.path.join("reports", "figures")

# Categorical slots in fixed order (validated: worst all-pairs CVD dE 13.0,
# normal-vision dE 19.6 on a light surface). Never cycled, never rank-ordered.
C_BLUE, C_GREEN, C_MAGENTA, C_YELLOW = "#2a78d6", "#008300", "#e87ba4", "#eda100"
C_ORANGE, C_VIOLET, C_RED = "#eb6834", "#4a3aa7", "#e34948"

# Colour follows the entity, not its rank.
MODEL_COLOR = {
    "naive_persist": "#8a8a85",
    "naive_seasonal": "#c2c2bb",
    "ridge": C_BLUE,
    "xgboost": C_GREEN,
}
MODEL_LABEL = {
    "naive_persist": "Naive (persistence)",
    "naive_seasonal": "Naive (seasonal)",
    "ridge": "Ridge",
    "xgboost": "XGBoost",
}

SURFACE, INK, INK_2, INK_MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a85"
GRID = "#e6e5e0"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2,
    "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.titlecolor": INK, "axes.titleweight": "600",
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
    "axes.axisbelow": True, "legend.frameon": False,
    "figure.dpi": 130, "savefig.bbox": "tight",
})


def _style(ax, title=None, sub=None, xlabel=None, ylabel=None):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    if title:
        # Offset in points, not axes fractions -- a tall figure would otherwise
        # push the subtitle into the title.
        ax.set_title(title, loc="left", fontsize=12.5, pad=28 if sub else 8)
    if sub:
        ax.annotate(sub, xy=(0, 1), xycoords="axes fraction",
                    textcoords="offset points", xytext=(0, 8),
                    fontsize=9.5, color=INK_2, va="bottom", ha="left")
    ax.set_xlabel(xlabel or "", fontsize=9.5)
    ax.set_ylabel(ylabel or "", fontsize=9.5)
    return ax


def _save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


def _sequential(vals, lo=0.18, hi=0.95):
    """Single-hue light->dark ramp (blue). Never a rainbow."""
    v = np.asarray(vals, dtype=float)
    rng = np.nanmax(v) - np.nanmin(v)
    t = np.zeros_like(v) if rng == 0 else (v - np.nanmin(v)) / rng
    return plt.cm.Blues(lo + t * (hi - lo))


# ------------------------------------------------------------------ figures

def fig_price_and_feed(df):
    """Two stacked panels sharing an x-axis -- never a dual y-axis."""
    nat = df.groupby("date")[["egg_price", "feed_cost_index"]].mean()
    nat = nat.rolling(30, min_periods=1).mean()

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.4), sharex=True,
                                 gridspec_kw={"height_ratios": [1.5, 1]})
    a1.plot(nat.index, nat["egg_price"], color=C_BLUE, lw=2)
    _style(a1, "Indian egg price and feed cost, 2009-2026",
           "National mean NECC egg rate (30-day moving average), 37 zones",
           ylabel="Egg price (paise/egg)")
    a2.plot(nat.index, nat["feed_cost_index"], color=C_ORANGE, lw=2)
    _style(a2, None, None, ylabel="Feed cost index")
    fig.align_ylabels([a1, a2])
    fig.text(0.9, 0.02, "Feed cost index = 0.70 x maize + 0.30 x soymeal, mean-normalised",
             ha="right", fontsize=8.5, color=INK_MUTED)
    _save(fig, "fig01_price_and_feed.png")


def fig_seasonality(df):
    """Deviation from each year's own mean -- the raw level is dominated by the
    long-run uptrend, which hides the seasonal cycle entirely."""
    from matplotlib.colors import LinearSegmentedColormap

    nat = df.groupby("date")["egg_price"].mean().reset_index()
    nat["year"], nat["month"] = nat["date"].dt.year, nat["date"].dt.month
    nat["dev"] = nat.groupby("year")["egg_price"].transform(
        lambda s: (s / s.mean() - 1) * 100)
    piv = nat.pivot_table(index="year", columns="month", values="dev", aggfunc="mean")

    # Diverging: two hues with a neutral gray midpoint. Never a rainbow.
    cmap = LinearSegmentedColormap.from_list(
        "dev", [C_BLUE, "#dcdbd5", C_ORANGE])
    lim = float(np.nanmax(np.abs(piv.values)))

    fig, ax = plt.subplots(figsize=(11, 5.8))
    im = ax.imshow(piv.values, cmap=cmap, aspect="auto", vmin=-lim, vmax=lim)
    ax.set_xticks(range(12), ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.grid(False)
    _style(ax, "Prices peak in Nov-Dec and trough in Mar-Apr, almost every year",
           "Deviation from each year's own mean -- de-trended, so the seasonal "
           "cycle a forecast must beat is visible")
    cb = fig.colorbar(im, ax=ax, pad=0.015)
    cb.set_label("Deviation from annual mean (%)", fontsize=9.5, color=INK_2)
    cb.outline.set_visible(False)
    _save(fig, "fig02_seasonality_heatmap.png")


def fig_month_profile(df):
    nat = df.groupby("date")["egg_price"].mean().reset_index()
    nat["month"] = nat["date"].dt.month
    g = nat.groupby("month")["egg_price"]
    med, q1, q3 = g.median(), g.quantile(0.25), g.quantile(0.75)
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(range(1, 13), q1, q3, color=C_BLUE, alpha=0.16, lw=0)
    ax.plot(range(1, 13), med, color=C_BLUE, lw=2, marker="o", ms=8,
            mec=SURFACE, mew=2)
    for m in (int(med.idxmax()), int(med.idxmin())):
        ax.annotate(f"{med[m]:.0f}", (m, med[m]), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=9.5, color=INK)
    ax.set_xticks(range(1, 13), names)
    _style(ax, "Within-year price profile",
           "Median across 2009-2026 with the interquartile band",
           ylabel="Egg price (paise/egg)")
    _save(fig, "fig03_month_profile.png")


def fig_zone_levels(df):
    """Zone premium relative to the national mean *on the same day*.

    A raw per-zone mean would be wrong here: 8 of the 37 zones only start
    reporting after 2015 (and 3 stop early), so a plain average would rank
    them high purely because their window sits in the high-price years.
    Differencing against the same-day national mean compares like with like.
    """
    d = df[["zone", "date", "egg_price"]].dropna().copy()
    d["national"] = d.groupby("date")["egg_price"].transform("mean")
    d["premium"] = d["egg_price"] - d["national"]
    z = d.groupby("zone")["premium"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    colors = [C_ORANGE if v >= 0 else C_BLUE for v in z.values]
    ax.barh(z.index, z.values, color=colors, height=0.74)
    ax.axvline(0, color=INK_MUTED, lw=1)
    pad = max(abs(z.min()), abs(z.max())) * 0.03
    for zone, v in z.items():
        ax.text(v + (pad if v >= 0 else -pad), zone, f"{v:+.0f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=INK_2)
    ax.set_xlim(z.min() * 1.35, z.max() * 1.35)
    ax.xaxis.grid(True); ax.yaxis.grid(False)
    _style(ax, "Egg prices differ persistently by zone",
           "Mean gap to the national rate on the same day (coverage-robust) -- "
           "justifies modelling zones jointly with zone features",
           xlabel="Premium vs national mean (paise/egg)")
    _save(fig, "fig04_zone_levels.png")


def fig_volatility(df):
    nat = df.groupby("date")["egg_price"].mean()
    ret = (nat / nat.shift(30) - 1) * 100
    ret = ret.dropna()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.fill_between(ret.index, 0, ret.values, where=ret.values >= 0,
                    color=C_GREEN, alpha=0.55, lw=0, label="30-day rise")
    ax.fill_between(ret.index, 0, ret.values, where=ret.values < 0,
                    color=C_RED, alpha=0.55, lw=0, label="30-day fall")
    ax.axhline(0, color=INK_MUTED, lw=1)
    ax.axhline(-15, color=INK_2, lw=1, ls="--")
    ax.annotate("crash threshold (-15%)", (ret.index[10], -15),
                textcoords="offset points", xytext=(4, 5), fontsize=9,
                color=INK_2, va="bottom")
    ax.legend(loc="upper left", ncol=2, fontsize=9.5)
    _style(ax, "The boom-bust cycle is visible in the price itself",
           "30-day percentage change in the national mean egg rate",
           ylabel="30-day change (%)")
    _save(fig, "fig05_volatility_cycle.png")


def fig_drawdowns(df):
    nat = df.groupby("date")["egg_price"].mean()
    ret = ((nat / nat.shift(30) - 1) * 100).dropna()
    crash = float((ret <= -15).mean() * 100)

    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins, patches = ax.hist(ret, bins=60, color=C_BLUE, alpha=0.9)
    for b, p in zip(bins[:-1], patches):
        if b <= -15:
            p.set_facecolor(C_RED)
    ax.axvline(-15, color=INK_2, lw=1.2, ls="--")
    ax.annotate(f"{crash:.1f}% of days sit in a\n30-day drawdown of 15% or worse",
                xy=(-15, ax.get_ylim()[1] * 0.72), xytext=(-46, ax.get_ylim()[1] * 0.82),
                fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK_2, lw=1))
    ax.yaxis.grid(True); ax.xaxis.grid(False)
    _style(ax, "How often does the market actually crash?",
           "Distribution of 30-day price changes, national mean, 2009-2026",
           xlabel="30-day change (%)", ylabel="Number of days")
    _save(fig, "fig06_drawdown_distribution.png")


def fig_model_bars(summary):
    order = ["naive_persist", "naive_seasonal", "ridge", "xgboost"]
    s = summary.set_index("model").loc[order]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = np.arange(len(order))
    bars = ax.bar(x, s["MAE"], width=0.6,
                  color=[MODEL_COLOR[m] for m in order])
    for b, (m, r) in zip(bars, s.iterrows()):
        ax.text(b.get_x() + b.get_width() / 2, r["MAE"] + 0.7, f"{r['MAE']:.1f}",
                ha="center", fontsize=11, color=INK, fontweight="600")
    best = s.drop(index=["naive_persist", "naive_seasonal"])["MAE"].idxmin()
    ax.axhline(s.loc["naive_persist", "MAE"], color=INK_MUTED, lw=1.2, ls="--")
    ax.text(len(order) - 0.45, s.loc["naive_persist", "MAE"] - 2.2,
            "baseline a farmer already has, free", ha="right", fontsize=9, color=INK_2)
    ax.set_xticks(x, [MODEL_LABEL[m] for m in order])
    ax.yaxis.grid(True); ax.xaxis.grid(False)
    skill = s.loc[best, "skill_vs_persist"] * 100
    _style(ax, f"Only {MODEL_LABEL[best]} beats the free baseline -- and only by {skill:.1f}%",
           "Mean absolute error across 5 rolling-origin folds; lower is better",
           ylabel="MAE (paise/egg)")
    _save(fig, "fig07_model_comparison.png")


def fig_fold_lines(per_fold):
    p = pd.DataFrame(per_fold)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for m in ["naive_persist", "naive_seasonal", "ridge", "xgboost"]:
        d = p[p["model"] == m].sort_values("fold")
        ax.plot(d["fold"], d["MAE"], color=MODEL_COLOR[m], lw=2, marker="o",
                ms=8, mec=SURFACE, mew=2, label=MODEL_LABEL[m])
    # No direct end-labels here: Ridge and persistence converge in the last fold,
    # so the labels would collide. The legend below carries identity instead.
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim(0.85, len(p["fold"].unique()) + 0.15)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4, fontsize=9.5)
    _style(ax, "Model ranking is not stable across time",
           "MAE per rolling-origin fold -- each fold trains only on earlier dates",
           xlabel="Walk-forward fold (later fold = later test window)",
           ylabel="MAE (paise/egg)")
    _save(fig, "fig08_fold_stability.png")


def fig_actual_vs_pred(preds, best):
    last = preds[preds["fold"] == preds["fold"].max()]
    zone = last["zone"].value_counts().idxmax()
    d = last[last["zone"] == zone].sort_values("date")

    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(d["date"], d["actual"], color=INK_2, lw=2, label="Actual")
    ax.plot(d["date"], d[best], color=C_GREEN, lw=2, label=f"{MODEL_LABEL[best]} forecast")
    ax.legend(loc="upper left", ncol=2, fontsize=9.5)
    _style(ax, f"Forecast vs actual, {zone} -- final walk-forward fold",
           "30 days ahead; the model never saw any date in this window during training",
           ylabel="Egg price (paise/egg)")
    _save(fig, "fig09_actual_vs_predicted.png")


def fig_residuals(preds, best):
    err = preds[best] - preds["actual"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8))

    a1.hist(err, bins=70, color=C_BLUE, alpha=0.9)
    a1.axvline(0, color=INK_2, lw=1.2, ls="--")
    a1.set_xlim(np.percentile(err, 0.2), np.percentile(err, 99.8))
    a1.yaxis.grid(True); a1.xaxis.grid(False)
    # State the bias in the title rather than claiming the error is centred.
    bias = err.mean()
    side = "under" if bias < 0 else "over"
    _style(a1, f"The model {side}-predicts by {abs(bias):.0f} paise on average",
           "Errors are wide and left-skewed, not a tight unbiased band",
           xlabel="Predicted - actual (paise/egg)", ylabel="Count")

    m = preds.groupby(preds["date"].dt.to_period("M").dt.to_timestamp()).apply(
        lambda g: float(np.mean(np.abs(g[best] - g["actual"]))))
    a2.plot(m.index, m.values, color=C_VIOLET, lw=2)
    _style(a2, "Error is not uniform over time",
           "Monthly MAE across all held-out folds", ylabel="MAE (paise/egg)")
    fig.tight_layout(w_pad=3)
    _save(fig, "fig10_residuals.png")


def fig_causality(causality):
    g = causality["granger_feed_to_egg"]["p_by_lag"]
    x = causality["crosscorr_feed_leads_egg"]["by_lag_months"]
    lags, pv = [int(k) for k in g], list(g.values())

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8))
    cols = [C_GREEN if p < 0.05 else C_BLUE for p in pv]
    a1.bar(lags, pv, color=cols, width=0.62)
    a1.axhline(0.05, color=C_RED, lw=1.4, ls="--")
    a1.set_ylim(0, max(pv) * 1.18)
    a1.annotate("p = 0.05", (max(lags) + 0.45, 0.05), textcoords="offset points",
                xytext=(0, 5), ha="right", va="bottom", fontsize=9, color=C_RED)
    a1.xaxis.set_major_locator(MaxNLocator(integer=True))
    a1.yaxis.grid(True); a1.xaxis.grid(False)
    _style(a1, "H1': feed cost does NOT Granger-cause egg price",
           f"No lag clears p<0.05 (best: lag {causality['granger_feed_to_egg']['best_lag_months']}"
           f" months, p={causality['granger_feed_to_egg']['best_p']:.3f})",
           xlabel="Lag (months)", ylabel="Granger p-value")

    xl, xv = [int(k) for k in x], list(x.values())
    peak = causality["crosscorr_feed_leads_egg"]["peak_lag_months"]
    a2.bar(xl, xv, color=[C_ORANGE if l == peak else C_BLUE for l in xl], width=0.62)
    a2.axhline(0, color=INK_MUTED, lw=1)
    peak_r = xv[xl.index(peak)]
    a2.set_ylim(min(xv) * 1.15, max(xv) * 1.35)
    a2.annotate(f"peak r={peak_r:.2f} at {peak} months", (peak, peak_r),
                textcoords="offset points", xytext=(12, 14), fontsize=9.5,
                color=INK, arrowprops=dict(arrowstyle="->", color=INK_2, lw=1))
    a2.yaxis.grid(True); a2.xaxis.grid(False)
    _style(a2, "H2': weak positive lead from feed cost",
           "Cross-correlation of differenced feed cost against egg price",
           xlabel="Feed cost leads by (months)", ylabel="Correlation")
    fig.tight_layout(w_pad=3)
    _save(fig, "fig11_causality.png")


def fig_importance(df):
    from xgboost import XGBRegressor
    from src.models.forecast import FEATURES

    d = df.dropna(subset=["target"] + FEATURES)
    cut = d["date"].quantile(0.5)
    tr = d[d["date"] < cut]
    m = XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                     subsample=0.8, colsample_bytree=0.8, n_jobs=4,
                     random_state=0, tree_method="hist")
    m.fit(tr[FEATURES].values, tr["target"].values)

    imp = pd.Series(m.feature_importances_, index=FEATURES).sort_values()
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    ax.barh(imp.index, imp.values, color=_sequential(imp.values), height=0.72)
    for k, v in imp.items():
        ax.text(v + imp.max() * 0.012, k, f"{v:.3f}", va="center",
                fontsize=8.5, color=INK_2)
    ax.set_xlim(0, imp.max() * 1.14)
    ax.xaxis.grid(True); ax.yaxis.grid(False)
    feed_share = imp[["feed_cost_index", "maize_usd_mt", "soy_usd_mt"]].sum()
    _style(ax, "What the model actually leans on",
           f"XGBoost gain importance -- yesterday's price and the calendar lead; "
           f"the three feed features together carry {feed_share:.0%}",
           xlabel="Relative importance")
    _save(fig, "fig12_feature_importance.png")


def fig_zone_year(df):
    d = df.copy()
    d["year"] = d["date"].dt.year
    piv = d.pivot_table(index="zone", columns="year", values="egg_price", aggfunc="mean")
    piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(11.5, 9))
    im = ax.imshow(piv.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(piv.index)), piv.index, fontsize=8.5)
    ax.grid(False)
    _style(ax, "Every zone rose together -- the shock is national, not local",
           "Mean egg price by zone and year. White = the zone did not report that "
           "year; 8 zones start only after 2015")
    cb = fig.colorbar(im, ax=ax, pad=0.012)
    cb.set_label("Egg price (paise/egg)", fontsize=9.5, color=INK_2)
    cb.outline.set_visible(False)
    _save(fig, "fig13_zone_year_heatmap.png")


def fig_coverage(df):
    d = df.copy()
    d["ym"] = d["date"].dt.to_period("M").dt.to_timestamp()
    cnt = d.groupby("ym")["zone"].nunique()

    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.fill_between(cnt.index, 0, cnt.values, color=C_BLUE, alpha=0.28, lw=0)
    ax.plot(cnt.index, cnt.values, color=C_BLUE, lw=2)
    ax.set_ylim(0, cnt.max() * 1.15)
    _style(ax, "Data coverage is dense and continuous",
           f"Zones reporting per month -- {len(df):,} zone-day records, "
           f"{df['date'].min():%b %Y} to {df['date'].max():%b %Y}",
           ylabel="Zones reporting")
    _save(fig, "fig14_data_coverage.png")


# ------------------------------------------------------------------ main

def main() -> int:
    for p in (PANEL, PREDS, METRICS):
        if not os.path.exists(p):
            print(f"missing {p}; run build_panel.py then forecast.py first",
                  file=sys.stderr)
            return 1

    os.makedirs(FIGDIR, exist_ok=True)
    df = pd.read_csv(PANEL, parse_dates=["date"])
    preds = pd.read_csv(PREDS, parse_dates=["date"])
    with open(METRICS) as fh:
        met = json.load(fh)
    summary = pd.DataFrame(met["summary"])
    best = met["best_model"]

    print(f"panel {len(df):,} rows | preds {len(preds):,} rows | best={best}\n")
    fig_price_and_feed(df)
    fig_seasonality(df)
    fig_month_profile(df)
    fig_zone_levels(df)
    fig_volatility(df)
    fig_drawdowns(df)
    fig_model_bars(summary)
    fig_fold_lines(met["per_fold"])
    fig_actual_vs_pred(preds, best)
    fig_residuals(preds, best)
    fig_causality(met["causality"])
    fig_importance(df)
    fig_zone_year(df)
    fig_coverage(df)
    print(f"\ndone: {len(os.listdir(FIGDIR))} figures in {FIGDIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
