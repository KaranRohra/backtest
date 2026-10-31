# Linear Gann Levels — BTCUSDT — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.02 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 44.60 | 12.01 | 29.10 | 132.47 |
| CAGR % | 13.84 | 6.90 | 27.93 | 32.88 |
| Max DD % | -35.85 | -35.85 | -27.83 | -52.97 |
| Trades | 4138 | 2750 | 1388 | – |
| Win rate % | 50.70 | 50.36 | 51.37 | – |
| Profit factor | 1.02 | 1.01 | 1.03 | – |
| Avg trade % | 0.01 | -0.00 | 0.02 | – |
| Avg R | 0.02 | 0.01 | 0.03 | – |
| Total R | 71.09 | 33.20 | 37.90 | – |
| Max losing streak | 10 | 9 | 10 | – |
| Sharpe | 0.45 | 0.30 | 0.71 | – |

Exits: target 2058, stoploss 1976, squareoff 104

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| tol_pct    |    0.02 | False     |              41.92 |      13.13 |             -30.72 |            1.02 |          50.72 |       3947 |    0.02 |
| tol_pct    |    0.1  | True      |              44.6  |      13.84 |             -35.85 |            1.02 |          50.7  |       4138 |    0.02 |
| tol_pct    |    0.2  | False     |               9.45 |       3.75 |             -45.02 |            1    |          50.5  |       4240 |    0.01 |
| valid_bars |    1    | False     |              90.89 |      24.88 |             -35.69 |            1.03 |          51.13 |       4109 |    0.02 |
| valid_bars |    2    | True      |              44.6  |      13.84 |             -35.85 |            1.02 |          50.7  |       4138 |    0.02 |
| valid_bars |    4    | False     |              89.63 |      24.6  |             -34.97 |            1.03 |          50.97 |       4165 |    0.02 |
| rr         |    1    | True      |              44.6  |      13.84 |             -35.85 |            1.02 |          50.7  |       4138 |    0.02 |
| rr         |    1.5  | False     |              40.11 |      12.65 |             -44.35 |            1.02 |          41.31 |       3428 |    0.02 |
| rr         |    2    | False     |              57.82 |      17.21 |             -34.7  |            1.02 |          35.73 |       3037 |    0.03 |
| marubozu   |    1    | True      |              44.6  |      13.84 |             -35.85 |            1.02 |          50.7  |       4138 |    0.02 |
| marubozu   |    0    | False     |              52.64 |      15.91 |             -39.49 |            1.02 |          50.77 |       4142 |    0.02 |
| max_sl     |    1    | False     |              -3.99 |      -1.02 |             -36.36 |            1    |          50.3  |       2161 |    0.01 |
| max_sl     |    2    | True      |              44.6  |      13.84 |             -35.85 |            1.02 |          50.7  |       4138 |    0.02 |
| max_sl     |   99    | False     |             -48.12 |     -19.1  |             -61.36 |            0.98 |          49.61 |       8147 |   -0    |
