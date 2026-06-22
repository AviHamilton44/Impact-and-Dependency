import sys
import uuid

# Add Backend folder to path
sys.path.append(r"c:\Users\Admin\OneDrive\Desktop\Impact & Dependency\Backend")

from app.database import SessionLocal
from app.models.models import Site, SiteEncoreScore, SiteSonScore

db = SessionLocal()

# Let's count before
site = db.query(Site).first()
if site:
    site_id = site.site_id
    print(f"Attempting to delete Site {site.name} ({site_id})...")
    try:
        # Check if we can delete SiteSonScore
        db.query(SiteSonScore).filter(SiteSonScore.site_id == site_id).delete()
        # Delete site (which cascades to SiteEncoreScore)
        db.delete(site)
        db.commit()
        print("Success! Site deleted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during deletion: {e}")
else:
    print("No sites to delete.")
