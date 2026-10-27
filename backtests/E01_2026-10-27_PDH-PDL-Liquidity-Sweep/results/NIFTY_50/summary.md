# PDH/PDL Liquidity Sweep — NIFTY 50 — MIXED

- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.09 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 20.67 | 15.94 | 4.07 | 19.60 |
| CAGR % | 6.71 | 8.08 | 3.87 | 6.48 |
| Max DD % | -23.74 | -21.22 | -8.91 | -15.67 |
| Trades | 939 | 597 | 342 | – |
| Win rate % | 22.15 | 21.44 | 23.39 | – |
| Profit factor | 1.09 | 1.10 | 1.06 | – |
| Avg trade % | 0.00 | 0.01 | 0.00 | – |
| Avg R | 0.08 | 0.08 | 0.09 | – |
| Total R | 77.47 | 46.97 | 30.50 | – |
| Max losing streak | 17 | 17 | 17 | – |
| Sharpe | 0.60 | 0.68 | 0.41 | – |

Exits: stoploss 731, tg1+tg2 119, tg1+cost 61, squareoff 18, tg1+squareoff 10

## Parameter sensitivity (one at a time)

| param      | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:-----------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| trigger    | low     | True      |              20.67 |       6.71 |             -23.74 |            1.09 |          22.15 |        939 |    0.08 |
| trigger    | body    | False     |              30.73 |       9.55 |             -16.48 |            1.12 |          20.15 |       1047 |    0.08 |
| max_sl_pct | 0.1     | False     |              32.47 |      10.08 |             -20.92 |            1.16 |          20.98 |        896 |    0.1  |
| max_sl_pct | 0.2     | True      |              20.67 |       6.71 |             -23.74 |            1.09 |          22.15 |        939 |    0.08 |
| max_sl_pct | 0.3     | False     |              28.66 |       9.02 |             -20.99 |            1.11 |          23.99 |        967 |    0.09 |
| max_sl_pct | 100     | False     |              22.24 |       7.17 |             -24.25 |            1.08 |          24.72 |        983 |    0.09 |
| pivot      | 3       | False     |              19.72 |       6.43 |             -19.62 |            1.09 |          26.22 |        965 |    0.07 |
| pivot      | 5       | True      |              20.67 |       6.71 |             -23.74 |            1.09 |          22.15 |        939 |    0.08 |
| pivot      | 10      | False     |              23.86 |       7.65 |             -27.97 |            1.09 |          17.43 |        912 |    0.09 |
| partial    | 0.5     | False     |              20.73 |       6.73 |             -25.63 |            1.09 |          22.04 |        939 |    0.08 |
| partial    | 0.8     | True      |              20.67 |       6.71 |             -23.74 |            1.09 |          22.15 |        939 |    0.08 |
| partial    | 1.0     | False     |              20.57 |       6.68 |             -22.47 |            1.09 |          22.15 |        939 |    0.09 |
