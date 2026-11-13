# Grandfather-Father-Son RSI — NIFTY 50 STOCKS — MIXED

- worse than buy & hold, both on return and on return per unit of drawdown
- edge fades in the most recent (out-of-sample) year
- thin edge (PF 1.09 < 1.3)

Period 2016-10-25 → 2026-10-26 · day · **before costs** · OOS from 2025-10-26

| Metric | Full | In-sample | Out-of-sample | Buy & hold |
|---|---|---|---|---|
| Return % | 7.86 | 11.63 | -3.38 | 164.10 |
| CAGR % | 0.76 | 1.23 | -3.39 | 10.20 |
| Max DD % | -11.58 | -11.58 | -4.41 | -38.44 |
| Trades | 418 | 390 | 28 | – |
| Win rate % | 37.80 | 38.46 | 28.57 | – |
| Profit factor | 1.09 | 1.15 | 0.44 | – |
| Avg trade % | 0.20 | 0.30 | -1.22 | – |
| Avg R | 0.07 | 0.10 | -0.33 | – |
| Total R | 29.89 | 39.09 | -9.20 | – |
| Max losing streak | 17 | 17 | 10 | – |
| Sharpe | 0.25 | 0.37 | -1.84 | – |

Exits: stoploss 257, rsi_target 161

## Parameter sensitivity (one at a time)

| param         |   value | default   |   total_return_pct |   cagr_pct |   max_drawdown_pct |   profit_factor |   win_rate_pct |   n_trades |   avg_r |
|:--------------|--------:|:----------|-------------------:|-----------:|-------------------:|----------------:|---------------:|-----------:|--------:|
| band_lo       |      37 | False     |               5.29 |       0.52 |             -11.46 |            1.07 |          37.23 |        411 |    0.06 |
| band_lo       |      39 | False     |               4.35 |       0.43 |             -11.05 |            1.06 |          37.05 |        386 |    0.06 |
| band_hi       |      42 | False     |              12.11 |       1.15 |              -6.9  |            1.3  |          40.41 |        193 |    0.18 |
| band_hi       |      45 | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| live_htf      |    True | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| live_htf      |   False | False     |              -8.54 |      -0.89 |             -21.01 |            0.92 |          31.2  |        532 |   -0.02 |
| touch_bars    |       1 | False     |               3.19 |       0.31 |              -4.53 |            1.12 |          28.23 |        124 |    0.12 |
| touch_bars    |       2 | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| touch_bars    |       3 | False     |               7.2  |       0.7  |             -11.19 |            1.08 |          40.23 |        517 |    0.05 |
| need_pullback |   False | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| need_pullback |    True | False     |               7.33 |       0.71 |             -10.16 |            1.09 |          38.01 |        392 |    0.07 |
| htf_level     |      55 | False     |             -15.92 |      -1.72 |             -36.07 |            0.92 |          33.02 |       1178 |    0    |
| htf_level     |      60 | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| exit_level    |      55 | False     |               1.6  |       0.16 |              -7.35 |            1.02 |          48.84 |        430 |    0.01 |
| exit_level    |      60 | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| exit_level    |      65 | False     |              26    |       2.34 |              -9.38 |            1.26 |          32.28 |        412 |    0.16 |
| allow_short   |    True | True      |               7.86 |       0.76 |             -11.58 |            1.09 |          37.8  |        418 |    0.07 |
| allow_short   |   False | False     |              14.95 |       1.4  |              -7.59 |            1.21 |          39.3  |        374 |    0.1  |
