import pandas as pd
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

df_csv = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_xlsx = pd.read_excel(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx", header=None)

headers = [str(x).strip() for x in df_xlsx.iloc[1]]
process_rows = {}
for idx, row in df_xlsx.iloc[2:].iterrows():
    p_name = str(row[2]).strip()
    process_rows[p_name] = row

def get_excel_justification(process, service):
    if process not in process_rows:
        return None
    row = process_rows[process]
    best_col_idx = None
    best_score = 0
    for idx, h in enumerate(headers):
        if idx < 3: continue
        score = similarity(service, h)
        if service.lower() in h.lower() or h.lower() in service.lower():
            score += 0.5
        if score > best_score:
            best_score = score
            best_col_idx = idx
            
    if best_col_idx is not None and best_score >= 0.5:
        val = row[best_col_idx]
        if pd.notna(val) and str(val).strip() != "" and str(val).strip().lower() != "nan":
            return str(val).strip()
    return None

# Test with Airport services and Ground water
p = "Airport services"
s = "Ground water"
excel_just = get_excel_justification(p, s)
csv_just = df_csv[(df_csv['Process'] == p) & (df_csv['Ecosystem Service'] == s)]['Justification'].values[0]

print(f"Process: {p}, Service: {s}")
print(f"Excel Justification:\n{excel_just}")
print(f"CSV Justification:\n{csv_just}")
