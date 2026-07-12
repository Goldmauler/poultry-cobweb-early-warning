"""Wayback Machine coverage feasibility check.

Answers the single most important question for this project before any build:
does the Internet Archive hold enough historical snapshots of the poultry
rate pages to reconstruct a multi-year daily panel?

For each target page it queries the CDX API, collapses to at most one capture
per day, keeps only HTTP 200 captures, and reports how many distinct days are
archived per calendar year. It prints a verdict per page.

Usage:
    python scripts/wayback_feasibility.py

No third-party deps beyond `requests`. Read-only; hits only the public CDX API.
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from datetime import datetime

import requests

CDX = "http://web.archive.org/cdx/search/cdx"

TARGETS = {
    "broiler_rates": "poultrybazaar.net/daily-rate-sheet/",
    "chick_rates": "poultrybazaar.net/daily-rate-sheet/chick-rates/",
    "chickenratetoday": "chickenratetoday.in/",
}

HEADERS = {"User-Agent": "poultry-cobweb-feasibility/0.1 (academic research)"}


def query_cdx(url: str, retries: int = 4, timeout: int = 90) -> list[list[str]]:
    """Return CDX rows [timestamp, original, statuscode], one per day, 200s only."""
    params = {
        "url": url,
        "output": "json",
        "fl": "timestamp,original,statuscode",
        "filter": "statuscode:200",
        "collapse": "timestamp:8",  # one capture per YYYYMMDD
    }
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(CDX, params=params, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            return data[1:] if data else []  # drop the header row
        except Exception as e:  # noqa: BLE001 - diagnostic script, report and retry
            last_err = e
            wait = attempt * 5
            print(f"    attempt {attempt}/{retries} failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"CDX query failed after {retries} attempts: {last_err}")


def summarise(rows: list[list[str]]) -> tuple[Counter, int, str, str]:
    per_year: Counter = Counter()
    days = set()
    for ts, _orig, _sc in rows:
        year = ts[:4]
        per_year[year] += 1
        days.add(ts[:8])
    if not days:
        return per_year, 0, "-", "-"
    lo, hi = min(days), max(days)
    fmt = lambda d: f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return per_year, len(days), fmt(lo), fmt(hi)


def verdict(total_days: int, years_covered: int) -> str:
    if total_days >= 500 and years_covered >= 3:
        return "STRONG  - multi-year daily-ish panel is reconstructable"
    if total_days >= 150:
        return "USABLE  - partial panel; expect gaps, may need to narrow scope/regions"
    if total_days > 0:
        return "THIN    - too sparse for a daily panel; rethink source or horizon"
    return "NONE    - no 200 captures found; this page is not reconstructable here"


def main() -> int:
    print(f"Wayback CDX feasibility check  ({datetime.now():%Y-%m-%d %H:%M})")
    print("=" * 68)
    for name, url in TARGETS.items():
        print(f"\n[{name}]  {url}")
        try:
            rows = query_cdx(url)
        except RuntimeError as e:
            print(f"  ERROR: {e}")
            continue
        per_year, total_days, lo, hi = summarise(rows)
        print(f"  archived days (200, 1/day): {total_days}   range: {lo} -> {hi}")
        if per_year:
            span = " ".join(
                f"{y}:{per_year[y]}" for y in sorted(per_year)
            )
            print(f"  by year: {span}")
        print(f"  VERDICT: {verdict(total_days, len(per_year))}")
    print("\n" + "=" * 68)
    print("Interpretation: >=500 days across >=3 years = the 5-year panel is viable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
