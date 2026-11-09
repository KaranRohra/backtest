# MTF Weekly Fakeout — MIDDLE RUN — FAILS

- loses money (PF 1.00, CAGR 0.3%)

Period 2023-10-26 → 2026-10-26 · 15minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | -0.52 | 0.94 | -1.44 | 30.41 |
| CAGR % | 0.30 | 1.19 | -1.14 | 9.27 |
| Max DD % | -20.99 | -16.62 | -14.00 | -18.76 |
| Trades | 1353 | 910 | 443 | – |
| Win rate % | 50.26 | 50.00 | 50.79 | – |
| Profit factor | 1.00 | 1.01 | 0.98 | – |
| Avg trade % | 0.01 | 0.02 | -0.01 | – |
| Avg R | 0.02 | 0.00 | 0.05 | – |
| Total R | 25.38 | 3.73 | 21.64 | – |
| Max losing streak | 9 | 9 | 6 | – |
| Sharpe | 0.09 | 0.16 | -0.03 | – |

Exits: stoploss 641, target_1r+breakeven 284, target_1r+target_week 279, reversed 61, target_1r+reversed 40, target_1r+time 21, time 20, eod 5, target_week+target_1r 2

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| pivot      |     1   | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| pivot      |     2   | False     |              -1.18 |      -0.26 |             -17.9  |            1    |          49.08 |       1298 |   -0.01 |
| sl_buf_pct |     0   | False     |              13.55 |       4.85 |             -13.22 |            1.04 |          50.93 |       1404 |    0.04 |
| sl_buf_pct |     0.1 | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| sl_buf_pct |     0.3 | False     |             -20.74 |      -7.3  |             -28.4  |            0.93 |          49.47 |       1237 |   -0    |
| partial    |     0   | False     |               9.2  |       3.41 |             -16.68 |            1.03 |          35.52 |       1160 |    0.04 |
| partial    |     0.5 | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| min_room_r |     0   | False     |              31.98 |      10.28 |             -11.15 |            1.09 |          55.43 |       1326 |    0.07 |
| min_room_r |     1   | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| max_days   |     5   | False     |              11.81 |       4.28 |             -19.08 |            1.03 |          50.39 |       1538 |    0.04 |
| max_days   |    10   | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| max_days   |    20   | False     |              -9.93 |      -2.99 |             -23.32 |            0.97 |          48.67 |       1319 |   -0    |
| setup_days |     2   | False     |              35.34 |      11.38 |             -11.35 |            1.13 |          52.4  |       1084 |    0.07 |
| setup_days |     4   | True      |              -0.52 |       0.3  |             -20.99 |            1    |          50.26 |       1353 |    0.02 |
| setup_days |     5   | False     |              -2.03 |      -0.29 |             -22.35 |            0.99 |          50.15 |       1350 |    0.05 |
