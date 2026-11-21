"""5-20 EMA crossover reversal — Abhishek (AbhishekXTrades)
https://www.youtube.com/watch?v=AgDZVDuxrec  (rules at 11:00-17:40, examples 17:40-25:30; 5-min intraday)

Rules (see README.md for where each comes from and what we had to assume):
  Crossover : the 5 EMA crosses the 20 EMA on a 5-min close. Only the day's first two crossovers count;
              from the third one the market is "sideways" and nothing more is traded that day.
  Pullback  : after a bullish cross, a red candle (the crossover candle itself counts). Up to 2 in a row is a
              correction; a 3rd red in a row is a reversal and kills that crossover's setup. Mirror for sells.
  Entry     : buy-stop a small buffer above the red candle's high. It must break within the next 3 candles;
              a newer red candle moves the level to its own high. No break in 3 candles -> wait for the next one.
  Stop      : below the red candle's low (sl_mode "candle") or the swing low of the last few candles
              (sl_mode "swing"). A stop wider than `half_above_pct` of price is halved ("bada hai to hafl kar do").
  Target    : 2R (the minimum he allows). One trade per crossover; after a stop-loss, no more trades that day.
  Intraday  : flat at the square-off time.

Signals come from 5-min candles built from 1-min data; entries, stops and targets are filled on the 1-min candles.
"""
from datetime import time as dtime

import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "tf": 5,
    "fast": 5,
    "slow": 20,
    "touch_pct": 0.0,  # >0: EMAs closing to within this % of price also count as the crossover (lines touch on the chart)
    "max_cross": 2,  # crossovers per day that can be traded
    "max_run": 2,  # pullback candles in a row allowed; one more kills the setup
    "trig_bars": 3,  # the level must break within this many candles
    "buf_pct": 0.006,  # entry / stop buffer, % of price (~1.5 pts on NIFTY, as in his 13-Jun-2025 trade)
    "sl_mode": "candle",  # "candle" = pullback candle's other end, "swing" = extreme of the last `swing_bars` candles
    "swing_bars": 5,
    "half_above_pct": 0.20,  # halve the stop when it is wider than this % of price (99 = never)
    "rr": 2.0,
    "first_entry": "09:15",
    "last_entry": "15:00",
    "stop_after_sl": True,  # "agar aapka stop loss lag gaya hai to bilkul nahi karna hai"
}


def bars5(df, tf):
    return df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                       close=("close", "last")).dropna()


def setups(df, p):
    """One row per pullback candle that arms a level: valid from its close until the trigger window ends."""
    tf = int(p["tf"])
    b = bars5(df, tf)
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    f = b.close.ewm(span=int(p["fast"]), adjust=False).mean().to_numpy()
    s = b.close.ewm(span=int(p["slow"]), adjust=False).mean().to_numpy()
    d = f - s
    day = b.index.normalize()
    end = b.index + pd.Timedelta(minutes=tf)
    nb, sw = int(p["trig_bars"]), int(p["swing_bars"])
    tol = c * p["touch_pct"] / 100
    rows, cross_n, cur, cx = [], 0, None, None  # cx = live crossover: dict(side, id, run)
    view = 1 if d[0] > 0 else -1  # the side of the last crossover
    for i in range(1, len(b)):
        if day[i] != cur:
            cur, cross_n, cx = day[i], 0, None
        now = 1 if d[i] > 0 else -1
        # a cross on this candle's close (EMAs run on across days, as on TradingView), or - with touch_pct - the
        # lines meeting while heading for a cross (then the actual flip a candle later is the same crossover)
        if now != view or (abs(d[i]) <= tol[i] and abs(d[i]) < abs(d[i - 1])):
            view = -view
            cross_n += 1
            cx = dict(side=view, id=b.index[i], n=cross_n, run=0) if cross_n <= p["max_cross"] else None
            # any level left from the previous crossover is cancelled: "view badal jayega"
            rows.append(dict(arm=end[i], until=end[i], side=0, cross=b.index[i], kill=True, bar=b.index[i],
                             trig=np.nan, stop=np.nan, n=cross_n))
        if cx is None:
            continue
        side = cx["side"]
        counter = (c[i] < o[i]) if side > 0 else (c[i] > o[i])
        if not counter:
            cx["run"] = 0
            continue
        cx["run"] += 1
        if cx["run"] > p["max_run"]:  # "teen matlab reversal"
            rows.append(dict(arm=end[i], until=end[i], side=side, cross=cx["id"], kill=True, bar=b.index[i],
                             trig=np.nan, stop=np.nan, n=cx["n"]))
            cx = None
            continue
        buf = c[i] * p["buf_pct"] / 100
        if p["sl_mode"] == "swing":
            lo = l[max(0, i - sw + 1): i + 1].min()
            hi = h[max(0, i - sw + 1): i + 1].max()
        else:
            lo, hi = l[i], h[i]
        last = min(i + nb, len(b) - 1)
        rows.append(dict(arm=end[i], until=end[last], side=side, cross=cx["id"], kill=False, bar=b.index[i],
                         trig=h[i] + buf if side > 0 else l[i] - buf,
                         stop=lo - buf if side > 0 else hi + buf, n=cx["n"]))
    return pd.DataFrame(rows)


def simulate(df, p, s, symbol, trade_from=None):
    sig = setups(df, p)
    idx = df.index
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tod = np.array([t.time() for t in idx])
    day = idx.normalize()
    first, last, sq = (dtime.fromisoformat(x) for x in (p["first_entry"], p["last_entry"], s.squareoff))
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    by_arm = {}
    for r in sig.itertuples():
        by_arm.setdefault(r.arm, []).append(r)

    equity, trades = s.capital, []
    live, pos, used, cur_day, locked = None, None, set(), None, False

    def close(k, px, reason):
        nonlocal equity, pos, locked
        side = pos["side"]
        pnl = side * pos["qty"] * (px - pos["entry"])
        equity += pnl
        r = pnl / (pos["qty"] * abs(pos["entry"] - pos["sl"]))
        trades.append(dict(
            symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[pos["i"]], entry_price=pos["entry"],
            exit_time=idx[k], exit_price=px, qty=pos["qty"], pnl=pnl, ret_pct=side * (px / pos["entry"] - 1) * 100,
            bars=k - pos["i"] + 1, exit_reason=reason, r=r, sl=pos["sl"], target=pos["tg"],
            cross_time=pos["cross"], cross_n=pos["n"], pullback_time=pos["bar"], halved=pos["halved"]))
        if reason == "stoploss" and p["stop_after_sl"]:
            locked = True
        pos = None

    def manage(k, entry_bar):
        side = pos["side"]
        if (l[k] <= pos["sl"]) if side > 0 else (h[k] >= pos["sl"]):  # stop first if both in one candle
            gap = not entry_bar and ((o[k] < pos["sl"]) if side > 0 else (o[k] > pos["sl"]))
            return close(k, o[k] if gap else pos["sl"], "stoploss")
        if (h[k] >= pos["tg"]) if side > 0 else (l[k] <= pos["tg"]):
            gap = not entry_bar and ((o[k] > pos["tg"]) if side > 0 else (o[k] < pos["tg"]))
            close(k, o[k] if gap else pos["tg"], "target")

    for k in range(len(idx)):
        if day[k] != cur_day:
            if pos is not None:  # data ended early (half-day): close at the last close
                close(k - 1, c[k - 1], "eod")
            cur_day, live, locked = day[k], None, False
        new = by_arm.get(idx[k])
        if new:
            for r in new:  # the newest pullback candle replaces the old level; a 3rd in a row kills it
                live = None if r.kill else r
        if live is not None and (idx[k] >= live.until or live.cross in used):
            live = None
        if idx[k] < start:
            continue
        if pos is not None:
            if tod[k] >= sq:
                close(k, o[k], "squareoff")
            else:
                manage(k, entry_bar=False)
            continue
        if live is None or locked or tod[k] > last or tod[k] < first:
            continue
        r = live
        if (h[k] >= r.trig) if r.side > 0 else (l[k] <= r.trig):
            entry = max(o[k], r.trig) if r.side > 0 else min(o[k], r.trig)
            stop = r.stop
            risk = abs(entry - stop)
            halved = risk > entry * p["half_above_pct"] / 100
            if halved:
                risk /= 2
                stop = entry - r.side * risk
            used.add(r.cross)
            live = None
            if risk > 0 and (stop < entry if r.side > 0 else stop > entry):
                pos = dict(side=r.side, entry=entry, sl=stop, tg=entry + r.side * p["rr"] * risk,
                           qty=risk_qty(equity, entry, stop, s), i=k, cross=r.cross, n=r.n, bar=r.bar, halved=halved)
                manage(k, entry_bar=True)

    if pos is not None:
        close(len(idx) - 1, c[-1], "eod")
    return pd.DataFrame(trades)
