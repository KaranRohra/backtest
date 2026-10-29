# Backtest Series

Trading strategies from YouTube, tested on real market data: Indian indices and gold.

Each episode takes one strategy from a YouTube video, writes its rules down as exactly as the video allows, and backtests it on 1–3 years of real data: NSE prices from Zerodha Kite, and spot gold from Dukascopy. Everything is here: the code, every trade, and the assumptions made where the video was vague. You can check the work or run it yourself.

## Leaderboard

<!-- leaderboard:start -->
| # | Strategy | Creator | Market | Trades | Win rate | Profit factor | Return | Buy & hold | Max DD | Verdict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| E01 | [PDH/PDL Liquidity Sweep](backtests/E01_2026-10-27_PDH-PDL-Liquidity-Sweep) | Stock Learners (Gautam Jha) | NIFTY 50 · 1-min | 939 | 22% | 1.09 | +20.7% | +19.6% | -23.7% | ⚠️ Mixed |
| E01 | [PDH/PDL Liquidity Sweep](backtests/E01_2026-10-27_PDH-PDL-Liquidity-Sweep) | Stock Learners (Gautam Jha) | NIFTY BANK · 1-min | 894 | 23% | 1.25 | +76.8% | +27.4% | -12.2% | ⚠️ Mixed |
| E01 | [PDH/PDL Liquidity Sweep](backtests/E01_2026-10-27_PDH-PDL-Liquidity-Sweep) | Stock Learners (Gautam Jha) | Gold (XAUUSD) · 1-min | 1136 | 21% | 1.02 | +6.1% | +102.0% | -25.8% | ⚠️ Mixed |
| E02 | [5 EMA Alert Candle](backtests/E02_2026-10-29_5-EMA-Alert-Candle) | Power of Stocks (Subhasish Pani) | NIFTY 50 · 5 & 15-min | 2990 | 30% | 1.04 | +54.5% | +19.6% | -32.3% | ⚠️ Mixed |
| E02 | [5 EMA Alert Candle](backtests/E02_2026-10-29_5-EMA-Alert-Candle) | Power of Stocks (Subhasish Pani) | NIFTY BANK · 5 & 15-min | 2856 | 29% | 0.99 | -11.0% | +27.4% | -34.9% | ❌ Fails |
<!-- leaderboard:end -->

All results are **before costs** (brokerage, STT, slippage). Each backtest's README says how much those costs would change the result. Verdict rules: [methodology](docs/methodology.md#verdict-scale).

## What's in each backtest

```
backtests/E01_<date>_<Strategy-Name>/
  README.md        the video, its rules, our assumptions, results, limitations
  strategy.py      the rules as code
  config.json      instruments, period, position sizing, parameters tested
  results/         summary.md · trades.csv (every trade) · equity.csv · stats.json · sensitivity.csv
  images/          result cards (equity + stats, drawdown)
```

## Run it yourself

You need Python 3.11+. Market data isn't included in this repo; it's downloaded on first run.
- **Gold (XAUUSD):** free from Dukascopy, no account needed.
- **NSE stocks and indices:** need a [Kite Connect](https://developers.kite.trade) app with historical data access, because the data comes from your own Zerodha account.

```bash
git clone https://github.com/KaranRohra/backtest.git && cd backtest
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add KITE_API_KEY and KITE_API_SECRET (only needed for NSE data)

python run.py E01_2026-10-27_PDH-PDL-Liquidity-Sweep --no-video
python -m tests.test_engine     # engine checks: fills, no lookahead, stops, square-off
```

- **Login:** the first run prints a Kite login link. Paste the `request_token` from the page you land on. The session is cached for the day.
- **Data:** candles are downloaded once into `data/` and reused by every backtest.

**Test your own idea:** copy `backtests/_TEMPLATE` to a new folder, write the rules in `strategy.py`, set instruments and dates in `config.json`, then `python run.py <folder> --no-video`.

## How the engine works

Details are in [docs/methodology.md](docs/methodology.md). In short:
- **No lookahead:** a signal on a candle's close fills at the next candle's open.
- **Conservative fills:** stops are checked inside each candle. If a stop and a target are both hit in the same candle, the stop counts.
- **Intraday:** positions are squared off at 15:15.
- **Robustness:** each backtest also reports the last 12 months on their own (out-of-sample) and a parameter-sensitivity table, so a result that only works at one exact setting is easy to spot.

## Disclaimer

For education only. This is not investment advice and not a recommendation to trade any strategy. Backtests are simulations: real trading has costs, slippage and execution limits these results don't include. Strategies are credited to their creators, and testing one is not a comment on the creator.
