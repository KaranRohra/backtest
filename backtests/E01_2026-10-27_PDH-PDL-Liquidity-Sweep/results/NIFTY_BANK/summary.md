# PDH/PDL Liquidity Sweep — NIFTY BANK — MIXED

- thin edge (PF 1.25 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 76.75 | 46.20 | 20.89 | 27.43 |
| CAGR % | 21.26 | 21.50 | 20.97 | 8.73 |
| Max DD % | -12.23 | -10.68 | -12.23 | -18.07 |
| Trades | 894 | 594 | 300 | – |
| Win rate % | 22.71 | 23.74 | 20.67 | – |
| Profit factor | 1.25 | 1.24 | 1.26 | – |
| Avg trade % | 0.01 | 0.01 | 0.01 | – |
| Avg R | 0.08 | 0.10 | 0.05 | – |
| Total R | 75.16 | 59.01 | 16.15 | – |
| Max losing streak | 22 | 15 | 22 | – |
| Sharpe | 1.28 | 1.31 | 1.21 | – |

Exits: stoploss 689, tg1+tg2 121, tg1+cost 54, squareoff 21, tg1+squareoff 9

## Parameter sensitivity (one at a time)

| param      | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| trigger    | low     | True      |              76.75 |      21.26 |             -12.23 |            1.25 |          22.71 |        894 |    0.08 |
| trigger    | body    | False     |             187.43 |      42.55 |             -14.58 |            1.41 |          21.64 |       1012 |    0.23 |
| max_sl_pct | 0.1     | False     |              -2.13 |      -0.42 |             -21.98 |            0.99 |          19.39 |        784 |   -0.03 |
| max_sl_pct | 0.2     | True      |              76.75 |      21.26 |             -12.23 |            1.25 |          22.71 |        894 |    0.08 |
| max_sl_pct | 0.3     | False     |              77.17 |      21.36 |             -13.81 |            1.22 |          24.08 |        926 |    0.09 |
| max_sl_pct | 100     | False     |              62.49 |      17.91 |             -16.16 |            1.18 |          25.49 |        961 |    0.08 |
| pivot      | 3       | False     |              49.18 |      14.6  |             -12.29 |            1.17 |          27.45 |        918 |    0.06 |
| pivot      | 5       | True      |              76.75 |      21.26 |             -12.23 |            1.25 |          22.71 |        894 |    0.08 |
| pivot      | 10      | False     |              74.62 |      20.77 |             -12.39 |            1.23 |          19.2  |        880 |    0.07 |
| partial    | 0.5     | False     |              81.33 |      22.3  |             -12.29 |            1.26 |          22.71 |        894 |    0.09 |
| partial    | 0.8     | True      |              76.75 |      21.26 |             -12.23 |            1.25 |          22.71 |        894 |    0.08 |
| partial    | 1.0     | False     |              73.64 |      20.55 |             -12.19 |            1.24 |          22.71 |        894 |    0.08 |
