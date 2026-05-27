from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.models.models import Site, SiteEncoreScore, SiteSonScore

def clear_data():
    db: Session = SessionLocal()
    print("Clearing all site-related data...")
    try:
        # Drop and recreate tables to be safe and clean
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE sites, site_encore_scores, site_son_scores CASCADE"))
            conn.commit()
        print("Database cleared. All sites and scores removed.")
    except Exception as e:
        print(f"Error clearing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
