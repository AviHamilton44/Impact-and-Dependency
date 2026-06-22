import pandas as pd

df_dep = pd.read_csv(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend\ENCORE dependency materialities.csv")
processes = sorted(df_dep['Process'].dropna().unique())
with open("unique_processes.txt", "w", encoding="utf-8") as f:
    for p in processes:
        f.write(f"{p}\n")

print(f"Written {len(processes)} unique processes to unique_processes.txt")
