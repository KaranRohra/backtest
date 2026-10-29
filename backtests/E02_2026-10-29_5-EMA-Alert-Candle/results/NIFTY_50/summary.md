# 5 EMA Alert Candle — NIFTY 50 — MIXED

- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.04 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 54.51 | 69.62 | -8.91 | 19.60 |
| CAGR % | 16.16 | 31.25 | -8.55 | 6.48 |
| Max DD % | -32.31 | -26.63 | -24.71 | -15.67 |
| Trades | 2990 | 1939 | 1051 | – |
| Win rate % | 29.63 | 30.22 | 28.54 | – |
| Profit factor | 1.04 | 1.07 | 0.97 | – |
| Avg trade % | 0.00 | 0.01 | 0.00 | – |
| Avg R | 0.03 | 0.05 | 0.00 | – |
| Total R | 96.26 | 91.50 | 4.76 | – |
| Max losing streak | 18 | 18 | 12 | – |
| Sharpe | 0.72 | 1.18 | -0.24 | – |

Exits: stoploss 2002, target 621, squareoff 364, eod 3

## Parameter sensitivity (one at a time)

| param       | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| rr          | 2.0     | False     |              10.93 |       3.62 |             -28.96 |            1.01 |          35.58 |       3069 |    0.02 |
| rr          | 3.0     | True      |              54.51 |      16.16 |             -32.31 |            1.04 |          29.63 |       2990 |    0.03 |
| rr          | 4.0     | False     |              91.02 |      24.67 |             -27.97 |            1.06 |          26.71 |       2935 |    0.05 |
| rr          | 5.0     | False     |             144.02 |      35.27 |             -27.12 |            1.08 |          25.48 |       2877 |    0.06 |
| sides       | both    | True      |              54.51 |      16.16 |             -32.31 |            1.04 |          29.63 |       2990 |    0.03 |
| sides       | short   | False     |              99.64 |      25.91 |             -19.84 |            1.12 |          29.15 |       1986 |    0.08 |
| sides       | long    | False     |             -25.21 |      -8.79 |             -48.16 |            0.94 |          30.58 |       1004 |   -0.06 |
| alert_valid | until   | True      |              54.51 |      16.16 |             -32.31 |            1.04 |          29.63 |       2990 |    0.03 |
| alert_valid | next    | False     |              10.02 |       4.01 |             -31.98 |            1.01 |          28.57 |       2877 |    0.02 |
| max_trades  | 1       | False     |              18.28 |       6.05 |             -29.1  |            1.03 |          29.37 |       1294 |    0.01 |
| max_trades  | 3       | True      |              54.51 |      16.16 |             -32.31 |            1.04 |          29.63 |       2990 |    0.03 |
| max_trades  | 10      | False     |              50.21 |      15.07 |             -31.89 |            1.03 |          29.15 |       4302 |    0.02 |
