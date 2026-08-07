import os
import sys
import uuid

# Setup PYTHONPATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = "c:\\Users\\Admin\\OneDrive\\Desktop\\Impact & Dependency\\Backend"
sys.path.append(BACKEND_DIR)

from app.database import SessionLocal
from app.models.models import Site, SiteEncoreScore, SiteSonScore
from app.services.computation_service import calculate_tnfd_outputs
import pprint

db = SessionLocal()
try:
    site_uuid = uuid.UUID('a3b31508-1541-43da-8f1e-5f753528c2f2')
    site = db.query(Site).filter(Site.site_id == site_uuid).first()
    encore = db.query(SiteEncoreScore).filter(SiteEncoreScore.site_id == site_uuid).first()
    son = db.query(SiteSonScore).filter(SiteSonScore.site_id == site_uuid).first()
    
    print("SITE FOUND:", site is not None)
    print("ENCORE FOUND:", encore is not None)
    print("SON FOUND:", son is not None)
    print("SON HAS METRICS:", hasattr(son, "metrics") and son.metrics is not None)
    
    if site and encore and son:
        print("\n--- Running TNFD Computations ---")
        outputs = calculate_tnfd_outputs(site, encore, son)
        print("Archetype:", outputs.get("archetype"))
        print("\nSensitivity Indices:")
        pprint.pprint(outputs.get("sensitivity_indices"))
        print("\nData Quality:")
        pprint.pprint(outputs.get("data_quality"))
        print("\nAll Indicators (All 32):")
        pprint.pprint(outputs.get("all_indicators"))
        
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
