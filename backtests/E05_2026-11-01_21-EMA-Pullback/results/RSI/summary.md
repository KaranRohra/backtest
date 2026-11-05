# 21 EMA Pullback — + RSI FILTER — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.02 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 8.29 | 7.64 | 0.61 | 19.60 |
| CAGR % | 2.44 | 3.38 | 1.51 | 6.48 |
| Max DD % | -16.29 | -16.29 | -11.68 | -15.67 |
| Trades | 1238 | 854 | 384 | – |
| Win rate % | 49.19 | 48.83 | 50.00 | – |
| Profit factor | 1.02 | 1.03 | 1.01 | – |
| Avg trade % | 0.00 | 0.00 | -0.00 | – |
| Avg R | -0.01 | -0.02 | 0.02 | – |
| Total R | -9.12 | -18.04 | 8.92 | – |
| Max losing streak | 9 | 9 | 5 | – |
| Sharpe | 0.26 | 0.32 | 0.18 | – |

Exits: stoploss 549, target 538, squareoff 150, eod 1

## Parameter sensitivity (one at a time)

| param     | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:----------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| pull_bars | 2       | False     |              -5.36 |      -1.92 |             -17.46 |            0.98 |          49.03 |        928 |    0.01 |
| pull_bars | 3       | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| pull_bars | 5       | False     |              10.88 |       3.48 |             -18.78 |            1.02 |          49.62 |       1590 |    0    |
| trig_bars | 1       | False     |              -4.07 |      -1.61 |             -19.87 |            0.98 |          48.81 |        967 |   -0.01 |
| trig_bars | 2       | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| trig_bars | 3       | False     |               7.81 |       2.56 |             -16.27 |            1.02 |          48.88 |       1338 |   -0.01 |
| near_pct  | 0.05    | False     |               3.44 |       0.89 |             -14.8  |            1.01 |          49.44 |       1062 |   -0.01 |
| near_pct  | 0.1     | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| near_pct  | 99      | False     |               6.46 |       1.86 |             -25.97 |            1.02 |          49.46 |       1395 |   -0    |
| sl_buf    | 0       | False     |              18.71 |       5.68 |             -14.76 |            1.06 |          51.07 |       1257 |    0.03 |
| sl_buf    | 2       | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| sl_buf    | 5       | False     |               1.78 |       0.27 |             -19.42 |            1    |          47.56 |       1188 |   -0.01 |
| rr        | 1.5     | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| rr        | 2.0     | False     |             -28.48 |     -10.49 |             -33.06 |            0.91 |          41.96 |       1194 |   -0.07 |
| rr        | 3.0     | False     |             -17.3  |      -6.06 |             -34.43 |            0.95 |          36.52 |       1139 |   -0.03 |
| sl_mode   | close   | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
| sl_mode   | wick    | False     |              39.66 |      11.5  |             -11.95 |            1.12 |          42.87 |       1269 |    0.04 |
| rsi       | False   | False     |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| rsi       | True    | True      |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
