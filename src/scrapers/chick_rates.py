"""Scraper stub: daily day-old-chick (DOC) rates by region.

STATUS
------
Proposal-stage stub. No working extraction implemented yet.

TARGET URL
----------
https://www.poultrybazaar.net/daily-rate-sheet/chick-rates/

WHY THIS IS THE KEY MODULE
--------------------------
The day-old-chick price is the leading indicator at the centre of this
project. A chick placed today is a market-ready bird in 40-45 days, so the
DOC price is the market-clearing price of placement demand -- the observable
proxy for the placement volume that India does not publish.

OUTPUT SCHEMA (data/raw/chick_rates_YYYYMMDD.csv)
-------------------------------------------------
region       : str   -- region/city label exactly as published
date         : date  -- publication date of the rate (ISO 8601)
chick_price  : float -- day-old-chick price, INR per chick
source_url   : str   -- page the row was parsed from
retrieved_at : datetime -- crawl timestamp (UTC)

DERIVED FEATURES (built later in src/features/build_panel.py)
-------------------------------------------------------------
chick_price_ma7  : 7-day moving average of chick_price
chick_price_yoy  : year-on-year change in chick_price
"""
