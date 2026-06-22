import pandas as pd

df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_imp = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE impacts materiality_Mar 2023_Transposed.csv")

p = 'Large-scale irrigated arable crops'
with open("duplicates_output.txt", "w", encoding="utf-8") as f:
    f.write(f"--- Unique dependencies for {p} ---\n")
    dep_p = df_dep[df_dep['Process'] == p]
    f.write(dep_p.drop_duplicates(subset=['Ecosystem Service']).to_string())
    f.write("\n\n")

    f.write(f"--- Unique impacts for {p} ---\n")
    imp_p = df_imp[df_imp['Production process'] == p]
    f.write(imp_p.drop_duplicates(subset=['Impact driver']).to_string())
    f.write("\n")

print("Done writing to duplicates_output.txt")
