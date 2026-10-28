# PDH/PDL Liquidity Sweep — XAUUSD — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.02 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 6.07 | 0.10 | 5.97 | 101.97 |
| CAGR % | 1.98 | 0.05 | 5.97 | 26.37 |
| Max DD % | -25.76 | -15.93 | -12.37 | -27.69 |
| Trades | 1136 | 775 | 361 | – |
| Win rate % | 20.51 | 20.52 | 20.50 | – |
| Profit factor | 1.02 | 1.00 | 1.06 | – |
| Avg trade % | 0.00 | 0.00 | 0.00 | – |
| Avg R | 0.02 | 0.03 | 0.01 | – |
| Total R | 26.42 | 21.33 | 5.09 | – |
| Max losing streak | 24 | 20 | 24 | – |
| Sharpe | 0.18 | 0.06 | 0.37 | – |

Exits: stoploss 902, tg1+tg2 158, tg1+cost 62, squareoff 8, tg1+squareoff 6

## Parameter sensitivity (one at a time)

| param         | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:--------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| trigger       | low     | True      |               6.07 |       1.98 |             -25.76 |            1.02 |          20.51 |       1136 |    0.02 |
| trigger       | body    | False     |              29.68 |       9.05 |             -17.81 |            1.11 |          17.47 |       1196 |    0.03 |
| max_sl_points | 4.0     | False     |              -9.79 |      -3.38 |             -18.47 |            0.96 |          18.3  |       1038 |   -0.01 |
| max_sl_points | 8.0     | True      |               6.07 |       1.98 |             -25.76 |            1.02 |          20.51 |       1136 |    0.02 |
| max_sl_points | 12.0    | False     |              22.75 |       7.07 |             -23.8  |            1.07 |          20.88 |       1154 |    0.03 |
| max_sl_points | 1000.0  | False     |              10.91 |       3.51 |             -25.99 |            1.04 |          21.16 |       1177 |    0.01 |
| pivot         | 3       | False     |               9.74 |       3.14 |             -21.87 |            1.04 |          26.7  |       1176 |    0.01 |
| pivot         | 5       | True      |               6.07 |       1.98 |             -25.76 |            1.02 |          20.51 |       1136 |    0.02 |
| pivot         | 10      | False     |               1.61 |       0.53 |             -21.9  |            1.01 |          16.02 |       1105 |    0.07 |
| partial       | 0.5     | False     |              11.75 |       3.77 |             -26.06 |            1.04 |          20.51 |       1136 |    0.05 |
| partial       | 0.8     | True      |               6.07 |       1.98 |             -25.76 |            1.02 |          20.51 |       1136 |    0.02 |
| partial       | 1.0     | False     |               2.35 |       0.78 |             -25.57 |            1.01 |          20.51 |       1136 |    0.01 |
