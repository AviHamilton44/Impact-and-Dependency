import os
import sys
import uuid

BACKEND_DIR = "c:\\Users\\Admin\\OneDrive\\Desktop\\Impact & Dependency\\Backend"
sys.path.append(BACKEND_DIR)

from app.database import SessionLocal
from app.models.models import Site, SiteEncoreScore, SiteSonScore

db = SessionLocal()
try:
    # Try to delete the first site we find
    site = db.query(Site).first()
    if site:
        site_id = site.site_id
        print("FOUND SITE TO DELETE:", site.name, site_id)
        
        # Try deleting just like the backend route does:
        print("Deleting SiteEncoreScore...")
        db.query(SiteEncoreScore).filter(SiteEncoreScore.site_id == site_id).delete()
        print("Deleting SiteSonScore...")
        db.query(SiteSonScore).filter(SiteSonScore.site_id == site_id).delete()
        print("Deleting Site...")
        db.delete(site)
        
        print("Committing transaction...")
        db.commit()
        print("TRANSACTION SUCCESS!")
    else:
        print("NO SITES FOUND IN DB")
except Exception as e:
    db.rollback()
    print("TRANSACTION FAILED!")
    import traceback
    traceback.print_exc()
finally:
    db.close()
