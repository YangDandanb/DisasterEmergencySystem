""" FastAPI entry point """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.landslides import router as landslide_router
from .api.facilities import router as facility_router
from .api.statistics import router as statistics_router
from .api.analysis import router as analysis_router

app = FastAPI(title="地质灾害应急系统 API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(landslide_router)
app.include_router(facility_router)
app.include_router(statistics_router)
app.include_router(analysis_router)

@app.get("/")
def root():
    return {"status": "running", "docs": "/docs"}
