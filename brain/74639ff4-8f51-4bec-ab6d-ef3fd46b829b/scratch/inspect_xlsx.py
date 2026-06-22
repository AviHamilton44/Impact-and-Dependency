import pandas as pd

try:
    xls = pd.ExcelFile(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependencies database.xlsx")
    print(f"Sheet names: {xls.sheet_names}")
    for name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=name)
        print(f"Sheet '{name}' - Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()[:10]}")
except Exception as e:
    print(f"Error reading xlsx: {e}")
