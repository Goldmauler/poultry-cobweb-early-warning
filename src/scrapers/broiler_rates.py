"""Scraper stub: daily broiler farm-gate rates by region.

STATUS
------
Proposal-stage stub. No working extraction implemented yet.

TARGET URL
----------
https://www.poultrybazaar.net/daily-rate-sheet/
(cross-checked against https://chickenratetoday.in/ where regions overlap)

WHAT THIS WILL DO
-----------------
Fetch the daily rate sheet, locate the broiler live-bird rate table, and emit
one row per (region, date). Rates on these pages are set by local Broiler
Coordination Committees, so the region label must be preserved verbatim for
later reconciliation.

OUTPUT SCHEMA (data/raw/broiler_rates_YYYYMMDD.csv)
---------------------------------------------------
region        : str   -- region/city label exactly as published
date          : date  -- publication date of the rate (ISO 8601)
broiler_price : float -- farm-gate live-bird price, INR per kg
source_url    : str   -- page the row was parsed from
retrieved_at  : datetime -- crawl timestamp (UTC)

NOTES
-----
Raw HTML of every fetch is archived under data/raw/ for reproducibility
before parsing, so a schema change on the source page never silently
corrupts the panel.
"""
