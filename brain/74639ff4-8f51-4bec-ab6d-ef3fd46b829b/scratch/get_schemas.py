with open(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\impacts_dependencies_PRD.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("prd_schemas.txt", "w", encoding="utf-8") as out_f:
    capture = False
    for idx, line in enumerate(lines):
        if "id=\"datamodel\"" in line or "<h2>Data Model</h2>" in line:
            capture = True
        if "id=\"computed\"" in line or "<h2>Computed Logic</h2>" in line:
            capture = False
        if capture:
            out_f.write(f"{idx+1}: {line}")

print("Done writing schemas to prd_schemas.txt")
