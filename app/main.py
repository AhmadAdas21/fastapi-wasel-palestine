from fastapi import FastApi

app=fastapi(
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