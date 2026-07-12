"""Fetch monthly global feed-commodity prices from FRED (free CSV, no key).

STATUS
------
Working. FRED serves clean monthly commodity price series as CSV with no API
key. These are global reference prices (USD per metric tonne), used to build a
feed-cost index that drives the egg-price model. Indian mandi feed prices
(Agmarknet) are only available as a current snapshot via the data.gov.in API;
FRED provides the dense multi-year history the model needs, and Indian feed
cost tracks these global benchmarks closely (maize and soy are traded globally).

SERIES
------
PMAIZMTUSDM : Global price of Maize, monthly, USD/MT (from 1992)
PSOYBUSDM   : Global price of Soybeans, monthly, USD/MT (from 1992)

OUTPUT (data/raw/feed_fred.csv), one row per month
--------------------------------------------------
date        : month start (ISO)
maize_usd_mt : float
soy_usd_mt   : float
retrieved_at : datetime (UTC)
"""

from __future__ import annotations

import io
import sys
from datetime import datetime, timezone

import pandas as pd
import requests

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
SERIES = {"maize_usd_mt": "PMAIZMTUSDM", "soy_usd_mt": "PSOYBUSDM"}
HEADERS = {"User-Agent": "poultry-cobweb/0.1 (academic research)"}


def fetch_series(series_id: str, timeout: int = 40) -> pd.Series:
    r = requests.get(FRED.format(sid=series_id), headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"].dropna()


def fetch_feed() -> pd.DataFrame:
    cols = {name: fetch_series(sid) for name, sid in SERIES.items()}
    out = pd.DataFrame(cols).reset_index()
    out["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    return out


def main() -> int:
    df = fetch_feed()
    out = "data/raw/feed_fred.csv"
    df.to_csv(out, index=False)
    print(f"feed: {len(df)} months, {df['date'].min().date()} -> {df['date'].max().date()} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
