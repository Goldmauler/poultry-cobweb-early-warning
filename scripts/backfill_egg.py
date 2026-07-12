"""Backfill NECC egg rates for a range of months and assemble the panel.

Loops month-by-month over a date range, calls the verified egg scraper for
each month, writes one raw CSV per month under data/raw/, and concatenates
everything into a single tidy panel under data/processed/. Polite fixed delay
between requests; months that return nothing (early gaps) are skipped and
reported rather than aborting the run.

Usage:
    python scripts/backfill_egg.py --start 2009-01 --end 2026-07
    python scripts/backfill_egg.py --start 2021-01 --end 2026-07 --delay 1.0
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date

import pandas as pd

# Make src importable when run from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from scrapers.egg_rates import scrape_month  # noqa: E402

RAW_DIR = os.path.join("data", "raw")
PROC_DIR = os.path.join("data", "processed")


def month_range(start: tuple[int, int], end: tuple[int, int]):
    y, m = start
    while (y, m) <= end:
        yield y, m
        m += 1
        if m > 12:
            m, y = 1, y + 1


def parse_ym(s: str) -> tuple[int, int]:
    y, m = s.split("-")
    return int(y), int(m)


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill NECC egg rates over a month range.")
    ap.add_argument("--start", type=parse_ym, required=True, help="YYYY-MM")
    ap.add_argument("--end", type=parse_ym, required=True, help="YYYY-MM")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    args = ap.parse_args()

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROC_DIR, exist_ok=True)

    frames: list[pd.DataFrame] = []
    ok, empty, failed = 0, 0, 0
    months = list(month_range(args.start, args.end))
    print(f"Backfilling {len(months)} months: {args.start} -> {args.end}")

    for i, (y, m) in enumerate(months, 1):
        tag = f"{y}-{m:02d}"
        try:
            df = scrape_month(m, y)
        except Exception as e:  # noqa: BLE001 - long crawl; report and continue
            failed += 1
            print(f"  [{i:>3}/{len(months)}] {tag}  FAILED: {e}")
            time.sleep(args.delay)
            continue
        if df.empty:
            empty += 1
            print(f"  [{i:>3}/{len(months)}] {tag}  empty (no data)")
        else:
            out = os.path.join(RAW_DIR, f"egg_necc_{y}{m:02d}.csv")
            df.to_csv(out, index=False)
            frames.append(df)
            ok += 1
            print(f"  [{i:>3}/{len(months)}] {tag}  {len(df):>5} rows, {df['zone'].nunique():>2} zones")
        time.sleep(args.delay)

    if not frames:
        print("No data collected; nothing written to processed/.")
        return 1

    panel = pd.concat(frames, ignore_index=True).sort_values(["zone", "date"])
    panel = panel.drop_duplicates(subset=["zone", "date"]).reset_index(drop=True)
    panel_path = os.path.join(PROC_DIR, "egg_panel.csv")
    panel.to_csv(panel_path, index=False)

    print("\n" + "=" * 60)
    print(f"months ok/empty/failed : {ok}/{empty}/{failed}")
    print(f"panel rows             : {len(panel):,}")
    print(f"zones                  : {panel['zone'].nunique()}")
    print(f"date range             : {panel['date'].min()} -> {panel['date'].max()}")
    print(f"written                : {panel_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
