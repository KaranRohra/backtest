"""Replication check: does the code find the signals Vishal Malkan marks on his own charts?

Arrows read from frames of his video (dates are approximate: read off the chart's month labels and candle count).
A marked signal counts as found when the code has a signal candle within 3 trading days of the arrow.

    .venv/bin/python backtests/E07_2026-11-13_Grandfather-Father-Son-RSI/replication.py ["D unfinished wk/mo, band 35-45 (used)"]
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parents[1]))
from core.datastore import get_candles  # noqa: E402

spec = importlib.util.spec_from_file_location("strategy", EP / "strategy.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# (symbol, side, arrow date, frame)
ARROWS = [
    ("JSWSTEEL", 1, "2021-01-29", "07m05_JSW_daily"),
    ("JINDALSTEL", 1, "2021-01-29", "07m36_JINDALSTEL_daily"),
    ("JINDALSTEL", 1, "2021-06-03", "07m36_JINDALSTEL_daily"),
    ("TATASTEEL", 1, "2021-01-29", "08m08_TATASTEEL_daily"),
    ("JUBLFOOD", 1, "2020-10-23", "08m50_JUBLFOOD_daily"),
    ("JUBLFOOD", 1, "2020-11-03", "08m50_JUBLFOOD_daily"),
    ("JUBLFOOD", 1, "2021-01-29", "08m50_JUBLFOOD_daily"),
    ("JUBLFOOD", 1, "2021-03-18", "08m50_JUBLFOOD_daily"),
    ("YESBANK", -1, "2019-11-28", "12m04_YESBANK_daily_short"),
    ("TMPV", -1, "2018-04-03", "12m32_TATAMOTORS_daily_short"),  # Tata Motors (now TMPV on Kite)
    ("TMPV", -1, "2018-08-21", "12m32_TATAMOTORS_daily_short"),
    ("TMPV", -1, "2018-09-11", "12m32_TATAMOTORS_daily_short"),
]


def signal_days(d, p):
    """Signal candles as the strategy defines them (direction +1 / -1), ignoring open trades."""
    ind = m.indicators(d, p)
    son = ind.son
    hl, blo, bhi = p["htf_level"], p["band_lo"], p["band_hi"]
    tb = int(p["touch_bars"])
    in_l = son.between(blo, bhi).astype(float).rolling(tb, min_periods=1).max() > 0
    in_s = son.between(100 - bhi, 100 - blo).astype(float).rolling(tb, min_periods=1).max() > 0
    green, red = d.close > d.open, d.close < d.open
    long_ = (ind.gf > hl) & (ind.fa > hl) & in_l & green
    short = (ind.gf < 100 - hl) & (ind.fa < 100 - hl) & in_s & red
    return long_.astype(int) - short.astype(int)


def check(p, verbose=False):
    found = 0
    for sym, side, day, _ in ARROWS:
        d = get_candles(f"NSE:{sym}", "day", "2010-01-01", "2022-01-14")
        sig = signal_days(d, p)
        i = d.index.searchsorted(pd.Timestamp(day))
        win = sig.iloc[max(i - 3, 0):i + 4]
        hit = win[win == side]
        found += len(hit) > 0
        if verbose:
            print(f"  {sym:10s} {'LONG ' if side > 0 else 'SHORT'} {day}  ->  "
                  + (", ".join(str(x.date()) for x in hit.index) if len(hit) else "not found"))
    return found


if __name__ == "__main__":
    base = m.PARAMS
    readings = {
        "A completed wk/mo, band 39-42 (as said)": {"live_htf": False, "band_lo": 39, "band_hi": 42},
        "B unfinished wk/mo, band 39-42 (as said)": {"live_htf": True, "band_lo": 39, "band_hi": 42},
        "C completed wk/mo, band 35-45": {"live_htf": False, "band_lo": 35, "band_hi": 45},
        "D unfinished wk/mo, band 35-45 (used)": {"live_htf": True, "band_lo": 35, "band_hi": 45},
    }
    for name, over in readings.items():
        p = {**base, **over}
        print(f"{name}: {check(p)}/{len(ARROWS)}")
    best = sys.argv[1] if len(sys.argv) > 1 else None
    if best:
        print("\nDetail for", best)
        check({**base, **readings[best]}, verbose=True)
