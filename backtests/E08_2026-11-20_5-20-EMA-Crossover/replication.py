"""Replication helper: list E08 setups/trades for a date window (NIFTY / BANK NIFTY, 5-min).

    .venv/bin/python backtests/E08_2026-11-20_5-20-EMA-Crossover/replication.py "NSE:NIFTY 50" 2025-06-02 2025-06-13 [k=v ...]
"""
import importlib.util, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, ".")
from core.datastore import get_candles
from core.engine import Settings
ep = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("st", ep / "strategy.py"); st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
sym, a, b, *kv = sys.argv[1:]
p = dict(st.PARAMS)
for x in kv:
    k, v = x.split("="); p[k] = type(p[k])(v) if not isinstance(p[k], bool) else v == "True"
df = get_candles(sym, "minute", pd.Timestamp(a) - pd.Timedelta(days=7), b)
s = Settings(capital=100000, sizing="risk", size=0.01, max_leverage=5, intraday=True, squareoff="15:20")
t = st.simulate(df, p, s, sym, trade_from=a)
pd.set_option("display.width", 250)
if len(t):
    t["day"] = t.entry_time.dt.date
    print(t[["day", "side", "cross_time", "cross_n", "pullback_time", "entry_time", "entry_price", "sl", "target",
             "exit_time", "exit_reason", "r", "halved"]].round(1).to_string(index=False))
