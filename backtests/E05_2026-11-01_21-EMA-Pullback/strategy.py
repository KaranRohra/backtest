"""21 EMA breakout + pullback continuation — Priyank Sharma (HOLD with Priyank)
https://www.youtube.com/watch?v=eKmr9Y8-bw0  (rules at 10:00-37:00; shown on NIFTY 50, 5-min)

Rules (see README.md for where each comes from and what we had to assume):
  Breakout : a green 5-min candle closes above the 21 EMA after closing below it (mirror for sells).
  Pullback : within the next 3 candles, a red candle that still closes above the EMA (a newer one replaces it)
             and comes near the EMA ("not very far" - within 0.1% of price here).
  Entry    : buy-stop at the pullback candle's high; it must trigger within 2 candles. A close back below
             the EMA first cancels the setup.
  Stop     : the pullback candle's low (or a lower low made before entry) minus a 1-2 point buffer,
             checked on a 5-min CLOSE ("closing basis"); "wick" stops on touch.
  Target   : 1.5R. One trade per breakout; intraday only.
  Optional : RSI(14) above 50 for buys / below 50 for sells.

Checked against the creator's own NIFTY trades (25-29 Nov 2024) before running - see README.
Signals come from 5-min candles built from 1-min data; entries, stops and targets are filled on the 1-min
candles.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "tf": 5,
    "ema": 21,
    "pull_bars": 3,  # the pullback candle must come within this many candles of the breakout
    "near_pct": 0.10,  # ...and its low (buy) / high (sell) within this % of price from the EMA
    "trig_bars": 2,  # the entry must trigger within this many candles of the pullback
    "sl_buf": 2.0,  # points beyond the pullback candle's low/high
    "sl_mode": "close",  # "close" = exit when a 5-min candle closes past the stop, "wick" = on touch
    "rr": 1.5,
    "rsi": False,  # require RSI(14) > 50 for buys, < 50 for sells
    "last_entry": "15:25",
}


def _rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def setups(df, p):
    """One row per pullback candle: when it arms, when it stops being valid, trigger and stop levels."""
    tf = int(p["tf"])
    b = df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                    close=("close", "last")).dropna()
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    ema = b.close.ewm(span=int(p["ema"]), adjust=False).mean().to_numpy()
    rsi = _rsi(b.close).to_numpy()
    above = c > ema
    end = b.index + pd.Timedelta(minutes=tf)  # candle close time
    rows, brk = [], None  # brk = (side, bar index) of the live breakout
    for i in range(1, len(b)):
        if above[i] != above[i - 1]:  # a close across the EMA: new breakout (if the candle has the right colour)
            side = 1 if above[i] else -1
            brk = (side, i) if (c[i] > o[i]) == (side > 0) and c[i] != o[i] else None
            continue
        if brk is None:
            continue
        side, bi = brk
        if i - bi > int(p["pull_bars"]):
            brk = None
            continue
        gap = (l[i] - ema[i]) if side > 0 else (ema[i] - h[i])  # how far the pullback stayed from the EMA
        # opposite colour, still on the breakout side, and near the EMA
        if ((c[i] < o[i]) if side > 0 else (c[i] > o[i])) and gap <= c[i] * p["near_pct"] / 100:
            # valid until the trigger window ends or a candle closes back across the EMA, whichever is first
            last = min(i + int(p["trig_bars"]), len(b) - 1)
            flip = next((j for j in range(i + 1, last + 1) if above[j] != above[i]), None)
            rows.append(dict(arm=end[i], until=end[flip - 1] if flip else end[last], side=side, brk=b.index[bi],
                             bar=b.index[i], trig=h[i] if side > 0 else l[i], stop=l[i] if side > 0 else h[i],
                             rsi=rsi[i]))
    return pd.DataFrame(rows)


def simulate(df, p, s, symbol, trade_from=None):
    sig = setups(df, p)
    if p["rsi"] and len(sig):
        sig = sig[np.where(sig.side > 0, sig.rsi > 50, sig.rsi < 50)]
    idx = df.index
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tod = np.array([t.time() for t in idx])
    day = idx.normalize()
    last, sq = dtime.fromisoformat(p["last_entry"]), dtime.fromisoformat(s.squareoff)
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    tf = int(p["tf"])
    candle_close = ((idx.minute + 1) % tf == 0) if tf <= 60 else np.zeros(len(idx), bool)
    by_arm = {}
    for r in sig.itertuples():
        by_arm.setdefault(r.arm, []).append(r)

    equity, trades = s.capital, []
    pending, pos, used, cur_day = [], None, set(), None

    def close(k, px, reason):
        nonlocal equity, pos
        side = pos["side"]
        pnl = side * pos["qty"] * (px - pos["entry"])
        equity += pnl
        trades.append(dict(
            symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[pos["i"]], entry_price=pos["entry"],
            exit_time=idx[k], exit_price=px, qty=pos["qty"], pnl=pnl, ret_pct=side * (px / pos["entry"] - 1) * 100,
            bars=k - pos["i"] + 1, exit_reason=reason, r=pnl / (pos["qty"] * abs(pos["entry"] - pos["sl"])),
            sl=pos["sl"], target=pos["tg"], breakout_time=pos["brk"], pullback_time=pos["bar"], rsi=pos["rsi"]))
        pos = None

    def manage(k, entry_bar):
        side = pos["side"]
        if p["sl_mode"] == "wick":
            if (l[k] <= pos["sl"]) if side > 0 else (h[k] >= pos["sl"]):  # SL first if both in one candle
                gap = not entry_bar and ((o[k] < pos["sl"]) if side > 0 else (o[k] > pos["sl"]))
                return close(k, o[k] if gap else pos["sl"], "stoploss")
        elif candle_close[k] and not entry_bar and ((c[k] < pos["sl"]) if side > 0 else (c[k] > pos["sl"])):
            return close(k, c[k], "stoploss")  # closing basis: out at the 5-min close beyond the stop
        if (h[k] >= pos["tg"]) if side > 0 else (l[k] <= pos["tg"]):
            gap = not entry_bar and ((o[k] > pos["tg"]) if side > 0 else (o[k] < pos["tg"]))
            close(k, o[k] if gap else pos["tg"], "target")

    for k in range(len(idx)):
        if day[k] != cur_day:
            if pos is not None:  # data ended early (holiday half-day): close at the last close
                close(k - 1, c[k - 1], "eod")
            cur_day, pending = day[k], []
        if idx[k] < start:
            continue
        new = by_arm.get(idx[k])
        if new:
            pending = [dict(r=r, low=r.stop, high=r.stop) for r in new] + pending  # newest pullback first
        pending = [x for x in pending if idx[k] < x["r"].until and x["r"].brk not in used]

        if pos is not None:
            if tod[k] >= sq:
                close(k, o[k], "squareoff")
            else:
                manage(k, entry_bar=False)
            continue
        if not pending or tod[k] > last:
            continue
        x = pending[0]
        r = x["r"]
        if (h[k] > r.trig) if r.side > 0 else (l[k] < r.trig):
            entry = max(o[k], r.trig) if r.side > 0 else min(o[k], r.trig)
            # stop: the pullback's low, or a lower low made before entry, plus the buffer
            stop = (x["low"] - p["sl_buf"]) if r.side > 0 else (x["high"] + p["sl_buf"])
            risk = abs(entry - stop)
            used.add(r.brk)
            pending = []
            if risk > 0:
                pos = dict(side=r.side, entry=entry, sl=stop, tg=entry + r.side * p["rr"] * risk,
                           qty=risk_qty(equity, entry, stop, s), i=k, brk=r.brk, bar=r.bar, rsi=r.rsi)
                manage(k, entry_bar=True)
            continue
        for y in pending:  # track lows/highs made while waiting (they can move the stop)
            y["low"], y["high"] = min(y["low"], l[k]), max(y["high"], h[k])

    if pos is not None:
        close(len(idx) - 1, c[-1], "eod")
    return pd.DataFrame(trades)
