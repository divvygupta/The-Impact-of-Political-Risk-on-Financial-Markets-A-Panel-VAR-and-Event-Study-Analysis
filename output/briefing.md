# Investment Briefing: Political Risk and the Global Equity Mix

Coverage: 10 equity markets, May 2008 to Sep 2026, monthly. Political Risk Index (PRI) combines Economic Policy Uncertainty and Geopolitical Risk (PCA weights: EPU 0.50, GPR 0.50).

## Key findings

1. **Return impact.** A one-standard-deviation surprise in a country's political risk is followed by a cumulative +0.20 pp excess return versus ACWI over four months (t+0 to t+3; p = 0.45, not statistically significant). Month fixed effects remove global moves, so this is the country-specific effect.
2. **Volatility impact.** The same shock moves next-month realised volatility by +1.3% (p = 0.10).
3. **Regimes.** Countries in the top third of political risk returned 0.4% a year relative to the bottom third the following month (p = 0.86), with average realised volatility of 21.8% vs 22.7%.
4. **Event risk.** Across 30 political events, the mean abnormal return over [0,+5] days was -1.22% (BMP p = 0.24). Largest moves: BRA Temer recording scandal -15.4%; DEU Russia's full-scale invasion of Ukraine -9.5%; IND Demonetisation announced -7.1%.
5. **Portfolio tilt.** Underweighting the three markets with the sharpest rise in real-time political risk gave a return/volatility ratio of 0.29 vs 0.28 for equal weight, a max drawdown of -46.0% vs -48.2%, tracking error of 1.3% and an information ratio of 0.18.

## Implications for the total fund

- Political risk is better treated as a **risk-budget input** (position sizing and hedging around known events) than as a standalone return signal; the evidence for lasting return effects should be judged on the significance figures above, not the point estimates.
- By event type, the largest average [0,+5] reaction was for **geopolitical** events (-4.20%) and the smallest for **election** (0.79%). Scheduled elections give time to hedge ahead of the vote; unscheduled shocks do not.
- Stress-test returns are in USD and so include currency moves. For a Canadian-dollar fund, the FX hedging decision is part of the political-risk exposure, not separate from it.

## Current read (latest month)

| Country | PRI (real time) | Model weight |
|---|---|---|
| CAN | +2.01 | 12.1% |
| BRA | +1.66 | 12.1% |
| USA | +1.41 | 12.1% |
| IND | +1.19 | 12.1% |
| ZAF | +1.01 | 5.0% |
| GBR | +0.98 | 12.1% |
| AUS | +0.71 | 5.0% |
| DEU | +0.59 | 12.1% |
| FRA | +0.57 | 12.1% |
| JPN | +0.31 | 5.0% |

## Stress tests (cumulative USD return)

|                                     |   USA |   DEU |   JPN |   GBR |   FRA |   CAN |   AUS |   IND |   BRA |   ZAF |   BENCH |   Equal-weight portfolio |
|:------------------------------------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|--------:|-------------------------:|
| Brexit referendum (Jun 2016)        |  -4.1 |  -9.1 |  -2.5 | -13.2 | -10.2 |  -4.2 |  -5.7 |  -2.9 |  -2.1 | -10.4 |    -5.4 |                     -6.4 |
| Trump election (Nov 2016)           |   1.8 |   0   |  -0.9 |   1.6 |   0   |   0.2 |   0   |  -3.5 | -10.2 |  -8.1 |     0.6 |                     -1.9 |
| UK mini-budget (Sep 2022)           |  -1.8 |  -3.7 |  -1.8 |  -5.6 |  -3.8 |  -3.7 |  -2.8 |  -3.7 |  -6.2 |  -2.1 |    -2.3 |                     -3.5 |
| Invasion of Ukraine (Feb-Mar 2022)  |  -3.1 | -15.6 |  -7.8 |  -8.6 | -13.7 |   0.4 |  -0.9 |  -7.7 |  -0.6 |  -1.5 |    -5.4 |                     -5.9 |
| U.S.-Canada tariff shock (Feb 2025) |  -0.5 |  -1.5 |  -1.2 |  -0.7 |  -0.8 |  -1.1 |  -0.7 |   0.9 |   0.3 |   0   |    -0.5 |                     -0.5 |

## Method notes and limitations

- PRI uses within-country z-scores; `pri_rt` uses expanding windows so the backtest has no look-ahead.
- Local projections include two lags of the outcome and the shock; Driscoll-Kraay errors allow for cross-country and serial correlation.
- Panel VAR is identified with political risk ordered first; results may depend on this ordering.
- Ten markets and roughly two decades of data limit statistical power. Treat estimates as indicative.
- Event dates are compiled by the author and should be checked before use.
