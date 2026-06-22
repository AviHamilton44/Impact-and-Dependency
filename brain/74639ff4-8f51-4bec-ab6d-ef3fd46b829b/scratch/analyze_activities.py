import pandas as pd

df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
df_imp = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE impacts materiality_Mar 2023_Transposed.csv")

print("--- Unique Processes in Dependency CSV ---")
print(df_dep['Process'].unique()[:10])
print(f"Total unique processes: {df_dep['Process'].nunique()}")

print("\n--- Unique Processes in Impact CSV ---")
print(df_imp['Production process'].unique()[:10])
print(f"Total unique processes: {df_imp['Production process'].nunique()}")

# Let's see an example process, e.g., 'Agricultural products'
print("\n--- Dependencies for 'Agricultural products' or 'Agriculture products' ---")
# Check if any process matches agriculture
agri_dep = df_dep[df_dep['Process'].str.contains('Agri', case=False, na=False)]
print(f"Matching processes in Dep: {agri_dep['Process'].unique()}")
print(agri_dep[['Process', 'Ecosystem Service', 'Rating']].head(10))

print("\n--- Impacts for 'Agricultural products' or 'Agriculture products' ---")
agri_imp = df_imp[df_imp['Production process'].str.contains('Agri', case=False, na=False)]
print(f"Matching processes in Imp: {agri_imp['Production process'].unique()}")
print(agri_imp[['Production process', 'Impact driver', 'Rating']].head(10))
