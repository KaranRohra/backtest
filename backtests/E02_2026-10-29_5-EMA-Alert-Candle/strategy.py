"""5 EMA "Alert Candle" setup — Power of Stocks (Subhasish Pani)
Video tested (published on Pushkar Raj Thakur's channel): https://www.youtube.com/watch?v=uu3zGIXaG8g
(shown on BANK NIFTY; tested on NIFTY 50 and BANK NIFTY)

Rules (see README.md for where each comes from and what we had to assume):
  Sell   : 5-min chart, 5 EMA. A candle that CLOSES above the EMA and whose LOW does not touch
           it is the alert candle. A newer alert candle replaces it. Enter short the moment price
           breaks the alert candle's low; SL = its high.
  Buy    : 15-min chart, mirror image: a candle that closes below the EMA with its HIGH not
           touching it; enter long when price breaks its high; SL = its low.
  Target : minimum 1:3 risk-reward (booked in full at 3R here).
  Per day: at most 3 trades on each side; squared off at 15:15 (intraday).

Signals come from 5/15-min candles built from 1-min data; entries, stops and targets are filled
on the 1-min candles inside them, so we know which came first.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "ema": 5,
    "sell_tf": 5,  # minutes
    "buy_tf": 15,
    "rr": 3.0,  # target = rr x risk
    "sides": "both",  # "both", "short" (5-min sell setup only) or "long" (15-min buy setup only)
    "alert_valid": "until",  # "until" broken/replaced/day end, or "next" (next candle only)
    "max_trades": 3,  # per side per day
    "last_entry": "15:00",
}


def _alerts(df, tf, ema_n, side):
    """Alert candles on the `tf`-minute chart: (bar start, trigger level, stop) per bar, NaN if none."""
    b = df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"),
                                    low=("low", "min"), close=("close", "last")).dropna()
    ema = b.close.ewm(span=ema_n, adjust=False).mean()
    if side < 0:  # sell: closes above the EMA, low doesn't touch it
        ok = (b.close > ema) & (b.low > ema)
        level, stop = b.low, b.high
    else:  # buy: closes below the EMA, high doesn't touch it
        ok = (b.close < ema) & (b.high < ema)
        level, stop = b.high, b.low
    return b.index, level.where(ok).to_numpy(float), stop.where(ok).to_numpy(float)


def simulate(df, p, s, symbol, trade_from=None):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    idx = df.index
    day = idx.normalize()
    tod = np.array([t.time() for t in idx])
    last, sq = dtime.fromisoformat(p["last_entry"]), dtime.fromisoformat(s.squareoff)
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]

    books = []  # one per side: its own alert chart, armed alert and open position
    for side, tf in ((-1, p["sell_tf"]), (1, p["buy_tf"])):
        if p["sides"] != "both" and (side < 0) != (p["sides"] == "short"):
            continue
        bidx, level, stop = _alerts(df, int(tf), int(p["ema"]), side)
        j = np.searchsorted(bidx, idx.floor(f"{int(tf)}min"))  # chart candle each 1-min bar belongs to
        books.append(dict(side=side, tf=tf, bidx=bidx, level=level, stop=stop, j=j))

    equity = s.capital
    trades = []

    def close(bk, k, px, reason):
        nonlocal equity
        pos = bk["pos"]
        pnl = pos["side"] * pos["qty"] * (px - pos["entry"])
        equity += pnl
        trades.append(dict(
            symbol=symbol, side="LONG" if pos["side"] > 0 else "SHORT", entry_time=idx[pos["i"]],
            entry_price=pos["entry"], exit_time=idx[k], exit_price=px, qty=pos["qty"], pnl=pnl,
            ret_pct=pos["side"] * (px / pos["entry"] - 1) * 100, bars=k - pos["i"] + 1, exit_reason=reason,
            r=pnl / (pos["qty"] * abs(pos["entry"] - pos["sl"])), sl=pos["sl"], target=pos["target"],
            alert_time=pos["alert_time"], chart=f"{bk['tf']}-min"))
        bk["pos"] = None

    def manage(bk, k, entry_bar):
        pos = bk["pos"]
        side = pos["side"]
        if (h[k] >= pos["sl"]) if side < 0 else (l[k] <= pos["sl"]):  # SL first if both in one bar
            gap = not entry_bar and ((o[k] > pos["sl"]) if side < 0 else (o[k] < pos["sl"]))
            close(bk, k, o[k] if gap else pos["sl"], "stoploss")
        elif (l[k] <= pos["target"]) if side < 0 else (h[k] >= pos["target"]):
            px = pos["target"] if entry_bar else (min(o[k], pos["target"]) if side < 0 else max(o[k], pos["target"]))
            close(bk, k, px, "target")

    bounds = np.flatnonzero(np.r_[True, day[1:] != day[:-1], True])
    for a, b in zip(bounds[:-1], bounds[1:]):
        if idx[a] < start:
            continue
        for bk in books:
            bk.update(armed=None, pos=None, n=0, seen=None)

        for k in range(a, b):
            for bk in books:
                side = bk["side"]
                # a chart candle just closed: does it arm (or replace, or cancel) the alert?
                jk = bk["j"][k]
                if jk != bk["seen"]:
                    prev = jk - 1
                    if bk["seen"] is not None and prev >= 0:
                        if not np.isnan(bk["level"][prev]):
                            bk["armed"] = (bk["level"][prev], bk["stop"][prev], bk["bidx"][prev])
                        elif p["alert_valid"] == "next":
                            bk["armed"] = None
                    bk["seen"] = jk

                if bk["pos"] is not None:
                    if tod[k] >= sq:
                        close(bk, k, o[k], "squareoff")
                    else:
                        manage(bk, k, entry_bar=False)

                armed = bk["armed"]
                if (bk["pos"] is None and armed is not None and bk["n"] < p["max_trades"] and tod[k] <= last
                        and ((l[k] < armed[0]) if side < 0 else (h[k] > armed[0]))):
                    level, stop, alert_time = armed
                    entry = min(o[k], level) if side < 0 else max(o[k], level)
                    risk = abs(stop - entry)
                    bk["armed"] = None
                    if risk > 0:
                        q = risk_qty(equity, entry, stop, s)
                        bk["pos"] = dict(side=side, entry=entry, sl=stop, target=entry + side * p["rr"] * risk,
                                         qty=q, i=k, alert_time=alert_time)
                        bk["n"] += 1
                        manage(bk, k, entry_bar=True)

        for bk in books:
            if bk["pos"] is not None:
                close(bk, b - 1, c[b - 1], "eod")

    t = pd.DataFrame(trades)
    return t.sort_values("exit_time", ignore_index=True) if len(t) else t
