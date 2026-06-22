with open(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\impacts_dependencies_PRD.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("prd_tasks.txt", "w", encoding="utf-8") as out_f:
    out_f.write(f"Total lines: {len(lines)}\n")
    for idx, line in enumerate(lines):
        if "kanban-title" in line or "h2" in line or "h3" in line or "h1" in line:
            out_f.write(f"\nLine {idx+1}: {line.strip()}\n")
            # print the next 20 lines
            for offset in range(1, 25):
                if idx + offset < len(lines):
                    out_f.write(f"  +{offset}: {lines[idx+offset].strip()}\n")

print("Done writing tasks to prd_tasks.txt")
