"""Scraper stub: broiler farm-gate rates — BLOCKED by source format.

STATUS
------
Not implemented: the data is not available in structured form. See
src/scrapers/chick_rates.py for the full verified finding.

SUMMARY
-------
Poultry Bazaar's broiler daily-rate-sheet renders no data cells server-side or
after JavaScript execution; rates are published as images, not tables.
chickenratetoday.in loads its regional broiler table via JavaScript and exposes
only a small static "brand-average" table. There is no free structured source
for daily regional broiler farm-gate prices that these checks could find.

CONSEQUENCE
-----------
Broiler price (the cobweb target) cannot be assembled as a structured series.
The project therefore demonstrates its forecasting methodology on the NECC egg
price -- the one dense, structured Indian poultry price series -- while keeping
the broiler cobweb as the motivating narrative (README Sections 4-5, 11).
"""
