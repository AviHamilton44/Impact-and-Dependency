import os
import sys
import uuid
import json

BACKEND_DIR = "c:\\Users\\Admin\\OneDrive\\Desktop\\Impact & Dependency\\Backend"
sys.path.append(BACKEND_DIR)

from app.database import SessionLocal
from app.models.models import SiteSonScore

db = SessionLocal()
try:
    site_uuid = uuid.UUID('a3b31508-1541-43da-8f1e-5f753528c2f2')
    son = db.query(SiteSonScore).filter(SiteSonScore.site_id == site_uuid).first()
    if son:
        with open("brain/74639ff4-8f51-4bec-ab6d-ef3fd46b829b/scratch/metrics_dump.json", "w") as f:
            json.dump(son.metrics, f, indent=2)
        print("DUMP SUCCESS")
except Exception as e:
    print("ERROR:", e)
finally:
    db.close()
