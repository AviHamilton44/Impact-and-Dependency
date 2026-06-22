import os
import pandas as pd
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import IndustryLeapData, Site, SiteEncoreScore, SiteSonScore
from app.services.encore_service import get_encore_scores_for_activities
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_and_seed_data(db: Session):
    # Check if we already have seeded data
    if db.query(IndustryLeapData).first() is not None:
        print("IndustryLeapData already seeded. Skipping auto-seed.")
        return

    print("Auto-seeding IndustryLeapData...")
    # Get paths relative to this script
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    dep_csv_path = os.path.join(backend_dir, "ENCORE dependency materialities.csv")
    xlsx_path = os.path.join(backend_dir, "ENCORE dependencies database.xlsx")
    imp_csv_path = os.path.join(backend_dir, "ENCORE impacts materiality_Mar 2023_Transposed.csv")

    # Clean rating mapping
    rating_map = {
        'very high': 'VH', 'vh': 'VH',
        'high': 'H', 'h': 'H',
        'medium': 'M', 'm': 'M',
        'low': 'L', 'l': 'L',
        'very low': 'VL', 'vl': 'VL',
        'nd': 'ND', 'no dependency': 'ND', 'no impact': 'ND'
    }

    # Load Excel justifications mapping
    print("Loading Excel justifications...")
    df_xlsx = pd.read_excel(xlsx_path, header=None)
    headers = [str(x).strip() for x in df_xlsx.iloc[1]]
    process_rows = {}
    for idx, row in df_xlsx.iloc[2:].iterrows():
        p_name = str(row[2]).strip()
        process_rows[p_name] = row

    def get_excel_justification(process, service):
        if process not in process_rows:
            return None
        row = process_rows[process]
        best_col_idx = None
        best_score = 0
        for idx, h in enumerate(headers):
            if idx < 3: continue
            score = similarity(service, h)
            if service.lower() in h.lower() or h.lower() in service.lower():
                score += 0.5
            if score > best_score:
                best_score = score
                best_col_idx = idx
                
        if best_col_idx is not None and best_score >= 0.5:
            val = row[best_col_idx]
            if pd.notna(val) and str(val).strip() != "" and str(val).strip().lower() != "nan":
                return str(val).strip()
        return None

    # 1. Seed IndustryLeapData (Dependencies)
    print("Seeding IndustryLeapData (Dependencies)...")
    try:
        df_dep = pd.read_csv(dep_csv_path)
        for _, row in df_dep.iterrows():
            process_val = str(row.get('Process', '')).strip()
            service_val = str(row.get('Ecosystem Service', '')).strip()
            rating_val = str(row.get('Rating', '')).strip()
            csv_just = str(row.get('Justification', '')).strip()
            
            if not process_val or process_val.lower() == 'nan':
                continue
                
            excel_just = get_excel_justification(process_val, service_val)
            justification_val = excel_just if excel_just else csv_just
            rating_clean = rating_map.get(rating_val.lower(), 'ND')
            
            item = IndustryLeapData(
                activity_name=process_val,
                sasb_code=None,
                industry=None,
                ecosystem_service=service_val,
                dependency_type=None,
                impact_driver=None,
                severity=rating_clean,
                impact_rating=None,
                justification=justification_val
            )
            db.add(item)
        db.commit()
    except Exception as e:
        print(f"Error seeding dependencies: {e}")

    # 2. Seed IndustryLeapData (Impacts)
    print("Seeding IndustryLeapData (Impacts)...")
    try:
        df_imp = pd.read_csv(imp_csv_path)
        for _, row in df_imp.iterrows():
            process_val = str(row.get('Production process', '')).strip()
            driver_val = str(row.get('Impact driver', '')).strip()
            rating_val = str(row.get('Rating', '')).strip()
            sub_ind_val = str(row.get('Sub-Industry', '')).strip()
            
            if not process_val or process_val.lower() == 'nan':
                continue
                
            rating_clean = rating_map.get(rating_val.lower(), 'ND')
            
            item = IndustryLeapData(
                activity_name=process_val,
                sasb_code=None,
                industry=sub_ind_val,
                ecosystem_service=None,
                dependency_type=None,
                impact_driver=driver_val,
                severity=None,
                impact_rating=rating_clean,
                justification=None
            )
            db.add(item)
        db.commit()
    except Exception as e:
        print(f"Error seeding impacts: {e}")

    db.commit()
    print("Seeding completed successfully.")

def seed_data():
    # Drop problematic tables from old schema manually if they exist
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS site_state_of_nature CASCADE"))
        conn.commit()

    # Drop all and recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        check_and_seed_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
