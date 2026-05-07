from fastapi import FastApi

router=routerAPI()

@router.get("/")
def get_incidents():
    return {"message": "List of road incidents will appear here"}

@router.post("/")
def create_incident():
    return{"message":"your incident created successfully"}