import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append("c:\\Users\\Admin\\OneDrive\Desktop\\Impact & Dependency\\Backend")
from app.models.models import Site, SiteEncoreScore, SiteSonScore

load_dotenv(dotenv_path="Backend/.env")
db_url = os.getenv("DATABASE_URL", "sqlite:///./tnfd_local.db")
print(f"Connecting to database: {db_url}")

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    site_id = uuid.uuid4()
    
    # 1. Create Site
    site = Site(
        site_id=site_id,
        name="Serengeti Conservation Area",
        country="Tanzania",
        latitude=-2.154,
        longitude=34.685,
        biome_code="T1",
        activities=["Crop production", "Ecotourism"],
        geometry={"type": "Polygon", "coordinates": [[[34.5, -2.2], [34.8, -2.2], [34.8, -2.0], [34.5, -2.0], [34.5, -2.2]]]}
    )
    db.add(site)
    
    # 2. Create SiteEncoreScore
    encore = SiteEncoreScore(
        site_id=site_id,
        ep_water_use="VH",
        ep_freshwater_use="VH",
        ep_toxic_emissions="M",
        ep_nutrient_emissions="L",
        ep_disturbances="VH",
        ep_non_ghg_air_pollution="L",
        ep_land_use="VH",
        ep_overall_pressure_biodiversity="VH",
        ep_ghg_emissions="H",
        ep_solid_waste="M",
        ep_other_resource_use="L",
        ep_marine_pollution="VL",
        dep_water_supply="VH",
        dep_soil_sediment_retention="H",
        dep_overall_dependency_biodiversity="VH",
        dep_flood_and_storm_protection="M",
        dep_pollination="VH",
        dep_pest_control="H",
        dep_climate_regulation="VH"
    )
    db.add(encore)
    
    # 3. Create SiteSonScore with GEE metrics
    son = SiteSonScore(
        site_id=site_id,
        dim1_extent_level="H",
        dim2_freshwater_level="H",
        dim2_terrestrial_level="H",
        dim3_population_level="M",
        dim4_extinction_level="L",
        biome_code="T1",
        data_confidence="high",
        measured_metrics_count=27,
        metrics={
            "SoN Score": 3.8,
            "Extent": 4.1,
            "Condition": 3.9,
            "Population": 3.2,
            "Extinction": 2.5,
            "metric_concerns": {
                "aridity_index": {"site_value": 0.45, "concern_numeric": 3.5, "protocol": "A", "intactness_used": 0.45},
                "tspi": {"site_value": 2.1, "concern_numeric": 2.0, "protocol": "A", "intactness_used": 0.8},
                "sabf": {"site_value": 0.05, "concern_numeric": 1.2, "protocol": "A", "intactness_used": 0.95},
                "wcpi": {"site_value": 0.88, "concern_numeric": 1.5, "protocol": "A", "intactness_used": 0.88},
                "wsdi": {"site_value": 0.12, "concern_numeric": 2.2, "protocol": "A", "intactness_used": 0.88},
                "jrc_water_persistence": {"site_value": 0.92, "concern_numeric": 1.1, "protocol": "A", "intactness_used": 0.92},
                "shdi": {"site_value": 0.75, "concern_numeric": 2.5, "protocol": "A", "intactness_used": 0.75},
                "rci": {"site_value": 0.65, "concern_numeric": 2.8, "protocol": "A", "intactness_used": 0.65},
                "natural_habitat": {"site_value": 0.82, "concern_numeric": 2.1, "protocol": "A", "intactness_used": 0.82},
                "natural_landcover": {"site_value": 0.85, "concern_numeric": 1.9, "protocol": "A", "intactness_used": 0.85},
                "cpland": {"site_value": 0.68, "concern_numeric": 2.8, "protocol": "A", "intactness_used": 0.68},
                "kba_overlap": {"site_value": 45.0, "concern_numeric": 3.0, "protocol": "A", "intactness_used": 0.45},
                "flii": {"site_value": 8.5, "concern_numeric": 1.8, "protocol": "A", "intactness_used": 0.85},
                "eii": {"site_value": 0.78, "concern_numeric": 2.2, "protocol": "A", "intactness_used": 0.78},
                "bii": {"site_value": 0.81, "concern_numeric": 2.0, "protocol": "A", "intactness_used": 0.81},
                "pdf": {"site_value": 0.12, "concern_numeric": 2.4, "protocol": "A", "intactness_used": 0.88},
                "endemic_richness": {"site_value": 0.62, "concern_numeric": 2.9, "protocol": "A", "intactness_used": 0.62},
                "flagship_habitat": {"site_value": 0.77, "concern_numeric": 2.3, "protocol": "A", "intactness_used": 0.77},
                "endemic_plant_richness": {"site_value": 0.58, "concern_numeric": 3.1, "protocol": "A", "intactness_used": 0.58},
                "threatened_richness": {"site_value": 35.0, "concern_numeric": 3.8, "protocol": "A", "intactness_used": 0.65},
                "ceri": {"site_value": 0.42, "concern_numeric": 3.2, "protocol": "A", "intactness_used": 0.58},
                "star_t": {"site_value": 2.8, "concern_numeric": 2.8, "protocol": "A", "intactness_used": 0.72},
                "threatened_plant_richness": {"site_value": 22.0, "concern_numeric": 3.4, "protocol": "A", "intactness_used": 0.78},
                "ndvi": {"site_value": 0.65, "concern_numeric": 2.2, "protocol": "A", "intactness_used": 0.65},
                "habitat_health": {"site_value": 0.72, "concern_numeric": 2.1, "protocol": "A", "intactness_used": 0.72},
                "lai": {"site_value": 2.4, "concern_numeric": 2.3, "protocol": "A", "intactness_used": 0.48},
                "chm": {"site_value": 12.0, "concern_numeric": 2.5, "protocol": "A", "intactness_used": 0.60},
                "forest_loss_rate": {"site_value": 1.2, "concern_numeric": 1.8, "protocol": "A", "intactness_used": 0.98},
                "riparian_ndvi_trend": {"site_value": 0.02, "concern_numeric": 2.0, "protocol": "A", "intactness_used": 0.50},
                "ghm": {"site_value": 0.15, "concern_numeric": 1.8, "protocol": "A", "intactness_used": 0.85},
                "hdi": {"site_value": 0.22, "concern_numeric": 2.2, "protocol": "A", "intactness_used": 0.78},
                "light_pollution": {"site_value": 0.08, "concern_numeric": 1.4, "protocol": "A", "intactness_used": 0.92}
            }
        }
    )
    db.add(son)
    db.commit()
    print(f"Successfully seeded Serengeti site with ID: {site_id}")
except Exception as e:
    db.rollback()
    print(f"Error seeding: {e}")
finally:
    db.close()
