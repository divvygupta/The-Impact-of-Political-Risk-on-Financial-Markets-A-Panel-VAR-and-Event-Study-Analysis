# Political Risk and the Global Equity Mix

How should a multi-asset fund account for political risk across its country exposures? This project builds a monthly political risk index for 10 major equity markets and asks three portfolio questions:

1. **Does a political-risk surprise move a market's returns and volatility, and for how long?** Panel local projections and a fixed-effects panel VAR.
2. **How do markets react to discrete political events, after removing global moves?** A market-model event study of 30 events.
3. **Is the signal useful for the asset mix?** Regime analysis, a political-risk-aware country tilt backtested out of sample, and stress tests over recent political shocks.

The output is a set of charts, CSV tables and an auto-generated investment briefing (`output/briefing.md`) written for a total-fund audience.

Version 2 rebuilds the [original project](#version-1-the-original-project) (kept in `legacy/`), which found no significant long-run effect on annual data. The new design addresses the main reasons a real effect could have been missed: annual frequency, a small panel (188 observations), index inputs that change slowly, and a mean-adjusted event model that did not remove global market moves.

## Data

| Input | Source | Frequency |
|---|---|---|
| Economic Policy Uncertainty (EPU) by country | Baker, Bloom and Davis, [policyuncertainty.com](https://www.policyuncertainty.com) | Monthly |
| Country Geopolitical Risk (GPR) | Caldara and Iacoviello (2022), [matteoiacoviello.com/gpr.htm](https://www.matteoiacoviello.com/gpr.htm) | Monthly |
| Country equity returns, in USD | iShares country ETFs (IVV, EWG, EWJ, EWU, EWQ, EWC, EWA, INDA, EWZ, EZA) via `yfinance` | Daily |
| Global benchmark | iShares MSCI ACWI (ACWI) | Daily |

USD ETF returns make the markets comparable and reflect what a foreign investor actually earns, currency included. The sample starts in April 2008, when ACWI launched. South Africa has no EPU series, so its index uses GPR alone.

## Method

**Political Risk Index (PRI).** Log EPU and log GPR are standardised within each country and combined with first-principal-component weights. Two versions are kept:
- `pri`: full-sample standardisation, used in the econometrics.
- `pri_rt`: expanding-window standardisation, using only data available at the time, so the backtest has no look-ahead.

The **political-risk shock** is the standardised innovation from a country-level AR(1), the part of political risk that markets could not have predicted from last month.

**Local projections** (Jordà, 2005). For each horizon h = 0 to 12 months, the cumulative excess return over ACWI (and log realised volatility) is regressed on the shock, with two lags of each as controls. **Country and month fixed effects** mean the estimate is the effect of a country's own political-risk surprise relative to other markets in the same month. Driscoll-Kraay standard errors allow for cross-country and serial correlation.

**Fixed-effects panel VAR** of [shock, excess return, log volatility]. Lags are built within each country, lag length is chosen by BIC, and impulse responses use Cholesky ordering with political risk first. Confidence bands come from 500 country-cluster bootstrap draws.

**Event study.** The normal return for each event is a market model of the country ETF on ACWI over trading days [−250, −30]. Cumulative abnormal returns are reported for [−1,+1], [0,+5] and [0,+10]. Significance is tested per event and across events with the Boehmer-Musumeci-Poulsen standardised test, both overall and by event type (election, policy shock, governance, geopolitical, unrest).

**Portfolio applications:**
- *Regimes:* each month, countries are ranked into terciles by real-time PRI, and next-month excess return, volatility and hit rate are compared.
- *Tilt backtest:* starting from an equal-weight country portfolio, the three markets with the sharpest 3-month rise in real-time PRI (known at the end of the previous month) have their weight halved, and the freed weight goes to the rest. Reported: return, volatility, return/volatility, max drawdown, tracking error, information ratio and turnover.
- *Stress tests:* cumulative USD returns for each market and the portfolio during the Brexit vote, the 2016 U.S. election, the Russian invasion of Ukraine, the UK mini-budget and the 2025 U.S.–Canada tariff shock.

## Outputs

| File | Content |
|---|---|
| `fig1_political_risk_index.png` | PRI over time, by country |
| `fig2_local_projections.png` | Return and volatility responses to a 1 s.d. shock, 90% bands |
| `fig3_panel_var_irf.png` | Panel VAR impulse responses with bootstrap bands |
| `fig4_event_study.png` | CAR by event, and the average abnormal-return path |
| `fig5_regimes.png` | Next-month outcomes by political-risk tercile |
| `fig6_backtest.png` | Tilt vs equal weight: growth of 100 and drawdowns |
| `fig7_stress_tests.png` | Returns by market during political-stress windows |
| `briefing.md` | Key findings, total-fund implications, current country read, limitations |
| `*.csv` | All underlying tables |

## How to run

```bash
pip install -r requirements.txt
python run_analysis.py              # real data: downloads once, then cached in data/
python run_analysis.py --synthetic  # offline demo on simulated data
pytest                              # tests
```

If a download fails, save the EPU file as `data/raw/All_Country_Data.xlsx` and the GPR file as `data/raw/data_gpr_export.xls`. The loader uses the local copies first.

## Tests

The test suite runs on simulated data in which a known effect is built in: a 1 s.d. shock lowers next-month excess return by 2%, and events carry a −2% abnormal return. The tests check that:
- local projections recover the planted effect, and the event study detects the planted event returns but finds nothing when there is no effect;
- the real-time index and the tilt weights do not use future data;
- portfolio weights always sum to 1.

## Limitations

- Ten markets and about 17 years limit statistical power, so estimates should be read as indicative.
- Panel VAR results depend on the ordering assumption (political risk first). The local projections do not rely on it.
- EPU and GPR are text-based measures and pick up media attention as well as underlying risk.
- Event dates in `political_risk/config.py` were compiled by hand and should be checked before the results are relied on.
- The backtest ignores transaction costs. Average turnover is reported so their effect can be judged.

## Project structure

```
political_risk/
  config.py        countries, tickers, data URLs, events, stress windows
  data.py          downloads with caching, plus a synthetic data generator
  index.py         Political Risk Index and shocks
  econometrics.py  monthly panel, local projections, panel VAR
  events.py        market-model event study with BMP tests
  allocation.py    regimes, tilt backtest, stress tests
  report.py        charts and briefing
run_analysis.py    end-to-end pipeline
tests/             tests on synthetic data
legacy/            version 1 code and report
```

## Version 1: the original project

The first version (`legacy/code_v1.py`, `legacy/Project_Report_v1.pdf`) built an annual Composite Political Risk Index from the World Bank Governance Indicators, the Database of Political Institutions and the Global Sanctions Data Base for 2005–2020. It estimated a VAR with FDI and market volatility and ran 10 mean-adjusted event studies. The composite index was not a significant predictor of volatility or FDI. Event reactions of 3–5% (UK mini-budget −3.5%, the German 2021 election −4.4%, the 2014 Modi election +2.8%) were economically meaningful but not significant at 5%.

**Tools:** Python, pandas, NumPy, SciPy, scikit-learn, linearmodels, Matplotlib, yfinance, pytest
