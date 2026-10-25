# The Impact of Political Risk on Financial Markets: A Panel VAR and Event Study Analysis

Does political risk move financial markets? This project separates the slow-moving political "climate" from acute political "weather" across 10 major economies. It uses a VAR model for long-run dynamics and event studies for short-term market reactions.

## Data

- **Countries:** United States, Germany, Japan, United Kingdom, France, Canada, Australia, India, Brazil, South Africa
- **Period:** 2005 to 2020 for the panel analysis, plus daily market data around each event
- **Political risk inputs:**
  - World Bank Worldwide Governance Indicators (political stability)
  - Database of Political Institutions (government ideology)
  - Global Sanctions Data Base
- **Economic and market data:** FDI inflows, plus stock index and currency volatility from Yahoo Finance via `yfinance`

## Method

1. **Composite Political Risk Index (CPRI).** Political stability, sanctions and ideology shifts are standardized and combined with principal component analysis.
2. **VAR model.** CPRI, FDI inflows, stock volatility and currency volatility are first-differenced, and lag length is selected by AIC. The analysis includes impulse responses with bootstrapped 95% confidence intervals and a Granger causality test of FDI on political risk.
3. **Event studies.** Ten political shocks, one per country, such as the UK "mini-budget" crisis, the 2014 Modi election and the U.S. Capitol attack. Each uses a 250-day estimation window, cumulative abnormal returns (CAR) over 10 days, and t-tests for significance.

## Key results

- **Long-run "climate":** the composite political risk index is **not** a statistically significant predictor of next-year stock volatility, currency volatility or FDI. The VAR does confirm strong persistence in stock and currency volatility (p < 0.01), and there is no evidence that FDI inflows predict future political risk.
- **Short-run "weather":** markets react visibly to political shocks. Examples:
  - UK mini-budget crisis: 10-day CAR of **−3.5%**
  - German election marking the end of the Merkel era: **−4.4%**
  - 2014 Modi election: **+2.8%**
- **Economic vs. statistical significance:** none of the 10 event reactions is significant at the 5% level. Moves of 3–5% matter to investors but cannot be statistically separated from normal market noise, which suggests markets are resilient to political shocks.

## Files

- `code.py`: full pipeline (index construction, VAR, impulse responses, event studies, plots)
- `Project__Report.pdf`: written report with methodology, tables, figures and discussion

## Tools

Python: pandas, NumPy, yfinance, scikit-learn (PCA), statsmodels (VAR), SciPy, Matplotlib

## How to run

The script expects these data files in the working directory:

- `WGI_Data.xlsx`
- `DPI2020.csv`
- `GSDB_V4.csv`
- `FDI_Data.xlsx`

```bash
pip install pandas numpy yfinance scikit-learn statsmodels scipy matplotlib openpyxl
python code.py
```

Plots are saved to `project_plots/`.
