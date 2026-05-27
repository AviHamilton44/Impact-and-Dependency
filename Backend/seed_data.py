import pandas as pd
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import IndustryLeapData, Site, SiteEncoreScore, SiteSonScore

def seed_data():
    # Drop problematic tables from old schema manually if they exist
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS site_state_of_nature CASCADE"))
        conn.commit()

    # Drop all and recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()

    # 1. Seed IndustryLeapData from CSV
    csv_path = "../ACTIVITY_LEAP_DATA.csv"
    try:
        df = pd.read_csv(csv_path)
        df['Activity Name'] = df['Activity Name'].ffill()
        df['SASB CODE'] = df['SASB CODE'].ffill()
        df['Industry'] = df['Industry'].ffill()

        print("Seeding IndustryLeapData...")
        for _, row in df.iterrows():
            item = IndustryLeapData(
                activity_name=str(row.get('Activity Name', '')).strip(),
                sasb_code=str(row.get('SASB CODE', '')).strip(),
                industry=str(row.get('Industry', '')).strip(),
                ecosystem_service=str(row.get('Ecosystem Service', '')).strip(),
                dependency_type=str(row.get('Dependency Type', '')).strip(),
                impact_driver=str(row.get('Impact Driver', '')).strip(),
                severity=str(row.get('Severity', '')).strip(),
                impact_rating=str(row.get('Impact Rating', '')).strip()
            )
            db.add(item)
        db.commit()
    except FileNotFoundError:
        print(f"CSV not found at {csv_path}, skipping industry data.")

    # 2. Seed Mock Sites
    print("Seeding 10 Mock Sites...")
    biomes = ["T1", "T2", "F1", "F2", "M1", "T8"]
    levels = ["VL", "L", "M", "H", "VH"]
    activities = db.query(IndustryLeapData.activity_name).distinct().all()
    activity_names = [a[0] for a in activities] if activities else ["Agriculture", "Mining", "Energy"]

    for i in range(10):
        site_id = uuid.uuid4()
        site_name = f"Site Alpha-{i+1}" if i < 5 else f"Project Green-{i-4}"
        
        # Site Metadata
        site = Site(
            site_id=site_id,
            name=site_name,
            country="India" if i % 2 == 0 else "Brazil",
            latitude=15.0 + random.uniform(-5, 5),
            longitude=75.0 + random.uniform(-5, 5),
            biome_code=random.choice(biomes),
            activities=[random.choice(activity_names)],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        db.add(site)

        # ENCORE Scores
        encore = SiteEncoreScore(
            site_id=site_id,
            ep_water_use=random.choice(levels),
            ep_freshwater_use=random.choice(levels),
            ep_toxic_emissions=random.choice(levels),
            ep_nutrient_emissions=random.choice(levels),
            ep_disturbances=random.choice(levels),
            ep_non_ghg_air_pollution=random.choice(levels),
            ep_land_use=random.choice(levels),
            ep_overall_pressure_biodiversity=random.choice(levels),
            ep_ghg_emissions=random.choice(levels),
            ep_solid_waste=random.choice(levels),
            ep_other_resource_use=random.choice(levels),
            ep_marine_pollution=random.choice(levels),
            dep_water_supply=random.choice(levels),
            dep_soil_sediment_retention=random.choice(levels),
            dep_overall_dependency_biodiversity=random.choice(levels),
            dep_flood_and_storm_protection=random.choice(levels),
            dep_pollination=random.choice(levels),
            dep_pest_control=random.choice(levels),
            dep_climate_regulation=random.choice(levels)
        )
        db.add(encore)

        # SoN Scores (Usually from SoN module, but we mock it here)
        son = SiteSonScore(
            site_id=site_id,
            dim1_extent_level=random.choice(levels),
            dim2_freshwater_level=random.choice(levels),
            dim2_terrestrial_level=random.choice(levels),
            dim3_population_level=random.choice(levels),
            dim4_extinction_level=random.choice(levels),
            biome_code=site.biome_code,
            data_confidence=random.choice(['low', 'medium', 'high']),
            measured_metrics_count=random.randint(0, 5)
        )
        db.add(son)

    db.commit()
    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_data()
