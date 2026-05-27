def enum_to_num(val: str) -> int:
    mapping = {'VL': 1, 'L': 2, 'M': 3, 'H': 4, 'VH': 5}
    return mapping.get(val, 1)

def num_to_enum(val: int) -> str:
    mapping = {1: 'VL', 2: 'L', 3: 'M', 4: 'H', 5: 'VH'}
    # clamp value between 1 and 5
    val = max(1, min(5, round(val)))
    return mapping.get(val, 'VL')

# Matrix: Rows = SoN Loss, Cols = ENCORE Dependency
# 1=VL, 2=L, 3=M, 4=H, 5=VH
# Indices: 0 to 4
DEPENDENCY_MATRIX = [
    [1, 1, 1, 1, 2], # VL Loss
    [1, 1, 2, 3, 4], # L Loss
    [1, 2, 3, 4, 4], # M Loss
    [2, 3, 4, 4, 5], # H Loss
    [3, 4, 4, 5, 5], # VH Loss
]

def calculate_site_scores(site_obj, encore_obj, son_obj):
    if not encore_obj or not son_obj:
        return None

    # Step 1 & 2: Impacts
    ep_water_use = enum_to_num(encore_obj.ep_water_use)
    ep_land_use = enum_to_num(encore_obj.ep_land_use)
    ep_toxic = enum_to_num(encore_obj.ep_toxic_emissions)
    ep_nutrient = enum_to_num(encore_obj.ep_nutrient_emissions)
    ep_biodiv = enum_to_num(encore_obj.ep_overall_pressure_biodiversity)

    son_water_scarcity = enum_to_num(son_obj.water_scarcity_level)
    son_water_pollution = enum_to_num(son_obj.water_pollution_level)
    son_land_deg = enum_to_num(son_obj.land_degradation_level)
    son_biodiv_loss = enum_to_num(son_obj.biodiversity_loss_level)

    water_scarcity = ep_water_use + son_water_scarcity
    water_pollution = max(ep_toxic, ep_nutrient) + son_water_pollution
    land_loss = ep_land_use + son_land_deg
    biodiversity_loss = ep_biodiv + son_biodiv_loss

    # Step 3: Impact Score (0-10)
    raw_sum = water_scarcity + water_pollution + land_loss + biodiversity_loss
    impact_score = ((raw_sum - 4) / 36) * 10
    
    # Ensure it's between 0 and 10
    impact_score = max(0.0, min(10.0, impact_score))

    # Step 4: Impact Level
    if impact_score <= 2.0:
        impact_level = 'VL'
    elif impact_score <= 4.0:
        impact_level = 'L'
    elif impact_score <= 6.0:
        impact_level = 'M'
    elif impact_score <= 8.0:
        impact_level = 'H'
    else:
        impact_level = 'VH'

    # Step 5: Dependency Matrix Lookups
    dep_water_encore = enum_to_num(encore_obj.dep_water_supply)
    dep_soil_encore = enum_to_num(encore_obj.dep_soil_sediment_retention)
    dep_biodiv_encore = enum_to_num(encore_obj.dep_overall_dependency_biodiversity)

    water_dep_level = DEPENDENCY_MATRIX[son_water_scarcity - 1][dep_water_encore - 1]
    soil_dep_level = DEPENDENCY_MATRIX[son_land_deg - 1][dep_soil_encore - 1]
    biodiv_dep_level = DEPENDENCY_MATRIX[son_biodiv_loss - 1][dep_biodiv_encore - 1]

    # Step 6: Dependency Risk Score
    dependency_risk_score = max(water_dep_level, soil_dep_level, biodiv_dep_level)

    # Step 7: Composite Priority Score
    priority_score = (impact_score * 5) + (dependency_risk_score * 5)

    return {
        "impact_score": round(impact_score, 2),
        "impact_level": impact_level,
        "dependency_risk_score": dependency_risk_score,
        "priority_score": round(priority_score, 2),
        # Extra details
        "impacts": {
            "water_scarcity": water_scarcity,
            "water_pollution": water_pollution,
            "land_loss": land_loss,
            "biodiversity_loss": biodiversity_loss
        },
        "dependencies": {
            "water_supply": num_to_enum(water_dep_level),
            "soil_retention": num_to_enum(soil_dep_level),
            "biodiversity": num_to_enum(biodiv_dep_level)
        },
        "is_tnfd_priority": impact_level in ['M', 'H', 'VH'] or any(num_to_enum(d) in ['H', 'VH'] for d in [water_dep_level, soil_dep_level, biodiv_dep_level]),
        "priority_tier": "Tier 1" if priority_score > 75 else "Tier 2" if priority_score >= 50 else "Tier 3"
    }

