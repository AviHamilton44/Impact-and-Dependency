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
            
        # Get dynamic levels if available, else fallback
        ep_water = "VL"
        ep_land = "VL"
        ep_biodiv = "VL"
        ep_pollute = "VL"
        ep_waste = "VL"
        
        dep_water = "VL"
        dep_soil = "VL"
        dep_biodiv = "VL"
        dep_climate = "VL"
        dep_pollin = "VL"
        
        if out:
            for imp in out.get("all_impacts", []):
                if "Water Use" in imp["category"]: ep_water = imp["level"]
                elif "Land Use" in imp["category"]: ep_land = imp["level"]
                elif "Biodiversity" in imp["category"]: ep_biodiv = imp["level"]
                elif "Water Pollution" in imp["category"]: ep_pollute = imp["level"]
                elif "Solid Waste" in imp["category"]: ep_waste = imp["level"]
            
            for dep in out.get("all_dependencies", []):
                if "Water Supply" in dep["category"]: dep_water = dep["level"]
                elif "Soil" in dep["category"]: dep_soil = dep["level"]
                elif "Biodiversity" in dep["category"]: dep_biodiv = dep["level"]
                elif "Climate" in dep["category"]: dep_climate = dep["level"]
                elif "Pollination" in dep["category"]: dep_pollin = dep["level"]
            
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
                {"label": "Water", "level": ep_water},
                {"label": "Land", "level": ep_land},
                {"label": "Biodiv", "level": ep_biodiv},
                {"label": "Pollution", "level": ep_pollute},
                {"label": "Waste", "level": ep_waste},
            ],
            # Dependency Chips (First 5)
            "dependencies": [
                {"label": "Water", "level": dep_water},
                {"label": "Soil", "level": dep_soil},
                {"label": "Biodiv", "level": dep_biodiv},
                {"label": "Climate", "level": dep_climate},
                {"label": "Pollin", "level": dep_pollin},
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

