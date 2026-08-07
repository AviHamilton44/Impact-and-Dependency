import json
from app.database import SessionLocal
from app.models.models import Site, SiteSonScore

def inspect_db():
    db = SessionLocal()
    scores = db.query(SiteSonScore).all()
    print(f"Total Son scores: {len(scores)}")
    for score in scores:
        print("="*50)
        print(f"Site ID: {score.site_id}")
        print(f"Data Confidence: {score.data_confidence}")
        print(f"Measured Metrics Count: {score.measured_metrics_count}")
        print(f"Metrics (JSON):")
        print(json.dumps(score.metrics, indent=2) if score.metrics else "None")
    db.close()

if __name__ == "__main__":
    inspect_db()
