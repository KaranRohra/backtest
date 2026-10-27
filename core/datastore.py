"""Shared candle cache: fetch from Kite once, reuse for every strategy.

    from core.datastore import get_candles
    df = get_candles("NSE:NIFTY 50", "5minute", "2023-10-01", "2026-10-24")

Only two intervals are stored on disk - "day" and "minute" - under
data/<interval>/<EXCH>_<SYMBOL>.parquet. Every other intraday interval is
resampled from minute candles on load (Kite-aligned: 09:15 session start).
data/<interval>/_meta.json records which date range was already requested per
symbol, so a re-run only fetches what is missing (usually nothing).

Symbols are "EXCHANGE:TRADINGSYMBOL" as in data/kite_instruments.csv (downloaded on first use).
Futures: "NFO:NIFTY-FUT" = continuous front-month (Kite continuous=True).
"""
import json
import time
from datetime import date, datetime, timedelta
from functools import lru_cache

import pandas as pd

from core.paths import DATA, INSTRUMENTS_CSV

STORED = {"day": 2000, "minute": 60}  # max days per Kite request
RESAMPLED = {"3minute": 3, "5minute": 5, "10minute": 10, "15minute": 15, "30minute": 30, "60minute": 60}
SESSION_OPEN_MIN = 9 * 60 + 15
COLS = ["open", "high", "low", "close", "volume", "oi"]
REQUEST_GAP = 0.35  # seconds between calls, keeps us under Kite's 3 req/s
INSTRUMENTS_URL = "https://api.kite.trade/instruments"

_kite = None
_last_call = 0.0


@lru_cache(maxsize=1)
def instruments() -> pd.DataFrame:
    if not INSTRUMENTS_CSV.exists():  # Kite publishes the full instrument list without login
        INSTRUMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
        pd.read_csv(INSTRUMENTS_URL).to_csv(INSTRUMENTS_CSV, index=False)
    return pd.read_csv(INSTRUMENTS_CSV, dtype={"tradingsymbol": str, "exchange": str}, parse_dates=["expiry"])


def resolve(symbol: str) -> tuple[int, bool]:
    """'NSE:RELIANCE' -> (instrument_token, continuous)."""
    exch, ts = symbol.split(":", 1)
    inst = instruments()
    if ts.endswith("-FUT"):
        name = ts[: -len("-FUT")]
        futs = inst[(inst.exchange == exch) & (inst.name == name) & (inst.instrument_type == "FUT")]
        if futs.empty:
            raise SystemExit(f"No futures for {name} on {exch} in kite_instruments.csv")
        return int(futs.sort_values("expiry").iloc[0].instrument_token), True
    rows = inst[(inst.exchange == exch) & (inst.tradingsymbol == ts)]
    if len(rows) != 1:
        hint = inst[inst.tradingsymbol.str.contains(ts, case=False, na=False, regex=False)].head(5)
        raise SystemExit(
            f"{symbol}: {len(rows)} matches in kite_instruments.csv (need exactly 1). "
            f"Close matches: {', '.join(hint.exchange + ':' + hint.tradingsymbol) or 'none'}"
        )
    return int(rows.iloc[0].instrument_token), False


def _path(symbol: str, interval: str):
    return DATA / interval / f"{symbol.replace(':', '_').replace(' ', '_')}.parquet"


def _meta_path(interval: str):
    return DATA / interval / "_meta.json"


def _load_meta(interval: str) -> dict:
    p = _meta_path(interval)
    return json.loads(p.read_text()) if p.exists() else {}


def _save_meta(interval: str, meta: dict):
    _meta_path(interval).write_text(json.dumps(meta, indent=1, sort_keys=True))


def _fetch(token: int, interval: str, start: date, end: date, continuous: bool) -> pd.DataFrame:
    global _kite, _last_call
    if _kite is None:
        from core.kite_session import get_kite

        _kite = get_kite()
    frames, chunk = [], timedelta(days=STORED[interval] - 1)
    cur = start
    while cur <= end:
        to = min(cur + chunk, end)
        for attempt in range(4):
            wait = REQUEST_GAP - (time.time() - _last_call)
            if wait > 0:
                time.sleep(wait)
            _last_call = time.time()
            try:
                rows = _kite.historical_data(
                    token,
                    datetime.combine(cur, datetime.min.time()),
                    datetime.combine(to, datetime.max.time().replace(microsecond=0)),
                    interval,
                    continuous=continuous,
                    oi=continuous,
                )
                break
            except Exception as e:  # network blips / rate limit
                if attempt == 3:
                    raise
                print(f"  retry {attempt + 1} for {cur}..{to}: {e}")
                time.sleep(2 ** attempt)
        print(f"  fetched {interval} {cur}..{to}: {len(rows)} candles")
        if rows:
            frames.append(pd.DataFrame(rows))
        cur = to + timedelta(days=1)
    if not frames:
        return pd.DataFrame(columns=COLS)
    df = pd.concat(frames)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)  # Kite sends IST (+05:30); keep wall-clock IST
    return df.set_index("date").reindex(columns=COLS)


def _ensure(symbol: str, interval: str, start: date, end: date) -> pd.DataFrame:
    """Return stored candles for symbol, fetching any missing head/tail first."""
    path = _path(symbol, interval)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = _load_meta(interval)
    have = meta.get(symbol)
    df = pd.read_parquet(path) if path.exists() else pd.DataFrame(columns=COLS)

    # Today's candles are still forming, so "covered" never goes past yesterday.
    end = min(end, date.today())
    done_to = min(end, date.today() - timedelta(days=1))
    gaps = []
    if have is None:
        gaps.append((start, end))
    else:
        h_from, h_to = date.fromisoformat(have["from"]), date.fromisoformat(have["to"])
        if start < h_from:
            gaps.append((start, h_from - timedelta(days=1)))
        if end > h_to:
            gaps.append((h_to + timedelta(days=1), end))
    if not gaps:
        return df

    token, continuous = resolve(symbol)
    print(f"{symbol} [{interval}] fetching {', '.join(f'{a}..{b}' for a, b in gaps)}")
    new = [_fetch(token, interval, a, b, continuous) for a, b in gaps]
    df = pd.concat([df, *new])
    dupes = df.index.duplicated(keep="last")
    df = df[~dupes].sort_index()
    df.to_parquet(path)

    if have:
        start, done_to = min(start, date.fromisoformat(have["from"])), max(done_to, date.fromisoformat(have["to"]))
    meta = _load_meta(interval)
    meta[symbol] = {"from": start.isoformat(), "to": done_to.isoformat(), "token": token, "rows": len(df)}
    _save_meta(interval, meta)
    return df


def _resample(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    # Kite bars start at 09:15; offset the bin origin so e.g. 60-min bars are 09:15, 10:15, ...
    rule, offset = f"{minutes}min", f"{SESSION_OPEN_MIN % minutes}min"
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum", "oi": "last"}
    out = df.resample(rule, origin="start_day", offset=offset, label="left", closed="left").agg(agg)
    return out.dropna(subset=["open"])


def get_candles(symbol: str, interval: str, start, end=None) -> pd.DataFrame:
    """OHLCV(+oi) indexed by IST timestamp, inclusive of start..end dates."""
    start = pd.Timestamp(start).date()
    end = pd.Timestamp(end).date() if end else date.today()
    if interval in STORED:
        df = _ensure(symbol, interval, start, end)
    elif interval in RESAMPLED:
        df = _resample(_ensure(symbol, "minute", start, end), RESAMPLED[interval])
    else:
        raise ValueError(f"interval must be one of {[*STORED, *RESAMPLED]}")
    df = df.loc[str(start) : str(end) + " 23:59:59"].copy()
    if not (df["oi"].fillna(0) != 0).any():
        df = df.drop(columns="oi")
    return df.astype(float)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Pre-fetch candles into the shared cache")
    ap.add_argument("symbols", nargs="+", help='e.g. "NSE:NIFTY 50" NSE:RELIANCE NFO:NIFTY-FUT')
    ap.add_argument("--interval", default="day", choices=[*STORED, *RESAMPLED])
    ap.add_argument("--years", type=float, default=3)
    a = ap.parse_args()
    begin = date.today() - timedelta(days=int(a.years * 365.25))
    for s in a.symbols:
        d = get_candles(s, a.interval, begin)
        print(f"{s}: {len(d)} {a.interval} candles, {d.index.min()} -> {d.index.max()}")
