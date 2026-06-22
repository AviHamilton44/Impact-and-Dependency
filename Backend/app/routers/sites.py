from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Site, SiteEncoreScore, SiteSonScore, IndustryLeapData
from app.services.computation_service import calculate_tnfd_outputs
import uuid
from typing import List, Dict, Any

router = APIRouter(tags=["Sites"])

@router.get("/sites")
def list_sites(db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).all()
    
    results = []
    for s in sites:
        out = {}
        if s.encore_score and s.son_score:
            out = calculate_tnfd_outputs(s, s.encore_score, s.son_score)
            
        results.append({
            "site_id": s.site_id,
            "name": s.name,
            "country": s.country,
            "activities": s.activities,
            "tnfd_priority": out.get("is_tnfd_priority", False),
            "priority_tier": out.get("priority_tier", "N/A"),
            "impact_level": out.get("impact_level", "N/A"),
            "priority_score": out.get("priority_score", 0),
            # Pressure Chips (First 5)
            "pressures": [
                {"label": "Water", "level": s.encore_score.ep_water_use if s.encore_score else "VL"},
                {"label": "Land", "level": s.encore_score.ep_land_use if s.encore_score else "VL"},
                {"label": "Biodiv", "level": s.encore_score.ep_overall_pressure_biodiversity if s.encore_score else "VL"},
                {"label": "Pollution", "level": s.encore_score.ep_toxic_emissions if s.encore_score else "VL"},
                {"label": "Waste", "level": s.encore_score.ep_solid_waste if s.encore_score else "VL"},
            ],
            # Dependency Chips (First 5)
            "dependencies": [
                {"label": "Water", "level": s.encore_score.dep_water_supply if s.encore_score else "VL"},
                {"label": "Soil", "level": s.encore_score.dep_soil_sediment_retention if s.encore_score else "VL"},
                {"label": "Biodiv", "level": s.encore_score.dep_overall_dependency_biodiversity if s.encore_score else "VL"},
                {"label": "Climate", "level": s.encore_score.dep_climate_regulation if s.encore_score else "VL"},
                {"label": "Pollin", "level": s.encore_score.dep_pollination if s.encore_score else "VL"},
            ]
        })
    return results

@router.get("/sites/{site_id}")
def get_site_detail(site_id: uuid.UUID, db: Session = Depends(get_db)):
    site = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    out = {}
    if site.encore_score and site.son_score:
        out = calculate_tnfd_outputs(site, site.encore_score, site.son_score)
        
    # Fetch all ENCORE data for the site's activities
    top_impacts = []
    top_dependencies = []
    if site.activities:
        records = db.query(IndustryLeapData).filter(IndustryLeapData.activity_name.in_(site.activities)).all()
        rating_rank = {"VL": 1, "L": 2, "M": 3, "H": 4, "VH": 5}
        
        # Aggregated impacts
        impacts_dict = {}
        for r in records:
            if r.impact_driver and r.impact_rating and r.impact_rating != 'ND':
                driver = r.impact_driver
                rating = r.impact_rating
                if driver not in impacts_dict or rating_rank.get(rating, 0) > rating_rank.get(impacts_dict[driver], 0):
                    impacts_dict[driver] = rating
        sorted_impacts = sorted(
            [{"impact_driver": k, "rating": v} for k, v in impacts_dict.items()],
            key=lambda x: (-rating_rank.get(x["rating"], 0), x["impact_driver"])
        )
        top_impacts = sorted_impacts[:5]
        
        # Aggregated dependencies
        deps_dict = {}
        for r in records:
            if r.ecosystem_service and r.severity and r.severity != 'ND':
                service = r.ecosystem_service
                rating = r.severity
                just = r.justification or ""
                if service not in deps_dict or rating_rank.get(rating, 0) > rating_rank.get(deps_dict[service]["rating"], 0):
                    deps_dict[service] = {"rating": rating, "justification": just}
        sorted_deps = sorted(
            [{"ecosystem_service": k, "rating": v["rating"], "justification": v["justification"]} for k, v in deps_dict.items()],
            key=lambda x: (-rating_rank.get(x["rating"], 0), x["ecosystem_service"])
        )
        top_dependencies = sorted_deps[:5]

    out["top_impacts"] = top_impacts
    out["top_dependencies"] = top_dependencies
        
    return {
        "metadata": {
            "site_id": site.site_id,
            "name": site.name,
            "country": site.country,
            "biome_code": site.biome_code,
            "activities": site.activities,
            "geometry": site.geometry,
            "created_at": site.created_at
        },
        "analysis": out
    }


@router.get("/sites/{site_id}/impact-dependency-summary")
def get_site_summary(site_id: uuid.UUID, db: Session = Depends(get_db)):
    # Lightweight version of detail for quick cards
    site = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    out = {}
    if site.encore_score and site.son_score:
        out = calculate_tnfd_outputs(site, site.encore_score, site.son_score)
        
    return {
        "impact_score": out.get("impact_score"),
        "impact_level": out.get("impact_level"),
        "dependency_risk_score": out.get("dependency_risk_score"),
        "priority_score": out.get("priority_score"),
        "is_tnfd_priority": out.get("is_tnfd_priority")
    }

@router.delete("/sites/{site_id}")
def delete_site(site_id: uuid.UUID, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.site_id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    # Explicitly delete child records to avoid database constraint conflicts
    db.query(SiteEncoreScore).filter(SiteEncoreScore.site_id == site_id).delete()
    db.query(SiteSonScore).filter(SiteSonScore.site_id == site_id).delete()
    db.delete(site)
    db.commit()
    return {"status": "success", "message": "Site deleted"}

@router.post("/sites/clear")
def clear_sites(db: Session = Depends(get_db)):
    db.query(SiteEncoreScore).delete()
    db.query(SiteSonScore).delete()
    db.query(Site).delete()
    db.commit()
    return {"status": "success", "message": "All sites cleared"}

