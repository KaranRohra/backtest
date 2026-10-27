"""Offline checks for the engine and resampler (no Kite needed).

    .venv/bin/python -m tests.test_engine
"""
import numpy as np
import pandas as pd

from core.datastore import _resample
from core.engine import Settings, backtest, run_symbol, stats


def bars(closes, start="2024-01-01", freq="D", spread=1.0):
    idx = pd.date_range(start, periods=len(closes), freq=freq)
    c = np.asarray(closes, float)
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + spread, "low": np.minimum(o, c) - spread,
                         "close": c, "volume": 0.0}, index=idx)


def sig(df, entries=(), exits=(), short=False):
    s = pd.DataFrame(False, index=df.index, columns=["entry_long", "exit_long", "entry_short", "exit_short"])
    for i in entries:
        s.iloc[i, 2 if short else 0] = True
    for i in exits:
        s.iloc[i, 3 if short else 1] = True
    return s


def test_next_bar_open_fill():
    df = bars([100, 101, 102, 103, 104, 105])
    t, eq = run_symbol(df, sig(df, [1], [3]), Settings(capital=1000), "X")
    assert len(t) == 1
    assert t.entry_price[0] == df.open.iloc[2] and t.exit_price[0] == df.open.iloc[4]
    assert t.entry_time[0] == df.index[2]


def test_no_lookahead():
    """Changing future prices must not change past trades or equity."""
    rng = np.random.default_rng(1)
    c = 100 + rng.standard_normal(300).cumsum()
    df1 = bars(c)
    c2 = c.copy()
    c2[200:] += 50
    df2 = bars(c2)

    class S:
        @staticmethod
        def signals(d, p):
            ma = d.close.rolling(10).mean()
            up = d.close > ma
            return pd.DataFrame({"entry_long": up & ~up.shift(1, fill_value=False),
                                 "exit_long": ~up & up.shift(1, fill_value=False)})

    t1, e1 = backtest({"X": df1}, S, {}, Settings())
    t2, e2 = backtest({"X": df2}, S, {}, Settings())
    cut = df1.index[199]
    assert e1.loc[:cut].equals(e2.loc[:cut])
    closed = t1[t1.exit_time <= cut]
    assert closed.reset_index(drop=True).equals(t2[t2.exit_time <= cut].reset_index(drop=True))


def test_stoploss_and_gap():
    df = bars([100, 100, 100, 95, 80, 80], spread=0.5)
    t, _ = run_symbol(df, sig(df, [0]), Settings(capital=1000, sl_pct=0.02), "X")
    assert t.exit_reason[0] == "stoploss" and t.exit_price[0] == 98.0  # intrabar stop
    df = bars([100, 100, 100, 100, 90], spread=0.1)
    df.loc[df.index[-1], "open"] = 90  # gap through the stop
    t, _ = run_symbol(df, sig(df, [0]), Settings(capital=1000, sl_pct=0.02), "X")
    assert t.exit_price[0] == 90 and t.exit_reason[0] == "stoploss"


def test_short_pnl():
    df = bars([100, 100, 90, 80, 80])
    t, eq = run_symbol(df, sig(df, [0], [2], short=True), Settings(capital=1000), "X")
    assert t.side[0] == "SHORT" and t.pnl[0] > 0 and eq.iloc[-1] > 1000


def test_intraday_squareoff():
    idx = pd.date_range("2024-01-01 09:15", "2024-01-01 15:25", freq="5min")
    df = bars(np.linspace(100, 110, len(idx)))
    df.index = idx
    t, _ = run_symbol(df, sig(df, [2]), Settings(capital=1000, intraday=True), "X")
    assert t.exit_reason[0] == "squareoff" and t.exit_time[0].strftime("%H:%M") == "15:15"


def test_intraday_no_overnight():
    idx = pd.date_range("2024-01-01 09:15", "2024-01-01 14:00", freq="15min").append(
        pd.date_range("2024-01-02 09:15", "2024-01-02 15:15", freq="15min"))
    df = bars(np.full(len(idx), 100.0))
    df.index = idx
    t, _ = run_symbol(df, sig(df, [5]), Settings(capital=1000, intraday=True), "X")
    assert t.exit_reason[0] == "eod" and t.exit_time[0].date() == idx[0].date()


def test_resample_alignment():
    idx = pd.date_range("2024-01-01 09:15", "2024-01-01 15:29", freq="1min")
    df = pd.DataFrame({"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "volume": 1.0, "oi": 0.0}, index=idx)
    h = _resample(df, 60)
    assert [t.strftime("%H:%M") for t in h.index] == ["09:15", "10:15", "11:15", "12:15", "13:15", "14:15", "15:15"]
    assert h.volume.iloc[0] == 60 and h.volume.iloc[-1] == 15
    assert _resample(df, 5).index[0].strftime("%H:%M") == "09:15" and len(_resample(df, 5)) == 75
    assert _resample(df, 10).index[1].strftime("%H:%M") == "09:25"


def test_stats():
    df = bars([100, 110, 121, 110, 121, 133.1])
    t, eq = run_symbol(df, sig(df, [0, 3], [1, 4]), Settings(capital=1000), "X")
    st = stats(t, eq)
    assert st["n_trades"] == 2 and st["win_rate_pct"] == 100


if __name__ == "__main__":
    tests = [f for n, f in sorted(globals().items()) if n.startswith("test_")]
    for f in tests:
        f()
        print(f"ok  {f.__name__}")
    print(f"{len(tests)} passed")
