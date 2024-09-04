import logging
from http.client import HTTPException

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.database import get_db

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/status")
async def health_check(db: Session = Depends(get_db)):
    try:
        logger.info("Health check initiated.")
        db.execute(text("SELECT 1"))
        logger.info("Health check successful.")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Unhealthy")
