"""Scraper: historical daily NECC egg rates by zone (e2necc.com).

STATUS
------
Working scraper. Verified against e2necc for 2009-2026.

SOURCE
------
https://e2necc.com/home/eggprice  (HTTP POST)
The page renders a monthly grid: one row per NECC zone, one column per day of
the month. This is the dense historical backbone of the project's panel -- the
National Egg Coordination Committee price series goes back to 2009 and is
served on demand for any month/year, unlike the broiler/chick rate pages whose
history was never preserved.

POST PARAMETERS
---------------
ddlMonth      : month number, 1-12
ddlYear       : four-digit year (>= 2009)
rblReportType : 1 = Daily Rate Sheet, 2 = Monthly Avg. Sheet
btnReport     : "View Report"

OUTPUT SCHEMA (data/raw/egg_necc_YYYYMM.csv), one row per (zone, date)
----------------------------------------------------------------------
zone         : str   -- NECC zone/city label as published
date         : date  -- ISO 8601 (year-month-day)
egg_price    : float -- declared NECC rate (paise per egg, as published)
source_url   : str
retrieved_at : datetime (UTC)

NOTE
----
NECC rates are quoted in paise per egg (e.g. 550 = Rs 5.50). Values are kept
as published; conversion is left to the feature layer. Cells that are blank or
non-numeric (holidays / not-yet-declared days) are dropped.
"""

from __future__ import annotations

import argparse
import calendar
import io
import sys
from datetime import datetime, timezone

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://e2necc.com/home/eggprice"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
}
HEADER_CELL = "Name Of Zone / Day"


def fetch_month_html(month: int, year: int, timeout: int = 60) -> str:
    """POST the report form and return the raw HTML for one month."""
    data = {
        "ddlMonth": str(month),
        "ddlYear": str(year),
        "rblReportType": "1",  # Daily Rate Sheet
        "btnReport": "View Report",
    }
    resp = requests.post(URL, data=data, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_month(html: str, month: int, year: int) -> pd.DataFrame:
    """Melt the wide zone-by-day grid into tidy (zone, date, egg_price) rows."""
    soup = BeautifulSoup(html, "lxml")
    table = None
    for t in soup.find_all("table"):
        if HEADER_CELL.lower() in t.get_text().lower():
            table = t
            break
    if table is None:
        raise ValueError(f"data table not found for {year}-{month:02d}")

    grid = pd.read_html(io.StringIO(str(table)))[0]
    grid = grid.rename(columns={grid.columns[0]: "zone"})
    grid = grid[grid["zone"].notna()]
    grid = grid[grid["zone"].astype(str).str.strip().str.lower() != HEADER_CELL.lower()]

    days_in_month = calendar.monthrange(year, month)[1]
    day_cols = [c for c in grid.columns if str(c).isdigit() and 1 <= int(str(c)) <= days_in_month]

    long_df = grid.melt(id_vars="zone", value_vars=day_cols, var_name="day", value_name="egg_price")
    long_df["egg_price"] = pd.to_numeric(long_df["egg_price"], errors="coerce")
    long_df = long_df.dropna(subset=["egg_price"])
    long_df = long_df[long_df["egg_price"] > 0]

    long_df["date"] = pd.to_datetime(
        {"year": year, "month": month, "day": long_df["day"].astype(int)},
        errors="coerce",
    )
    long_df = long_df.dropna(subset=["date"])
    long_df["zone"] = long_df["zone"].astype(str).str.strip()
    long_df["source_url"] = URL
    long_df["retrieved_at"] = datetime.now(timezone.utc).isoformat()

    return long_df[["zone", "date", "egg_price", "source_url", "retrieved_at"]].sort_values(
        ["zone", "date"]
    ).reset_index(drop=True)


def scrape_month(month: int, year: int) -> pd.DataFrame:
    return parse_month(fetch_month_html(month, year), month, year)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape NECC egg rates for one month.")
    ap.add_argument("--month", type=int, required=True)
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    df = scrape_month(args.month, args.year)
    out = args.out or f"data/raw/egg_necc_{args.year}{args.month:02d}.csv"
    df.to_csv(out, index=False)
    print(f"{args.year}-{args.month:02d}: {len(df)} rows, "
          f"{df['zone'].nunique()} zones -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
