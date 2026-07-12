# Sources / Bibliography

Full evidence base for *Breaking the Poultry Cobweb*. This list is the single
source of truth for citations; the README draws only from these entries.

**Link-status conventions**

- Unmarked link: resolved with a 200 response at time of verification.
- `[link rot — verify]`: returned HTTP 404 at time of verification (confirmed dead). Retained rather than silently dropped or replaced.
- `[403 to automated access — verify in browser]`: blocks automated fetchers (HTTP 403) but is expected to load in a normal browser. Content could not be machine-verified.

No source has been substituted for one that could not be read. No DOIs, authors, or page numbers have been invented.

---

## Foundational theory

| Source | Relevance | Link |
|---|---|---|
| Ezekiel, M. (1938). "The Cobweb Theorem." *Quarterly Journal of Economics*, 52(2), 255–280. | The 1938 origin of the problem this project addresses. | Cited bibliographically; no stable open-access URL asserted. |

## The Indian feed crisis (why the margin buffer is gone)

| Source | Key fact | Link |
|---|---|---|
| Down To Earth — "Lost in maize" | Maize-to-ethanol rose from 315M litres (ESY 2022-23) to **2.86 billion litres (ESY 2023-24)** = 42% of all ethanol. Poultry/cattle feed uses **60–70% of India's maize** and was worst hit. India became a **net maize importer in 2024**; exports fell 1.9M → 0.5M tonnes. | https://www.downtoearth.org.in/agriculture/lost-in-maize |
| Nutrinews — "India's poultry sector faces feed crisis amid GM import debate" | **Crisil Ratings: poultry profitability expected to decline by up to 50% in the 2025/26 marketing year**, based on a survey of 30 poultry farms. | `[link rot — verify]` https://nutrinews.com/en/indias-poultry-sector-faces-feed-crisis-amid-gm-import-debate/ |
| ChiniMandi — interview with Poultry India President Uday Singh Bias | Ethanol demand driving up maize prices; industry requesting duty-free maize/soy imports. | https://www.chinimandi.com/rising-ethanol-demand-drives-maize-prices-impacting-poultry-feed-costs-poultry-india-president-uday-singh-bias/ |
| Poultry India — "Poultry Feed Crisis" | Maize is **>70% of feed composition**; ethanol requirement projected ~17M tonnes. | `[link rot — verify]` https://www.poultryindia.co.in/poultry-feed-crisis-why-four-neighboring-countries-could-pos/ |
| Food & Agribusiness (historical precedent, 2013–14) | Production cost **₹68/kg** vs farm gate **₹57–58/kg** = **₹10/kg loss**; **20–30% of farmers** closed or suspended operations; NECC sought a loan moratorium. Proves the problem is chronic, not new. | https://www.foodagribusiness.world/poultry/feed-price-hikes-cause-unrest-in-indian-poultry-sector |

## The price crash, and the evidence of the data vacuum

| Source | Key fact | Link |
|---|---|---|
| ICRA — Indian Poultry Industry, March 2025 | Feed = **~70% of variable cost**; maize 65–70% and soymeal 25–30% of feed. **Broiler prices fell 18–19% MoM in West/South India (Feb 2025)**, 11–14% East/North; 22–25% YoY. FCR 1.6–1.9. Attributes supply shortage to "reduction in broiler placements by poultry farmers." **ICRA cites `Poultrybazaar` as its data source** — the single best evidence that no official Indian placement/price statistic exists. | https://www.icra.in/Rating/DownloadResearchSummaryReport?id=6224 |

## Unit economics

| Source | Key fact | Link |
|---|---|---|
| The Global Statistics — Chicks Rate Today | DOC **₹20–25**; **₹80–90** to raise a bird; **40–45 day** rearing to 2–2.5 kg; India produces **1.5 billion broilers/year**. | https://www.theglobalstatistics.com/chicks-rate-today/ |
| PoultryApp — Broiler rates in India | **65–70 million broiler placements per week**; farm gate ₹115 → consumer ₹250; Suguna, Venky's, CP, Sneha, Shalimar ≈ 60% of the market; ~1/3 of production is independent farmers. | https://www.poultryapp.com/broiler-rates-in-india/ |

## The US comparison — proof the method works and that India lacks the instrument

| Source | Key fact | Link |
|---|---|---|
| USDA Economic Research Service — Poultry & Eggs Market Outlook | Broiler production forecasts for 2026–27 adjusted "reflecting hatchery and placements data." The placement→price link is official US methodology. | https://www.ers.usda.gov/topics/animal-products/poultry-eggs/market-outlook |
| Brownfield Ag News — "Broiler placements stay 2% ahead of the 2025 pace" | The weekly USDA Broiler Hatchery report: 255.839M eggs set, **197.497M chicks placed**, hatchability 79.4%. The public good India does not have. | `[403 to automated access — verify in browser]` https://www.brownfieldagnews.com/news/broiler-placements-stay-2-ahead-of-the-2025-pace/ |
| US Foods — Farmer's Report (Chicken) | **199 million chicks placed** in the week ending 20 June 2026, up 2% YoY — routine, published, weekly. | https://www.usfoods.com/tools-tips-and-ideas/articles-and-publications/farmer-s-report/chicken |

## Biological grow-out cycle (justifies the 42-day lag)

| Source | Key fact | Link |
|---|---|---|
| *Poultry Science* (2025) — broiler performance under commercial conditions | Analysis of **4,842 commercial broiler flocks** (Ross/Cobb); **42 days** is the standard slaughter reference age. Anchors the lag in peer-reviewed literature. | `[403 to automated access — verify in browser]` https://www.sciencedirect.com/science/article/pii/S0032579125009691 |

## Data sources (verified during the feasibility phase)

Status reflects checks run before building scrapers (see `scripts/wayback_feasibility.py` and the working `src/scrapers/egg_rates.py`).

| Source | What it provides | Verified status | Link |
|---|---|---|---|
| NECC egg rates (e2necc) | Daily egg rate by zone, historical to 2009; month/year POST form | **Verified working** — the panel's dense historical backbone (~37 zones, full daily coverage) | https://e2necc.com/home/eggprice |
| data.gov.in mandi price API | Daily maize/soybean market prices (state/district/market, min/max/modal) | Verified working; **current-snapshot only** (used for forward feed collection) | https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi |
| Agmarknet | Multi-year daily maize and soybean-meal mandi prices (feed cost index) via report generator | Data exists; stateful ASP.NET portal (harder scrape) | https://agmarknet.gov.in |
| Poultry Bazaar — daily rate sheet | Daily broiler rates by region | Live; **forward collection** (no dense archive) | https://www.poultrybazaar.net/daily-rate-sheet/ |
| Poultry Bazaar — chick rates | Daily day-old-chick rates by region — the key leading-indicator variable | Live; **forward collection** (no dense archive) | https://www.poultrybazaar.net/daily-rate-sheet/chick-rates/ |
| Chicken Rate Today | Daily live/retail broiler rates by city; rates set by local Broiler Coordination Committees | Live; forward collection | https://chickenratetoday.in/ |
| Internet Archive Wayback CDX API | Attempted historical reconstruction of the rate pages | **Coverage too sparse** (~20–33 days total); retained only as scattered validation anchors | http://web.archive.org/cdx/search/cdx |
