# Breaking the Poultry Cobweb: Forecasting Broiler Price Crashes in India Using Day-Old-Chick Prices as a Leading Indicator

A Business Analytics case study that reconstructs an unobservable national supply statistic from an observable market price, forecasts broiler farm-gate price crashes 42 days ahead, and turns that forecast into a **"place / do not place this week"** chick-placement decision for the farmer.

*Design target vs. what runs today: see the [scope note](#summary) in Section 4 and the [executable core](#10-reproducing-the-analysis) in Section 10.*

## Table of contents

1. [Student Information](#1-student-information)
2. [Business Domain](#2-business-domain)
3. [Case Study Title](#3-case-study-title)
4. [Business Problem Statement](#4-business-problem-statement)
5. [The Research Gap](#5-the-research-gap)
6. [Business Objectives](#6-business-objectives)
7. [Planned Dataset Size](#7-planned-dataset-size)
8. [Proposed Data Collection Method](#8-proposed-data-collection-method)
9. [Modelling Approach](#9-modelling-approach)
10. [Reproducing the Analysis](#10-reproducing-the-analysis)
11. [Exploratory Data Analysis](#11-exploratory-data-analysis)
12. [Results](#12-results)
13. [Expected Business Impact](#13-expected-business-impact)
14. [Limitations and Threats to Validity](#14-limitations-and-threats-to-validity)
15. [Sources](#15-sources)

---

## 1. Student Information

| Field | Value |
|---|---|
| Student Name | _____________________ |
| Register Number | CB.SC.U4CSE23___ |
| Class / Section | _____________________ |
| Course | Business Analytics |
| Programme | B.Tech CSE (3rd year), Amrita Vishwa Vidyapeetham |

---

## 2. Business Domain

Agriculture and agri-commodity markets — specifically the poultry supply chain and price-risk analytics. The unit of interest is the regional broiler market, where farm-gate live-bird prices are set daily and are subject to recurrent boom-and-bust cycles.

---

## 3. Case Study Title

**Breaking the Poultry Cobweb: Forecasting Broiler Price Crashes in India Using Day-Old-Chick Prices as a Leading Indicator.**

---

## 4. Business Problem Statement

### Summary

Indian broiler farmers and contract growers operate with thin margins and face a recurring **cobweb cycle** driven by the fixed 40–45-day biological production lag. When farm-gate prices are high, producers increase day-old chick placements; six weeks later these birds reach the market simultaneously, creating a supply glut that crashes prices below the cost of production. With feed costs now significantly elevated due to maize diversion to ethanol, these periodic crashes have become **severe financial shocks rather than manageable downturns**. Placement decisions are currently driven by today's visible spot price — which actively misleads farmers into buying chicks just before a glut — rather than any forward-looking supply signal.

This study develops a data-driven **early-warning model that recommends optimal chick placement decisions** by forecasting regional broiler farm-gate prices 42 days ahead. It uses publicly observable day-old chick prices (as a leading proxy for placement volume), feed costs, seasonality, weather, and other factors to generate actionable **"place / do not place this week"** signals tailored to a producer's budget, risk tolerance, and regional market conditions.

> **Scope note.** The paragraph above states the study's full design target. The chick → broiler forecasting layer and the producer-tailored recommendation layer both depend on the forward-collected chick and broiler series (Section 8.0), and are **not yet implemented**. What runs today is the executable core described in [Section 10](#10-reproducing-the-analysis), which validates the same modelling machinery on the one series with dense history. This boundary is stated wherever a claim is made.

### (a) What is the business problem?

The problem is the **cobweb cycle** in broiler production. The mechanism is self-reinforcing:

1. Broiler price is high, so farmers place more day-old chicks.
2. 40–45 days later, those birds all reach market weight at roughly the same time.
3. Simultaneous supply produces a **glut**, and price crashes below the cost of production.
4. Loss-making farmers exit or skip a cycle, so placements fall.
5. 40–45 days later there is a **shortage**, and price spikes.
6. The high price pulls farmers back in, and the cycle repeats.

This is not a new observation. It is the textbook **Cobweb Theorem**, formally described by Mordecai Ezekiel in *The Cobweb Theorem* (1938). What is notable is that the cycle remains unresolved in Indian broiler markets in 2026 — the coordination failure that Ezekiel modelled almost a century ago still plays out on Indian rate sheets every quarter.

### (b) Why is it important to solve?

The cycle has always existed, but the **margin buffer that used to absorb a crash has been removed by the current feed crisis.** Feed is roughly 70% of broiler variable cost, and maize is 65–70% of feed. India's ethanol programme has diverted maize away from feed on a large scale: maize used for ethanol rose from 315 million litres of output equivalent (ESY 2022–23) to **2.86 billion litres (ESY 2023–24), about 42% of all ethanol**, and India became a **net maize importer in 2024** as exports collapsed from 1.9 million to about 0.5 million tonnes ([Down To Earth](https://www.downtoearth.org.in/agriculture/lost-in-maize)). Poultry and cattle feed, which consume 60–70% of India's maize, were the worst hit. Crisil Ratings has projected poultry profitability could **decline by up to 50% in the 2025/26 marketing year** ([Nutrinews `[link rot — verify]`](https://nutrinews.com/en/indias-poultry-sector-faces-feed-crisis-amid-gm-import-debate/)).

When feed cost is high and margins are already thin, a price crash is no longer a bad quarter — it is an insolvency event. The economic-cost derivation in this section quantifies the exposure.

### (c) Who will benefit?

- **Broiler farmers and contract growers** — the party that bears the placement decision and, for independents, the price risk.
- **Integrators** — Suguna, Venky's, Sneha, CP — who plan placements and bear grower price risk under contract.
- **Feed mills** — whose demand is a direct function of bird numbers in production.
- **Lenders and rating agencies** — who underwrite the sector and currently lack a forward supply signal (see Section 5).
- **Policymakers** — who manage feed, trade, and farmer-distress interventions.

### (d) How can data analytics contribute?

The core insight is biological, not statistical:

> A day-old chick placed today *is* a market-ready bird in 40–45 days. That is biology, not a modelling assumption. **The supply that will crash the market in six weeks has already been ordered.** The crash is therefore knowable in advance — if, and only if, someone is recording chick placements.

Analytics contributes by supplying the missing observation. If placement volume were recorded, the future glut would be visible directly. It is not recorded in India — but the **price** of day-old chicks is published daily, and price is the market-clearing signal of placement demand. The project turns that published price into the forward supply signal that does not otherwise exist.

### Economic Cost — derived, not fabricated

The figures below are a transparent, assumption-labelled derivation. Each unit input is sourced in [Section 15](#15-sources). No aggregate loss figure is attributed to a source that does not state one.

**Unit economics (sourced):**

- Day-old chick: **₹20–25** ([The Global Statistics](https://www.theglobalstatistics.com/chicks-rate-today/))
- Cost to raise a bird to market weight: **₹80–90/bird**; rearing **40–45 days** to **2–2.5 kg** ([The Global Statistics](https://www.theglobalstatistics.com/chicks-rate-today/))
- India produces **~1.5 billion broilers/year**; **~65–70 million placements/week** ([PoultryApp](https://www.poultryapp.com/broiler-rates-in-india/))
- Feed is **~70% of variable cost**; maize 65–70% and soymeal 25–30% of feed ([ICRA, March 2025](https://www.icra.in/Rating/DownloadResearchSummaryReport?id=6224))
- Documented crash magnitude: broiler prices fell **18–19% month-on-month in West/South India in Feb 2025** ([ICRA, March 2025](https://www.icra.in/Rating/DownloadResearchSummaryReport?id=6224))
- Documented loss precedent (2013–14 feed crisis): production cost hit **₹68/kg** against a farm-gate price of **₹57–58/kg** — a **₹10/kg loss** — and **20–30% of farmers suspended or closed operations** ([Food & Agribusiness](https://www.foodagribusiness.world/poultry/feed-price-hikes-cause-unrest-in-indian-poultry-sector))

**Farm-level worked example:**

```
A 7,000-bird shed in a crash window:
  Cost of production      Rs 88/bird   (mid-point of Rs 80-90)
  Farm-gate in a glut     Rs 75/bird   (2 kg x Rs 37.5/kg after an ~18% crash)
  Loss per bird           Rs 13
  Loss per cycle          Rs 13 x 7,000 = Rs 91,000
```

**Sector-level order-of-magnitude estimate:**

```
ESTIMATE - derived, not published. Assumptions stated.
  Annual production                    1.5 billion birds
  Share sold in crash windows          assume 20%  -> 300 million birds
  Loss per bird in a crash             Rs 10-20    (from the Rs 10/kg precedent x ~2 kg)
  Implied annual value destruction     Rs 300-600 crore  (~USD 36-72 million)
```

*The 20% share is an assumption, not a measurement. The true figure depends on crash frequency and duration — which this project is designed to quantify for the first time. The estimate is presented so a reader can audit and replace each assumption, not as a published statistic.*

---

## 5. The Research Gap

This is the intellectual core of the proposal, and it is stated honestly.

### Claim 1 — The insight is NOT novel. In the US it is institutionalised.

The United States has treated placements as a leading indicator for decades. The **USDA publishes a weekly Broiler Hatchery report** covering eggs set and chicks placed; a single recent week records **255.839 million eggs set and 197.497 million chicks placed** at 79.4% hatchability ([Brownfield Ag News `[403 to automated access — verify in browser]`](https://www.brownfieldagnews.com/news/broiler-placements-stay-2-ahead-of-the-2025-pace/)), and the figure is reported routinely — **199 million chicks placed** in the week ending 20 June 2026 ([US Foods](https://www.usfoods.com/tools-tips-and-ideas/articles-and-publications/farmer-s-report/chicken)). USDA's Economic Research Service explicitly adjusts its broiler production forecasts **"reflecting hatchery and placements data"** ([USDA ERS](https://www.ers.usda.gov/topics/animal-products/poultry-eggs/market-outlook)). The placement-to-price link is not a research hypothesis in the US; it is official methodology.

### Claim 2 — India has no equivalent, and that is the gap.

There is **no Indian broiler hatchery report** — no official weekly or regional placement statistic. The clearest evidence of the vacuum is who reads what: **ICRA, a credit rating agency, cites `Poultrybazaar` — a daily rate website — as its data source** in published poultry sector research ([ICRA, March 2025](https://www.icra.in/Rating/DownloadResearchSummaryReport?id=6224)). India's professional analysts read the same public webpage a farmer reads, because the public good the USDA has provided since the 1930s does not exist here.

### Claim 3 — The contribution is the *instrument*, not the insight.

> Placements are unobservable in India because nobody reports them. But the **day-old-chick price is observable** — and DOC price is the market-clearing price *of placement demand*.
> **This project reconstructs an unobservable national statistic from an observable market price.**

**Testable hypothesis:**

> **H1:** `chick_price[t]` Granger-causes `broiler_price[t+42]`, and adds predictive power **beyond** what broiler price history alone provides.

**Free secondary finding:**

> **H2:** The cross-correlation between DOC price and broiler price should peak at a lag of ~40–45 days — independently recovering the biological grow-out cycle of a chicken from price data alone.

---

## 6. Business Objectives

1. Build the **first public daily panel** of Indian broiler, day-old-chick, egg, and feed prices by region.
2. Test whether **DOC price Granger-causes broiler price at t+42**.
3. Estimate the lag empirically via **cross-correlation** and check it against the 40–45 day biological cycle.
4. **Forecast** regional broiler farm-gate price 42 days ahead.
5. Benchmark against an **autoregressive baseline** (broiler price from its own history) — the model only matters if it beats this.
6. Produce a **"placement glut warning"**: a regional signal advising against chick placement when a crash is forecast.
7. Convert that forecast into an actionable **"place / do not place this week"** recommendation, tailored to the producer's **budget, risk tolerance, and regional market** — so the output is a decision, not just a number. *(Design-stage: depends on objectives 2–4 above.)*

---

## 7. Planned Dataset Size

The **10,000-record minimum is met by the historical backbone alone**: NECC egg rates across ~37 zones × daily × 2009–2026 yield well over 200,000 zone-day records (verified retrievable), joined with feed prices. The broiler-target panel below (~20 regions × daily) is assembled **forward** from the start of collection for the leading-indicator test; the attribute schema is the design target for that panel. **20 attributes** per record:

| # | Attribute | Type | Source |
|---|---|---|---|
| 1 | region | categorical | Poultry Bazaar / Chicken Rate Today |
| 2 | date | date | scrape date |
| 3 | broiler_price (farm-gate) | numeric | Poultry Bazaar daily rate sheet |
| 4 | chick_price (day-old-chick) | numeric | Poultry Bazaar chick rates |
| 5 | chick_price_ma7 (7-day MA) | numeric | derived |
| 6 | chick_price_yoy (YoY change) | numeric | derived |
| 7 | egg_price (NECC) | numeric | NECC via Poultry Bazaar |
| 8 | maize_price | numeric | Agmarknet |
| 9 | soybean_meal_price | numeric | Agmarknet |
| 10 | feed_cost_index | numeric | derived (maize + soymeal) |
| 11 | gross_margin (broiler − feed cost) | numeric | derived |
| 12 | broiler_price_lag_1 (t−1) | numeric | derived |
| 13 | broiler_price_lag_7 (t−7) | numeric | derived |
| 14 | broiler_price_lag_42 (t−42) | numeric | derived |
| 15 | heat_stress_index | numeric | Open-Meteo |
| 16 | rainfall | numeric | Open-Meteo |
| 17 | birdflu_flag (region, 30-day window) | binary | DAHD / WOAH |
| 18 | festival_or_fasting_flag | binary | public festival calendar |
| 19 | day_of_week | categorical | derived |
| 20 | month / season | categorical | derived |
| — | **target: broiler_price at t+42** | numeric | derived from column 3 |

**Weather** (attributes 15–16) supports the seasonality and heat-stress effects named in the Section 4 summary. **Producer budget and risk tolerance are not dataset attributes** — they are user-supplied parameters consumed by the recommendation layer (Objective 7), which converts the forecast into a place / do-not-place call at the producer's own risk threshold. They are collected per user at decision time, not scraped.

---

## 8. Proposed Data Collection Method

Web scraping only — no surveys. The method is a **hybrid of dense historical backfill (for series that were preserved) and forward daily collection (for series that were not)**. This design is the result of a feasibility check run before any scraper was built — see the honest note below.

### 8.0 Feasibility finding (why the plan is hybrid, not pure backfill)

An earlier version of this plan proposed reconstructing the full daily history of the broiler and day-old-chick rate pages from the **Internet Archive Wayback Machine**. A coverage check (reproducible via [`scripts/wayback_feasibility.py`](scripts/wayback_feasibility.py)) showed this is not viable: the archive holds only ~33 captured days for the chick-rate page and ~20 for the broiler-rate page across 2019–2026 — roughly 60× too sparse for a daily panel. These committee-set rates are published fresh and overwritten daily, and were never preserved. **That vacuum is the project's own thesis, confirmed empirically.** The plan therefore backfills history only where a source genuinely retains it, and collects the rest forward from today.

### 8.1 Historical backbone (dense, real, retrievable today)

- **NECC egg rates — [e2necc.com](https://e2necc.com/home/eggprice) (verified).** A month/year POST form serves daily egg rates by zone back to **2009**. Verified working: one month returns ~1,100+ tidy rows across ~37 zones. Implemented in [`src/scrapers/egg_rates.py`](src/scrapers/egg_rates.py). This is the panel's dense historical spine.
- **Feed prices — Agmarknet report generator** ([link](https://agmarknet.gov.in)) for multi-year daily maize and soybean-meal mandi prices, used to build the feed-cost index. (Agmarknet is a stateful portal; where deep history is impractical, feed cost is supplemented forward via the data.gov.in daily mandi-price API and monthly reference series.)

### 8.2 Forward daily collection (the series with no retrievable history)

Collected daily from today via cron / GitHub Actions, because no dense archive exists:

- Poultry Bazaar — broiler and day-old-chick rates by region ([rates](https://www.poultrybazaar.net/daily-rate-sheet/), [chick rates](https://www.poultrybazaar.net/daily-rate-sheet/chick-rates/))
- `chickenratetoday.in` — live/retail broiler rates by city ([link](https://chickenratetoday.in/))

The sparse Wayback captures that *do* exist are retained as scattered historical validation anchors, not as a primary series.

### 8.3 Joins

- **DAHD / WOAH** — avian-influenza outbreak dates by district
- **Open-Meteo** — heat-stress and rainfall
- **Public festival / fasting calendar** — demand-side seasonality

### 8.4 Consequence for the analysis

The historical backbone (egg + feed) supports a **fully validated forecasting model with walk-forward validation on real multi-year data**. The novel **day-old-chick → broiler 42-day leading-indicator test (H1/H2)** runs on the **forward-collected** chick and broiler series and is therefore reported as *accruing evidence*: the biological 42-day lag is anchored in literature and in cross-correlation as data accumulates, rather than claimed as fully validated at submission. This split is stated plainly rather than hidden.

**Ethics:** public pages only, no login; `robots.txt` respected; rate-limited crawling; raw HTML archived for reproducibility; no personal data collected.

---

## 9. Modelling Approach

**Baseline (must be beaten):** ARIMA / SARIMA on broiler price alone. This baseline is **structurally blind**: it can only chase the cycle, because the cause of the cycle — placements — is not present in its input data. It extrapolates the pattern; it cannot see the supply that has already been ordered.

**Proposed:** SARIMAX with DOC price as an **exogenous regressor**; XGBoost / Ridge on the lag-feature panel.

**Causality test:** Granger causality, DOC price → broiler price at t+42 (H1).

**Lag recovery:** cross-correlation of DOC price against broiler price; the peak is expected near 40–45 days (H2).

**Validation:** **walk-forward (rolling-origin) cross-validation only. Never random k-fold** — a random split leaks future observations into the training past on time-series data and produces a meaningless R².

**Metrics:** MAE, RMSE, MAPE, and a **skill score versus a seasonal-naive baseline**.

**Interpretability:** SHAP, to confirm the chick-price features (not just autoregressive lags) carry the model's forward information.

---

## 10. Reproducing the Analysis

Everything below this line is generated by the code in this repository. No figure or number is hand-entered.

```bash
pip install -r requirements.txt

python scripts/backfill_egg.py                        # scrape NECC egg rates, 2009-2026
python src/features/build_panel.py --horizon 30       # -> data/processed/analysis_panel.csv
python src/models/forecast.py --horizon 30 --folds 5  # -> reports/metrics.json
python src/viz/make_figures.py                        # -> reports/figures/*.png
```

**What the executable core actually is.** The chick -> broiler leading-indicator study (H1/H2) is the proposal's novel contribution, but it *cannot be run at submission* — the chick and broiler rate pages were never densely archived, so those series only begin accruing from the start of forward collection (Section 8.0). Rather than present an untestable model, the executable core runs the **same shape of hypothesis** on the one series with dense history:

| Proposed (Section 5) | Executable now |
|---|---|
| H1: chick price Granger-causes broiler price at t+42 | **H1'**: feed cost Granger-causes egg price |
| H2: cross-correlation peaks at the 40-45 day grow-out lag | **H2'**: cross-correlation shows feed cost leading egg price |

Both are the claim "an upstream input price leads a downstream output price," and H1'/H2' run on 195,519 real zone-day records instead of on a promise.

**Panel actually built:** 195,519 zone-day records | 37 zones | 2009-01-01 to 2026-07-12 | 16 features | 99.3% feed coverage. This clears the 10,000-record requirement of Section 7 by a factor of ~19.

---

## 11. Exploratory Data Analysis

**The series itself, and the cost shock behind it.** Plotted as two stacked panels rather than one dual-axis chart — a second y-scale would let the two lines be slid into any apparent relationship.

![Egg price and feed cost, 2009-2026](reports/figures/fig01_price_and_feed.png)

**Data coverage** — dense and continuous, which is what makes the historical backbone usable at all.

![Data coverage](reports/figures/fig14_data_coverage.png)

**Seasonality.** The raw price level is dominated by the long-run uptrend, which hides the seasonal cycle completely; de-trending against each year's own mean exposes it. Prices peak in Nov-Dec (+15 to +17%) and trough in Mar-Apr (-13 to -17%), in almost every one of the 18 years.

![Seasonality heatmap](reports/figures/fig02_seasonality_heatmap.png)

![Within-year price profile](reports/figures/fig03_month_profile.png)

**This seasonality is why the baseline is hard to beat.** A model that merely rediscovers "December is expensive" adds nothing a farmer does not already know.

**Regional structure.** Reported as each zone's mean gap to the national rate *on the same day*, not as a raw per-zone average — 8 of the 37 zones only begin reporting after 2015, so a plain mean would rank them high purely for having a recent, high-price window. The corrected view shows consumption centres (Kolkata belt, Mumbai, Pune) at a premium and production belts (Ludhiana, Barwala, Hospet) at a discount, which is the economically sensible direction.

![Zone premium vs national mean](reports/figures/fig04_zone_levels.png)

![Zone by year heatmap](reports/figures/fig13_zone_year_heatmap.png)

**The boom-bust cycle, quantified.** This is the phenomenon the whole proposal is about, measured rather than asserted: **11.4% of all days sit in a 30-day drawdown of 15% or worse.**

![Volatility cycle](reports/figures/fig05_volatility_cycle.png)

![Drawdown distribution](reports/figures/fig06_drawdown_distribution.png)

---

## 12. Results

All results are walk-forward (rolling-origin), 5 folds, 30-day horizon. Every fold trains strictly on dates before its test window.

### 12.1 Forecasting — the model wins, but narrowly

| Model | MAE | RMSE | MAPE | Skill vs persistence |
|---|---|---|---|---|
| Naive (persistence) | 50.75 | 63.46 | 11.10% | — |
| Naive (seasonal) | 63.26 | 76.19 | 13.47% | **-24.7%** |
| Ridge | 49.76 | 60.44 | 10.52% | +1.9% |
| **XGBoost** | **47.53** | **58.66** | **10.03%** | **+6.3%** |

![Model comparison](reports/figures/fig07_model_comparison.png)

**Read this honestly.** XGBoost beats the free baseline by 6.3% MAE — a real but modest gain, not a breakthrough. The seasonal naive baseline is *worse than doing nothing*, which tells us the year-on-year pattern alone is not reliable. And the ranking is **not stable across folds**: XGBoost is the best model in folds 1 and 5 and the worst non-seasonal model in fold 2.

![Fold stability](reports/figures/fig08_fold_stability.png)

![Actual vs predicted](reports/figures/fig09_actual_vs_predicted.png)

The forecast tracks turning points but **systematically under-predicts the peaks** — visible as a -20 paise mean bias. For a crash-warning tool this is the *safer* direction of error, but it is a bias, not noise.

![Residuals](reports/figures/fig10_residuals.png)

### 12.2 Causality — H1' is NOT supported

![Causality tests](reports/figures/fig11_causality.png)

**H1' fails.** No lag from 1 to 12 months clears p < 0.05; the best is lag 7 at **p = 0.099**. On this data, feed cost does *not* Granger-cause the egg price at conventional significance.

**H2' is weak.** Cross-correlation peaks at 7 months with **r = 0.22** — the right sign, and consistent with feed cost leading rather than following, but far too weak to call the lag recovered.

This is a **negative result, reported as one.** It does not refute the chick -> broiler hypothesis, which is a different and much tighter mechanism: a chick placed today *is* a market bird in 42 days (biology), whereas feed cost reaches the egg price through diffuse, substitutable, and partly hedged cost pass-through. If anything, the weakness of the feed -> egg link is an argument for why the *placement* signal is worth collecting: it is causal by construction in a way that an input-cost correlation is not.

### 12.3 What the model leans on

![Feature importance](reports/figures/fig12_feature_importance.png)

Yesterday's price and the calendar month dominate. The three feed features together carry about 22% of gain — non-trivial, but consistent with the weak Granger result: feed carries some information, just not enough to establish causality.

### 12.4 Honest summary

- The pipeline runs end-to-end on 195,519 real records and is fully reproducible.
- The best model beats the free baseline, but by 6.3% — useful, not transformative.
- **H1' is not supported at p < 0.05.** The headline causal claim of the executable core does not hold on this data.
- The novel chick -> broiler test (H1/H2) remains untested pending forward data collection, exactly as Section 8.4 anticipated.

---

## 13. Expected Business Impact

The decisive point is that the **forecast horizon matches the decision horizon exactly.** A broiler farmer makes essentially one recurring decision — *should I place chicks this week?* — and that decision commits him for 42 days. Every existing rate service tells him **today's** price, which is precisely the number that misleads him: today's high price is the trap that triggers the next glut. A 42-day-ahead forecast speaks to the decision the farmer is actually making, at the moment he is making it.

| Stakeholder | Concrete benefit |
|---|---|
| Broiler farmer / contract grower | A "place / do not place this week" signal tied to the 42-day commitment, instead of a today-only rate that encourages placing into a coming glut. |
| Integrator (Suguna, Venky's, Sneha, CP) | Regional placement planning against a forward price, smoothing throughput and reducing grower-loss exposure under contract. |
| Feed mill | Forward view of bird numbers in production — an early read on feed demand for procurement and inventory. |
| Lender / rating agency | A leading sector-stress indicator to replace reliance on the same daily rate webpage analysts currently read. |
| Policymaker | An early-warning basis for feed, trade, and farmer-distress interventions before a crash matures. |

---

## 14. Limitations and Threats to Validity

This section is deliberately blunt. It leads with the weakness in the project's own instrument.

> **Does DOC price actually proxy placement volume?**
> A high chick price may indicate strong farmer demand for chicks (the assumption behind this project) — **or constrained hatchery supply, which implies the opposite for future output.** Demand-driven and supply-driven price rises have *opposite* predictions for the market in six weeks, and they cannot be separated from price alone.
> **Mitigations:** cross-check DOC price against hatchery listing volumes on IndiaMART / TradeIndia; examine whether DOC and broiler prices co-move (consistent with demand-driven placement) or diverge (consistent with a supply constraint); and report the proxy's weakness explicitly rather than burying it.

Additional threats:

- **No historical chick/broiler series (the binding data constraint).** The rate pages were never densely archived (feasibility-tested: ~20–33 Wayback days total), so the day-old-chick and broiler series exist only forward from the start of collection. The novel H1/H2 test therefore rests on a short and growing window at submission, not on years of history. This is the single largest limitation and is stated as such, not buried.
- **Administered prices.** Regional Broiler Coordination Committee rates are negotiated, not purely market-clearing, so the "price" is partly an administered number. This may attenuate or distort the price-signal relationship in some regions.
- **Contract farming.** Under integration, the integrator — not the grower — bears the price risk. The model therefore matters most for the roughly one-third of production run by independent farmers ([PoultryApp](https://www.poultryapp.com/broiler-rates-in-india/)); its private value to contract growers is smaller.
- **Structural breaks.** Bird-flu outbreaks and ethanol/trade policy shifts can break the historical price relationship, so a model fit on the past may misfire across a regime change. These are flagged as features where possible and acknowledged as residual risk where not.

---

## 15. Sources

All links were checked for resolution. Confirmed-dead links are marked `[link rot — verify]`; links that block automated fetching but are expected to load in a browser are marked `[403 to automated access — verify in browser]`. No source was substituted for one that could not be read.

**Foundational theory**

- Ezekiel, M. (1938). "The Cobweb Theorem." *Quarterly Journal of Economics*, 52(2), 255–280. *(Cited bibliographically; no stable open-access URL asserted.)*

**The Indian feed crisis (why the margin buffer is gone)**

- Down To Earth — "Lost in maize." https://www.downtoearth.org.in/agriculture/lost-in-maize
- Nutrinews — "India's poultry sector faces feed crisis amid GM import debate." `[link rot — verify]` https://nutrinews.com/en/indias-poultry-sector-faces-feed-crisis-amid-gm-import-debate/
- ChiniMandi — interview with Poultry India President Uday Singh Bias. https://www.chinimandi.com/rising-ethanol-demand-drives-maize-prices-impacting-poultry-feed-costs-poultry-india-president-uday-singh-bias/
- Poultry India — "Poultry Feed Crisis." `[link rot — verify]` https://www.poultryindia.co.in/poultry-feed-crisis-why-four-neighboring-countries-could-pos/
- Food & Agribusiness — "Feed price hikes cause unrest in Indian poultry sector" (2013–14 precedent). https://www.foodagribusiness.world/poultry/feed-price-hikes-cause-unrest-in-indian-poultry-sector

**The price crash, and the evidence of the data vacuum**

- ICRA — Indian Poultry Industry, March 2025. https://www.icra.in/Rating/DownloadResearchSummaryReport?id=6224

**Unit economics**

- The Global Statistics — Chicks Rate Today. https://www.theglobalstatistics.com/chicks-rate-today/
- PoultryApp — Broiler rates in India. https://www.poultryapp.com/broiler-rates-in-india/

**The US comparison — proof the method works and that India lacks the instrument**

- USDA Economic Research Service — Poultry & Eggs Market Outlook. https://www.ers.usda.gov/topics/animal-products/poultry-eggs/market-outlook
- Brownfield Ag News — "Broiler placements stay 2% ahead of the 2025 pace." `[403 to automated access — verify in browser]` https://www.brownfieldagnews.com/news/broiler-placements-stay-2-ahead-of-the-2025-pace/
- US Foods — Farmer's Report (Chicken). https://www.usfoods.com/tools-tips-and-ideas/articles-and-publications/farmer-s-report/chicken

**Biological grow-out cycle (justifies the 42-day lag)**

- *Poultry Science* (2025) — broiler performance under commercial conditions (4,842 commercial flocks; 42-day slaughter reference age). `[403 to automated access — verify in browser]` https://www.sciencedirect.com/science/article/pii/S0032579125009691

**Data sources (verified during the feasibility phase)**

- NECC egg rates — e2necc daily rate sheet by zone, historical to 2009 (verified working; the panel's historical backbone). https://e2necc.com/home/eggprice
- data.gov.in — daily mandi commodity price API (maize, soybean; current-snapshot, used for forward feed collection). https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
- Agmarknet — maize and soybean-meal mandi prices (multi-year history via report generator). https://agmarknet.gov.in
- Poultry Bazaar — daily rate sheet (broiler; forward collection). https://www.poultrybazaar.net/daily-rate-sheet/
- Poultry Bazaar — chick rates (the key leading-indicator variable; forward collection). https://www.poultrybazaar.net/daily-rate-sheet/chick-rates/
- Chicken Rate Today. https://chickenratetoday.in/
- Internet Archive Wayback CDX API (coverage tested: too sparse for backfill; retained only as scattered validation anchors). http://web.archive.org/cdx/search/cdx

---

## What in this repository runs

| Component | Status |
|---|---|
| [`src/scrapers/egg_rates.py`](src/scrapers/egg_rates.py) + [`scripts/backfill_egg.py`](scripts/backfill_egg.py) | **Working** — 212 months scraped, 2009-2026 |
| [`src/features/build_panel.py`](src/features/build_panel.py) | **Working** — builds the 195,519-row modelling panel |
| [`src/models/forecast.py`](src/models/forecast.py) | **Working** — walk-forward validation, 4 models, Granger + cross-correlation |
| [`src/viz/make_figures.py`](src/viz/make_figures.py) | **Working** — generates all 14 figures in this README |
| [`src/scrapers/broiler_rates.py`](src/scrapers/broiler_rates.py), [`chick_rates.py`](src/scrapers/chick_rates.py), [`feed_prices.py`](src/scrapers/feed_prices.py) | Documented stubs — forward collection, pending deployment |

*The data-collection plan is hybrid (historical backbone + forward collection) following the Wayback feasibility finding. Derived economic figures are labelled as derived and are not attributed to any source that does not state them. The causality result in Section 12.2 is negative and is reported as negative.*
