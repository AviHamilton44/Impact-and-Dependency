from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Site, SiteEncoreScore, SiteSonScore
from app.services.computation_service import calculate_tnfd_outputs
from typing import List, Dict, Any

def enum_to_num(val: str) -> int:
    return {"VL": 1, "L": 2, "M": 3, "H": 4, "VH": 5}.get(val, 1)

router = APIRouter(tags=["Portfolio"])

@router.get("/dashboard/kpis")
def get_dashboard_kpis(db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).all()
    
    total_sites = len(sites)
    priority_count = 0
    top_pressure = "N/A"
    top_dependency = "N/A"
    
    all_scores = []
    for s in sites:
        if s.encore_score and s.son_score:
            out = calculate_tnfd_outputs(s, s.encore_score, s.son_score)
            if out.get("is_tnfd_priority"):
                priority_count += 1
            all_scores.append(out)

    # Simple logic for top pressure/dependency across portfolio
    if all_scores:
        # Flatten impact breakdowns to find the most common 'VH' or 'H'
        # For MVP, we just return the count of priority sites
        pass

    return {
        "analysed_sites": total_sites,
        "top_pressure": "Land Use" if total_sites > 0 else "N/A", # Placeholder logic
        "top_dependency": "Water Supply" if total_sites > 0 else "N/A",
        "tnfd_priority_sites": priority_count
    }

@router.get("/dashboard/map")
def get_dashboard_map(db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).all()
    
    features = []
    for s in sites:
        impact_level = "N/A"
        out = {}
        if s.encore_score and s.son_score:
            out = calculate_tnfd_outputs(s, s.encore_score, s.son_score)
            impact_level = out.get("impact_level", "VL")

        features.append({
            "type": "Feature",
            "properties": {
                "site_id": str(s.site_id),
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "impact_level": impact_level,
                "priority_tier": out.get("priority_tier") if impact_level != "N/A" else "N/A",
                "priority_score": out.get("priority_score", 0) if impact_level != "N/A" else 0,
                "activities": s.activities
            },
            "geometry": s.geometry
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/dashboard/top-priority-sites")
def get_top_priority_sites(db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).all()
    
    results = []
    for s in sites:
        if s.encore_score and s.son_score:
            out = calculate_tnfd_outputs(s, s.encore_score, s.son_score)
            results.append({
                "site_id": s.site_id,
                "name": s.name,
                "priority_score": out.get("priority_score"),
                "priority_tier": out.get("priority_tier"),
                "impact_level": out.get("impact_level")
            })
    
    return sorted(results, key=lambda x: x["priority_score"], reverse=True)[:5]

@router.get("/portfolio/impact-dependency-overview")
def get_portfolio_overview(db: Session = Depends(get_db)):
    sites = db.query(Site).options(joinedload(Site.encore_score), joinedload(Site.son_score)).all()
    
    impact_totals = {
        "Extent Loss": 0.0,
        "Freshwater Condition": 0.0,
        "Terrestrial Condition": 0.0,
        "Species Populations": 0.0,
        "Extinction Risk": 0.0
    }
    dependency_totals = {
        "Water Supply": 0.0,
        "Soil Retention": 0.0,
        "Biodiversity Regulation": 0.0,
        "Climate Regulation": 0.0,
        "Pollination": 0.0
    }
    
    overall_impact_counts = {"VL": 0, "L": 0, "M": 0, "H": 0, "VH": 0}
    overall_dep_counts = {"VL": 0, "L": 0, "M": 0, "H": 0, "VH": 0}
    
    count = 0
    for s in sites:
        if s.encore_score and s.son_score:
            out = calculate_tnfd_outputs(s, s.encore_score, s.son_score)
            ib = out["impact_breakdown"]
            db_breakdown = out["dependency_breakdown"]
            
            # Map impact score (0-100) to 0-5 scale
            impact_totals["Extent Loss"] += ib["extent"]["score"] / 20.0
            impact_totals["Freshwater Condition"] += ib["freshwater"]["score"] / 20.0
            impact_totals["Terrestrial Condition"] += ib["terrestrial"]["score"] / 20.0
            impact_totals["Species Populations"] += ib["population"]["score"] / 20.0
            impact_totals["Extinction Risk"] += ib["extinction"]["score"] / 20.0
            
            dependency_totals["Water Supply"] += enum_to_num(db_breakdown.get("water", "VL"))
            dependency_totals["Soil Retention"] += enum_to_num(db_breakdown.get("soil", "VL"))
            dependency_totals["Biodiversity Regulation"] += enum_to_num(db_breakdown.get("biodiversity", "VL"))
            dependency_totals["Climate Regulation"] += enum_to_num(db_breakdown.get("climate", "VL"))
            dependency_totals["Pollination"] += enum_to_num(db_breakdown.get("pollination", "VL"))
            
            overall_impact_counts[out["impact_level"]] += 1
            overall_dep_counts[out["dependency_risk_level"]] += 1
            count += 1
            
    if count > 0:
        for k in impact_totals:
            impact_totals[k] = round(impact_totals[k] / count, 2)
        for k in dependency_totals:
            dependency_totals[k] = round(dependency_totals[k] / count, 2)
            
    return {
        "impact_distribution": impact_totals,
        "dependency_distribution": dependency_totals,
        "overall_impact_counts": overall_impact_counts,
        "overall_dep_counts": overall_dep_counts
    }

