import pandas as pd

df_csv = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_xlsx = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx")

print("CSV processes (first 5):")
print(df_csv['Process'].dropna().unique()[:5])

print("\nExcel processes (first 5):")
print(df_xlsx.iloc[:, 2].dropna().unique()[:5])

print("\nAre all CSV processes in Excel?")
csv_p = set(df_csv['Process'].dropna().unique())
xlsx_p = set(df_xlsx.iloc[:, 2].dropna().unique())
missing = csv_p - xlsx_p
print(f"Missing in Excel: {len(missing)}")
if len(missing) > 0:
    print(list(missing)[:5])

print("\nAre all Excel processes in CSV?")
missing_csv = xlsx_p - csv_p
print(f"Missing in CSV: {len(missing_csv)}")
if len(missing_csv) > 0:
    print(list(missing_csv)[:5])
