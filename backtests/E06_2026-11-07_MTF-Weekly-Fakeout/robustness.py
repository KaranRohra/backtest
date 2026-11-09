"""How much does the result depend on WHICH signals the account takes?

With 500 stocks, many setups trigger at the same moment (often the 9:15 open) and only 5 slots are free, so the
account has to pick, in a random order. This re-runs the same trades with seeds 0-19 and writes
results/NIFTY500/seeds.csv. The published result (config.json) uses seed 15, the median of these 20 runs.

    python backtests/E06_2026-11-07_MTF-Weekly-Fakeout/robustness.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.datastore import get_candles  # noqa: E402
from core.engine import Settings, benchmark, shared_capital, stats  # noqa: E402

EP = Path(__file__).resolve().parent
SEEDS = range(20)


def main():
    cfg = json.loads((EP / "config.json").read_text())
    spec = importlib.util.spec_from_file_location("strategy", EP / "strategy.py")
    strat = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(strat)
    start, end = pd.Timestamp(cfg["start"]), pd.Timestamp(cfg["end"])
    fetch_from = start - pd.Timedelta(days=cfg.get("warmup_days", 0))
    s = Settings(**cfg["settings"])
    per = Settings(**{**s.__dict__, "capital": s.capital / len(cfg["symbols"])})

    trades, index = [], None
    for sym in cfg["symbols"]:  # each stock's trades don't depend on the account, so simulate them once
        df = get_candles(sym, cfg["interval"], fetch_from, end)
        trades.append(strat.simulate(df, {**strat.PARAMS, **cfg.get("params", {})}, per, sym, start))
        idx = df.loc[start:].index
        index = idx if index is None else index.union(idx)
    trades = pd.concat([t for t in trades if len(t)], ignore_index=True)
    bh = benchmark(get_candles(cfg["benchmark"], cfg["interval"], start, end), s.capital)

    rows = []
    for seed in SEEDS:
        run = Settings(**{**s.__dict__, "extra": {**s.extra, "seed": seed}})
        t, eq = shared_capital(trades, index, run)
        st = stats(t, eq, bh)
        rows.append({"seed": seed, "trades": st["n_trades"], "win_rate_pct": st["win_rate_pct"],
                     "profit_factor": st["profit_factor"], "return_pct": st["total_return_pct"],
                     "max_drawdown_pct": st["max_drawdown_pct"]})
    out = pd.DataFrame(rows).round(2)
    out.to_csv(EP / "results" / "NIFTY500" / "seeds.csv", index=False)
    print(out.to_string(index=False))
    print("\nreturn %: min {:.1f} / median {:.1f} / max {:.1f}".format(*out.return_pct.quantile([0, .5, 1])))


if __name__ == "__main__":
    main()
