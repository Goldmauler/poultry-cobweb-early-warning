"""Scraper stub: historical backfill via the Internet Archive Wayback CDX API.

STATUS
------
Proposal-stage stub. No working extraction implemented yet.

TARGET API
----------
http://web.archive.org/cdx/search/cdx?url=<page>&output=json

WHY THIS IS THE KEY MOVE
------------------------
The rate pages are published daily and overwritten daily -- yesterday's rate
table is gone. The Wayback CDX API lists every archived snapshot of a URL with
its timestamp; fetching each snapshot and parsing the rate table out of the
archived HTML reconstructs years of history that would otherwise be
unrecoverable. This is what stops the project being hostage to the calendar
(i.e. having to wait years to accumulate a panel forward in time).

WHAT THIS WILL DO
-----------------
1. Query the CDX API for all snapshots of each rate page.
2. For each snapshot, fetch the archived HTML at its timestamped URL.
3. Delegate table parsing to the matching forward scraper's parser so the
   historical and live rows share one schema.
4. Emit region-day rows tagged with the snapshot's capture date.

OUTPUT SCHEMA
-------------
Same per-series schema as the forward scrapers, plus:
snapshot_timestamp : datetime -- Wayback capture timestamp (14-digit)
archived_url       : str      -- full web.archive.org snapshot URL

KNOWN LIMITATION
----------------
Wayback coverage of these rate pages is uneven -- capture frequency varies by
page and period, so the reconstructed panel will have gaps. Coverage is
measured and reported rather than assumed complete (see README, Section 11).
"""
