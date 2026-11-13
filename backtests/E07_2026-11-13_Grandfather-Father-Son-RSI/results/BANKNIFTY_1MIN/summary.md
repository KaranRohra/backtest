# Grandfather-Father-Son RSI — BANK NIFTY · 1-MIN — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- thin edge (PF 1.10 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 23.64 | 7.20 | 15.34 | 27.43 |
| CAGR % | 7.18 | 3.34 | 15.33 | 8.73 |
| Max DD % | -15.96 | -8.09 | -10.33 | -18.07 |
| Trades | 1309 | 824 | 485 | – |
| Win rate % | 35.60 | 36.04 | 34.85 | – |
| Profit factor | 1.10 | 1.05 | 1.19 | – |
| Avg trade % | 0.00 | 0.00 | 0.01 | – |
| Avg R | 0.05 | 0.07 | 0.02 | – |
| Total R | 70.76 | 61.22 | 9.54 | – |
| Max losing streak | 13 | 12 | 13 | – |
| Sharpe | 0.85 | 0.42 | 1.73 | – |

Exits: stoploss 827, rsi_target 466, squareoff 16

## Parameter sensitivity (one at a time)

| param    |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:---------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| band_lo  |      37 | False     |              26.97 |       8.14 |             -15.11 |            1.11 |          35.69 |       1272 |    0.06 |
| band_lo  |      39 | False     |              20.43 |       6.25 |             -16.5  |            1.09 |          35.08 |       1220 |    0.05 |
| band_hi  |      42 | False     |              21.41 |       6.47 |              -8.86 |            1.17 |          34.29 |        662 |    0.08 |
| band_hi  |      45 | True      |              23.64 |       7.18 |             -15.96 |            1.1  |          35.6  |       1309 |    0.05 |
| live_htf |    True | True      |              23.64 |       7.18 |             -15.96 |            1.1  |          35.6  |       1309 |    0.05 |
| live_htf |   False | False     |              46.38 |      13.39 |             -11.09 |            1.15 |          32.76 |       1572 |    0.07 |
