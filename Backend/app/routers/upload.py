import os
import uuid
# pyrefly: ignore [missing-import]
import httpx
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Site, SiteEncoreScore, IndustryLeapData, SiteSonScore
from app.services.spatial_service import parse_kml_geometry, process_kmz_to_geojson
from app.services.encore_service import get_encore_scores_for_activities
from pydantic import BaseModel

router = APIRouter(prefix="/api")

SON_BACKEND_URL = os.getenv("SON_BACKEND_URL", "http://localhost:8001")

@router.get("/activities", response_model=List[str])
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(IndustryLeapData.activity_name).distinct().all()
    return sorted([a[0] for a in activities])

async def trigger_son_analysis(site_id: uuid.UUID, geometry: Dict[str, Any]):
    """
    Background task to notify SoN backend to process the geometry.
    SoN backend is expected to write to site_son_scores table directly.
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: Upload to SoN
            # Assuming SoN has an endpoint that accepts geometry and site_id
            resp = await client.post(f"{SON_BACKEND_URL}/api/external/sync-site", json={
                "site_id": str(site_id),
                "geometry": geometry
            })
            resp.raise_for_status()
    except Exception as e:
        print(f"Failed to notify SoN backend: {e}")

@router.post("/upload-kml")
async def upload_kml(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    site_name: str = Form(...),
    activities_json: str = Form(...), # Passed as JSON string from frontend
    db: Session = Depends(get_db)
):
    print(f"DEBUG: Received upload request for {site_name} with file {file.filename}")
    # 1. Parse activities
    try:
        activities = json.loads(activities_json)
        if not isinstance(activities, list):
            activities = [activities]
    except:
        activities = [activities_json]

    # 2. Process File
    print("DEBUG: Reading file content...")
    content = await file.read()
    geometry = None
    lat, lng = 0.0, 0.0
    
    print(f"DEBUG: Processing file: {file.filename}")
    if file.filename.lower().endswith('.kmz'):
        geometry, (lat, lng) = process_kmz_to_geojson(content)
    elif file.filename.lower().endswith('.kml'):
        geometry, (lat, lng) = parse_kml_geometry(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .kml or .kmz")

    print(f"DEBUG: Geometry parsed. Centroid: ({lat}, {lng})")
    if not geometry:
        raise HTTPException(status_code=400, detail="Could not parse geometry from file")

    # 3. Create Site Entry (Persistent)
    print("DEBUG: Creating database entry...")
    site_id = uuid.uuid4()
    new_site = Site(
        site_id=site_id,
        name=site_name,
        country="India", # Fallback
        latitude=lat,
        longitude=lng,
        biome_code="T1", # Default
        activities=activities,
        geometry=geometry,
        uploaded_kml_path=file.filename
    )
    db.add(new_site)
    
    # 4. Run ENCORE Ingestion (Sync)
    print("DEBUG: Running ENCORE lookup...")
    encore_data = get_encore_scores_for_activities(db, activities)
    new_encore = SiteEncoreScore(
        site_id=site_id,
        **encore_data
    )
    db.add(new_encore)
    
    print("DEBUG: Inserting default SoN score...")
    default_son = SiteSonScore(
        site_id=site_id,
        dim1_extent_level='VL',
        dim2_freshwater_level='VL',
        dim2_terrestrial_level='VL',
        dim3_population_level='VL',
        dim4_extinction_level='VL',
        biome_code='T1',
        data_confidence='low',
        measured_metrics_count=0
    )
    db.add(default_son)
    
    print("DEBUG: Committing to database...")
    db.commit()
    print("DEBUG: Database commit successful.")

    # 5. Trigger Background SoN Analysis
    print("DEBUG: Triggering SoN background task...")
    background_tasks.add_task(trigger_son_analysis, site_id, geometry)

    return {
        "status": "success",
        "message": "Site created and analysis queued",
        "site_id": site_id,
        "site_name": site_name
    }
