"""MTF (multi-timeframe) weekly fakeout swing strategy — Priyank Sharma (HOLD with Priyank), on Bazaar Ke Mahir
https://www.youtube.com/watch?v=XuW_VXHD7gc  (rules at 04:00-22:00; shown on CUMMINS INDIA; "works on stocks and index")

Rules (see README.md for where each comes from and what we had to assume):
  Weekly : mark the previous week's high and low.
  Daily  : in the first 4 trading days of the week, price trades above the previous week's high and a daily
           candle then CLOSES back below it (same day counts) -> sell setup. Mirror at the low -> buy setup.
  15-min : market-structure shift - a 15-min close below the last swing low made before the fakeout's highest
           high. Already happened by the setup day's close -> enter at the next morning's open; otherwise it must
           happen on the next trading day (entry at that candle's close), or there is no trade.
  Stop   : just beyond the fakeout's extreme.
  Target : book half at 1:1 and move the stop to entry; the rest runs to the previous week's low (sell) / high
           (buy). Skipped when that level is less than 1R away.
  One trade per stock at a time; a setup in the other direction closes the open trade and reverses it.

Checked against the creator's own example (CUMMINS INDIA, 14-23 Oct 2024) before running - see README.
Simulated on Kite's 15-min candles (1-min data also works: it is resampled to 15-min); the daily close is the
day's last traded price.
"""
import numpy as np
import pandas as pd

from core.engine import risk_qty

PARAMS = {
    "tf": 15,
    "setup_days": 4,  # the daily close back inside must come in the first N trading days of the week
    "pivot": 1,  # swing low/high = lower/higher than this many 15-min candles on each side
    "sl_buf_pct": 0.1,  # stop beyond the fakeout extreme (% of price)
    "partial": 0.5,  # share booked at 1R (stop then moves to entry); 0 = no partial, all runs to the weekly level
    "min_room_r": 1.0,  # skip unless the previous week's opposite level is this many R away (R to the extreme)
    "max_days": 10,  # time exit: close the trade at the close of this trading day after entry
}


def _pivots(x, k, low):
    """Indices i where x[i] is the lowest (highest) of x[i-k .. i+k]."""
    n = len(x)
    out = np.zeros(n, bool)
    for i in range(k, n - k):
        w = x[i - k:i + k + 1]
        out[i] = x[i] == (w.min() if low else w.max())
    return out


def setups(df, p):
    """One row per setup that reached an entry: side, entry bar, entry price, stop, weekly target."""
    tf = int(p["tf"])
    b = df.resample(f"{tf}min").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                    close=("close", "last")).dropna()
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    day = b.index.normalize()
    days = pd.DatetimeIndex(day.unique())
    first = np.searchsorted(day, days)  # first bar of each day
    last = np.r_[first[1:], len(b)] - 1  # last bar of each day
    dclose = c[last]
    week = days.to_period("W-SUN")
    piv_lo, piv_hi = _pivots(l, int(p["pivot"]), True), _pivots(h, int(p["pivot"]), False)

    rows = []
    weeks = pd.Series(np.arange(len(days)), index=week).groupby(level=0)
    wlist = list(weeks)
    for (_, prev), (_, cur) in zip(wlist[:-1], wlist[1:]):
        pd_, cd = prev.to_numpy(), cur.to_numpy()
        pwh, pwl = h[first[pd_[0]]:last[pd_[-1]] + 1].max(), l[first[pd_[0]]:last[pd_[-1]] + 1].min()
        for side in (-1, 1):
            level, target = (pwh, pwl) if side < 0 else (pwl, pwh)
            for j, d in enumerate(cd[:int(p["setup_days"])]):
                seg = slice(first[cd[0]], last[d] + 1)
                poked = h[seg].max() > level if side < 0 else l[seg].min() < level
                back = dclose[d] < level if side < 0 else dclose[d] > level
                if poked and back:
                    nxt = d + 1 if d + 1 < len(days) else None
                    r = _entry(b, o, h, l, c, piv_lo, piv_hi, side, level, first[cd[0]], last[d],
                               last[nxt] if nxt is not None else None, first[nxt] if nxt is not None else None, p)
                    if r:
                        rows.append(dict(side=side, setup_day=days[d], pw_level=level, target=target, **r))
                    break  # one setup per side per week
    t = pd.DataFrame(rows)
    return (t.sort_values("entry_i").reset_index(drop=True) if len(t) else t), b


def _entry(b, o, h, l, c, piv_lo, piv_hi, side, level, w0, setup_end, next_end, next_start, p):
    """Find the market-structure shift; returns entry bar/price, stop and the swing level, or None."""
    stop_end = next_end if next_end is not None else setup_end
    ext_i, swing = None, None
    for i in range(w0, stop_end + 1):
        beyond = h[i] > level if side < 0 else l[i] < level
        new_ext = ext_i is None or (h[i] > h[ext_i] if side < 0 else l[i] < l[ext_i])
        if beyond and new_ext:  # a new fakeout extreme: the swing to break is the last pivot before it
            ext_i = i
            piv = piv_lo if side < 0 else piv_hi
            # only pivots already confirmed when the extreme printed, on the inside of the weekly level
            lo = max(w0 - 200, 0)
            js = np.flatnonzero(piv[lo:i - int(p["pivot"]) + 1]) + lo
            js = js[(l[js] < level) if side < 0 else (h[js] > level)]
            swing = (l if side < 0 else h)[js[-1]] if len(js) else None
            continue
        if ext_i is None or swing is None:
            continue
        if (c[i] < swing) if side < 0 else (c[i] > swing):  # structure shift on a 15-min close
            ext = h[ext_i] if side < 0 else l[ext_i]
            if i <= setup_end:  # seen after the setup day's close -> next morning's open
                if next_start is None:
                    return None
                return dict(entry_i=next_start, entry=o[next_start], ext=ext, swing=swing, shift_i=i, at_close=False)
            return dict(entry_i=i, entry=c[i], ext=ext, swing=swing, shift_i=i, at_close=True)
    return None


def simulate(df, p, s, symbol, trade_from=None):
    sig, b = setups(df, p)
    idx = b.index
    o, h, l, c = (b[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    day = idx.normalize()
    day_no = np.cumsum(np.r_[True, day[1:] != day[:-1]]) - 1
    start = pd.Timestamp(trade_from) if trade_from is not None else idx[0]
    equity, trades, busy_until = s.capital, [], -1

    def levels(r):
        stop = r.ext * (1 + p["sl_buf_pct"] / 100) if r.side < 0 else r.ext * (1 - p["sl_buf_pct"] / 100)
        risk = (stop - r.entry) * -r.side
        # room to the weekly level, measured as he does on the chart: entry to the fakeout extreme
        ok = risk > 0 and (r.target - r.entry) * r.side >= p["min_room_r"] * (r.ext - r.entry) * -r.side
        return stop, risk, ok

    rows = [r for r in sig.itertuples() if levels(r)[2]]
    for n, r in enumerate(rows):
        i0 = int(r.entry_i)
        if idx[i0] < start or i0 <= busy_until:
            continue
        side, entry = r.side, float(r.entry)
        stop, risk, _ = levels(r)
        # a setup in the other direction closes this trade and reverses it
        rev = next((x for x in rows[n + 1:] if x.side != side and x.entry_i > i0), None)
        qty = risk_qty(equity, entry, stop, s)
        legs = [[p["partial"], entry + side * risk], [1 - p["partial"], float(r.target)]] if p["partial"] else \
            [[1.0, float(r.target)]]
        legs = [g for g in legs if g[0] > 0]
        sl, open_legs = stop, list(legs)
        last_day = day_no[i0] + int(p["max_days"])
        k = i0 + 1 if r.at_close else i0  # entered at a close: manage from the next bar
        exits = []
        while open_legs and k < len(idx):
            if rev is not None and k == rev.entry_i and not rev.at_close:  # reversed at the open
                exits += [(g[0], k, o[k], "reversed") for g in open_legs]
                open_legs = []
                break
            if (h[k] >= sl) if side < 0 else (l[k] <= sl):  # stop first if both in one candle
                gap = (o[k] > sl) if side < 0 else (o[k] < sl)
                for g in open_legs:
                    exits.append((g[0], k, o[k] if gap else sl, "stoploss" if sl != entry else "breakeven"))
                open_legs = []
                break
            for g in list(open_legs):
                if (l[k] <= g[1]) if side < 0 else (h[k] >= g[1]):
                    gap = (o[k] < g[1]) if side < 0 else (o[k] > g[1])
                    exits.append((g[0], k, o[k] if gap else g[1], "target_1r" if g is legs[0] and len(legs) > 1
                                  else "target_week"))
                    open_legs.remove(g)
                    sl = entry  # after the 1R booking the rest is risk-free
            if open_legs and rev is not None and k == rev.entry_i:  # reversed at this candle's close
                exits += [(g[0], k, c[k], "reversed") for g in open_legs]
                open_legs = []
                break
            if open_legs and (day_no[k] >= last_day and (k + 1 == len(idx) or day_no[k + 1] != day_no[k])):
                for g in open_legs:
                    exits.append((g[0], k, c[k], "time"))
                open_legs = []
            k += 1
        for g in open_legs:  # data ended
            exits.append((g[0], len(idx) - 1, c[-1], "eod"))
        # one row per trade: the legs' P&L combined, booked at the last exit
        k_end = max(k for _, k, _, _ in exits)
        px = sum(share * px for share, _, px, _ in exits)  # share-weighted exit price
        pnl = side * qty * (px - entry)
        equity += pnl
        trades.append(dict(
            symbol=symbol, side="LONG" if side > 0 else "SHORT", entry_time=idx[i0], entry_price=entry,
            exit_time=idx[k_end], exit_price=px, qty=qty, pnl=pnl, ret_pct=side * (px / entry - 1) * 100,
            bars=k_end - i0 + 1, exit_reason="+".join(dict.fromkeys(e[3] for e in exits)), r=side * (px - entry) / risk,
            sl=stop, target=r.target, setup_day=r.setup_day, swing=r.swing, fakeout_extreme=r.ext))
        busy_until = k_end - 1 if exits[-1][3] == "reversed" else k_end
    return pd.DataFrame(trades)
