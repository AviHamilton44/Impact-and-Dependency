import pandas as pd

df = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\ACTIVITY_LEAP_DATA.csv")
print("Columns in ACTIVITY_LEAP_DATA.csv:")
print(df.columns.tolist())
print("\nUnique Activity Names in ACTIVITY_LEAP_DATA.csv:")
print(df['Activity Name'].dropna().unique()[:20])
