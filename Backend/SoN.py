import os
import sys
import shutil
import ee
import json
import math
import geopandas as gpd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add backend and current server dir to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append("c:\\Users\\Admin\\OneDrive\\Desktop\\State Of Nature v2")
sys.path.append("c:\\Users\\Admin\\OneDrive\\Desktop\\State Of Nature v2\\backend")
sys.path.append("c:\\Users\\Admin\\OneDrive\\Desktop\\State Of Nature v2\\server")
sys.path.append(os.path.join(PARENT_DIR, "backend"))
sys.path.append(PARENT_DIR)

try:
    from backend.gee_client import init_gee, extract_metrics
except ImportError:
    logger.warning("Could not import backend.gee_client. GEE features will be disabled.")
    init_gee = lambda: False
    extract_metrics = lambda *args, **kwargs: {}

try:
    from server.sector_data import get_sector_son_matrix
    from server.darukaa_reference.pipeline import Pipeline
    from server.darukaa_reference.config import Config
    from server.darukaa_reference.indicators import create_default_registry
    from server.scoring import calculate_scorecard
except ImportError:
    # Fallback for local development
    sys.path.append(CURRENT_DIR)
    from sector_data import get_sector_son_matrix
    from darukaa_reference.pipeline import Pipeline
    from darukaa_reference.config import Config
    from darukaa_reference.indicators import create_default_registry
    from scoring import calculate_scorecard

def sanitize_nan(data):
    """Recursively replace NaN values with None for JSON compliance."""
    if isinstance(data, dict):
        return {k: sanitize_nan(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_nan(x) for x in data]
    elif isinstance(data, float):
        return None if math.isnan(data) or math.isinf(data) else data
    return data


app = FastAPI(title="State of Nature Dashboard API")

# Environment Variables
PORT = int(os.getenv("PORT", 8001))
DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "https://state-of-nature-v2.vercel.app",
    "https://state-of-nature-v2-mjh9kv3vz-avihamilton44s-projects.vercel.app",
    "https://state-of-nature-v2.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "State of Nature Dashboard API is running", "environment": ENVIRONMENT}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gee_initialized": GEE_INITIALIZED,
        "database": "connected" if DATABASE_URL else "not_configured"
    }

GEE_INITIALIZED = False

@app.on_event("startup")
def startup_event():
    global GEE_INITIALIZED
    try:
        logger.info("Starting up Backend...")
        if DATABASE_URL:
            logger.info(f"Database URL configured: {DATABASE_URL[:10]}...")
        
        success = init_gee()
        if success:
            GEE_INITIALIZED = True
            logger.info("GEE initialized successfully.")
        else:
            logger.warning("GEE initialization skipped or failed.")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

# Initialize Pipeline Registry
REGISTRY = create_default_registry()

def get_pipeline_config(year: int):
    return Config(
        gee_project="darukaa-earth-product",
        bii_gee_asset="projects/darukaa-earth-product/assets/Biodiversity/bii-2020_v2-1-1",
        hmi_hard_ceiling=0.10,
        elevation_band_m=300.0,
        min_reference_pixels=5,
        ndvi_year=year,
        lst_year=year,
        raster_paths={
            "iucn_mammals": "projects/darukaa-earth-product/assets/Biodiversity/RedList_Mammals_Terrestrial",
            "iucn_birds":   "projects/darukaa-earth-product/assets/Biodiversity/RedList_Bird_IUCN_Category",
            "kba_global":   "projects/darukaa-earth-product/assets/Biodiversity/KBA_Global_POL_SEP25",
            "pv_binary":    "projects/darukaa-earth-product/assets/biodiversity_India_PV_Binary_2025_Full_Mosaic",
            "msa":          "projects/ee-jayankandir/assets/TerrestrialMSA_2015_World",
        },
        output_dir="./output"
    )

@app.post("/api/run-pipeline")
async def run_pipeline(
    file: UploadFile = File(...),
    year: int = Form(...),
    analysis_type: str = Form("single"),
    selected_metrics: str = Form(None)
):
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1. Load Geometry for return using SiteLoader
        from darukaa_reference.site_loader import SiteLoader
        loader = SiteLoader()
        try:
            gdf = loader.load(temp_file_path)
        except Exception as e:
            logger.error(f"Failed loading spatial file with SiteLoader: {e}")
            try:
                gdf = gpd.read_file(temp_file_path)
            except Exception as ex:
                raise HTTPException(status_code=400, detail=f"Invalid or unreadable spatial file '{file.filename}': {str(ex)}")

        if gdf.empty:
            raise HTTPException(status_code=400, detail="Invalid or empty spatial file")
        
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
            
        from shapely.geometry import mapping, Polygon, MultiPolygon, GeometryCollection
        from shapely.validation import make_valid
        
        # 2. Configure Pipeline
        logger.info(f"RUNNING: Darukaa Pipeline for {file.filename} (Year: {year})...")
        config = get_pipeline_config(year)
        
        # Filter registry if metrics are selected
        if selected_metrics:
            try:
                if selected_metrics.startswith('['):
                    selected_slugs = set(json.loads(selected_metrics))
                else:
                    selected_slugs = set(selected_metrics.split(','))
                    
                from darukaa_reference.registry import IndicatorRegistry
                filtered_registry = IndicatorRegistry()
                for ind in REGISTRY.all():
                    if ind.name in selected_slugs:
                        filtered_registry._indicators[ind.name] = ind
                logger.info(f"Filtered registry to {len(filtered_registry._indicators)} selected metrics.")
                active_registry = filtered_registry
            except Exception as e:
                import traceback
                logger.error(f"Error parsing selected_metrics '{selected_metrics}': {e}")
                logger.error(traceback.format_exc())
                active_registry = REGISTRY
        else:
            active_registry = REGISTRY

        pipeline = Pipeline(config, active_registry)
        
        if analysis_type == "agroforestry" and len(gdf) > 1:
            logger.info("Agroforestry mode selected. Running Phase 3b clustering.")
            from cluster_logic import cluster_polygons, aggregate_scorecards
            # Set eps to 100000 (100km) to group into 1 massive cluster and prevent GEE thread timeouts!
            clusters = cluster_polygons(gdf, eps=100000, min_samples=1)
            
            cluster_scorecards = []
            cluster_areas = []
            
            for idx, cluster in enumerate(clusters):
                logger.info(f"Processing cluster {idx+1}/{len(clusters)}: {cluster['n_farms']} farms, {cluster['area_ha']:.1f} Ha")
                cluster_geom = cluster["geometry"]
                cluster_areas.append(cluster["area_ha"])
                
                valid_cluster_geom = make_valid(cluster_geom)
                if isinstance(valid_cluster_geom, GeometryCollection):
                    polys = [g for g in valid_cluster_geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
                    if polys:
                        from shapely.ops import unary_union
                        valid_cluster_geom = unary_union(polys)

                cluster_temp_path = f"temp_cluster_{idx}.geojson"
                geojson_data = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"name": f"cluster_{idx}", "site_id": f"cluster_{idx}_0000"},
                            "geometry": mapping(valid_cluster_geom)
                        }
                    ]
                }
                with open(cluster_temp_path, "w", encoding="utf-8") as f:
                    json.dump(geojson_data, f)
                
                try:
                    report = pipeline.run(cluster_temp_path)
                    if "scorecard" in report and report["scorecard"]:
                        cluster_scorecards.append(report["scorecard"])
                    else:
                        logger.warning(f"Empty scorecard for cluster {idx+1}")
                finally:
                    if os.path.exists(cluster_temp_path):
                        os.remove(cluster_temp_path)
                        
            if not cluster_scorecards:
                raise Exception("All cluster pipeline runs failed or returned empty scorecards.")
                
            scorecard = aggregate_scorecards(cluster_scorecards, cluster_areas)
            
            from shapely.ops import unary_union
            project_union = unary_union(gdf.geometry.tolist())
            valid_proj_geom = make_valid(project_union)
            if isinstance(valid_proj_geom, GeometryCollection):
                polys = [g for g in valid_proj_geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
                if polys:
                    valid_proj_geom = unary_union(polys)
            geometry = mapping(valid_proj_geom)
            
        else:
            logger.info(f"Single site mode (or single polygon). Running standard pipeline.")
            from shapely.ops import unary_union
            from shapely.validation import make_valid
            if len(gdf) > 1:
                # If they select Single Site but upload multi-polygon, we union it as one site
                project_union = unary_union(gdf.geometry.tolist())
                valid_merged_geom = make_valid(project_union)
                if isinstance(valid_merged_geom, GeometryCollection):
                    polys = [g for g in valid_merged_geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
                    if polys:
                        valid_merged_geom = unary_union(polys)
                geometry = mapping(valid_merged_geom)
                # Create a temporary file with the merged polygon to process
                temp_merged_path = f"temp_merged_{file.filename}.geojson"
                geojson_data = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {"name": file.filename, "site_id": "site_merged_0000"},
                            "geometry": mapping(valid_merged_geom)
                        }
                    ]
                }
                with open(temp_merged_path, "w", encoding="utf-8") as f:
                    json.dump(geojson_data, f)
                report = pipeline.run(temp_merged_path)
                if os.path.exists(temp_merged_path):
                    os.remove(temp_merged_path)
            else:
                valid_single_geom = make_valid(gdf.geometry.iloc[0])
                if isinstance(valid_single_geom, GeometryCollection):
                    polys = [g for g in valid_single_geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
                    if polys:
                        valid_single_geom = unary_union(polys)
                geometry = mapping(valid_single_geom)
                report = pipeline.run(temp_file_path)
                
            scorecard = report.get("scorecard", [])
        
        # 3. Calculate Scorecard using updated scoring logic
        if not scorecard:
            raise Exception("Pipeline returned empty scorecard")
            
        scoring_results = calculate_scorecard(scorecard, active_registry)
        
        # 4. Final Response
        result = {
            "status": "success",
            "scoring": scoring_results,
            "geojson": geometry,
            "metadata": {
                "filename": file.filename,
                "year": year
            }
        }

        return JSONResponse(content=sanitize_nan(result))
        
    except Exception as e:
        import traceback
        logger.error(f"PIPELINE ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

from pydantic import BaseModel

class SyncSiteRequest(BaseModel):
    site_id: str
    geometry: dict

@app.post("/api/external/sync-site")
async def sync_site(req: SyncSiteRequest):
    logger.info(f"Received external sync-site request for site_id: {req.site_id}")
    
    # 1. Write geometry to a temporary GeoJSON file for the pipeline
    temp_sync_path = f"temp_sync_{req.site_id}.geojson"
    try:
        from shapely.geometry import mapping
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": f"site_{req.site_id}", "site_id": req.site_id},
                    "geometry": req.geometry
                }
            ]
        }
        with open(temp_sync_path, "w", encoding="utf-8") as f:
            json.dump(geojson_data, f)
            
        # 2. Configure and run the pipeline
        logger.info(f"Running GEE pipeline for synced site {req.site_id}...")
        config = get_pipeline_config(2024)
        pipeline = Pipeline(config, REGISTRY)
        report = pipeline.run(temp_sync_path)
        scorecard = report.get("scorecard", [])
        
        if not scorecard:
            raise Exception("GEE pipeline returned empty scorecard")
            
        # 3. Calculate scores
        scoring_results = calculate_scorecard(scorecard, REGISTRY)
        
        # 4. Save/update database
        from app.database import SessionLocal
        from app.models.models import SiteSonScore
        import uuid
        
        db = SessionLocal()
        try:
            site_uuid = uuid.UUID(req.site_id)
            son_score = db.query(SiteSonScore).filter(SiteSonScore.site_id == site_uuid).first()
            if not son_score:
                son_score = SiteSonScore(site_id=site_uuid)
                db.add(son_score)
                
            def map_score_to_level(score):
                if score is None: return 'VL'
                s = round(score)
                return {1: 'VL', 2: 'L', 3: 'M', 4: 'H', 5: 'VH'}.get(s, 'VL')
                
            son_score.dim1_extent_level = map_score_to_level(scoring_results.get("Extent"))
            son_score.dim2_freshwater_level = map_score_to_level(scoring_results.get("Condition"))
            son_score.dim2_terrestrial_level = map_score_to_level(scoring_results.get("Condition"))
            son_score.dim3_population_level = map_score_to_level(scoring_results.get("Population"))
            son_score.dim4_extinction_level = map_score_to_level(scoring_results.get("Extinction"))
            son_score.data_confidence = "medium" # default fallback
            son_score.measured_metrics_count = len(scorecard)
            son_score.metrics = sanitize_nan(scoring_results)
            
            db.commit()
            logger.info(f"Successfully committed synced scores for site_id {req.site_id} to database.")
        except Exception as db_err:
            db.rollback()
            logger.error(f"Database error during sync-site commit: {db_err}")
            raise db_err
        finally:
            db.close()
            
        return JSONResponse(content={
            "status": "success",
            "message": "Site synced and analyzed",
            "scoring": sanitize_nan(scoring_results)
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Sync-site error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_sync_path):
            os.remove(temp_sync_path)

@app.get("/api/sector-son-matrix")
async def sector_son_matrix():
    return get_sector_son_matrix()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
