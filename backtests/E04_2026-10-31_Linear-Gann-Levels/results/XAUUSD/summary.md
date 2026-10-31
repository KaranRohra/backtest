# Linear Gann Levels — XAUUSD — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- thin edge (PF 1.06 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 16.65 | -10.61 | 30.49 | 101.97 |
| CAGR % | 5.27 | -5.46 | 31.84 | 26.37 |
| Max DD % | -21.74 | -21.74 | -10.83 | -27.69 |
| Trades | 735 | 399 | 336 | – |
| Win rate % | 51.56 | 49.62 | 53.87 | – |
| Profit factor | 1.06 | 0.93 | 1.18 | – |
| Avg trade % | 0.00 | -0.01 | 0.01 | – |
| Avg R | 0.03 | -0.02 | 0.09 | – |
| Total R | 19.90 | -8.69 | 28.59 | – |
| Max losing streak | 9 | 7 | 9 | – |
| Sharpe | 0.39 | -0.37 | 1.52 | – |

Exits: target 339, stoploss 320, squareoff 72, eod 4

## Parameter sensitivity (one at a time)

| param      |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| tol_pct    |    0.02 | False     |              14.35 |       4.57 |             -17.66 |            1.06 |          51.3  |        579 |    0.03 |
| tol_pct    |    0.1  | True      |              16.65 |       5.27 |             -21.74 |            1.06 |          51.56 |        735 |    0.03 |
| tol_pct    |    0.2  | False     |              27.43 |       8.41 |             -14.91 |            1.07 |          51.89 |        952 |    0.03 |
| valid_bars |    1    | False     |              21.42 |       6.68 |             -20.13 |            1.08 |          51.96 |        664 |    0.03 |
| valid_bars |    2    | True      |              16.65 |       5.27 |             -21.74 |            1.06 |          51.56 |        735 |    0.03 |
| valid_bars |    4    | False     |              19.4  |       6.09 |             -15.78 |            1.06 |          51.87 |        777 |    0.03 |
| rr         |    1    | True      |              16.65 |       5.27 |             -21.74 |            1.06 |          51.56 |        735 |    0.03 |
| rr         |    1.5  | False     |              21.49 |       6.7  |             -26.81 |            1.07 |          43.37 |        664 |    0.03 |
| rr         |    2    | False     |              33.07 |       9.99 |             -24.96 |            1.1  |          39.03 |        638 |    0.05 |
| marubozu   |    1    | True      |              16.65 |       5.27 |             -21.74 |            1.06 |          51.56 |        735 |    0.03 |
| marubozu   |    0    | False     |              19.02 |       5.97 |             -22.51 |            1.06 |          51.71 |        733 |    0.03 |
| max_sl     |    1    | False     |              14.18 |       4.52 |             -19.65 |            1.07 |          51.79 |        502 |    0.03 |
| max_sl     |    2    | True      |              16.65 |       5.27 |             -21.74 |            1.06 |          51.56 |        735 |    0.03 |
| max_sl     |   99    | False     |               6.07 |       1.98 |             -26.82 |            1.02 |          50.33 |        896 |    0.01 |
