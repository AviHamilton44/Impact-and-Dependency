import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import Site, SiteSonScore

db = SessionLocal()
sites = db.query(Site).all()

count = 0
for s in sites:
    if not s.son_score:
        default_son = SiteSonScore(
            site_id=s.site_id,
            dim1_extent_level='VL',
            dim2_freshwater_level='VL',
            dim2_terrestrial_level='VL',
            dim3_population_level='VL',
            dim4_extinction_level='VL',
            biome_code='T1',
            data_confidence='low',
            measured_metrics_count=0
        )
        db.add(default_son)
        count += 1

db.commit()
print(f"Added {count} default SoN scores.")
