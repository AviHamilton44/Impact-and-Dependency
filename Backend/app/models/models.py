import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.database import Base

level_enum = ENUM('VL', 'L', 'M', 'H', 'VH', name='level_enum', create_type=True)

class Site(Base):
    __tablename__ = 'sites'

    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    biome_code = Column(String)
    activities = Column(JSON)  # List of activity names
    uploaded_kml_path = Column(String)
    geometry = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    encore_score = relationship("SiteEncoreScore", back_populates="site", uselist=False, cascade="all, delete-orphan")
    # Note: SiteSonScore is managed by the SoN module, we only READ it.
    son_score = relationship("SiteSonScore", primaryjoin="Site.site_id == SiteSonScore.site_id", foreign_keys="SiteSonScore.site_id", uselist=False, viewonly=True)

class SiteEncoreScore(Base):
    __tablename__ = 'site_encore_scores'

    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey('sites.site_id'), unique=True)
    encore_refreshed_at = Column(DateTime, default=datetime.utcnow)

    # 12 Environmental Pressures (MANDATORY)
    ep_water_use = Column(level_enum)
    ep_freshwater_use = Column(level_enum)
    ep_toxic_emissions = Column(level_enum)
    ep_nutrient_emissions = Column(level_enum)
    ep_disturbances = Column(level_enum)
    ep_non_ghg_air_pollution = Column(level_enum)
    ep_land_use = Column(level_enum)
    ep_overall_pressure_biodiversity = Column(level_enum)
    ep_ghg_emissions = Column(level_enum)
    ep_solid_waste = Column(level_enum)
    ep_other_resource_use = Column(level_enum)
    ep_marine_pollution = Column(level_enum)

    # 25 Ecosystem Dependencies (Representative subset for MVP)
    dep_water_supply = Column(level_enum)
    dep_soil_sediment_retention = Column(level_enum)
    dep_overall_dependency_biodiversity = Column(level_enum)
    dep_flood_and_storm_protection = Column(level_enum)
    dep_pollination = Column(level_enum)
    dep_pest_control = Column(level_enum)
    dep_climate_regulation = Column(level_enum)
    # ... others can be added as JSON if needed, but we keep core ones as columns
    additional_dependencies = Column(JSON)

    site = relationship("Site", back_populates="encore_score")

class SiteSonScore(Base):
    """READ ONLY - Managed by State of Nature Module"""
    __tablename__ = 'site_son_scores'

    site_id = Column(UUID(as_uuid=True), primary_key=True)
    dim1_extent_level = Column(level_enum)
    dim2_freshwater_level = Column(level_enum)
    dim2_terrestrial_level = Column(level_enum)
    dim3_population_level = Column(level_enum)
    dim4_extinction_level = Column(level_enum)
    biome_code = Column(String)
    data_confidence = Column(String) # 'low', 'medium', 'high'
    measured_metrics_count = Column(Integer, default=0)
    metrics = Column(JSON)

class IndustryLeapData(Base):
    __tablename__ = 'industry_leap_data'
    
    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String, index=True)
    sasb_code = Column(String)
    industry = Column(String)
    ecosystem_service = Column(String)
    dependency_type = Column(String)
    impact_driver = Column(String)
    severity = Column(String)
    impact_rating = Column(String)
    justification = Column(String)


