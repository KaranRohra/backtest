"""PDH/PDL Liquidity Sweep (1-min scalping) — Stock Learners (Gautam Jha)
https://www.youtube.com/watch?v=wI9b968AvW8  (taught on Gold; tested on XAUUSD, NIFTY 50 and BANK NIFTY)

Rules (see README.md for where each comes from and what we had to assume):
  Levels : previous day's high (PDH) and low (PDL).
  Short  : price trades above PDH. A red 1-min candle that makes a fresh high of the day
           (above PDH) is the setup; enter short when the NEXT candle breaks its low.
           SL = that red candle's high. Skip if the SL is wider than max_sl_pct.
  Long   : mirror at PDL — a green candle at a fresh low of the day below PDL, next candle
           breaks its high; SL = its low.
  Exits  : TG1 = most recent swing low (short) / swing high (long). Book `partial` (80%)
           there and move SL to cost; the rest rides to TG2 = the next swing beyond TG1.
           No trailing. Anything still open is squared off at 15:15.
  Per day: at most 3 trades; stop after 2 full stop-losses.

Sessions: "nse" uses the calendar day (IST timestamps). "fx" (gold) runs ~23h, so a trading
day goes from one 17:00 New York close to the next, the usual broker day; the times below
are then on that clock (00:00 = 17:00 NY) and timestamps are expected in UTC.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "trigger": "low",  # break of the setup candle's "low"/"high" (wick), or its "body" (close)
    "max_sl_pct": 0.2,  # skip setups with SL wider than this % of price (video skips 70-90+ pip SLs on gold)
    "max_sl_points": None,  # or an absolute cap in price units (gold: 8.0 = 80 pips, the creator's own unit)
    "session": "nse",  # "nse" or "fx" (see docstring)
    "pivot": 5,  # swing = high/low with `pivot` 1-min bars on each side (confirmed only after them)
    "partial": 0.8,  # fraction booked at TG1; 20% left for TG2
    "max_trades": 3,
    "max_full_sl": 2,
    "first_entry": "09:16",
    "last_entry": "15:00",
}


def _pivots(x: np.ndarray, n: int, high: bool) -> np.ndarray:
    s = pd.Series(x)
    w = s.rolling(2 * n + 1, center=True)
    ext = w.max() if high else w.min()
    return np.flatnonzero((s == ext).to_numpy())  # bar j is usable only from bar j + n (confirmed)


def _swing_targets(piv_idx, levels, confirmed_upto, entry, side, n):
    """Most recent confirmed swing beyond entry (TG1) and the next one further out (TG2)."""
    k = np.searchsorted(piv_idx, confirmed_upto - n, side="right")
    cand = levels[piv_idx[:k]][::-1]  # newest first
    beyond = cand[cand < entry] if side < 0 else cand[cand > entry]
    if not len(beyond):
        return np.nan, np.nan
    tg1 = beyond[0]
    further = beyond[beyond < tg1] if side < 0 else beyond[beyond > tg1]
    return tg1, (further[0] if len(further) else np.nan)


def simulate(df, p, s, symbol, trade_from=None):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    idx = df.index
    clock = idx
    if p["session"] == "fx":  # broker day: 17:00 New York -> 00:00
        clock = idx.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None) + pd.Timedelta(hours=7)
    day = clock.normalize()
    tod = np.array([t.time() for t in clock])
    first, last, sq = (dtime.fromisoformat(p[k] if k in p else s.squareoff)
                       for k in ("first_entry", "last_entry", "squareoff"))
    n = int(p["pivot"])
    ph, pl = _pivots(h, n, True), _pivots(l, n, False)

    daily = df.groupby(day).agg(high=("high", "max"), low=("low", "min"))
    pdh = pd.Series(daily.high.shift(1).reindex(day).to_numpy())
    pdl = pd.Series(daily.low.shift(1).reindex(day).to_numpy())
    bounds = np.flatnonzero(np.r_[True, day[1:] != day[:-1], True])

    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    equity = s.capital
    trades = []

    for a, b in zip(bounds[:-1], bounds[1:]):
        if idx[a] < start or np.isnan(pdh[a]):
            continue
        PDH, PDL = pdh[a], pdl[a]
        n_trades = full_sl = 0
        day_hi, day_lo = -np.inf, np.inf
        pending = None  # setup armed on bar k, valid for bar k+1 only
        pos = None

        def close_all(k, px, reason):
            nonlocal pos, equity, full_sl
            pnl = pos["booked"] + pos["side"] * pos["open_qty"] * (px - pos["entry"])
            avg_exit = pos["entry"] + pnl / (pos["side"] * pos["qty"])
            equity += pnl
            if reason == "stoploss" and not pos["partial_done"]:
                full_sl += 1
            trades.append(dict(
                symbol=symbol, side="LONG" if pos["side"] > 0 else "SHORT", entry_time=idx[pos["i"]],
                entry_price=pos["entry"], exit_time=idx[k], exit_price=avg_exit, qty=pos["qty"], pnl=pnl,
                ret_pct=pos["side"] * (avg_exit / pos["entry"] - 1) * 100, bars=k - pos["i"] + 1,
                exit_reason=("tg1+" if pos["partial_done"] else "") + reason,
                r=pnl / (pos["qty"] * abs(pos["entry"] - pos["sl0"])), sl=pos["sl0"], tg1=pos["tg1"],
                tg2=pos["tg2"], pdh=PDH, pdl=PDL))
            pos = None

        def manage(k, entry_bar):
            side = pos["side"]
            hit_sl = h[k] >= pos["stop"] if side < 0 else l[k] <= pos["stop"]
            if hit_sl:  # if SL and a target share a bar, assume SL came first
                gap = not entry_bar and (o[k] > pos["stop"] if side < 0 else o[k] < pos["stop"])
                close_all(k, o[k] if gap else pos["stop"], "cost" if pos["partial_done"] else "stoploss")
                return
            if not pos["partial_done"]:
                if (l[k] <= pos["tg1"]) if side < 0 else (h[k] >= pos["tg1"]):
                    px = pos["tg1"] if entry_bar else (min(o[k], pos["tg1"]) if side < 0 else max(o[k], pos["tg1"]))
                    q = pos["qty"] * p["partial"]
                    pos["booked"] += side * q * (px - pos["entry"])
                    pos["open_qty"] -= q
                    pos["partial_done"] = True
                    pos["stop"] = pos["entry"]  # SL to cost
                    if pos["open_qty"] <= 1e-12:
                        close_all(k, px, "tg1")
                        return
            if pos["partial_done"] and not np.isnan(pos["tg2"]):
                if (l[k] <= pos["tg2"]) if side < 0 else (h[k] >= pos["tg2"]):
                    close_all(k, pos["tg2"], "tg2")

        for k in range(a, b):
            # 1) manage an open position on this bar
            if pos is not None:
                if tod[k] >= sq:
                    close_all(k, o[k], "squareoff")
                else:
                    manage(k, entry_bar=False)

            # 2) the armed setup triggers only on this (next) candle
            if pos is None and pending is not None and first <= tod[k] <= last:
                side, level, stop = pending
                if (l[k] < level) if side < 0 else (h[k] > level):
                    entry = min(o[k], level) if side < 0 else max(o[k], level)
                    tg1, tg2 = _swing_targets(pl if side < 0 else ph, l if side < 0 else h, k - 1, entry, side, n)
                    risk = abs(stop - entry)
                    sl_ok = risk / entry * 100 <= p["max_sl_pct"] and (p["max_sl_points"] is None or risk <= p["max_sl_points"])
                    if not np.isnan(tg1) and risk > 0 and sl_ok:
                        q = risk_qty(equity, entry, stop, s)
                        pos = dict(side=side, entry=entry, stop=stop, sl0=stop, tg1=tg1, tg2=tg2, qty=q,
                                   open_qty=q, booked=0.0, partial_done=False, i=k)
                        n_trades += 1
                        manage(k, entry_bar=True)
            pending = None

            # 3) fresh extremes and new setups (decided on this candle's close)
            fresh_hi, fresh_lo = h[k] >= day_hi, l[k] <= day_lo
            day_hi, day_lo = max(day_hi, h[k]), min(day_lo, l[k])
            can_trade = pos is None and n_trades < p["max_trades"] and full_sl < p["max_full_sl"]
            if can_trade and tod[k] < last:
                if c[k] < o[k] and fresh_hi and h[k] > PDH:
                    pending = (-1, c[k] if p["trigger"] == "body" else l[k], h[k])
                elif c[k] > o[k] and fresh_lo and l[k] < PDL:
                    pending = (1, c[k] if p["trigger"] == "body" else h[k], l[k])

        if pos is not None:
            close_all(b - 1, c[b - 1], "eod")

    return pd.DataFrame(trades)
