import pandas as pd

df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
services = sorted(df_dep['Ecosystem Service'].dropna().unique())
with open("unique_services.txt", "w", encoding="utf-8") as f:
    for s in services:
        f.write(f"{s}\n")

print(f"Written {len(services)} unique services to unique_services.txt")
