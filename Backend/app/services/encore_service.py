from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import IndustryLeapData, SiteEncoreScore

def get_encore_scores_for_activities(db: Session, activity_names: List[str]) -> Dict[str, str]:
    """
    Fetches and aggregates ENCORE scores for multiple activities using MAX value logic.
    """
    # Mapping of impact_driver to EP fields
    EP_MAP = {
        "Water use": "ep_water_use",
        "Freshwater ecosystem use": "ep_freshwater_use",
        "Soil pollutants": "ep_toxic_emissions",
        "Water pollutants": "ep_nutrient_emissions",
        "Disturbances": "ep_disturbances",
        "Air pollutants": "ep_non_ghg_air_pollution",
        "Non-GHG air pollutants": "ep_non_ghg_air_pollution",
        "Terrestrial ecosystem use": "ep_land_use",
        "GHG emissions": "ep_ghg_emissions",
        "Solid waste": "ep_solid_waste",
        "Other resource use": "ep_other_resource_use",
        "Marine ecosystem use": "ep_marine_pollution",
    }
    
    # Mapping of dependency_type to Dependency fields
    DEP_MAP = {
        "Water supply": "dep_water_supply",
        "Surface water": "dep_water_supply",
        "Ground water": "dep_water_supply",
        "Soil sediment retention": "dep_soil_sediment_retention",
        "Mass stabilisation and erosion control": "dep_soil_sediment_retention",
        "Soil quality": "dep_soil_sediment_retention",
        "Biodiversity": "dep_overall_dependency_biodiversity",
        "Maintain nursery habitats": "dep_overall_dependency_biodiversity",
        "Flood and storm protection": "dep_flood_and_storm_protection",
        "Pollination": "dep_pollination",
        "Pest control": "dep_pest_control",
        "Climate regulation": "dep_climate_regulation",
    }

    # Initial scores
    scores = {field: "VL" for field in [
        "ep_water_use", "ep_freshwater_use", "ep_toxic_emissions", "ep_nutrient_emissions",
        "ep_disturbances", "ep_non_ghg_air_pollution", "ep_land_use", "ep_overall_pressure_biodiversity",
        "ep_ghg_emissions", "ep_solid_waste", "ep_other_resource_use", "ep_marine_pollution",
        "dep_water_supply", "dep_soil_sediment_retention", "dep_overall_dependency_biodiversity",
        "dep_flood_and_storm_protection", "dep_pollination", "dep_pest_control", "dep_climate_regulation"
    ]}
    
    rating_rank = {"VL": 1, "L": 2, "M": 3, "H": 4, "VH": 5, "ND": 1}
    rank_rating = {1: "VL", 2: "L", 3: "M", 4: "H", 5: "VH"}

    for activity in activity_names:
        data = db.query(IndustryLeapData).filter(IndustryLeapData.activity_name == activity).all()
        for row in data:
            # Handle Pressures
            if row.impact_driver in EP_MAP:
                field = EP_MAP[row.impact_driver]
                current_rank = rating_rank.get(scores[field], 1)
                new_rank = rating_rank.get(row.impact_rating, 1)
                if new_rank > current_rank:
                    scores[field] = rank_rating[new_rank]
            
            # Special case for overall biodiversity pressure (often GHG or Land Use)
            if row.impact_driver in ["GHG emissions", "Terrestrial ecosystem use"]:
                field = "ep_overall_pressure_biodiversity"
                current_rank = rating_rank.get(scores[field], 1)
                new_rank = rating_rank.get(row.impact_rating, 1)
                if new_rank > current_rank:
                    scores[field] = rank_rating[new_rank]

            # Handle Dependencies
            if row.ecosystem_service in DEP_MAP:
                field = DEP_MAP[row.ecosystem_service]
                current_rank = rating_rank.get(scores[field], 1)
                new_rank = rating_rank.get(row.severity, 1) # severity is the rating for dependencies
                if new_rank > current_rank:
                    scores[field] = rank_rating[new_rank]

                    
    return scores
