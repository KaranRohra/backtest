# MTF Weekly Fakeout — GOLD — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- thin edge (PF 1.26 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 7.10 | -0.51 | 7.65 | 101.97 |
| CAGR % | 2.31 | -0.25 | 7.65 | 26.37 |
| Max DD % | -5.74 | -5.74 | -2.97 | -27.69 |
| Trades | 65 | 40 | 25 | – |
| Win rate % | 47.69 | 45.00 | 52.00 | – |
| Profit factor | 1.26 | 1.24 | 1.29 | – |
| Avg trade % | 0.21 | 0.16 | 0.29 | – |
| Avg R | 0.11 | 0.09 | 0.13 | – |
| Total R | 7.00 | 3.63 | 3.37 | – |
| Max losing streak | 5 | 5 | 3 | – |
| Sharpe | 0.42 | -0.04 | 0.97 | – |

Exits: stoploss 34, target_1r+target_week 12, target_1r+breakeven 11, target_1r+reversed 6, target_1r+time 1, reversed 1

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| pivot      |     1   | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| pivot      |     2   | False     |               4.81 |       1.58 |              -5.91 |            1.19 |          47.46 |         59 |    0.09 |
| sl_buf_pct |     0   | False     |              10.04 |       3.24 |              -5.87 |            1.4  |          52.31 |         65 |    0.12 |
| sl_buf_pct |     0.1 | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| sl_buf_pct |     0.3 | False     |              10.25 |       3.31 |              -6.24 |            1.39 |          51.61 |         62 |    0.13 |
| partial    |     0   | False     |              19.59 |       6.14 |              -5.22 |            1.6  |          36.92 |         65 |    0.28 |
| partial    |     0.5 | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| min_room_r |     0   | False     |               8.15 |       2.64 |              -3.96 |            1.26 |          50    |         80 |    0.1  |
| min_room_r |     1   | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| max_days   |     5   | False     |               4.44 |       1.46 |              -5.95 |            1.17 |          44.62 |         65 |    0.07 |
| max_days   |    10   | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| max_days   |    20   | False     |               6.88 |       2.24 |              -5.74 |            1.25 |          47.69 |         65 |    0.1  |
| setup_days |     2   | False     |               9.65 |       3.12 |              -3.31 |            1.65 |          54.76 |         42 |    0.27 |
| setup_days |     4   | True      |               7.1  |       2.31 |              -5.74 |            1.26 |          47.69 |         65 |    0.11 |
| setup_days |     5   | False     |               4.87 |       1.6  |              -6.93 |            1.16 |          46.48 |         71 |    0.06 |
