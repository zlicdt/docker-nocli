from fastapi import FastAPI

router = FastAPI()

@router.get("/")
def status_root():
    return {"status": "online"}