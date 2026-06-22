from fastapi import FastAPI
from app.api.v1.api import api_router
from app.db.database import Base, engine
from app.models import incident
from app.models import report
##Base.metadata.create_all(bind=engine)

Base.metadata.create_all(bind=engine)
app=FastAPI(
title="Wasel Palestine API",
    description="Backend API for Wasel Palestine project",
    version="1.0.0")


app.include_router(api_router, prefix="/api/v1")



@app.get("/")
def home():
    return {"message": "Welcome to Wasel Palestine:_:"}

@app.get("/health")
def health_check():
    return {"status": "OK"}