"""VWAP + Fibonacci Pivots + Stochastic RSI intraday strategy — Anish Singh Thakur (Booming Bulls)
https://www.youtube.com/watch?v=8OurAiVyhE4  (shown on Bajaj Finance; tested on BAJFINANCE, HDFCBANK, RELIANCE)

Rules (see README.md for where each comes from and what we had to assume):
  Chart   : 5-min. Daily Fibonacci pivots (P, R1-R3, S1-S3), VWAP, Stochastic RSI (default 14/14/3/3).
  Time    : no trades before 10:45.
  Filter  : above VWAP only buy, below VWAP only sell.
  Entry   : price breaks a pivot level, VWAP, or the day's high/low in that direction,
            with Stochastic RSI agreeing (blue %K above red %D for a buy, below for a sell).
  Exit    : target ~1%; stop-loss 0.5% ("15 rupees SL, 30 target, 1:2").
  Per day : stop after a target; at most 2 trades (stop after 2 stop-losses). Squared off at 15:15.

Signals come from 5-min candles built from 1-min data; the break, the stop and the target are
filled on the 1-min candles inside them, so we know which came first.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "tf": 5,
    "first_entry": "10:45",
    "last_entry": "14:30",
    "target_pct": 1.0,
    "sl": "pct",  # "pct" (sl_pct below/above entry) or "vwap" (just beyond VWAP, skip if wider than the target)
    "sl_pct": 0.5,
    "vwap_buffer_pct": 0.05,  # "leave Rs 1-2 of space" below VWAP on a ~Rs 3,000 stock
    "stoch": True,  # require Stochastic RSI to agree
    "entry": "break",  # "break" (the moment price crosses the level) or "close" (a 5-min candle closes beyond it)
    "max_trades": 2,
}

LEVELS = ("S3", "S2", "S1", "P", "R1", "R2", "R3")


def _stoch_rsi(close: pd.Series, n_rsi=14, n_st=14, k=3, d=3):
    """TradingView's Stochastic RSI: %K (blue) and %D (red)."""
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n_rsi, adjust=False).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / n_rsi, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    lo, hi = rsi.rolling(n_st).min(), rsi.rolling(n_st).max()
    K = (100 * (rsi - lo) / (hi - lo)).rolling(k).mean()
    return K, K.rolling(d).mean()


def _chart(df, tf):
    """5-min candles with session VWAP, day high/low so far, Stochastic RSI and that day's Fibonacci pivots."""
    b = df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                    close=("close", "last"), volume=("volume", "sum")).dropna()
    day = b.index.normalize()
    pv = (b.high + b.low + b.close) / 3 * b.volume
    b["vwap"] = (pv.groupby(day).cumsum() / b.volume.groupby(day).cumsum().replace(0, np.nan)).fillna(b.close)
    b["day_hi"] = b.high.groupby(day).cummax()
    b["day_lo"] = b.low.groupby(day).cummin()
    b["k"], b["d"] = _stoch_rsi(b.close)

    d = df.groupby(df.index.normalize()).agg(high=("high", "max"), low=("low", "min"), close=("close", "last"))
    H, L, C = d.high.shift(1), d.low.shift(1), d.close.shift(1)  # previous day
    P = (H + L + C) / 3
    R = H - L
    piv = pd.DataFrame({"P": P, "R1": P + 0.382 * R, "R2": P + 0.618 * R, "R3": P + R,
                        "S1": P - 0.382 * R, "S2": P - 0.618 * R, "S3": P - R})
    return b.join(piv, on=day)


def _setups(row, stoch):
    """Nearest level to break on each side after the candle `row` closed: ((price, name) or None, same for short)."""
    lv = {name: getattr(row, name) for name in LEVELS}
    lv.update(VWAP=row.vwap, DH=row.day_hi, DL=row.day_lo)
    up = [(v, k) for k, v in lv.items() if v > row.close and v >= row.vwap]  # after the break we're above VWAP
    dn = [(v, k) for k, v in lv.items() if v < row.close and v <= row.vwap]  # ... or below it
    ok_long = not stoch or row.k > row.d
    ok_short = not stoch or row.k < row.d
    return (min(up) if up and ok_long else None), (max(dn) if dn and ok_short else None)


def simulate(df, p, s, symbol, trade_from=None):
    idx = df.index
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tod = np.array([t.time() for t in idx])
    first, last = dtime.fromisoformat(p["first_entry"]), dtime.fromisoformat(p["last_entry"])
    sq = dtime.fromisoformat(s.squareoff)
    tf = int(p["tf"])
    B = _chart(df.dropna(), tf)
    rows = list(B.itertuples())
    j_of = np.searchsorted(B.index, idx.floor(f"{tf}min"))  # chart candle each 1-min bar belongs to
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]

    equity = s.capital
    trades = []
    pos = None

    def close(k, px, reason):
        nonlocal equity, pos
        side = pos["side"]
        pnl = side * pos["qty"] * (px - pos["entry"])
        equity += pnl
        trades.append(dict(
            symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[pos["i"]], entry_price=pos["entry"],
            exit_time=idx[k], exit_price=px, qty=pos["qty"], pnl=pnl, ret_pct=side * (px / pos["entry"] - 1) * 100,
            bars=k - pos["i"] + 1, exit_reason=reason, r=pnl / (pos["qty"] * abs(pos["entry"] - pos["sl"])),
            sl=pos["sl"], target=pos["tg"], level=pos["level"], level_price=pos["level_px"]))
        pos = None
        return reason

    def manage(k, entry_bar):
        """Exit on this 1-min candle if the SL or target is touched (SL first if both)."""
        side = pos["side"]
        if (l[k] <= pos["sl"]) if side > 0 else (h[k] >= pos["sl"]):
            gap = not entry_bar and ((o[k] < pos["sl"]) if side > 0 else (o[k] > pos["sl"]))
            return close(k, o[k] if gap else pos["sl"], "stoploss")
        if (h[k] >= pos["tg"]) if side > 0 else (l[k] <= pos["tg"]):
            gap = not entry_bar and ((o[k] > pos["tg"]) if side > 0 else (o[k] < pos["tg"]))
            return close(k, o[k] if gap else pos["tg"], "target")
        return None

    day = idx.normalize()
    bounds = np.flatnonzero(np.r_[True, day[1:] != day[:-1], True])
    for a, b in zip(bounds[:-1], bounds[1:]):
        if idx[a] < start:
            continue
        n_trades, done = 0, False
        setups = (None, None)
        seen = None
        for k in range(a, b):
            closed = None  # the chart candle that closed just before this 1-min bar
            if j_of[k] != seen:
                if seen is not None:
                    closed = rows[j_of[k] - 1]
                    armed = setups
                    setups = _setups(closed, p["stoch"])
                seen = j_of[k]

            if pos is not None:
                if tod[k] >= sq:
                    close(k, o[k], "squareoff")
                elif manage(k, entry_bar=False) == "target":
                    done = True
                continue  # one position at a time; no new entry on an exit candle

            if done or n_trades >= p["max_trades"] or not (first <= tod[k] <= last):
                continue

            hit = None
            if p["entry"] == "break":
                ls, ss = setups
                if ls and h[k] > ls[0]:
                    hit = (1, max(o[k], ls[0]), ls)
                elif ss and l[k] < ss[0]:
                    hit = (-1, min(o[k], ss[0]), ss)
            elif closed is not None:  # "close": the candle that just closed is beyond the level armed before it
                ls, ss = armed
                agree_l = not p["stoch"] or closed.k > closed.d
                agree_s = not p["stoch"] or closed.k < closed.d
                if ls and closed.close > ls[0] and closed.close >= closed.vwap and agree_l:
                    hit = (1, o[k], ls)
                elif ss and closed.close < ss[0] and closed.close <= closed.vwap and agree_s:
                    hit = (-1, o[k], ss)
            if hit is None:
                continue

            side, entry, (level_px, level) = hit
            if p["sl"] == "vwap":
                sl = rows[j_of[k] - 1].vwap * (1 - side * p["vwap_buffer_pct"] / 100)
                if (entry - sl) * side <= 0 or abs(entry - sl) / entry * 100 > p["target_pct"]:
                    continue  # VWAP on the wrong side, or further away than the target: skip
            else:
                sl = entry * (1 - side * p["sl_pct"] / 100)
            tg = entry * (1 + side * p["target_pct"] / 100)
            pos = dict(side=side, entry=entry, sl=sl, tg=tg, qty=risk_qty(equity, entry, sl, s), i=k,
                       level=level, level_px=level_px)
            n_trades += 1
            setups = (None, setups[1]) if side > 0 else (setups[0], None)  # this level is used up
            if manage(k, entry_bar=True) == "target":
                done = True

        if pos is not None:
            close(b - 1, c[b - 1], "eod")

    return pd.DataFrame(trades)
