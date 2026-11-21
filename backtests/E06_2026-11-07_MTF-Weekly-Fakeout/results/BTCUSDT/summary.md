# MTF Weekly Fakeout — BITCOIN — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- thin edge (PF 1.18 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 6.48 | 3.02 | 3.36 | 132.47 |
| CAGR % | 2.12 | 1.50 | 3.36 | 32.88 |
| Max DD % | -7.25 | -7.25 | -5.74 | -52.97 |
| Trades | 75 | 50 | 25 | – |
| Win rate % | 49.33 | 46.00 | 56.00 | – |
| Profit factor | 1.18 | 1.12 | 1.33 | – |
| Avg trade % | 0.06 | -0.09 | 0.36 | – |
| Avg R | 0.08 | 0.06 | 0.10 | – |
| Total R | 5.64 | 3.05 | 2.59 | – |
| Max losing streak | 4 | 4 | 2 | – |
| Sharpe | 0.31 | 0.22 | 0.53 | – |

Exits: stoploss 37, target_1r+breakeven 16, target_1r+target_week 15, target_1r+reversed 4, reversed 2, time 1

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| pivot      |     1   | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| pivot      |     2   | False     |               8.46 |       2.74 |              -6.21 |            1.26 |          50    |         68 |    0.11 |
| sl_buf_pct |     0   | False     |              10.79 |       3.47 |              -7.06 |            1.31 |          51.32 |         76 |    0.12 |
| sl_buf_pct |     0.1 | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| sl_buf_pct |     0.3 | False     |              18.6  |       5.85 |              -4.07 |            1.54 |          54.67 |         75 |    0.23 |
| partial    |     0   | False     |               8.93 |       2.89 |             -12.18 |            1.18 |          30.67 |         75 |    0.13 |
| partial    |     0.5 | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| min_room_r |     0   | False     |               5.63 |       1.84 |              -7.4  |            1.14 |          48.81 |         84 |    0.06 |
| min_room_r |     1   | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| max_days   |     5   | False     |               5.66 |       1.85 |              -6.9  |            1.16 |          49.33 |         75 |    0.06 |
| max_days   |    10   | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| max_days   |    20   | False     |               7.39 |       2.41 |              -7.25 |            1.21 |          50.67 |         75 |    0.09 |
| setup_days |     2   | False     |              10.13 |       3.27 |              -4.99 |            1.43 |          52    |         50 |    0.18 |
| setup_days |     4   | True      |               6.48 |       2.12 |              -7.25 |            1.18 |          49.33 |         75 |    0.08 |
| setup_days |     5   | False     |               4.14 |       1.36 |              -7.55 |            1.1  |          50.59 |         85 |    0.04 |
