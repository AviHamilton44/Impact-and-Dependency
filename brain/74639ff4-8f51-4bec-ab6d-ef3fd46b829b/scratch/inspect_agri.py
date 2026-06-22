import pandas as pd

df = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\ACTIVITY_LEAP_DATA.csv")
df['Activity Name'] = df['Activity Name'].ffill()

agri_rows = df[df['Activity Name'].str.contains('Agricultural Products', case=False, na=False)]
print(f"Number of rows: {len(agri_rows)}")
print(agri_rows[['Activity Name', 'Ecosystem Service', 'Severity', 'Impact Driver', 'Impact Rating']].to_string())
