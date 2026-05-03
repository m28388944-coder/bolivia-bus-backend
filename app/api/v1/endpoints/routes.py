from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.route_service import get_departamentos, search_schedules
from app.schemas.route import SearchRequest
from typing import List

router = APIRouter()

@router.get("/departamentos")
def list_departamentos():
    return {"departamentos": get_departamentos()}

@router.post("/search")
def search(data: SearchRequest, db: Session = Depends(get_db)):
    results = search_schedules(db, data.origin, data.destination, data.date)
    return {"results": results, "total": len(results)}
