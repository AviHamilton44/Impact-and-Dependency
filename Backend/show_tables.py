import pandas as pd
from app.database import SessionLocal
from app.models.models import Site, SiteEncoreScore

def show_tables():
    db = SessionLocal()
    
    # Query the joined data
    query = db.query(
        Site.name, 
        Site.activities,
        SiteEncoreScore.ep_water_use,
        SiteEncoreScore.ep_land_use,
        SiteEncoreScore.ep_toxic_emissions,
        SiteEncoreScore.ep_nutrient_emissions,
        SiteEncoreScore.ep_overall_pressure_biodiversity,
        SiteEncoreScore.dep_water_supply,
        SiteEncoreScore.dep_soil_sediment_retention,
        SiteEncoreScore.dep_overall_dependency_biodiversity
    ).join(SiteEncoreScore, Site.site_id == SiteEncoreScore.site_id).limit(15)
    
    data = query.all()
    
    # Format into a DataFrame for a nice markdown table output
    df = pd.DataFrame(data, columns=[
        "Site Name", "Industry", 
        "Water Use (Impact)", "Land Use (Impact)", "Toxic Emissions (Impact)", 
        "Nutrient Emissions (Impact)", "Biodiversity (Impact)",
        "Water Supply (Dep)", "Soil Retention (Dep)", "Biodiversity (Dep)"
    ])
    
    # Clean up the Industry array column
    df["Industry"] = df["Industry"].apply(lambda x: x[0] if x else "N/A")
    
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    show_tables()
