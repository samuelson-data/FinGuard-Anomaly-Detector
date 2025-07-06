import pandas as pd
import numpy as np

# Simulate realistic banking transaction data
np.random.seed(42)

data = {
    "Account Number": np.random.choice(["0123456789", "9876543210", "1234567890"], size=100),
    "Date": pd.date_range(start="2025-01-01", periods=100, freq='D'),
    "Transaction Type": np.random.choice(["Credit", "Debit"], size=100),
    "Amount (₦)": np.random.randint(1_000, 3_000_000, size=100),
    "Country": np.random.choice(["Nigeria", "Ghana", "UK", "Kenya"], size=100, p=[0.7, 0.1, 0.1, 0.1]),
    "Channel": np.random.choice(["ATM", "POS", "USSD", "Mobile", "Online"], size=100)
}

df = pd.DataFrame(data)
# Rule-based flags
df["Flag_Amount"] = df["Amount (₦)"] > 1_000_000
df["Flag_Foreign"] = df["Country"] != "Nigeria"
df["Flag_Channel"] = (df["Amount (₦)"] > 500_000) & (df["Channel"].isin(["POS", "USSD"]))

# Burst detection
df['Day_Count'] = df.groupby(['Account Number', 'Date'])['Date'].transform('count')
df["Flag_Burst"] = df["Day_Count"] > 3

# Combine flags
df["Flagged"] = df[["Flag_Amount", "Flag_Foreign", "Flag_Channel", "Flag_Burst"]].any(axis=1)
# Create flag reason column
def get_reasons(row):
    reasons = []
    if row["Flag_Amount"]: reasons.append("High Amount")
    if row["Flag_Foreign"]: reasons.append("Foreign")
    if row["Flag_Channel"]: reasons.append("Channel Risk")
    if row["Flag_Burst"]: reasons.append("Burst Activity")
    return ", ".join(reasons)

df["Reason"] = df.apply(get_reasons, axis=1)

# Summary
summary = pd.DataFrame({
    "Total Transactions": [len(df)],
    "Flagged": [df["Flagged"].sum()],
    "Percentage Flagged": [round(df["Flagged"].mean() * 100, 2)]
})

# Export to Excel
with pd.ExcelWriter("/mnt/data/FinGuard_Transaction_Report.xlsx", engine="openpyxl") as writer:
    df[df["Flagged"]].to_excel(writer, sheet_name="Suspicious_Transactions", index=False)
    df[~df["Flagged"]].to_excel(writer, sheet_name="Normal_Transactions", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)
