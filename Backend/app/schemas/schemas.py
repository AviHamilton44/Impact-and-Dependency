from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Literal
from uuid import UUID
from datetime import datetime

LevelEnum = Literal['VL', 'L', 'M', 'H', 'VH']

class SiteStateOfNatureBase(BaseModel):
    water_scarcity_level: LevelEnum
    water_pollution_level: LevelEnum
    land_degradation_level: LevelEnum
    biodiversity_loss_level: LevelEnum
    msa_score: float
    bii_score: float

class SiteEncoreScoreBase(BaseModel):
    ep_water_use: LevelEnum
    ep_land_use: LevelEnum
    ep_toxic_emissions: LevelEnum
    ep_nutrient_emissions: LevelEnum
    ep_overall_pressure_biodiversity: LevelEnum
    dep_water_supply: LevelEnum
    dep_soil_sediment_retention: LevelEnum
    dep_overall_dependency_biodiversity: LevelEnum
    encore_refreshed_at: Optional[datetime] = None

class SiteBase(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float
    biome_code: str
    activities: List[str]
    geometry: Optional[dict] = None


class SiteResponse(SiteBase):
    site_id: UUID
    encore_score: Optional[SiteEncoreScoreBase] = None
    state_of_nature: Optional[SiteStateOfNatureBase] = None
    
    # Calculated fields
    impact_score: Optional[float] = None
    impact_level: Optional[str] = None
    dependency_risk_score: Optional[int] = None
    priority_score: Optional[float] = None
    is_tnfd_priority: Optional[bool] = None
    priority_tier: Optional[str] = None

    
    model_config = ConfigDict(from_attributes=True)

class PortfolioSummaryResponse(BaseModel):
    total_sites: int
    priority_sites: int
    top_pressure: str
    top_dependency: str
    aggregate_stats: dict


class ImpactDistributionResponse(BaseModel):
    VL: int = 0
    L: int = 0
    M: int = 0
    H: int = 0
    VH: int = 0
