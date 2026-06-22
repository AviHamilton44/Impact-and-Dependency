import pandas as pd

print("--- ENCORE dependency materialities.csv ---")
try:
    df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
    print(f"Shape: {df_dep.shape}")
    print(f"Columns: {df_dep.columns.tolist()[:15]}")
    print("First 3 rows:")
    print(df_dep.head(3).to_string())
except Exception as e:
    print(f"Error reading dep: {e}")

print("\n--- ENCORE impacts materiality_Mar 2023_Transposed.csv ---")
try:
    df_imp = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE impacts materiality_Mar 2023_Transposed.csv")
    print(f"Shape: {df_imp.shape}")
    print(f"Columns: {df_imp.columns.tolist()[:15]}")
    print("First 3 rows:")
    print(df_imp.head(3).to_string())
except Exception as e:
    print(f"Error reading imp: {e}")
