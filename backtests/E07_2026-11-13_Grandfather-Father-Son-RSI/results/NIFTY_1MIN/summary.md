# Grandfather-Father-Son RSI — NIFTY 50 · 1-MIN — MIXED

- thin edge (PF 1.19 < 1.3)

Period 2023-10-26 → 2026-10-26 · minute · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 45.46 | 19.09 | 22.15 | 19.60 |
| CAGR % | 13.22 | 9.03 | 22.01 | 6.48 |
| Max DD % | -5.89 | -5.89 | -3.73 | -15.67 |
| Trades | 1535 | 961 | 574 | – |
| Win rate % | 37.79 | 37.15 | 38.85 | – |
| Profit factor | 1.19 | 1.12 | 1.29 | – |
| Avg trade % | 0.00 | 0.00 | 0.01 | – |
| Avg R | 0.13 | 0.14 | 0.12 | – |
| Total R | 200.59 | 134.42 | 66.17 | – |
| Max losing streak | 18 | 18 | 9 | – |
| Sharpe | 1.58 | 1.16 | 2.32 | – |

Exits: stoploss 934, rsi_target 576, squareoff 25

## Parameter sensitivity (one at a time)

| param    |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:---------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| band_lo  |      37 | False     |              50.41 |      14.49 |              -5.53 |            1.21 |          38.07 |       1505 |    0.14 |
| band_lo  |      39 | False     |              48.6  |      13.96 |              -4.67 |            1.22 |          37.71 |       1416 |    0.15 |
| band_hi  |      42 | False     |              23.79 |       7.3  |              -5.87 |            1.19 |          36.04 |        838 |    0.09 |
| band_hi  |      45 | True      |              45.46 |      13.22 |              -5.89 |            1.19 |          37.79 |       1535 |    0.13 |
| live_htf |    True | True      |              45.46 |      13.22 |              -5.89 |            1.19 |          37.79 |       1535 |    0.13 |
| live_htf |   False | False     |              62.37 |      17.45 |              -6.91 |            1.21 |          33.77 |       1768 |    0.12 |
