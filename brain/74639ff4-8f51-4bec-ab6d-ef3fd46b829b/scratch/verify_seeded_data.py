import sys
import os

# Add Backend folder to path to import app modules
sys.path.append(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend")

from app.database import SessionLocal
from app.models.models import IndustryLeapData, Site
from app.routers.sites import get_site_detail

db = SessionLocal()

leap_count = db.query(IndustryLeapData).count()
site_count = db.query(Site).count()

print(f"Number of IndustryLeapData rows: {leap_count}")
print(f"Number of Site rows: {site_count}")

# Fetch one site
site = db.query(Site).first()
if site:
    print(f"\nVerifying Site: {site.name} (Activities: {site.activities})")
    detail = get_site_detail(site.site_id, db)
    analysis = detail["analysis"]
    
    print("\nTop 5 Impacts:")
    top_impacts = analysis.get("top_impacts", [])
    print(f"Count: {len(top_impacts)}")
    for imp in top_impacts:
        print(f"  - {imp['impact_driver']}: {imp['rating']}")
        
    print("\nTop 5 Dependencies:")
    top_dependencies = analysis.get("top_dependencies", [])
    print(f"Count: {len(top_dependencies)}")
    for dep in top_dependencies:
        print(f"  - {dep['ecosystem_service']}: {dep['rating']} (Justification: {dep['justification'][:60]}...)")
else:
    print("No sites found!")
