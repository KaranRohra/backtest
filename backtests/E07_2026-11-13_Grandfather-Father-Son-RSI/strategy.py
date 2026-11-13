"""Grandfather-Father-Son RSI ("5-star strategy") — Vishal Malkan, on Pushkar Raj Thakur's channel
https://www.youtube.com/watch?v=s63l6K_ggCM  (rules at 03:00-14:00)

Rules as taught (see README.md for where each comes from and what we had to assume):
  Timeframes : grandfather = monthly, father = weekly, son = daily (faster: 15-min / 5-min / 1-min).
  Long setup : grandfather RSI > 60 and father RSI > 60; the son's RSI pulls back to ~40 ("40 or 41,
               sometimes 42 or 39") and a bullish signal candle forms there.
  Entry      : buy above the signal candle's high.
  Stop       : the signal candle's low.
  Target     : the son's RSI back to 60 ("it will go till 60 minimum, that would be my target").
  Re-entry   : stopped out, but the son hasn't closed below 40 -> the same setup can be taken again.
  Short      : the mirror - grandfather and father RSI < 40, son's RSI rises to ~60 (58-61), red signal
               candle; sell below its low, stop above its high, target son's RSI back to 40.

Grandfather / father RSI is read the way his charts show it: the current, unfinished month / week, i.e.
the monthly RSI on a given day uses that day's close as the month's close so far.
The son "near 40" = his RSI is in the 35-45 band on the signal candle or the candle before it (his arrows
often mark the low candle; the green candle after it is the signal), and the signal candle is green
(red for shorts). Nothing after the signal candle's close is used. Checked against his 12 marked
examples in replication.py (11 found).
One trade per stock at a time.
"""
import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "rsi_len": 14,
    "frames": "MWD",  # "MWD" = monthly/weekly/daily on daily candles; "15-5-1" = 15/5/1-min on 1-min candles
    "htf_level": 60,  # grandfather and father above this (long) / below 100 - this (short)
    "band_lo": 35,  # son's RSI "near 40" (short: near 60 = 55-65). He says 39-42; his own marked
    "band_hi": 45,  # examples dip to 36.6 / 37.6 and bounce at 44-45, so 35-45 (see README replication)
    "exit_level": 60,  # long target: son's RSI back to 60 (short: 40)
    "touch_bars": 2,  # the son's RSI is in the band on the signal candle or the candle before it
    "need_pullback": False,  # True = the son must come down from 60 without closing below the band (long)
    "live_htf": True,  # read the unfinished month/week as it stands (his charts do); False = last completed one
    "allow_short": True,
}


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """Wilder RSI (as on TradingView / Kite charts)."""
    ch = np.diff(close, prepend=np.nan)
    up, dn = pd.Series(np.clip(ch, 0, None)), pd.Series(np.clip(-ch, 0, None))
    ag = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    al = dn.ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(al == 0, 100.0, 100 - 100 / (1 + ag / al))


def htf_rsi(close: np.ndarray, key: np.ndarray, n: int, live: bool) -> np.ndarray:
    """RSI of a higher timeframe, aligned to every base candle.

    `key` labels each base candle with its higher-timeframe period (month, week, 15-min block...).
    live=True: the current period's RSI as it stands at this candle's close (what the chart shows).
    live=False: the RSI of the last completed period.
    """
    starts = np.r_[True, key[1:] != key[:-1]]
    gid = np.cumsum(starts) - 1
    ends = np.r_[starts[1:], True]
    gclose = close[ends]  # each period's final close
    ch = np.diff(gclose, prepend=np.nan)
    up, dn = pd.Series(np.clip(ch, 0, None)), pd.Series(np.clip(-ch, 0, None))
    ag = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    al = dn.ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
    out = np.full(len(close), np.nan)
    prev = gid - 1
    ok = prev >= 0
    if not live:
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where(al == 0, 100.0, 100 - 100 / (1 + ag / al))
        out[ok] = r[prev[ok]]
        return out
    c = close[ok] - gclose[prev[ok]]  # change of the unfinished period so far
    g = (ag[prev[ok]] * (n - 1) + np.clip(c, 0, None)) / n
    l = (al[prev[ok]] * (n - 1) + np.clip(-c, 0, None)) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        out[ok] = np.where(l == 0, 100.0, 100 - 100 / (1 + g / l))
    return out


def _keys(idx: pd.DatetimeIndex, frames: str):
    """Period labels for grandfather and father."""
    if frames == "MWD":
        return idx.to_period("M").asi8, idx.to_period("W-SUN").asi8
    big, mid, _ = (int(x) for x in frames.split("-"))
    day = idx.normalize().asi8 // 86_400_000_000_000
    m = (idx.hour * 60 + idx.minute - (9 * 60 + 15)).to_numpy()
    return day * 10_000 + m // big, day * 10_000 + m // mid


def indicators(df: pd.DataFrame, p: dict) -> pd.DataFrame:
    c = df["close"].to_numpy(float)
    kg, kf = _keys(df.index, p["frames"])
    n = int(p["rsi_len"])
    return pd.DataFrame({"gf": htf_rsi(c, kg, n, p["live_htf"]), "fa": htf_rsi(c, kf, n, p["live_htf"]),
                         "son": rsi(c, n)}, index=df.index)


def simulate(df, p, s, symbol, trade_from=None):
    ind = indicators(df, p)
    idx = df.index
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    gf, fa, son = (ind[k].to_numpy() for k in ("gf", "fa", "son"))
    intraday = p["frames"] != "MWD"
    day = idx.normalize()
    new_day = np.r_[True, day[1:] != day[:-1]]
    last_bar = np.r_[new_day[1:], True]
    tod = (idx.hour * 60 + idx.minute).to_numpy()
    sq = int(s.squareoff[:2]) * 60 + int(s.squareoff[3:])
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    i0 = int(np.searchsorted(idx, start))

    hl, blo, bhi, xl = p["htf_level"], p["band_lo"], p["band_hi"], p["exit_level"]
    tb = int(p["touch_bars"])
    son_s = pd.Series(son)
    # long: son in [blo, bhi] on any of the last `tb` candles; short: in [100-bhi, 100-blo]
    in_l = son_s.between(blo, bhi).astype(float).rolling(tb, min_periods=1).max().to_numpy() > 0
    in_s = son_s.between(100 - bhi, 100 - blo).astype(float).rolling(tb, min_periods=1).max().to_numpy() > 0
    # pullback state: long armed after son >= exit level, disarmed by a close below the band
    arm_l = arm_s = not p["need_pullback"]
    equity, trades = s.capital, []
    pos, pend = 0, None  # pend = (side, trigger, stop) for the next candle only
    for i in range(len(df)):
        sv = son[i]
        if p["need_pullback"] and not np.isnan(sv):
            arm_l = True if sv >= xl else (False if sv < blo else arm_l)
            arm_s = True if sv <= 100 - xl else (False if sv > 100 - blo else arm_s)
        if i < i0:
            continue
        # 1) a pending stop-entry order from the previous candle's signal
        if pend and pos == 0:
            side, trig, stop = pend
            pend = None
            if (intraday and (new_day[i] or tod[i] >= sq)) or trig == stop:
                pass  # orders don't carry over to the next day / past square-off; no zero-range candles
            elif (h[i] >= trig) if side > 0 else (l[i] <= trig):
                gap = (o[i] > trig) if side > 0 else (o[i] < trig)
                pos, entry, sl, ei = side, (o[i] if gap else trig), stop, i
                qty = risk_qty(equity, entry, sl, s)
        # 2) manage the open trade inside this candle
        if pos:
            reason = px = None
            if intraday and tod[i] >= sq and i > ei:
                reason, px = "squareoff", o[i]
            elif (l[i] <= sl) if pos > 0 else (h[i] >= sl):  # same-candle entry + stop: stop counts
                gap = (o[i] < sl) if pos > 0 else (o[i] > sl)
                reason, px = "stoploss", (o[i] if gap and i > ei else sl)
            elif intraday and last_bar[i]:
                reason, px = "eod", c[i]
            if reason:
                trades.append(_trade(symbol, pos, idx, ei, i, entry, px, qty, sl, reason))
                equity += trades[-1]["pnl"]
                pos = 0
            elif (son[i] >= xl) if pos > 0 else (son[i] <= 100 - xl):  # target: exit at the next open
                if i + 1 < len(df) and not (intraday and new_day[i + 1]):
                    trades.append(_trade(symbol, pos, idx, ei, i + 1, entry, o[i + 1], qty, sl, "rsi_target"))
                else:
                    trades.append(_trade(symbol, pos, idx, ei, i, entry, c[i], qty, sl, "rsi_target"))
                equity += trades[-1]["pnl"]
                pos = 0
                continue  # flat from the next open; no new signal on this candle
        # 3) a new signal on this candle's close
        if pos == 0 and not np.isnan(sv) and not np.isnan(gf[i]) and not np.isnan(fa[i]):
            if intraday and tod[i] >= sq:
                continue
            if gf[i] > hl and fa[i] > hl and in_l[i] and c[i] > o[i] and arm_l:
                pend = (1, h[i], l[i])
            elif (p["allow_short"] and s.allow_short and gf[i] < 100 - hl and fa[i] < 100 - hl
                  and in_s[i] and c[i] < o[i] and arm_s):
                pend = (-1, l[i], h[i])
    if pos:
        trades.append(_trade(symbol, pos, idx, ei, len(df) - 1, entry, c[-1], qty, sl, "end_of_data"))
    return pd.DataFrame(trades)


def _trade(symbol, side, idx, ei, xi, entry, px, qty, sl, reason):
    risk = abs(entry - sl)
    return dict(symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[ei], entry_price=entry,
                exit_time=idx[xi], exit_price=px, qty=qty, pnl=side * qty * (px - entry),
                ret_pct=side * (px / entry - 1) * 100, bars=xi - ei + 1, exit_reason=reason,
                r=side * (px - entry) / risk if risk > 0 else 0.0, sl=sl)
