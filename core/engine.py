"""Bar-by-bar backtest engine shared by every episode.

A strategy only produces signals; this module turns them into trades.

strategy.signals(df, params) returns a DataFrame aligned to df with any of:
    entry_long, exit_long, entry_short, exit_short   bool
    sl, target                                        optional absolute prices, read on the entry bar
                                                      (overrides sl_pct / target_pct for that trade)

Execution rules (no lookahead):
  * A signal seen on bar i's close is filled at bar i+1's open.
  * Stops are checked intrabar: a gap through the stop fills at the open; if SL and target
    are both inside one bar's range we assume SL hit first (conservative).
  * intraday=True: no entries at/after `squareoff`; open positions exit at the open of the
    first bar at/after `squareoff`, or at the last bar's close of the day if data ends earlier.
  * Costs are zero (series rule) - every output is labelled "before costs".

Strategies that need execution this model can't express (stop-entry orders, partial
exits, per-day trade limits) define instead:
    simulate(df, params, settings, symbol, trade_from) -> trades DataFrame
with the same columns run_symbol produces (pnl, ret_pct, ...; optional r = R-multiple).
Equity is then built from realised P&L at each exit (fine for intraday: flat every night).
Use risk_qty() for sizing so every strategy sizes the same way.
"""
from dataclasses import dataclass, field
from datetime import time as dtime

import numpy as np
import pandas as pd


@dataclass
class Settings:
    capital: float = 100_000
    sizing: str = "percent"  # "percent" of current equity, "fixed_qty", or "risk" (simulate() strategies)
    size: float = 1.0  # fraction of equity (percent), units (fixed_qty), or fraction of equity risked (risk)
    max_leverage: float = 1.0  # cap on position value / equity for "risk" sizing
    sl_pct: float | None = None  # e.g. 0.01 = 1% stop
    target_pct: float | None = None
    trail_pct: float | None = None
    intraday: bool = False
    squareoff: str = "15:15"
    allow_short: bool = True
    extra: dict = field(default_factory=dict)


def _flag(sig: pd.DataFrame, col: str) -> np.ndarray:
    return sig[col].fillna(False).to_numpy(bool) if col in sig else np.zeros(len(sig), bool)


def run_symbol(df: pd.DataFrame, sig: pd.DataFrame, s: Settings, symbol: str):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    idx = df.index
    days = idx.normalize()
    sq = dtime.fromisoformat(s.squareoff)
    at_sq = np.array([t.time() >= sq for t in idx]) if s.intraday else np.zeros(len(df), bool)
    last_of_day = np.r_[days[1:] != days[:-1], True]

    el, xl = _flag(sig, "entry_long"), _flag(sig, "exit_long")
    es, xs = _flag(sig, "entry_short"), _flag(sig, "exit_short")
    if not s.allow_short:
        es[:] = False
    sl_col = sig["sl"].to_numpy(float) if "sl" in sig else None
    tg_col = sig["target"].to_numpy(float) if "target" in sig else None

    cash = s.capital
    pos = 0  # +1 long, -1 short
    qty = entry_px = stop = target = peak = 0.0
    entry_i = 0
    trades, equity = [], np.empty(len(df))

    def close(i, px, reason):
        nonlocal cash, pos
        pnl = pos * qty * (px - entry_px)
        cash += pnl
        trades.append(
            dict(symbol=symbol, side="LONG" if pos > 0 else "SHORT", entry_time=idx[entry_i], entry_price=entry_px,
                 exit_time=idx[i], exit_price=px, qty=qty, pnl=pnl, ret_pct=pos * (px / entry_px - 1) * 100,
                 bars=i - entry_i + 1, exit_reason=reason)
        )
        pos = 0

    for i in range(len(df)):
        # 1) act on the previous bar's signals at this bar's open
        if i > 0:
            p = i - 1
            if pos > 0 and (xl[p] or es[p]):
                close(i, o[i], "signal")
            elif pos < 0 and (xs[p] or el[p]):
                close(i, o[i], "signal")
            if pos == 0 and not at_sq[i] and (el[p] or es[p]):
                pos = 1 if el[p] else -1
                entry_px, entry_i, peak = o[i], i, o[i]
                qty = s.size if s.sizing == "fixed_qty" else cash * s.size / entry_px
                stop = sl_col[p] if sl_col is not None and not np.isnan(sl_col[p]) else (
                    entry_px * (1 - pos * s.sl_pct) if s.sl_pct else np.nan)
                target = tg_col[p] if tg_col is not None and not np.isnan(tg_col[p]) else (
                    entry_px * (1 + pos * s.target_pct) if s.target_pct else np.nan)

        # 2) intraday square-off at this bar's open
        if pos and at_sq[i] and s.intraday:
            close(i, o[i], "squareoff")

        # 3) stops / targets inside this bar
        if pos:
            if s.trail_pct:
                peak = max(peak, h[i]) if pos > 0 else min(peak, l[i])
                trail = peak * (1 - pos * s.trail_pct)
                stop = trail if np.isnan(stop) else (max(stop, trail) if pos > 0 else min(stop, trail))
            hit_sl = not np.isnan(stop) and (l[i] <= stop if pos > 0 else h[i] >= stop)
            hit_tg = not np.isnan(target) and (h[i] >= target if pos > 0 else l[i] <= target)
            if hit_sl:
                gap = o[i] < stop if pos > 0 else o[i] > stop
                close(i, o[i] if gap else stop, "trail" if s.trail_pct else "stoploss")
            elif hit_tg:
                gap = o[i] > target if pos > 0 else o[i] < target
                close(i, o[i] if gap else target, "target")

        # 4) intraday safety: never hold past the day's last bar
        if pos and s.intraday and last_of_day[i]:
            close(i, c[i], "eod")

        equity[i] = cash + (pos * qty * (c[i] - entry_px) if pos else 0.0)

    if pos:
        close(len(df) - 1, c[-1], "end_of_data")
        equity[-1] = cash
    return pd.DataFrame(trades), pd.Series(equity, index=idx, name=symbol)


def backtest(data: dict[str, pd.DataFrame], strategy, params: dict, s: Settings, trade_from=None):
    """Equal capital per symbol; returns (trades, portfolio equity).

    Signals are computed on all of `data` (so indicators can warm up) but trading
    starts at `trade_from`.
    """
    per = Settings(**{**s.__dict__, "capital": s.capital / len(data)})
    all_trades, curves = [], []
    for sym, df in data.items():
        if hasattr(strategy, "simulate"):
            t = strategy.simulate(df, params, per, sym, trade_from)
            all_trades.append(t)
            curves.append(_equity_from_trades(t, df.loc[trade_from:].index, per.capital, sym))
            continue
        sig = strategy.signals(df.copy(), params).reindex(df.index)
        if trade_from is not None:
            df, sig = df.loc[trade_from:], sig.loc[trade_from:]
        t, eq = run_symbol(df, sig, per, sym)
        all_trades.append(t)
        curves.append(eq)
    eq = pd.concat(curves, axis=1).sort_index().ffill()
    eq = eq.fillna(per.capital).sum(axis=1).rename("equity")
    trades = pd.concat(all_trades, ignore_index=True) if any(len(t) for t in all_trades) else pd.DataFrame()
    return trades, eq


def risk_qty(equity: float, entry: float, stop: float, s: Settings) -> float:
    """Units so that hitting `stop` loses s.size of equity, capped at s.max_leverage x equity."""
    qty = equity * s.size / abs(entry - stop)
    return min(qty, equity * s.max_leverage / entry)


def _equity_from_trades(t: pd.DataFrame, index: pd.DatetimeIndex, capital: float, name: str) -> pd.Series:
    eq = pd.Series(0.0, index=index)
    if len(t):
        pnl = t.groupby("exit_time").pnl.sum()
        eq = eq.add(pnl.reindex(index, fill_value=0.0), fill_value=0.0)
    return (capital + eq.cumsum()).rename(name)


def benchmark(df: pd.DataFrame, capital: float) -> pd.Series:
    return (df["close"] / df["open"].iloc[0] * capital).rename("buy_hold")


def _max_dd(eq: pd.Series) -> float:
    return float((eq / eq.cummax() - 1).min() * 100)


def _cagr(eq: pd.Series) -> float:
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    return float(((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1) * 100) if yrs > 0 else float("nan")


def stats(trades: pd.DataFrame, eq: pd.Series, bench: pd.Series | None = None) -> dict:
    daily = eq.resample("D").last().dropna()
    r = daily.pct_change().dropna()
    out = {
        "start": str(eq.index[0].date()), "end": str(eq.index[-1].date()),
        "start_equity": float(eq.iloc[0]), "end_equity": float(eq.iloc[-1]),
        "total_return_pct": float((eq.iloc[-1] / eq.iloc[0] - 1) * 100),
        "cagr_pct": _cagr(daily), "max_drawdown_pct": _max_dd(daily),
        "sharpe": float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else float("nan"),
        "n_trades": int(len(trades)),
    }
    if len(trades):
        wins, losses = trades[trades.pnl > 0], trades[trades.pnl <= 0]
        streak = run = 0
        for w in trades.sort_values("exit_time").pnl > 0:
            run = 0 if w else run + 1
            streak = max(streak, run)
        held = (trades.exit_time - trades.entry_time).sum()
        out |= {
            "win_rate_pct": float(len(wins) / len(trades) * 100),
            "profit_factor": float(wins.pnl.sum() / -losses.pnl.sum()) if losses.pnl.sum() < 0 else float("inf"),
            "avg_win_pct": float(wins.ret_pct.mean()) if len(wins) else 0.0,
            "avg_loss_pct": float(losses.ret_pct.mean()) if len(losses) else 0.0,
            "expectancy_pct": float(trades.ret_pct.mean()),
            "max_consecutive_losses": int(streak),
            "exposure_pct": float(held / (eq.index[-1] - eq.index[0]) * 100 / max(trades.symbol.nunique(), 1)),
            "exit_reasons": trades.exit_reason.value_counts().to_dict(),
        }
        if "r" in trades:
            out |= {"avg_r": float(trades.r.mean()), "total_r": float(trades.r.sum()),
                    "avg_win_r": float(wins.r.mean()) if len(wins) else 0.0,
                    "avg_loss_r": float(losses.r.mean()) if len(losses) else 0.0,
                    "best_r": float(trades.r.max()), "trades_per_month": float(
                        len(trades) / max((eq.index[-1] - eq.index[0]).days / 30.44, 1))}
            if "sl" in trades:  # cost per trade (price points) at which avg R hits zero
                risk = (trades.entry_price - trades.sl).abs()
                out["breakeven_cost_pts"] = float(trades.r.mean() / (1 / risk).mean())
    if bench is not None:
        b = bench.loc[eq.index[0] : eq.index[-1]]
        out |= {
            "bh_total_return_pct": float((b.iloc[-1] / b.iloc[0] - 1) * 100),
            "bh_cagr_pct": _cagr(b.resample("D").last().dropna()),
            "bh_max_drawdown_pct": _max_dd(b.resample("D").last().dropna()),
        }
    return out


def verdict(full: dict, oos: dict | None) -> tuple[str, list[str]]:
    """Series-wide verdict: WORKS / MIXED / FAILS, with the reasons."""
    why = []
    pf, cagr, n = full.get("profit_factor", 0), full["cagr_pct"], full["n_trades"]
    if n < 30:
        why.append(f"only {n} trades (<30) - small sample")
    if pf < 1.0 or cagr <= 0:
        why.append(f"loses money (PF {pf:.2f}, CAGR {cagr:.1f}%)")
        return "FAILS", why
    risk_adj = cagr / abs(full["max_drawdown_pct"] or 1)
    bh_risk_adj = full.get("bh_cagr_pct", 0) / abs(full.get("bh_max_drawdown_pct") or 1)
    beats_bh = cagr >= full.get("bh_cagr_pct", -1e9) or risk_adj >= bh_risk_adj
    if not beats_bh:
        why.append("worse than buy & hold, both on return and on return per unit of drawdown")
    # with <3 new trades in the OOS window (e.g. one long hold), judge it by its equity return instead
    oos_ok = oos is None or (oos.get("profit_factor", 0) >= 1.1 if oos.get("n_trades", 0) >= 3
                             else oos["total_return_pct"] >= 0)
    if not oos_ok:
        why.append("edge fades in the most recent (out-of-sample) year")
    if pf < 1.3:
        why.append(f"thin edge (PF {pf:.2f} < 1.3)")
    return ("WORKS" if not why else "MIXED"), why or ["PF >= 1.3, 30+ trades, beats buy & hold, holds up out-of-sample"]
