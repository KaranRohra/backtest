# 21 EMA Pullback — AS TAUGHT — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.04 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 13.76 | 3.76 | 9.63 | 19.60 |
| CAGR % | 4.14 | 1.50 | 10.14 | 6.48 |
| Max DD % | -14.99 | -14.99 | -10.14 | -15.67 |
| Trades | 1372 | 945 | 427 | – |
| Win rate % | 49.42 | 48.68 | 51.05 | – |
| Profit factor | 1.04 | 1.01 | 1.08 | – |
| Avg trade % | 0.00 | 0.00 | 0.00 | – |
| Avg R | -0.00 | -0.03 | 0.06 | – |
| Total R | -1.74 | -26.62 | 24.88 | – |
| Max losing streak | 10 | 10 | 5 | – |
| Sharpe | 0.37 | 0.18 | 0.79 | – |

Exits: stoploss 608, target 601, squareoff 162, eod 1

## Parameter sensitivity (one at a time)

| param     | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:----------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| pull_bars | 2       | False     |               4.11 |       1.25 |             -19.48 |            1.01 |          49.81 |       1062 |    0.02 |
| pull_bars | 3       | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| pull_bars | 5       | False     |              14.14 |       4.49 |             -20.81 |            1.03 |          49.73 |       1695 |    0    |
| trig_bars | 1       | False     |              -2.52 |      -1.09 |             -19.14 |            0.99 |          49.03 |       1085 |   -0.01 |
| trig_bars | 2       | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| trig_bars | 3       | False     |               5.82 |       1.92 |             -18    |            1.01 |          48.92 |       1480 |   -0.01 |
| near_pct  | 0.05    | False     |               7    |       2.03 |             -12.16 |            1.02 |          49.54 |       1197 |   -0    |
| near_pct  | 0.1     | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| near_pct  | 99      | False     |              13.85 |       4.17 |             -26.8  |            1.03 |          49.71 |       1527 |    0.01 |
| sl_buf    | 0       | False     |              38.17 |      11.17 |             -11.32 |            1.1  |          51.79 |       1398 |    0.06 |
| sl_buf    | 2       | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| sl_buf    | 5       | False     |               9.7  |       2.8  |             -17.73 |            1.02 |          48.05 |       1311 |   -0    |
| rr        | 1.5     | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| rr        | 2.0     | False     |             -19.35 |      -6.84 |             -30.05 |            0.95 |          42.55 |       1316 |   -0.05 |
| rr        | 3.0     | False     |              -9.45 |      -3.18 |             -29.65 |            0.98 |          36.66 |       1252 |   -0.02 |
| sl_mode   | close   | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| sl_mode   | wick    | False     |              37.33 |      10.88 |              -7.92 |            1.1  |          42.71 |       1426 |    0.03 |
| rsi       | False   | True      |              13.76 |       4.14 |             -14.99 |            1.04 |          49.42 |       1372 |   -0    |
| rsi       | True    | False     |               8.29 |       2.44 |             -16.29 |            1.02 |          49.19 |       1238 |   -0.01 |
