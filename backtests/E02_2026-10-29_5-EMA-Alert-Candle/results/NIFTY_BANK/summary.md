# 5 EMA Alert Candle — NIFTY BANK — FAILS

- loses money (PF 0.99, CAGR -3.0%)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | -11.04 | -25.90 | 20.06 | 27.43 |
| CAGR % | -3.00 | -12.84 | 21.34 | 8.73 |
| Max DD % | -34.91 | -28.23 | -17.64 | -18.07 |
| Trades | 2856 | 1862 | 994 | – |
| Win rate % | 29.03 | 28.41 | 30.18 | – |
| Profit factor | 0.99 | 0.96 | 1.05 | – |
| Avg trade % | 0.00 | -0.00 | 0.01 | – |
| Avg R | -0.02 | -0.04 | 0.04 | – |
| Total R | -48.37 | -83.34 | 34.97 | – |
| Max losing streak | 22 | 22 | 12 | – |
| Sharpe | 0.02 | -0.37 | 0.86 | – |

Exits: stoploss 1916, target 545, squareoff 394, eod 1

## Parameter sensitivity (one at a time)

| param       | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| rr          | 2.0     | False     |              14.4  |       5.26 |             -32.02 |            1.01 |          35.04 |       2948 |   -0.01 |
| rr          | 3.0     | True      |             -11.04 |      -3    |             -34.91 |            0.99 |          29.03 |       2856 |   -0.02 |
| rr          | 4.0     | False     |              42.83 |      13.58 |             -27.91 |            1.03 |          26.67 |       2786 |   -0    |
| rr          | 5.0     | False     |              98.67 |      26.78 |             -29.71 |            1.07 |          25.56 |       2739 |    0.03 |
| sides       | both    | True      |             -11.04 |      -3    |             -34.91 |            0.99 |          29.03 |       2856 |   -0.02 |
| sides       | short   | False     |              -3.24 |      -0.35 |             -39.12 |            0.99 |          27.54 |       1903 |   -0.01 |
| sides       | long    | False     |             -12.02 |      -4.07 |             -30.58 |            0.97 |          32    |        953 |   -0.03 |
| alert_valid | until   | True      |             -11.04 |      -3    |             -34.91 |            0.99 |          29.03 |       2856 |   -0.02 |
| alert_valid | next    | False     |             -31.69 |     -11.18 |             -42.94 |            0.97 |          27.9  |       2724 |   -0.03 |
| max_trades  | 1       | False     |              45.25 |      13.78 |             -23.29 |            1.06 |          30.57 |       1289 |    0.06 |
| max_trades  | 3       | True      |             -11.04 |      -3    |             -34.91 |            0.99 |          29.03 |       2856 |   -0.02 |
| max_trades  | 10      | False     |               6.34 |       3.07 |             -46.66 |            1    |          29.51 |       3876 |   -0.01 |
