# Linear Gann Levels — NIFTY 50 — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.05 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 11.06 | 13.04 | -1.76 | 19.60 |
| CAGR % | 3.56 | 6.34 | -1.75 | 6.48 |
| Max DD % | -14.73 | -12.82 | -9.36 | -15.67 |
| Trades | 602 | 377 | 225 | – |
| Win rate % | 50.66 | 50.93 | 50.22 | – |
| Profit factor | 1.05 | 1.09 | 0.98 | – |
| Avg trade % | 0.01 | 0.02 | 0.00 | – |
| Avg R | 0.02 | 0.03 | -0.01 | – |
| Total R | 11.63 | 13.13 | -1.50 | – |
| Max losing streak | 8 | 8 | 7 | – |
| Sharpe | 0.37 | 0.62 | -0.08 | – |

Exits: target 226, stoploss 214, squareoff 161, eod 1

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| tol_pct    |    0.02 | False     |               4.98 |       1.63 |             -15.26 |            1.03 |          49.65 |        431 |    0.01 |
| tol_pct    |    0.1  | True      |              11.06 |       3.56 |             -14.73 |            1.05 |          50.66 |        602 |    0.02 |
| tol_pct    |    0.2  | False     |              -2.54 |      -0.85 |             -24.39 |            0.99 |          50.12 |        826 |    0    |
| valid_bars |    1    | False     |              13.21 |       4.22 |             -14.24 |            1.07 |          50.95 |        526 |    0.03 |
| valid_bars |    2    | True      |              11.06 |       3.56 |             -14.73 |            1.05 |          50.66 |        602 |    0.02 |
| valid_bars |    4    | False     |              14.77 |       4.7  |             -16.24 |            1.06 |          50.31 |        646 |    0.02 |
| rr         |    1    | True      |              11.06 |       3.56 |             -14.73 |            1.05 |          50.66 |        602 |    0.02 |
| rr         |    1.5  | False     |              19.41 |       6.09 |             -13.06 |            1.08 |          46.7  |        561 |    0.04 |
| rr         |    2    | False     |               6.02 |       1.97 |             -19.31 |            1.02 |          43.89 |        540 |    0.01 |
| marubozu   |    1    | True      |              11.06 |       3.56 |             -14.73 |            1.05 |          50.66 |        602 |    0.02 |
| marubozu   |    0    | False     |               9.61 |       3.11 |             -14.73 |            1.04 |          50.43 |        575 |    0.02 |
| max_sl     |    1    | False     |               4.91 |       1.61 |             -11.85 |            1.03 |          50.52 |        485 |    0.01 |
| max_sl     |    2    | True      |              11.06 |       3.56 |             -14.73 |            1.05 |          50.66 |        602 |    0.02 |
| max_sl     |   99    | False     |               7.36 |       2.4  |             -15.21 |            1.03 |          50.57 |        615 |    0.01 |
