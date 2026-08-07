import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv(dotenv_path="Backend/.env")
db_url = os.getenv("DATABASE_URL", "sqlite:///./tnfd_local.db")
print(f"Connecting to database: {db_url}")

try:
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)
        
    with engine.begin() as conn:
        if "postgresql" in db_url:
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='site_son_scores' AND column_name='metrics'"))
            if not res.fetchone():
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN metrics JSONB"))
                print("Successfully added metrics JSONB column to site_son_scores table in Postgres.")
            else:
                print("Column metrics already exists in Postgres.")
        else:
            res = conn.execute(text("PRAGMA table_info(site_son_scores)"))
            columns = [row[1] for row in res.fetchall()]
            if 'metrics' not in columns:
                conn.execute(text("ALTER TABLE site_son_scores ADD COLUMN metrics JSON"))
                print("Successfully added metrics JSON column to site_son_scores table in SQLite.")
            else:
                print("Column metrics already exists in SQLite.")
except Exception as e:
    print(f"Error during migration: {e}")
