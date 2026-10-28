# Methodology

## Data
- **Sources** (`core/datastore.py`):
  - **NSE:** the Zerodha Kite historical API. Symbols are `EXCHANGE:TRADINGSYMBOL`, e.g. `NSE:RELIANCE`, `NSE:NIFTY 50`, `NSE:NIFTY BANK`. `NFO:NIFTY-FUT` means continuous front-month futures (daily candles only). Timestamps are IST.
  - **Spot gold / forex:** Dukascopy Bank's free historical feed (bid prices), as `DUKAS:XAUUSD`. Timestamps are UTC. Gold's trading day runs from one 17:00 New York close to the next, the usual broker day.
- **Storage:** only daily and 1-minute candles are stored (`data/day/`, `data/minute/`, parquet). 3/5/10/15/30/60-minute candles are built from 1-minute data, aligned to the 09:15 open like Kite's own charts.
- **Caching:** requests are chunked to Kite's per-request limits and cached, so a re-run downloads only new days.
- **Limits:**
  - Kite has no data for expired option contracts, and continuous futures are daily-only.
  - Option strategies can only be approximated on the underlying index or stock.
  - Multi-year intraday tests use the NSE spot index, or spot gold from Dukascopy.

## Execution rules (`core/engine.py`)
- **No lookahead:** a signal decided on a candle's close fills at the **next candle's open**. A test checks that changing future prices never changes past trades.
- **Stops and targets:** checked inside each candle.
  - If the candle opens beyond the stop, the fill is at the open (gap).
  - If a stop and a target are both inside one candle, the **stop counts first**.
- **Intraday:** no new entries after the square-off time (default 15:15). Open positions exit at 15:15 and are never held overnight.
- **Custom strategies:** some strategies need stop-entry orders, partial profit booking or daily trade limits. These implement `simulate()` with the same conservative rules (see E01's `strategy.py`).
- **Costs:** zero. Every result is labelled "before costs". For intraday strategies, the backtest reports the **cost per trade at which the profit disappears**, so you can compare it with real charges.

## Position sizing
- **Default:** 100% of equity per trade (`"sizing": "percent"`).
- **Risk-based** (`"sizing": "risk"`): each trade risks a fixed fraction of equity (e.g. 1%) based on the stop distance, capped at a maximum leverage (e.g. 5×, roughly index-futures margin).
- **R:** the amount risked on a trade. Results are also reported in R, so the edge is visible independent of sizing.

## Statistics
- **Return / CAGR / max drawdown:** measured on daily closes, the same way for the strategy and for buy & hold of the same instrument.
- **Trade stats:** win rate, profit factor (₹ won per ₹1 lost), average win/loss, longest losing streak, exposure.
- **In-sample vs out-of-sample:** the last 12 months are reported separately. An edge that disappears there is a warning sign.
- **Sensitivity:** each tunable rule is varied one at a time (`results/*/sensitivity.csv`). A strategy that only works at one exact setting is probably curve-fit.

## Verdict scale
| Verdict | Rule |
|---|---|
| ✅ Works | profit factor ≥ 1.3, at least 30 trades, beats buy & hold (on CAGR, or on CAGR per unit of max drawdown), and the last 12 months hold up |
| ⚠️ Mixed | profitable, but at least one of the above fails |
| ❌ Fails | profit factor < 1 or CAGR ≤ 0 |

The verdict is computed before costs. Read the cost note in each backtest's README before drawing conclusions.
