from typing import Dict, Any, List, Optional
import math

def enum_to_num(val: str) -> int:
    mapping = {'VL': 1, 'L': 2, 'M': 3, 'H': 4, 'VH': 5}
    return mapping.get(val, 1)

def num_to_enum(val: int) -> str:
    mapping = {1: 'VL', 2: 'L', 3: 'M', 4: 'H', 5: 'VH'}
    val = max(1, min(5, round(val)))
    return mapping.get(val, 'VL')

# TNFD Dependency Matrix Logic
# Rows = SoN Loss (1-5), Cols = ENCORE Dependency (1-5)
DEPENDENCY_MATRIX = [
    [1, 1, 1, 1, 2], # VL Loss
    [1, 1, 2, 3, 4], # L Loss
    [1, 2, 3, 4, 4], # M Loss
    [2, 3, 4, 4, 5], # H Loss
    [3, 4, 4, 5, 5], # VH Loss
]

def get_matrix_score(son_val: int, encore_val: int) -> int:
    try:
        return DEPENDENCY_MATRIX[son_val - 1][encore_val - 1]
    except IndexError:
        return 1

def calculate_tnfd_outputs(site_obj: Any, encore_obj: Any, son_obj: Any) -> Dict[str, Any]:
    """
    Main computation service for TNFD Impact & Dependency.
    site_obj: Site model
    encore_obj: SiteEncoreScore model
    son_obj: SiteSonScore model (Read from site_son_scores table)
    """
    if not encore_obj or not son_obj:
        return {}

    # Helper to get numeric values
    e = lambda field: enum_to_num(getattr(encore_obj, field, 'VL'))
    s = lambda field: enum_to_num(getattr(son_obj, field, 'VL'))

    biome = site_obj.biome_code or 'T1'
    
    # ----------------------------------------------------
    # IMPACT 1 — Loss of Ecosystem Extent
    # ----------------------------------------------------
    imp1_ep = e('ep_land_use')
    imp1_son = s('dim1_extent_level')
    imp1_pair = imp1_ep + imp1_son

    # ----------------------------------------------------
    # IMPACT 2 — Degradation of Freshwater Condition
    # ----------------------------------------------------
    imp2_ep = max(e('ep_water_use'), e('ep_freshwater_use'), e('ep_toxic_emissions'), e('ep_nutrient_emissions'))
    imp2_son = s('dim2_freshwater_level')
    imp2_pair = imp2_ep + imp2_son

    # ----------------------------------------------------
    # IMPACT 3 — Degradation of Terrestrial Ecosystem Condition
    # ----------------------------------------------------
    imp3_ep = max(e('ep_disturbances'), e('non_ghg_air_pollution')) # Fix: field name check
    # Check if field name in model is ep_non_ghg_air_pollution
    imp3_ep = max(e('ep_disturbances'), e('ep_non_ghg_air_pollution'))
    imp3_son = s('dim2_terrestrial_level')
    imp3_pair = imp3_ep + imp3_son

    # ----------------------------------------------------
    # IMPACT 4 — Decline in Species Populations
    # ----------------------------------------------------
    imp4_ep = e('ep_overall_pressure_biodiversity')
    imp4_son = s('dim3_population_level')
    imp4_pair = imp4_ep + imp4_son

    # ----------------------------------------------------
    # IMPACT 5 — Species Extinction Risk Escalation
    # ----------------------------------------------------
    # IF biome_code is: T1–T8, M biomes -> USE: ep_land_use
    # IF biome_code is: F1, F2 -> USE: MAX(ep_water_use, ep_freshwater_use)
    if biome.startswith('F'):
        imp5_ep = max(e('ep_water_use'), e('ep_freshwater_use'))
    else:
        imp5_ep = e('ep_land_use')
    
    imp5_son = s('dim4_extinction_level')
    imp5_pair = imp5_ep + imp5_son

    # ----------------------------------------------------
    # OVERALL IMPACT SCORE
    # ----------------------------------------------------
    raw_sum = imp1_pair + imp2_pair + imp3_pair + imp4_pair + imp5_pair
    # IS = (raw_sum - 10) / (50 - 10) × 10
    impact_score = ((raw_sum - 10) / 40) * 10
    impact_score = max(0.0, min(10.0, impact_score))
    
    impact_level = num_to_enum(1 + (impact_score / 2)) # 0-2=VL, 2-4=L, 4-6=M, 6-8=H, 8-10=VH

    # ----------------------------------------------------
    # DEPENDENCIES (MATRIX LOOKUP)
    # ----------------------------------------------------
    water_dep = get_matrix_score(s('dim2_freshwater_level'), e('dep_water_supply'))
    soil_dep = get_matrix_score(s('dim1_extent_level'), e('dep_soil_sediment_retention'))
    biodiv_dep = get_matrix_score(s('dim2_terrestrial_level'), e('dep_overall_dependency_biodiversity'))
    climate_dep = get_matrix_score(s('dim2_terrestrial_level'), e('dep_climate_regulation'))
    pollin_dep = get_matrix_score(s('dim2_terrestrial_level'), e('dep_pollination'))

    dependency_risk_score = max(water_dep, soil_dep, biodiv_dep, climate_dep, pollin_dep)

    # ----------------------------------------------------
    # COMPOSITE PRIORITY SCORE
    # ----------------------------------------------------
    priority_score = (impact_score * 5) + (dependency_risk_score * 5)

    # ----------------------------------------------------
    # TNFD PRIORITY LOGIC
    # ----------------------------------------------------
    # TRUE IF impact_level IN [M, H, VH] OR ANY dep IN [H, VH]
    is_priority = (impact_score >= 4.0) or (dependency_risk_score >= 4)
    
    priority_tier = "Tier 1" if priority_score > 75 else "Tier 2" if priority_score >= 50 else "Tier 3"

    return {
        "impact_score": round(impact_score, 2),
        "impact_level": impact_level,
        "dependency_risk_score": dependency_risk_score,
        "dependency_risk_level": num_to_enum(dependency_risk_score),
        "priority_score": round(priority_score, 1),
        "priority_tier": priority_tier,
        "is_tnfd_priority": is_priority,
        "impact_breakdown": {
            "extent": {"ep": imp1_ep, "son": imp1_son, "score": imp1_pair, "level": num_to_enum(imp1_pair/2)},
            "freshwater": {"ep": imp2_ep, "son": imp2_son, "score": imp2_pair, "level": num_to_enum(imp2_pair/2)},
            "terrestrial": {"ep": imp3_ep, "son": imp3_son, "score": imp3_pair, "level": num_to_enum(imp3_pair/2)},
            "population": {"ep": imp4_ep, "son": imp4_son, "score": imp4_pair, "level": num_to_enum(imp4_pair/2)},
            "extinction": {"ep": imp5_ep, "son": imp5_son, "score": imp5_pair, "level": num_to_enum(imp5_pair/2)}
        },
        "dependency_breakdown": {
            "water": num_to_enum(water_dep),
            "soil": num_to_enum(soil_dep),
            "biodiversity": num_to_enum(biodiv_dep),
            "climate": num_to_enum(climate_dep),
            "pollination": num_to_enum(pollin_dep)
        },
        "data_quality": {
            "confidence": son_obj.data_confidence or 'medium',
            "measured_metrics": son_obj.measured_metrics_count or 0
        }
    }
