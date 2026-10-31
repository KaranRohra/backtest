"""Linear Gann levels + candlestick patterns — Adib Noorani (on Trading Titans by InCred Money)
https://www.youtube.com/watch?v=ZaniJwJIwJg  (strategy at 10:00-37:00; shown on NIFTY 15-min;
"works on any instrument in the world" - tested on NIFTY 50, gold and Bitcoin)

Rules (see README.md for where each comes from and what we had to assume):
  Levels : square every whole number; if the square is even, add 1 (24,025 / 24,337 / 24,649 on NIFTY).
           Static - they never change and never "weaken".
  Setup  : one of six patterns at a level on the 15-min chart - hammer, bullish engulfing, morning star
           (buy) or inverted hammer, bearish engulfing, evening star (sell) - plus a session-opening
           marubozu (open = high: sell, open = low: buy). The pattern must CLOSE on the trade side of the level.
  Entry  : stop order a small buffer beyond the pattern; SL a buffer beyond its other end; target 1:1.
  Per day: stop after 2 stop-losses; intraday only.

Checked against the creator's own NIFTY examples (4-26 Aug 2026) before running - see README.
Signals come from 15-min candles built from 1-min data; entries, stops and targets are filled on the 1-min
candles.

Sessions: "nse" = IST calendar day. "fx" (gold) = broker day from one 17:00 New York close to the next, on a
clock where 00:00 = 17:00 NY (timestamps UTC). "utc" (Bitcoin) = UTC calendar day.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "tf": 15,
    "session": "nse",
    "tol_pct": 0.10,  # how close the pattern must come to a level (% of price; ~24 pts on NIFTY)
    "buffer_pct": 0.02,  # entry/SL buffer beyond the pattern (% of price; "5-10 points" on NIFTY ~ 0.02-0.04%)
    "rr": 1.0,
    "max_sl": 2,
    "valid_bars": 2,  # the stop order must trigger within this many candles of the pattern
    "marubozu": True,  # session-opening candle with open = high (sell) / open = low (buy) at a level
    "first_entry": "09:30",
    "last_entry": "15:00",
}

BUY_PATTERNS = ("hammer", "bullish engulfing", "morning star")


def gann_levels(lo, hi):
    """n^2 for every whole n, +1 when the square is even."""
    a, b = int(np.floor(np.sqrt(max(lo, 1)))) - 1, int(np.ceil(np.sqrt(hi))) + 1
    return np.array([n * n + (1 - (n * n) % 2) for n in range(max(a, 1), b + 1)], float)


def _clock(idx, session):
    if session == "fx":
        return idx.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None) + pd.Timedelta(hours=7)
    return idx


def patterns(b):
    """(bar, side, name, high, low) for every completed pattern on the candles in `b`."""
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    body, rng = np.abs(c - o), h - l
    up, dn = h - np.maximum(o, c), np.minimum(o, c) - l
    out = []
    for i in range(len(b)):
        r = rng[i] if rng[i] > 0 else 1e-9
        if dn[i] >= 2 * max(body[i], 0.1 * r) and up[i] <= 0.3 * r:
            out.append((i, 1, "hammer", h[i], l[i]))
        if up[i] >= 2 * max(body[i], 0.1 * r) and dn[i] <= 0.3 * r:
            out.append((i, -1, "inverted hammer", h[i], l[i]))
        if i >= 1:
            j = i - 1
            if c[j] < o[j] and c[i] > o[i] and c[i] >= o[j] and o[i] <= c[j]:
                out.append((i, 1, "bullish engulfing", max(h[i], h[j]), min(l[i], l[j])))
            if c[j] > o[j] and c[i] < o[i] and c[i] <= o[j] and o[i] >= c[j]:
                out.append((i, -1, "bearish engulfing", max(h[i], h[j]), min(l[i], l[j])))
        if i >= 2:
            a, m = i - 2, i - 1
            small = body[m] <= 0.5 * body[a]
            if c[a] < o[a] and small and c[i] > o[i] and c[i] > (o[a] + c[a]) / 2:
                out.append((i, 1, "morning star", h[a:i + 1].max(), l[a:i + 1].min()))
            if c[a] > o[a] and small and c[i] < o[i] and c[i] < (o[a] + c[a]) / 2:
                out.append((i, -1, "evening star", h[a:i + 1].max(), l[a:i + 1].min()))
    return out


def setups(df, p):
    """Patterns at a Gann level whose last candle closed on the trade side of that level."""
    tf = int(p["tf"])
    b = df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                    close=("close", "last")).dropna()
    clock = _clock(b.index, p["session"])
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    lv = gann_levels(b.low.min() * 0.9, b.high.max() * 1.1)
    pats = patterns(b)
    if p["marubozu"]:  # first candle of each session day
        first = np.r_[True, clock.normalize()[1:] != clock.normalize()[:-1]]
        for i in np.flatnonzero(first):
            r = h[i] - l[i]
            if r > 0 and h[i] - o[i] <= 0.15 * r and o[i] - c[i] >= 0.6 * r:
                pats.append((i, -1, "opening marubozu", h[i], l[i]))
            if r > 0 and o[i] - l[i] <= 0.15 * r and c[i] - o[i] >= 0.6 * r:
                pats.append((i, 1, "opening marubozu", h[i], l[i]))
    rows = []
    for i, side, name, ph, pl in pats:
        tol = c[i] * p["tol_pct"] / 100
        near = lv[(lv >= pl - tol) & (lv <= ph + tol)]
        beyond = near[near > c[i]] if side < 0 else near[near < c[i]]  # closed below (sell) / above (buy) it
        if len(beyond):
            rows.append(dict(close_time=b.index[i] + pd.Timedelta(minutes=tf), bar=b.index[i], side=side,
                             pattern=name, level=beyond.min() if side < 0 else beyond.max(), pat_high=ph, pat_low=pl))
    return pd.DataFrame(rows)


def simulate(df, p, s, symbol, trade_from=None):
    sig = setups(df, p)
    idx = df.index
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    clock = _clock(idx, p["session"])
    tod = np.array([t.time() for t in clock])
    day = clock.normalize()
    first, last, sq = (dtime.fromisoformat(x) for x in (p["first_entry"], p["last_entry"], s.squareoff))
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    expiry = pd.Timedelta(minutes=int(p["tf"]) * int(p["valid_bars"]))
    by_close = {}
    for r in sig.itertuples():
        by_close.setdefault(r.close_time, []).append(r)

    equity, trades = s.capital, []
    pending, pos, sl_today, cur_day = [], None, 0, None

    def close(k, px, reason):
        nonlocal equity, pos, sl_today
        side = pos["side"]
        pnl = side * pos["qty"] * (px - pos["entry"])
        equity += pnl
        sl_today += reason == "stoploss"
        trades.append(dict(
            symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[pos["i"]], entry_price=pos["entry"],
            exit_time=idx[k], exit_price=px, qty=pos["qty"], pnl=pnl, ret_pct=side * (px / pos["entry"] - 1) * 100,
            bars=k - pos["i"] + 1, exit_reason=reason, r=pnl / (pos["qty"] * abs(pos["entry"] - pos["sl"])),
            sl=pos["sl"], target=pos["tg"], pattern=pos["pattern"], level=pos["level"], pattern_time=pos["bar"]))
        pos = None

    def manage(k, entry_bar):
        side = pos["side"]
        if (l[k] <= pos["sl"]) if side > 0 else (h[k] >= pos["sl"]):  # SL first if both in one candle
            gap = not entry_bar and ((o[k] < pos["sl"]) if side > 0 else (o[k] > pos["sl"]))
            close(k, o[k] if gap else pos["sl"], "stoploss")
        elif (h[k] >= pos["tg"]) if side > 0 else (l[k] <= pos["tg"]):
            gap = not entry_bar and ((o[k] > pos["tg"]) if side > 0 else (o[k] < pos["tg"]))
            close(k, o[k] if gap else pos["tg"], "target")

    for k in range(len(idx)):
        if day[k] != cur_day:
            if pos is not None:  # data ended early (holiday half-day): close at the last close
                close(k - 1, c[k - 1], "eod")
            cur_day, sl_today, pending = day[k], 0, []
        if idx[k] < start:
            continue
        new = by_close.get(idx[k])
        if new:
            pending = list(new) + pending  # newest pattern first
        pending = [r for r in pending if idx[k] < r.close_time + expiry]

        if pos is not None:
            if tod[k] >= sq:
                close(k, o[k], "squareoff")
            else:
                manage(k, entry_bar=False)
            continue
        if sl_today >= p["max_sl"] or not (first <= tod[k] <= last):
            continue
        keep = []
        for r in pending:
            buf = r.pat_high * p["buffer_pct"] / 100
            trig = r.pat_low - buf if r.side < 0 else r.pat_high + buf
            stop = r.pat_high + buf if r.side < 0 else r.pat_low - buf
            if (h[k] >= stop) if r.side < 0 else (l[k] <= stop):
                continue  # ran through the stop before triggering: setup dead
            if pos is None and ((l[k] <= trig) if r.side < 0 else (h[k] >= trig)):
                entry = min(o[k], trig) if r.side < 0 else max(o[k], trig)
                risk = abs(stop - entry)
                pos = dict(side=r.side, entry=entry, sl=stop, tg=entry + r.side * p["rr"] * risk,
                           qty=risk_qty(equity, entry, stop, s), i=k, pattern=r.pattern, level=r.level, bar=r.bar)
                manage(k, entry_bar=True)
                continue
            keep.append(r)
        pending = keep

    if pos is not None:
        close(len(idx) - 1, c[-1], "eod")
    return pd.DataFrame(trades)
