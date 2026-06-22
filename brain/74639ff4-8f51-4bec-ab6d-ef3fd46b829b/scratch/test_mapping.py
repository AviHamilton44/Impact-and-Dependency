import pandas as pd
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

df_csv = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_xlsx = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx", header=None)

csv_services = sorted(df_csv['Ecosystem Service'].dropna().unique())
excel_services = [str(x).strip() for x in df_xlsx.iloc[1, 3:32]]

print("Mapping CSV services to Excel columns:")
for s in csv_services:
    # Find exact or best match
    best_match = None
    best_score = 0.0
    for es in excel_services:
        score = similarity(s, es)
        # Check substrings
        if s.lower() in es.lower() or es.lower() in s.lower():
            score += 0.5
        if score > best_score:
            best_score = score
            best_match = es
    print(f"  '{s}' => '{best_match}' (score: {best_score:.2f})")
