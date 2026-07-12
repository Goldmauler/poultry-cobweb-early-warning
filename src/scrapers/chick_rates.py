"""Scraper stub: day-old-chick (DOC) rates — BLOCKED by source format.

STATUS
------
Not implemented: the data is not available in structured form. Documented here
because the DOC price is the project's motivating leading indicator.

FINDING (verified with headless Chromium via Playwright)
--------------------------------------------------------
The Poultry Bazaar chick-rates page (https://www.poultrybazaar.net/daily-rate-sheet/chick-rates/)
is an ASP.NET WebForms page whose served and rendered HTML contains only a
table header and ZERO data cells. Selecting a year/month and submitting
navigates to e.g. /chick-rates/2024/January/ but the rate "sheet" is published
as an IMAGE (Files/Rate_Sheet/.../Chick-Rates.jpg), not a data table, and
appears gated behind sign-up. chickenratetoday.in likewise loads its regional
tables via JavaScript with no static data.

CONSEQUENCE
-----------
The day-old-chick price series cannot be scraped to structured numbers from the
free public sources. Per the project's data-availability decision, the chick ->
broiler 42-day forecast is retained as the *motivating* hypothesis (README
Sections 4-5) and the executable model is built on the dense, structured NECC
egg series instead (see src/scrapers/egg_rates.py and src/features/build_panel.py).

TO REVIVE THIS SERIES one would need either OCR of the rate-sheet images
(unreliable on dense city x day grids) or a structured DOC price source that
does not currently appear to exist publicly.
"""
