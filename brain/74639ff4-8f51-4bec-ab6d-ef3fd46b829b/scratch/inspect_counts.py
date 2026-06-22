import pandas as pd

df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_imp = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE impacts materiality_Mar 2023_Transposed.csv")

processes = ['Large-scale irrigated arable crops', 'Airport services', 'Mining']
for p in processes:
    dep_subset = df_dep[df_dep['Process'] == p]
    imp_subset = df_imp[df_imp['Production process'] == p]
    print(f"\nProcess: {p}")
    print(f"  Dependencies count: {len(dep_subset)}")
    print(dep_subset[['Ecosystem Service', 'Rating']].to_string())
    print(f"  Impacts count: {len(imp_subset)}")
    print(imp_subset[['Impact driver', 'Rating']].to_string())
