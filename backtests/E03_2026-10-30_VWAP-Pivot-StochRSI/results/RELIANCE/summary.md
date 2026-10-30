# VWAP + Pivots + Stoch RSI — RELIANCE — MIXED

- thin edge (PF 1.14 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 86.49 | 50.86 | 23.62 | 6.74 |
| CAGR % | 22.74 | 22.36 | 23.57 | 2.62 |
| Max DD % | -26.67 | -21.39 | -10.36 | -27.81 |
| Trades | 967 | 637 | 330 | – |
| Win rate % | 46.23 | 46.94 | 44.85 | – |
| Profit factor | 1.14 | 1.13 | 1.15 | – |
| Avg trade % | 0.04 | 0.04 | 0.04 | – |
| Avg R | 0.07 | 0.07 | 0.07 | – |
| Total R | 68.09 | 44.78 | 23.31 | – |
| Max losing streak | 10 | 9 | 10 | – |
| Sharpe | 1.19 | 1.19 | 1.18 | – |

Exits: squareoff 430, stoploss 363, target 138, eod 36

## Parameter sensitivity (one at a time)

| param       | value   | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:------------|:--------|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| sl          | pct     | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
| sl          | vwap    | False     |             -48.42 |     -20.22 |             -57.89 |            0.84 |          19.75 |       1190 |   -0.16 |
| stoch       | True    | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
| stoch       | False   | False     |              50.32 |      14.51 |             -28.75 |            1.09 |          43.89 |        998 |    0.05 |
| entry       | break   | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
| entry       | close   | False     |              60.42 |      16.75 |             -22.86 |            1.12 |          44.94 |        890 |    0.06 |
| target_pct  | 0.75    | False     |              49.77 |      14.09 |             -25.84 |            1.09 |          46.99 |        964 |    0.05 |
| target_pct  | 1.0     | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
| target_pct  | 1.5     | False     |             111.81 |      28.06 |             -26.85 |            1.16 |          45.76 |        968 |    0.08 |
| first_entry | 09:20   | False     |              36.38 |      10.93 |             -34.21 |            1.06 |          41.06 |       1096 |    0.04 |
| first_entry | 10:45   | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
| max_trades  | 1       | False     |              31.78 |       9.33 |             -27.27 |            1.08 |          43.78 |        740 |    0.04 |
| max_trades  | 2       | True      |              86.49 |      22.74 |             -26.67 |            1.14 |          46.23 |        967 |    0.07 |
