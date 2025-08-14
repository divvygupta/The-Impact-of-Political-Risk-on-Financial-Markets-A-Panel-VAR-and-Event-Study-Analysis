

import pandas as pd
import yfinance as yf
import time
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================
FINANCIAL_DATA_FILE = 'financial_data_final.csv'
COUNTRY_CONFIG = {
    'USA': '^GSPC', 'DEU': '^GDAXI', 'JPN': '^N225', 'GBR': '^FTSE', 'FRA': '^FCHI',
    'CAN': '^GSPTSE', 'AUS': '^AXJO', 'IND': '^BSESN', 'BRA': '^BVSP', 'ZAF': 'EZA'
}
CURRENCY_MAP = {
    'USA': 'EUR', 'DEU': 'EUR', 'JPN': 'JPY', 'GBR': 'GBP', 'FRA': 'EUR',
    'CAN': 'CAD', 'AUS': 'AUD', 'IND': 'INR', 'BRA': 'BRL', 'ZAF': 'ZAR'
}
START_YEAR = 2005
END_YEAR = 2020
COUNTRY_LIST = list(COUNTRY_CONFIG.keys())
EVENT_LIST = {
    'USA': {'date': '2021-01-06', 'name': 'U.S. Capitol Attack'},
    'DEU': {'date': '2021-09-26', 'name': 'German Federal Election (End of Merkel Era)'},
    'JPN': {'date': '2022-07-08', 'name': 'Assassination of Shinzo Abe'},
    'GBR': {'date': '2022-09-23', 'name': 'Truss Government "Mini-Budget" Crisis'},
    'FRA': {'date': '2022-04-24', 'name': 'Macron Re-election Victory'},
    'CAN': {'date': '2015-10-20', 'name': 'Trudeau Election Victory'},
    'AUS': {'date': '2022-05-21', 'name': 'Albanese Election Victory'},
    'IND': {'date': '2014-05-16', 'name': 'Modi Election Victory'},
    'BRA': {'date': '2022-10-30', 'name': 'Lula da Silva Election Victory'},
    'ZAF': {'date': '2021-07-12', 'name': 'Escalation of Civil Unrest'},
}
### NEW: Define the folder name for saving plots ###
PLOT_FOLDER = 'project_plots'


# =============================================================================
# SECTION 2: FUNCTION DEFINITIONS
# =============================================================================

def get_annual_volatility_df(ticker, start_date, end_date, data_type='Stock'):
    try:
        data = yf.download(ticker, start=f"{start_date}-01-01", end=f"{end_date}-12-31", progress=False,
                           auto_adjust=True)
        if len(data) < 50: raise ValueError("Not enough data points.")
        daily_returns = data['Close'].pct_change().dropna()
        annual_volatility = daily_returns.resample('A').std() * np.sqrt(252)
        annual_volatility.index = annual_volatility.index.year
        result_df = pd.DataFrame(annual_volatility)
        result_df.columns = [f'{data_type}_Volatility']
        return result_df
    except Exception as e:
        return None


def download_all_financial_data():
    print("--- Starting Financial Data Download Process ---")
    all_data_list = []
    for country, ticker in COUNTRY_CONFIG.items():
        time.sleep(1)
        stock_vol_df = get_annual_volatility_df(ticker, START_YEAR, END_YEAR, 'Stock')
        time.sleep(1)
        currency_code = CURRENCY_MAP.get(country)
        currency_ticker = f"{currency_code}USD=X" if country != 'USA' else 'EURUSD=X'
        currency_vol_df = get_annual_volatility_df(currency_ticker, START_YEAR, END_YEAR, 'Currency')
        if stock_vol_df is not None and currency_vol_df is not None:
            country_df = stock_vol_df.join(currency_vol_df)
            country_df['Country'] = country
            country_df.reset_index(inplace=True).rename(columns={'index': 'Year'}, inplace=True)
            all_data_list.append(country_df)
    if all_data_list:
        pd.concat(all_data_list, ignore_index=True).to_csv(FINANCIAL_DATA_FILE, index=False)
        print(f"\n--- SUCCESS! Financial data saved to '{FINANCIAL_DATA_FILE}' ---")
    else:
        print(f"\n--- FAILURE: No financial data was saved. ---")


def load_real_political_data(start_year, end_year):
    print("\n--- Loading REAL Political & Economic Data ---")
    try:
        wgi_df = pd.read_excel('WGI_Data.xlsx', sheet_name='Data', header=0)
        wgi_df = wgi_df[wgi_df['Series Name'] == 'Political Stability and Absence of Violence/Terrorism: Estimate']
        wgi_long = pd.melt(wgi_df, id_vars=['Country Name'], value_name='Political_Stability', var_name='Year')
        wgi_long['Year'] = wgi_long['Year'].str.extract(r'(\d{4})')
        wgi_long.dropna(subset=['Year'], inplace=True)
        wgi_long['Year'] = wgi_long['Year'].astype(int)
        wgi_final = wgi_long.rename(columns={'Country Name': 'Country'})
        dpi_df = pd.read_csv('DPI2020.csv', encoding='ISO-8859-1')
        dpi_subset = dpi_df[['countryname', 'year', 'execrlc']].rename(
            columns={'countryname': 'Country', 'year': 'Year', 'execrlc': 'Gov_Ideology'})
        dpi_subset['Gov_Ideology'] = pd.to_numeric(dpi_subset['Gov_Ideology'], errors='coerce')
        gsdb_df = pd.read_csv('GSDB_V4.csv')
        all_country_years = pd.DataFrame(
            [(country, year) for country in wgi_final['Country'].unique() for year in range(start_year, end_year + 1)],
            columns=['Country', 'Year'])
        sanction_years_list = []
        for index, row in gsdb_df.iterrows():
            end_year_val = int(row['end']) if pd.notna(row['end']) else end_year
            start_year_val = int(row['begin'])
            for year in range(start_year_val, end_year_val + 1):
                sanction_years_list.append({'Country': row['sanctioned_state'], 'Year': year, 'Sanctions': 1})
        if sanction_years_list:
            sanctions_df = pd.DataFrame(sanction_years_list).drop_duplicates()
            gsdb_final = pd.merge(all_country_years, sanctions_df, on=['Country', 'Year'], how='left')
            gsdb_final['Sanctions'] = gsdb_final['Sanctions'].fillna(0).astype(int)
        else:
            gsdb_final = all_country_years.assign(Sanctions=0)
        fdi_df = pd.read_excel('FDI_Data.xlsx', sheet_name='Data', header=3)
        fdi_long = pd.melt(fdi_df, id_vars=['Country Name'], value_name='FDI_Inflows', var_name='Year')
        fdi_long['Year'] = fdi_long['Year'].astype(str).str.extract(r'(\d{4})')
        fdi_long.dropna(subset=['Year'], inplace=True)
        fdi_long['Year'] = fdi_long['Year'].astype(int)
        fdi_final = fdi_long.rename(columns={'Country Name': 'Country'})
        master_political_df = pd.merge(wgi_final, dpi_subset, on=['Country', 'Year'], how='left')
        master_political_df = pd.merge(master_political_df, gsdb_final, on=['Country', 'Year'], how='left')
        master_political_df = pd.merge(master_political_df, fdi_final, on=['Country', 'Year'], how='left')
        country_name_map = {'United States': 'USA', 'Germany': 'DEU', 'Japan': 'JPN', 'United Kingdom': 'GBR',
                            'France': 'FRA',
                            'Canada': 'CAN', 'Australia': 'AUS', 'India': 'IND', 'Brazil': 'BRA', 'South Africa': 'ZAF'}
        master_political_df['Country'] = master_political_df['Country'].map(country_name_map)
        master_political_df = master_political_df[master_political_df['Country'].isin(COUNTRY_LIST)]
        master_political_df['Gov_Ideology'] = master_political_df.groupby('Country')['Gov_Ideology'].transform(
            lambda x: x.interpolate().fillna(method='ffill').fillna(method='bfill'))
        master_political_df['Sanctions'] = master_political_df['Sanctions'].fillna(0)
        master_political_df['FDI_Inflows'] = master_political_df['FDI_Inflows'].fillna(0)
        master_political_df.dropna(subset=['Political_Stability'], inplace=True)
        return master_political_df
    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: Data file not found -> {e.filename}")
        return None
    except KeyError as e:
        print(f"\nFATAL KeyError: The column {e} was not found.")
        return None


### NEW: Function signature updated to accept plot_folder ###
def perform_event_study(ticker, event_date_str, window_size, country_name, event_name, plot_folder):
    """
    Performs an event study, generates a plot, and saves it to a folder.
    """
    print(f"\n--- Performing Event Study for {country_name}: {event_name} ---")
    try:
        event_date = pd.to_datetime(event_date_str)
        estimation_start = event_date - pd.Timedelta(days=250)
        event_window_end = event_date + pd.Timedelta(days=window_size + 1)
        estimation_end = event_date - pd.Timedelta(days=30)
        event_window_start = event_date - pd.Timedelta(days=window_size)
        data = yf.download(ticker, start=estimation_start, end=event_window_end, progress=False, auto_adjust=True)
        if len(data) < 50: raise ValueError("Not enough data downloaded.")
        data['Return'] = data['Close'].pct_change()
        estimation_data = data.loc[estimation_start:estimation_end]
        if estimation_data['Return'].count() < 30: raise ValueError("Not enough data in estimation window.")
        std_dev_normal_returns = estimation_data['Return'].std()
        normal_return = estimation_data['Return'].mean()
        event_data = data.loc[event_window_start:event_window_end].copy()
        if event_data.empty: raise ValueError("Event window is empty.")
        event_data['Abnormal_Return'] = event_data['Return'] - normal_return
        post_event_window = event_data.loc[event_date:].head(window_size + 1)
        final_car = post_event_window['Abnormal_Return'].sum()
        N = len(post_event_window)
        if N == 0: raise ValueError("Post-event window is empty.")
        t_stat = final_car / (std_dev_normal_returns * np.sqrt(N))
        p_value = stats.t.sf(np.abs(t_stat), df=N - 1) * 2
        event_data['CAR'] = event_data['Abnormal_Return'].cumsum()

        plt.figure(figsize=(12, 6))
        event_data['CAR'].plot(marker='o', linestyle='-', color='navy')
        plt.axvline(x=event_date, color='r', linestyle='--', label=f'Event Date: {event_date_str}')
        plt.title(f'CAR for {country_name} ({ticker})\n{event_name}')
        plt.ylabel('Cumulative Abnormal Return')
        plt.xlabel('Date')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        ### NEW: Save the plot to the specified folder ###
        safe_event_name = "".join([c for c in event_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        filename = os.path.join(plot_folder, f'Event_Study_{country_name}_{safe_event_name}.png')
        plt.savefig(filename)
        print(f"Plot saved to {filename}")

        plt.show()

        return {"Country": country_name, "Event": event_name, f"CAR ({window_size} days)": f"{final_car:.4f}",
                "t-statistic": f"{t_stat:.4f}", "p-value": f"{p_value:.4f}"}
    except Exception as e:
        print(f"--> SKIPPING event for {ticker}. Reason: {e}")
        return None


# =============================================================================
# SECTION 3: MAIN SCRIPT EXECUTION
# =============================================================================

### NEW: Create the plot directory if it doesn't exist ###
if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)
    print(f"Created directory to save plots: {PLOT_FOLDER}")

if not os.path.exists(FINANCIAL_DATA_FILE):
    download_all_financial_data()
else:
    print(f"Data file '{FINANCIAL_DATA_FILE}' found. Skipping download.")

try:
    financial_df = pd.read_csv(FINANCIAL_DATA_FILE)
    print("\nStep 1: Successfully loaded financial data.")
except FileNotFoundError:
    print(f"\nFATAL ERROR: Could not find or create '{FINANCIAL_DATA_FILE}'.")
    exit()

political_df = load_real_political_data(START_YEAR, END_YEAR)
if political_df is None: exit()

master_df = pd.merge(political_df, financial_df, on=['Country', 'Year'], how='inner')
if master_df.empty:
    print("FATAL: Merged dataframe is empty.")
    exit()
master_df.set_index(['Country', 'Year'], inplace=True)
master_df.sort_index(inplace=True)

print("\n--- Head of Final Merged Data (with REAL FDI) ---")
print(master_df.head())

master_df['Ideology_Shift'] = master_df.groupby('Country')['Gov_Ideology'].diff().fillna(0).astype(bool).astype(int)
risk_components = ['Political_Stability', 'Sanctions', 'Ideology_Shift']
X = master_df[risk_components].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
pca = PCA(n_components=1)
master_df['CPRI'] = pca.fit_transform(X_scaled)
if pca.components_[0][0] > 0: master_df['CPRI'] = -master_df['CPRI']

print("Step 5: Performing Panel VAR analysis.")
master_df.rename(columns={'Stock_Volatility': 'StockVol', 'Currency_Volatility': 'CurrencyVol'}, inplace=True)
var_data = master_df[['CPRI', 'FDI_Inflows', 'StockVol', 'CurrencyVol']].dropna()
print(f"DIAGNOSTIC: Shape of data for VAR analysis (after dropping NaNs): {var_data.shape}")
var_data_diff = var_data.groupby('Country').diff().dropna()
if var_data_diff.empty or len(var_data_diff) < 20:
    print(f"DIAGNOSTIC: Shape of data after differencing: {var_data_diff.shape}")
    print("FATAL: Not enough data for VAR analysis after merging and cleaning.")
    exit()

model = VAR(var_data_diff)
results = model.fit(maxlags=2, ic='aic')
print("\n--- VAR Model Summary ---")
print(results.summary())

print("\nStep 6: Generating result plots (Impulse Response Functions).")
irf = results.irf(periods=5)

fig_irf_full = irf.plot(orth=False)
fig_irf_full.suptitle('Impulse Responses to a Shock in Each Variable', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
### NEW: Save the plot ###
plt.savefig(os.path.join(PLOT_FOLDER, 'IRF_Full_Matrix.png'))
print(f"Plot saved to {os.path.join(PLOT_FOLDER, 'IRF_Full_Matrix.png')}")
plt.show()

fig_irf_cpri = irf.plot(impulse='CPRI')
fig_irf_cpri.suptitle('Responses to a Political Risk Shock (CPRI)', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
### NEW: Save the plot ###
plt.savefig(os.path.join(PLOT_FOLDER, 'IRF_Response_to_CPRI_Shock.png'))
print(f"Plot saved to {os.path.join(PLOT_FOLDER, 'IRF_Response_to_CPRI_Shock.png')}")
plt.show()

# =============================================================================
# SECTION 7: DEEPER ANALYSIS OF THE FDI -> CPRI FEEDBACK LOOP
# =============================================================================
print("\n" + "=" * 80)
print(" " * 15 + "SECTION 7: Deeper Analysis of the FDI->CPRI Feedback Loop")
print("=" * 80)

causality_test = results.test_causality('FDI_Inflows', ['CPRI'], kind='f')
print(causality_test)
p_value_granger = causality_test.pvalue
print(f"\nInterpretation: The p-value for this test is {p_value_granger:.4f}.")
if p_value_granger < 0.05:
    print("This provides strong statistical evidence that past FDI inflows help predict future political risk.")
else:
    print("There is not enough statistical evidence to claim that FDI Granger-causes Political Risk in this model.")

ax = irf.plot(impulse='FDI_Inflows', response='CPRI')
ax.suptitle('Response of Political Risk (CPRI) to an FDI Inflows Shock', fontsize=16)
### NEW: Save the plot ###
plt.savefig(os.path.join(PLOT_FOLDER, 'IRF_Response_of_CPRI_to_FDI_Shock.png'))
print(f"Plot saved to {os.path.join(PLOT_FOLDER, 'IRF_Response_of_CPRI_to_FDI_Shock.png')}")
plt.show()

# =============================================================================
# SECTION 8: INDIVIDUAL EVENT STUDIES WITH QUANTITATIVE RESULTS
# =============================================================================
country_full_names = {
    'USA': 'United States', 'DEU': 'Germany', 'JPN': 'Japan', 'GBR': 'United Kingdom', 'FRA': 'France',
    'CAN': 'Canada', 'AUS': 'Australia', 'IND': 'India', 'BRA': 'Brazil', 'ZAF': 'South Africa'
}
event_study_results = []
for country_code, event_details in EVENT_LIST.items():
    result = perform_event_study(
        ticker=COUNTRY_CONFIG[country_code],
        event_date_str=event_details['date'],
        window_size=10,
        country_name=country_full_names[country_code],
        event_name=event_details['name'],
        plot_folder=PLOT_FOLDER  ### NEW: Pass the folder name ###
    )
    if result is not None:
        event_study_results.append(result)

if event_study_results:
    results_df = pd.DataFrame(event_study_results)
    print("\n\n" + "=" * 80)
    print(" " * 15 + "SECTION 8: Quantitative Event Study Summary")
    print("=" * 80)
    print(results_df.to_string())
    print("=" * 80)

print("\n--- Project Complete ---")