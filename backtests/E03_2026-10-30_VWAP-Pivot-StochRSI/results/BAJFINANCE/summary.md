# VWAP + Pivots + Stoch RSI — BAJFINANCE — MIXED

- thin edge (PF 1.17 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 124.33 | 68.75 | 32.93 | 20.10 |
| CAGR % | 30.99 | 30.11 | 34.41 | 7.43 |
| Max DD % | -18.64 | -18.64 | -15.85 | -26.50 |
| Trades | 1003 | 659 | 344 | – |
| Win rate % | 43.47 | 43.70 | 43.02 | – |
| Profit factor | 1.17 | 1.17 | 1.16 | – |
| Avg trade % | 0.04 | 0.04 | 0.05 | – |
| Avg R | 0.09 | 0.09 | 0.09 | – |
| Total R | 88.03 | 56.91 | 31.12 | – |
| Max losing streak | 10 | 10 | 7 | – |
| Sharpe | 1.37 | 1.36 | 1.42 | – |

Exits: stoploss 440, squareoff 320, target 211, eod 32

## Parameter sensitivity (one at a time)

| param       | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| sl          | pct     | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
| sl          | vwap    | False     |             -36.86 |     -14.34 |             -50.5  |            0.89 |          18.91 |       1174 |   -0.26 |
| stoch       | True    | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
| stoch       | False   | False     |              64.56 |      18.03 |             -20.98 |            1.1  |          41.92 |       1052 |    0.05 |
| entry       | break   | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
| entry       | close   | False     |              90.58 |      23.86 |             -17.3  |            1.17 |          42.51 |        894 |    0.08 |
| target_pct  | 0.75    | False     |              78.55 |      21.39 |             -18.57 |            1.12 |          45.98 |        994 |    0.06 |
| target_pct  | 1.0     | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
| target_pct  | 1.5     | False     |             116.6  |      29.46 |             -23.31 |            1.17 |          42.06 |       1008 |    0.09 |
| first_entry | 09:20   | False     |              -6.56 |      -2.88 |             -35.34 |            0.99 |          36.87 |       1169 |    0    |
| first_entry | 10:45   | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
| max_trades  | 1       | False     |              95.21 |      25.39 |             -17.49 |            1.2  |          43.11 |        726 |    0.1  |
| max_trades  | 2       | True      |             124.33 |      30.99 |             -18.64 |            1.17 |          43.47 |       1003 |    0.09 |
