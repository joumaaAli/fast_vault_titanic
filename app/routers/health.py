from http.client import HTTPException

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.database import get_db

router = APIRouter()

@router.get("/status")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unhealthy")
