import pandas as pd

df = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx", header=None)
print("Row 0:")
print(df.iloc[0].tolist()[:15])
print("\nRow 1:")
print(df.iloc[1].tolist()[:15])
print("\nRow 2:")
print(df.iloc[2].tolist()[:15])
print("\nRow 3:")
print(df.iloc[3].tolist()[:15])
