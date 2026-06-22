import pandas as pd

df_csv = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_xlsx = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx")

csv_services = sorted(df_csv['Ecosystem Service'].dropna().unique())
excel_services = list(df_xlsx.columns[3:32]) # Col 3 to Col 31

print("CSV Services:")
for s in csv_services:
    print(f"  - {s}")

print("\nExcel columns (Services):")
for idx, s in enumerate(excel_services):
    print(f"  - {idx}: {s}")
