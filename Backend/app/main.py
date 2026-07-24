from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal, get_db
from seed_data import check_and_seed_data
from app.routers import portfolio, sites, upload
from sqlalchemy.orm import Session
from app.models.models import IndustryLeapData, Site
import os

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Database migration helper: Ensure metrics, measured_metrics_count, and data_confidence columns exist in site_son_scores
from sqlalchemy import text
try:
    with engine.begin() as conn:
        # Postgres check
        if "postgresql" in str(engine.url):
            # Check metrics column
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='site_son_scores' AND column_name='metrics'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN metrics JSONB"))
                print("Migration: Added metrics JSONB column to site_son_scores.")
            
            # Check measured_metrics_count column
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='site_son_scores' AND column_name='measured_metrics_count'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN measured_metrics_count INTEGER DEFAULT 0"))
                print("Migration: Added measured_metrics_count column to site_son_scores.")
                
            # Check data_confidence column
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='site_son_scores' AND column_name='data_confidence'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN data_confidence VARCHAR"))
                print("Migration: Added data_confidence column to site_son_scores.")
        else:
            # SQLite check
            res = conn.execute(text("PRAGMA table_info(site_son_scores)"))
            columns = [row[1] for row in res.fetchall()]
            if 'metrics' not in columns:
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN metrics JSON"))
                print("Migration: Added metrics JSON column to site_son_scores (SQLite).")
            if 'measured_metrics_count' not in columns:
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN measured_metrics_count INTEGER DEFAULT 0"))
                print("Migration: Added measured_metrics_count column to site_son_scores (SQLite).")
            if 'data_confidence' not in columns:
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN data_confidence VARCHAR"))
                print("Migration: Added data_confidence column to site_son_scores (SQLite).")
except Exception as e:
    print(f"Error executing startup database migration: {e}")

# Auto-seed ENCORE dataset if empty
db = SessionLocal()
try:
    check_and_seed_data(db)
except Exception as e:
    print(f"Error during auto-seeding: {e}")
finally:
    db.close()

app = FastAPI(title="TNFD Impacts & Dependencies API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


app.include_router(portfolio.router, prefix="/api")
app.include_router(sites.router, prefix="/api")
app.include_router(upload.router) # upload already has /api in its own definition


@app.get("/")
def read_root():
    return {"message": "!!! TNFD V2 IS HERE !!!"}

@app.get("/api/test")
def test_route():
    return {"message": "API is working"}

@app.get("/api/debug-db")
def debug_db(db: Session = Depends(get_db)):
    try:
        leap_count = db.query(IndustryLeapData).count()
        site_count = db.query(Site).count()
        first_leap = db.query(IndustryLeapData).first()
        first_leap_data = {
            "id": first_leap.id,
            "activity_name": first_leap.activity_name,
            "ecosystem_service": first_leap.ecosystem_service,
            "impact_driver": first_leap.impact_driver
        } if first_leap else None
        
        # Check files
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        files = {
            "dep_csv": os.path.exists(os.path.join(backend_dir, "ENCORE dependency materialities.csv")),
            "xlsx": os.path.exists(os.path.join(backend_dir, "ENCORE dependencies database.xlsx")),
            "imp_csv": os.path.exists(os.path.join(backend_dir, "ENCORE impacts materiality_Mar 2023_Transposed.csv"))
        }
        
        # Check db url (redacted password)
        db_url = str(engine.url)
        if "@" in db_url:
            parts = db_url.split("@")
            db_url = parts[0].split(":")[0] + "://***@" + parts[1]
            
        return {
            "status": "success",
            "db_url": db_url,
            "leap_count": leap_count,
            "site_count": site_count,
            "first_leap": first_leap_data,
            "files": files,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
