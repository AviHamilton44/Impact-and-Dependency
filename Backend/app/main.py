from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import portfolio, sites, upload

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TNFD Impacts & Dependencies API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/api")
app.include_router(sites.router, prefix="/api")
app.include_router(upload.router) # upload already has /api in its own definition


@app.get("/")
def read_root():
    return {"message": "!!! TNFD V2 IS HERE !!!"}

@app.get("/api/test")
def test_route():
    return {"message": "API is working"}
