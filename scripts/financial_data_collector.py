import yfinance as yf
import pandas as pd
import os

# --- Prepare folder ---
os.makedirs("data", exist_ok=True)

# --- Load ticker ---
ticker = yf.Ticker("BRK-B")

# --- Download financial statements and verify ---
income = ticker.financials
balance = ticker.balance_sheet

if income.empty or balance.empty:
    raise RuntimeError(f"No financial data for {ticker.ticker}: "
                       f"income.empty={income.empty}, balance.empty={balance.empty}")

print("Income statement rows:", income.index.tolist())
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
df.to_csv(csv_path, index=False)
print(f"Financial data saved to {csv_path}")
print(df)