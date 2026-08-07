import os
import json
import hashlib
import random
import uuid
from typing import Dict, Any, List, Optional

# Load weights configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "weights_config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        WEIGHTS_CONFIG = json.load(f)
except Exception as e:
    print(f"Error loading weights_config.json: {e}")
    WEIGHTS_CONFIG = {"indices": {}}

# Conversion map from ENCORE rating to weight (0.0 to 1.0)
RATING_WEIGHT_MAP = {
    "VL": 0.2,
    "L": 0.4,
    "M": 0.6,
    "H": 0.8,
    "VH": 1.0,
    "ND": 0.2
}

def get_rating_level(score: float) -> str:
    """Map a 0-100 score to a level rating."""
    if score < 20:
        return "VL"
    elif score < 40:
        return "L"
    elif score < 60:
        return "M"
    elif score < 80:
        return "H"
    else:
        return "VH"

def generate_site_indicators(site_obj: Any, config: dict) -> tuple:
    """
    Deterministically generates 36 normalized spatial environmental indicators (0-100)
    for a site based on its geometry or UUID.
    """
    geom_str = str(site_obj.geometry) if hasattr(site_obj, "geometry") and site_obj.geometry else str(getattr(site_obj, "site_id", uuid.uuid4()))
    seed_hash = int(hashlib.md5(geom_str.encode('utf-8')).hexdigest(), 16) % (2**32)
    rng = random.Random(seed_hash)
    
    # Choose archetype deterministically
    archetype = rng.choice(["rainforest", "arid", "coastal", "agricultural"])
    
    indicators = {}
    
    for index_name, index_data in config.get("indices", {}).items():
        for ind_name, ind_props in index_data.items():
            direction = ind_props.get("direction", "direct")
            
            # Base value generation based on archetype
            val = 50.0
            if archetype == "rainforest":
                if ind_name in ["forest_cover", "species_richness", "threatened_species", "endemic_species", 
                               "mammal_richness", "bird_richness", "edna_richness", "wetland_area", 
                               "ndvi", "evi", "carbon_stock", "above_ground_biomass", "rainfall", 
                               "soil_organic_carbon", "soil_moisture", "soil_fertility", "ecosystem_integrity"]:
                    val = rng.uniform(70.0, 98.0)
                elif ind_name in ["water_stress", "drought_risk", "fire_risk", "built_up_area", "agricultural_land"]:
                    val = rng.uniform(5.0, 25.0)
                elif ind_name in ["distance_to_rivers"]:
                    val = rng.uniform(5.0, 30.0) # meaning close to rivers
                else:
                    val = rng.uniform(30.0, 70.0)
                    
            elif archetype == "arid":
                if ind_name in ["water_stress", "drought_risk", "fire_risk", "temperature", "soil_erosion"]:
                    val = rng.uniform(75.0, 99.0)
                elif ind_name in ["forest_cover", "wetland_area", "mangrove_area", "ndvi", "evi", 
                               "carbon_stock", "above_ground_biomass", "rainfall", "soil_moisture", 
                               "ecosystem_integrity"]:
                    val = rng.uniform(0.0, 15.0)
                elif ind_name in ["distance_to_rivers"]:
                    val = rng.uniform(70.0, 95.0) # far from rivers
                else:
                    val = rng.uniform(20.0, 50.0)
                    
            elif archetype == "coastal":
                if ind_name in ["mangrove_area", "wetland_area", "water_bodies", "surface_water_availability", 
                               "rainfall", "soil_moisture"]:
                    val = rng.uniform(65.0, 95.0)
                elif ind_name in ["fire_risk", "drought_risk", "built_up_area", "grassland"]:
                    val = rng.uniform(10.0, 30.0)
                elif ind_name in ["distance_to_rivers"]:
                    val = rng.uniform(5.0, 20.0) # close to water
                else:
                    val = rng.uniform(40.0, 75.0)
                    
            else: # agricultural
                if ind_name in ["agricultural_land", "soil_fertility", "soil_erosion", "temperature", "built_up_area"]:
                    val = rng.uniform(60.0, 90.0)
                elif ind_name in ["forest_cover", "wetland_area", "mangrove_area", "ecosystem_integrity"]:
                    val = rng.uniform(5.0, 25.0)
                else:
                    val = rng.uniform(30.0, 70.0)
            
            # Apply Direct/Inverse mapping (where higher = higher ecological concern/sensitivity)
            if direction == "inverse":
                normalized = 100.0 - val
            else:
                normalized = val
                
            indicators[ind_name] = round(normalized, 1)
            
    return archetype, indicators

def compute_sensitivity_index(indicators: dict, index_config: dict, raw_indicators: dict = None) -> float:
    """Compute weighted sum of indicators for a specific index utilizing official Protocol thresholds."""
    PROTOCOL_A = {
        "bii":  {"breaks": [0.20, 0.40, 0.60, 0.80], "scores": [5, 4, 3, 2, 1]},
        "flii": {"breaks": [2.0,  4.0,  6.0,  8.0],  "scores": [5, 4, 3, 2, 1]},
        "msa":  {"breaks": [0.20, 0.40, 0.60, 0.80], "scores": [5, 4, 3, 2, 1]},
        "flagship_habitat": {"breaks": [0.20, 0.40, 0.60, 0.80], "scores": [5, 4, 3, 2, 1]},
        "ceri": {"breaks": [0.10, 0.20, 0.35, 0.50], "scores": [1, 2, 3, 4, 5]},
        "star_t": {"breaks": [1.0, 3.0, 6.0, 9.0], "scores": [1, 2, 3, 4, 5]},
        "kba_overlap": {"breaks": [1.0, 25.0, 75.0, 99.9], "scores": [1, 2, 3, 4, 5]},
        "lst_day": {"breaks": [32.0, 36.0, 40.0, 44.0], "scores": [1, 2, 3, 4, 5]},
        "lst_night": {"breaks": [22.0, 26.0, 30.0, 34.0], "scores": [1, 2, 3, 4, 5]},
        "ghm": {"breaks": [0.1, 0.3, 0.6, 0.9], "scores": [1, 2, 3, 4, 5]},
        "hdi": {"breaks": [0.5, 0.6, 0.7, 0.8], "scores": [1, 2, 3, 4, 5]},
        "light_pollution": {"breaks": [1.0, 5.0, 30.0, 100.0], "scores": [1, 2, 3, 4, 5]},
    }

    PROTOCOL_B_BREAKS = [30, 50, 70, 85]
    PROTOCOL_B_SCORES = [5,  4,  3,  2, 1]

    weighted_sum = 0.0
    weight_total = 0.0
    
    for ind_name, props in index_config.items():
        weight = props.get("weight", 0.0)
        direction = props.get("direction", "direct")
        
        # Default concern score if missing
        concern_score = 3.0
        
        raw_val = None
        if raw_indicators:
            raw_val = raw_indicators.get(ind_name)
            
        # Try Protocol A first
        if ind_name in PROTOCOL_A and raw_val is not None:
            spec = PROTOCOL_A[ind_name]
            val = float(raw_val)
            matched = False
            for i, b in enumerate(spec["breaks"]):
                if val < b:
                    concern_score = float(spec["scores"][i])
                    matched = True
                    break
            if not matched:
                concern_score = float(spec["scores"][-1])
        else:
            # Fallback to Protocol B/C using normalized values
            concern_0_100 = indicators.get(ind_name, 50.0)
            
            if direction == "inverse":
                intactness = (100.0 - concern_0_100) / 100.0
                matched = False
                for i, b in enumerate(PROTOCOL_B_BREAKS):
                    if (intactness * 100.0) < b:
                        concern_score = float(PROTOCOL_B_SCORES[i])
                        matched = True
                        break
                if not matched:
                    concern_score = float(PROTOCOL_B_SCORES[-1])
            else:
                concern_score = 1.0 + (concern_0_100 / 25.0)
                
        # Map 1-5 concern score back to 0-100 scale
        val_0_100 = (concern_score - 1.0) / 4.0 * 100.0
        
        weighted_sum += val_0_100 * weight
        weight_total += weight
        
    if weight_total > 0:
        return round(weighted_sum / weight_total, 1)
    return 50.0

def calculate_tnfd_outputs(site_obj: Any, encore_obj: Any, son_obj: Any) -> Dict[str, Any]:
    """
    Main dynamic site-specific computation service for TNFD.
    Calculates dynamic dependency and impact scores by combining:
      1. ENCORE baseline weights (0-1)
      2. Deterministic spatial environmental sensitivity (0-100)
    """
    if not encore_obj:
        return {}

    # 1. Generate Site Environmental Indicators & Sensitivity Indices
    use_simulated = True
    indicators = {}
    measured_slugs = set()
    flat_slugged = {}
    archetype = "GEE Spatial Analysis"
    measured_count = 27
    
    if son_obj and hasattr(son_obj, "metrics") and son_obj.metrics:
        use_simulated = False
        son_metrics = son_obj.metrics
        metric_concerns = son_metrics.get("metric_concerns", {})
        
        # Substring mapping from GEE display names to config slugs
        DISPLAY_NAME_TO_SLUG = {
            "aridity": "aridity_index",
            "trophic state": "tspi",
            "ndci": "tspi",
            "algal bloom": "sabf",
            "water clarity": "wcpi",
            "water surface dynamics": "wsdi",
            "persistence": "jrc_water_persistence",
            "shoreline development": "shdi",
            "riparian complexity": "rci",
            "natural habitat": "natural_habitat",
            "natural land cover": "natural_landcover",
            "connectivity": "cpland",
            "cpland": "cpland",
            "kba": "kba_overlap",
            "forest landscape integrity": "flii",
            "flii": "flii",
            "ecosystem integrity": "eii",
            "biodiversity intactness": "bii",
            "bii": "bii",
            "potentially disappeared fraction": "pdf",
            "endemic species richness": "endemic_richness",
            "flagship habitat": "flagship_habitat",
            "endemic plant": "endemic_plant_richness",
            "threatened species richness": "threatened_richness",
            "extinction-risk index": "ceri",
            "ceri": "ceri",
            "star_t": "star_t",
            "threatened plant": "threatened_plant_richness",
            "vegetation structure": "ndvi",
            "ndvi": "ndvi",
            "habitat health": "habitat_health",
            "leaf area": "lai",
            "lai": "lai",
            "canopy height": "chm",
            "chm": "chm",
            "tree cover loss": "forest_loss_rate",
            "riparian ndvi temporal trend": "riparian_ndvi_trend",
            "human modification": "ghm",
            "human disturbance": "hdi",
            "light pollution": "light_pollution"
        }
        
        raw_metrics = son_metrics.get("raw_metrics", {})
        
        # Flatten raw_metrics (which is nested by pillar)
        flat_raw = {}
        for pillar_name, pillar_data in raw_metrics.items():
            if isinstance(pillar_data, dict):
                for key, val in pillar_data.items():
                    flat_raw[key] = val
                    
        # Sort patterns by length descending to prevent key collisions (e.g. ndvi vs riparian ndvi temporal trend)
        sorted_patterns = sorted(DISPLAY_NAME_TO_SLUG.items(), key=lambda x: len(x[0]), reverse=True)
        
        # Map raw keys to slugs
        flat_slugged = {}
        for raw_key, raw_val in flat_raw.items():
            raw_key_lower = raw_key.lower()
            matched_slug = None
            for pattern, slug in sorted_patterns:
                if pattern in raw_key_lower:
                    matched_slug = slug
                    break
            if matched_slug:
                flat_slugged[matched_slug] = raw_val
                
        # Double safe: fall back to metric_concerns flat structure if raw_metrics didn't have it
        for slug, concern_info in metric_concerns.items():
            if isinstance(concern_info, dict):
                site_val = concern_info.get("site_value")
                if site_val is not None and site_val != "Coming soon":
                    if flat_slugged.get(slug) is None:
                        flat_slugged[slug] = site_val

        # Count active matched indicators in config
        all_weights_slugs = set()
        for idx_name, idx_data in WEIGHTS_CONFIG.get("indices", {}).items():
            for ind_slug in idx_data.keys():
                all_weights_slugs.add(ind_slug)
        measured_count = len([k for k, v in flat_slugged.items() if k in all_weights_slugs and v is not None])

        for index_name, index_data in WEIGHTS_CONFIG.get("indices", {}).items():
            for ind_name, ind_props in index_data.items():
                direction = ind_props.get("direction", "direct")
                
                # Retrieve indicator value on 0-100 scale
                val = 50.0
                fval = flat_slugged.get(ind_name)
                
                if fval is not None:
                    measured_slugs.add(ind_name)
                    try:
                        fval = float(fval)
                        # Normalize fval to 0-100 scale based on slug
                        if ind_name in ["natural_habitat", "natural_landcover", "cpland", "forest_loss_rate", "kba_overlap"]:
                            val = fval
                        elif ind_name in ["bii", "pdf", "eii", "eii_structural", "eii_compositional", "eii_functional", "flagship_habitat", "ghm", "hdi", "sabf", "wcpi", "wsdi", "hsas", "edpp", "mspl", "rci", "jrc_water_persistence", "ceri", "sdi", "stsi", "iri", "ivsi"]:
                            val = fval * 100.0
                        elif ind_name == "flii":
                            val = fval * 10.0
                        elif ind_name == "star_t":
                            val = (fval / 10.0) * 100.0
                        elif ind_name == "aridity_index":
                            val = (fval / 5.0) * 100.0
                        elif ind_name in ["ndvi", "tspi"]:
                            val = (fval + 1.0) / 2.0 * 100.0
                        elif ind_name == "habitat_health":
                            val = (fval / 50.0) * 100.0
                        elif ind_name == "lai":
                            val = (fval / 8.0) * 100.0
                        elif ind_name == "chm":
                            val = (fval / 80.0) * 100.0
                        elif ind_name == "riparian_ndvi_trend":
                            val = (fval + 0.5) * 100.0
                        elif ind_name == "light_pollution":
                            val = (fval / 500.0) * 100.0
                        elif ind_name in ["endemic_richness", "threatened_richness"]:
                            val = (fval / 500.0) * 100.0
                        elif ind_name in ["endemic_plant_richness", "threatened_plant_richness"]:
                            val = (fval / 1000.0) * 100.0
                        elif ind_name == "shdi":
                            val = ((fval - 1.0) / 19.0) * 100.0
                        elif ind_name == "lst_day":
                            val = ((fval + 40.0) / 110.0) * 100.0
                        elif ind_name == "lst_night":
                            val = ((fval + 40.0) / 90.0) * 100.0
                        else:
                            # Default multiplier if 0-1 fraction
                            if fval <= 1.0:
                                val = fval * 100.0
                            else:
                                val = fval
                                
                        # Clamp to [0, 100]
                        val = max(0.0, min(100.0, val))
                    except Exception:
                        val = 50.0
                
                # Apply Direct/Inverse mapping (where higher = higher ecological concern/sensitivity)
                if direction == "inverse":
                    normalized = 100.0 - val
                else:
                    normalized = val
                    
                indicators[ind_name] = round(normalized, 1)
                
    if use_simulated:
        archetype, indicators = generate_site_indicators(site_obj, WEIGHTS_CONFIG)
        measured_count = len(indicators)
    
    sensitivity_indices = {}
    for index_name, index_data in WEIGHTS_CONFIG.get("indices", {}).items():
        sensitivity_indices[index_name] = compute_sensitivity_index(indicators, index_data, flat_slugged)
        
    # Helper to get ENCORE weights
    get_weight = lambda field: RATING_WEIGHT_MAP.get(getattr(encore_obj, field, "VL"), 0.2)
    get_rating = lambda field: getattr(encore_obj, field, "VL")

    # 2. Calculate Dynamic Dependency Scores (Weight * ESI)
    dependencies_data = [
        {
            "id": "water_supply",
            "name": "Water Supply",
            "encore_field": "dep_water_supply",
            "index_name": "WaterSensitivity",
            "description": "Reliance on freshwater sources (groundwater and surface water) for operations."
        },
        {
            "id": "soil_quality",
            "name": "Soil Quality & Retention",
            "encore_field": "dep_soil_sediment_retention",
            "index_name": "SoilSensitivity",
            "description": "Dependence on healthy soils, slope stability, and prevention of land erosion."
        },
        {
            "id": "biodiversity",
            "name": "Biodiversity & Nursery Habitats",
            "encore_field": "dep_overall_dependency_biodiversity",
            "index_name": "HabitatSensitivity",
            "description": "Reliance on local ecosystems to maintain species diversity and habitat structure."
        },
        {
            "id": "flood_regulation",
            "name": "Flood & Storm Regulation",
            "encore_field": "dep_flood_and_storm_protection",
            "index_name": "WaterSensitivity",
            "description": "Dependence on natural flood buffers like wetlands and vegetated catchments."
        },
        {
            "id": "pollination",
            "name": "Pollination",
            "encore_field": "dep_pollination",
            "index_name": "HabitatSensitivity",
            "description": "Reliance on wild pollinators for agricultural/botanical outputs."
        },
        {
            "id": "pest_control",
            "name": "Pest & Disease Control",
            "encore_field": "dep_pest_control",
            "index_name": "HabitatSensitivity",
            "description": "Reliance on natural predators to regulate pests and vector diseases."
        },
        {
            "id": "climate_regulation",
            "name": "Climate Regulation",
            "encore_field": "dep_climate_regulation",
            "index_name": "ClimateSensitivity",
            "description": "Reliance on local/global climate stabilization services like carbon sequestration."
        }
    ]

    all_dependencies = []
    for dep in dependencies_data:
        weight = get_weight(dep["encore_field"])
        rating = get_rating(dep["encore_field"])
        esi = sensitivity_indices.get(dep["index_name"], 50.0)
        
        # Calculate dynamic score (0-100 scale)
        score = weight * esi
        
        # Indicators list with their names, values, and sources
        indicators_used = []
        indicators_config = WEIGHTS_CONFIG["indices"][dep["index_name"]]
        for ind_name, props in indicators_config.items():
            indicators_used.append({
                "name": ind_name.replace("_", " ").title(),
                "value": indicators.get(ind_name, 50.0),
                "source": props.get("source", "Satellite Observation"),
                "resolution": props.get("resolution", "1km")
            })
            
        all_dependencies.append({
            "category": dep["name"],
            "score": round(score, 1),
            "level": get_rating_level(score),
            "encore_weight": round(weight, 2),
            "encore_rating": rating,
            "sensitivity_index_name": dep["index_name"].replace("Sensitivity", " Sensitivity"),
            "sensitivity_score": esi,
            "description": dep["description"],
            "indicators": indicators_used,
            "dataset_sources": list(set([ind["source"] for ind in indicators_used]))
        })

    # Sort all dependencies by dynamic score descending
    sorted_dependencies = sorted(all_dependencies, key=lambda x: -x["score"])
    top_dependencies = sorted_dependencies[:5]

    # 3. Calculate Dynamic Impact Scores (Weight * ESI)
    impacts_data = [
        {
            "id": "water_use",
            "name": "Water Use & Consumption",
            "encore_fields": ["ep_water_use", "ep_freshwater_use"],
            "index_name": "WaterSensitivity",
            "description": "Potential pressure exerted on local water resources through extraction."
        },
        {
            "id": "water_pollution",
            "name": "Water Pollution",
            "encore_fields": ["ep_toxic_emissions", "ep_nutrient_emissions"],
            "index_name": "WaterSensitivity",
            "description": "Discharges of toxic substances or excess nutrients into water systems."
        },
        {
            "id": "land_use",
            "name": "Land Use & Habitat Impact",
            "encore_fields": ["ep_land_use"],
            "index_name": "HabitatSensitivity",
            "description": "Transformation and fragmentation of terrestrial ecosystems and wildlife corridors."
        },
        {
            "id": "climate_change",
            "name": "Climate Change & GHG",
            "encore_fields": ["ep_ghg_emissions"],
            "index_name": "ClimateSensitivity",
            "description": "Emissions of greenhouse gases accelerating global warming."
        },
        {
            "id": "soil_degradation",
            "name": "Soil Degradation & Pollutants",
            "encore_fields": ["ep_toxic_emissions", "ep_solid_waste"],
            "index_name": "SoilSensitivity",
            "description": "Decline in soil health, chemical contamination, and structure breakdown."
        },
        {
            "id": "solid_waste",
            "name": "Solid Waste generation",
            "encore_fields": ["ep_solid_waste"],
            "index_name": "SoilSensitivity",
            "description": "Accumulation of industrial/non-hazardous solids and landfill impacts."
        },
        {
            "id": "biodiversity_pressure",
            "name": "Direct Biodiversity Pressure",
            "encore_fields": ["ep_overall_pressure_biodiversity"],
            "index_name": "HabitatSensitivity",
            "description": "Direct stress on species survival, invasive species introduction, or harvesting."
        },
        {
            "id": "marine_pollution",
            "name": "Marine & Coastal Pollution",
            "encore_fields": ["ep_marine_pollution"],
            "index_name": "WaterSensitivity",
            "description": "Discharge of toxic agents or waste affecting marine life and shorelines."
        }
    ]

    all_impacts = []
    for imp in impacts_data:
        # Take max weight of related ENCORE fields
        weight = max(get_weight(field) for field in imp["encore_fields"])
        rating = get_rating(imp["encore_fields"][0])
        esi = sensitivity_indices.get(imp["index_name"], 50.0)
        
        # Calculate dynamic score
        score = weight * esi
        
        # Indicators list
        indicators_used = []
        indicators_config = WEIGHTS_CONFIG["indices"][imp["index_name"]]
        for ind_name, props in indicators_config.items():
            indicators_used.append({
                "name": ind_name.replace("_", " ").title(),
                "value": indicators.get(ind_name, 50.0),
                "source": props.get("source", "Satellite Observation"),
                "resolution": props.get("resolution", "1km")
            })
            
        all_impacts.append({
            "category": imp["name"],
            "score": round(score, 1),
            "level": get_rating_level(score),
            "encore_weight": round(weight, 2),
            "encore_rating": rating,
            "sensitivity_index_name": imp["index_name"].replace("Sensitivity", " Sensitivity"),
            "sensitivity_score": esi,
            "description": imp["description"],
            "indicators": indicators_used,
            "dataset_sources": list(set([ind["source"] for ind in indicators_used]))
        })

    # Sort all impacts by dynamic score descending
    sorted_impacts = sorted(all_impacts, key=lambda x: -x["score"])
    top_impacts = sorted_impacts[:5]

    # 4. Calculate Overall Indices
    overall_dependency_index = round(sum(d["score"] for d in all_dependencies) / len(all_dependencies), 1)
    overall_impact_index = round(sum(i["score"] for i in all_impacts) / len(all_impacts), 1)

    # 5. Composite Priority Logic
    # Standard composite priority score
    composite_priority = round((overall_dependency_index + overall_impact_index) / 2, 1)
    
    # Priority Site if either index is high (>= 40) or any category is very high (>= 75)
    is_priority = (overall_dependency_index >= 40.0) or (overall_impact_index >= 40.0) or any(d["score"] >= 75.0 for d in all_dependencies) or any(i["score"] >= 75.0 for i in all_impacts)
    
    priority_tier = "Tier 1" if composite_priority >= 65 else "Tier 2" if composite_priority >= 40 else "Tier 3"

    # 6. Calculate Confidence Score
    # The confidence score is calculated as a percentage of valid, real-measured indicators
    # versus the total number of indicators in the index weights configuration.
    all_weights_slugs = set()
    for index_name, index_data in WEIGHTS_CONFIG.get("indices", {}).items():
        for ind_slug in index_data.keys():
            all_weights_slugs.add(ind_slug)
            
    total_indicators_count = len(all_weights_slugs) if all_weights_slugs else 1
    
    if use_simulated:
        avg_conf_pct = 0.0
    else:
        avg_conf_pct = round((len(measured_slugs) / total_indicators_count) * 100.0, 1)
        
    confidence_label = "High" if avg_conf_pct >= 85 else "Medium" if avg_conf_pct >= 70 else "Low"

    # Build old-style impact_breakdown to prevent breaking existing endpoints
    legacy_impact_breakdown = {
        "extent": {"ep": get_rating("ep_land_use"), "son": get_rating_level(sensitivity_indices.get("HabitatSensitivity", 50.0)), "score": all_impacts[2]["score"], "level": all_impacts[2]["level"]},
        "freshwater": {"ep": get_rating("ep_freshwater_use"), "son": get_rating_level(sensitivity_indices.get("WaterSensitivity", 50.0)), "score": all_impacts[0]["score"], "level": all_impacts[0]["level"]},
        "terrestrial": {"ep": get_rating("ep_land_use"), "son": get_rating_level(sensitivity_indices.get("HabitatSensitivity", 50.0)), "score": all_impacts[6]["score"], "level": all_impacts[6]["level"]},
        "population": {"ep": get_rating("ep_overall_pressure_biodiversity"), "son": get_rating_level(sensitivity_indices.get("HabitatSensitivity", 50.0)), "score": all_impacts[6]["score"], "level": all_impacts[6]["level"]},
        "extinction": {"ep": get_rating("ep_land_use"), "son": get_rating_level(sensitivity_indices.get("HabitatSensitivity", 50.0)), "score": all_impacts[2]["score"], "level": all_impacts[2]["level"]}
    }

    legacy_dependency_breakdown = {
        "water": get_rating_level(all_dependencies[0]["score"]),
        "soil": get_rating_level(all_dependencies[1]["score"]),
        "biodiversity": get_rating_level(all_dependencies[2]["score"]),
        "climate": get_rating_level(all_dependencies[6]["score"]),
        "pollination": get_rating_level(all_dependencies[4]["score"])
    }

    return {
        "impact_score": overall_impact_index,
        "impact_level": get_rating_level(overall_impact_index),
        "dependency_risk_score": overall_dependency_index,
        "dependency_risk_level": get_rating_level(overall_dependency_index),
        "priority_score": composite_priority,
        "priority_tier": priority_tier,
        "is_tnfd_priority": is_priority,
        "sensitivity_indices": sensitivity_indices,
        "all_indicators": indicators,
        "archetype": archetype,
        "all_dependencies": all_dependencies,
        "all_impacts": all_impacts,
        "top_dependencies": top_dependencies,
        "top_impacts": top_impacts,
        "impact_breakdown": legacy_impact_breakdown,
        "dependency_breakdown": legacy_dependency_breakdown,
        "data_quality": {
            "confidence": confidence_label.lower(),
            "confidence_pct": avg_conf_pct,
            "measured_metrics": measured_count
        }
    }
