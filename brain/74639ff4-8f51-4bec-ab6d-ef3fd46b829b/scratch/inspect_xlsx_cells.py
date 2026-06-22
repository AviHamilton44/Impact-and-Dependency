import pandas as pd

df = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx")
# Let's inspect unique values in a few columns
for col in df.columns[3:8]:
    print(f"\nUnique values in '{col}' (first 5 unique values):")
    print(df[col].dropna().unique()[:5])
