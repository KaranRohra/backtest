# VWAP + Pivots + Stoch RSI — HDFCBANK — MIXED

- thin edge (PF 1.12 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 57.26 | 19.76 | 31.30 | -7.29 |
| CAGR % | 15.75 | 8.71 | 31.01 | -2.05 |
| Max DD % | -22.42 | -22.42 | -8.91 | -32.13 |
| Trades | 924 | 607 | 317 | – |
| Win rate % | 48.48 | 47.94 | 49.53 | – |
| Profit factor | 1.12 | 1.07 | 1.22 | – |
| Avg trade % | 0.03 | 0.02 | 0.05 | – |
| Avg R | 0.05 | 0.03 | 0.09 | – |
| Total R | 49.88 | 20.88 | 29.01 | – |
| Max losing streak | 8 | 8 | 7 | – |
| Sharpe | 0.95 | 0.59 | 1.57 | – |

Exits: squareoff 472, stoploss 305, target 102, eod 45

## Parameter sensitivity (one at a time)

| param       | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| sl          | pct     | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
| sl          | vwap    | False     |             -21.48 |      -8.19 |             -52.49 |            0.94 |          22.11 |       1167 |   -0.15 |
| stoch       | True    | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
| stoch       | False   | False     |              55.99 |      15.44 |             -25.64 |            1.11 |          48.17 |        955 |    0.05 |
| entry       | break   | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
| entry       | close   | False     |              34.83 |      10.11 |             -34.56 |            1.09 |          47.9  |        856 |    0.04 |
| target_pct  | 0.75    | False     |              74.83 |      19.87 |             -15.12 |            1.16 |          49.35 |        920 |    0.07 |
| target_pct  | 1.0     | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
| target_pct  | 1.5     | False     |              59.69 |      16.35 |             -23.81 |            1.13 |          48.11 |        925 |    0.06 |
| first_entry | 09:20   | False     |              72.02 |      19.72 |             -27.62 |            1.1  |          44.08 |       1055 |    0.06 |
| first_entry | 10:45   | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
| max_trades  | 1       | False     |              30.19 |       8.69 |             -23.72 |            1.09 |          47.56 |        738 |    0.04 |
| max_trades  | 2       | True      |              57.26 |      15.75 |             -22.42 |            1.12 |          48.48 |        924 |    0.05 |
