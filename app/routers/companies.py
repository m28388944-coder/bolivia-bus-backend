from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Company, Bus, Route

router = APIRouter()

@router.get("/")
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.activa == True).all()
    result = []
    for c in companies:
        total_buses = db.query(Bus).filter(Bus.company_id == c.id, Bus.activo == True).count()
        total_rutas = db.query(Route).filter(Route.company_id == c.id, Route.activa == True).count()
        result.append({
            "id": c.id,
            "nombre": c.nombre,
            "ruc": c.ruc,
            "color_flota": c.color_flota,
            "telefono": c.telefono,
            "email": c.email,
            "activa": c.activa,
            "total_buses": total_buses,
            "total_rutas": total_rutas,
        })
    return result