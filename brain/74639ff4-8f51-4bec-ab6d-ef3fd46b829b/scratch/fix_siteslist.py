path = r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Client\src\pages\SitesList.jsx"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace onClick
old_str = "onClick={() => handleDeleteSite(site.site_id)}"
new_str = "onClick={(e) => handleDeleteSite(site.site_id, e)}"

if old_str in content:
    content = content.replace(old_str, new_str)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully replaced onClick handler in SitesList.jsx!")
else:
    print("Target string not found in SitesList.jsx!")
