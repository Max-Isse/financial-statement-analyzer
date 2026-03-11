import pandas as pd

data = pd.read_csv("../data/company_financials.csv")

data["Profit_Margin"] = data["Net_Income"] / data["Revenue"]

data["Debt_Ratio"] = data["Total_Debt"] / data["Total_Assets"]

print(data[["Year","Profit_Margin","Debt_Ratio"]])