import yfinance as yf
import pandas as pd
import os

# --- Prepare folder ---
os.makedirs("data", exist_ok=True)

# --- choose ticker symbol (can also be overridden by env var) ---
ticker_symbol = os.environ.get("TICKER", "BRK-B")
print(f"Fetching financials for {ticker_symbol} ...")

ticker = yf.Ticker(ticker_symbol)

# --- Download financial statements ---
try:
    income = ticker.financials
    balance = ticker.balance_sheet
except Exception as exc:
    # network or parsing error; still build empty DataFrame later
    print(f"Warning: failed to fetch financials: {exc}")
    income = pd.DataFrame()
    balance = pd.DataFrame()

if income.empty or balance.empty:
    print(f"Warning: missing data for {ticker_symbol} (income.empty={income.empty}, balance.empty={balance.empty})")

if not income.empty:
    print("Income statement rows:", income.index.tolist())
if not balance.empty:
    print("Balance sheet rows:", balance.index.tolist())

# --- Safe extraction function ---
def safe_extract(df, possible_names):
    """Try several row names and warn if none are present."""
    for name in possible_names:
        if name in df.index:
            return df.loc[name]
    print(f"Warning: none of {possible_names} found in index {df.index.tolist()}")
    return pd.Series([None]*df.shape[1], index=df.columns)

# --- Extract metrics ---
revenue = safe_extract(income, ["Total Revenue", "Revenue", "Revenues"])
net_income = safe_extract(income, ["Net Income", "Net Earnings"])
total_assets = safe_extract(balance, ["Total Assets"])
total_debt = safe_extract(balance, ["Long Term Debt", "Total Debt"])

# if all values are None/NaN, warn but continue
for name, series in ("revenue", revenue), ("net_income", net_income), ("total_assets", total_assets), ("total_debt", total_debt):
    if series.isnull().all():
        print(f"Warning: extracted {name} contains only nulls")

# --- Combine into DataFrame ---
df = pd.DataFrame({
    "Revenue": revenue,
    "Net_Income": net_income,
    "Total_Assets": total_assets,
    "Total_Debt": total_debt
})

df = df.T
df.reset_index(inplace=True)
df.rename(columns={"index":"Year"}, inplace=True)

# --- Convert all year/period columns to numeric (values in rows are metrics) ---
for col in df.columns:
    if col == "Year":
        continue
    df[col] = pd.to_numeric(df[col], errors="coerce") / 1e6

# --- Save CSV ---
csv_path = os.path.join("data","company_financials.csv")
try:
    df.to_csv(csv_path, index=False)
    print(f"Financial data saved to {csv_path}")
except Exception as exc:
    print(f"Error saving CSV: {exc}")

print(df)