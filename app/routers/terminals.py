from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Terminal, TerminalService

router = APIRouter()

@router.get("/")
def get_terminals(db: Session = Depends(get_db)):
    terminals = db.query(Terminal).filter(Terminal.activa == True).all()
    return [{"id": t.id, "nombre": t.nombre, "ciudad": t.ciudad, "direccion": t.direccion, "lat": t.lat, "lng": t.lng} for t in terminals]

@router.get("/{terminal_id}")
def get_terminal(terminal_id: str, db: Session = Depends(get_db)):
    t = db.query(Terminal).options(joinedload(Terminal.services)).filter(Terminal.id == terminal_id).first()
    if not t:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Terminal no encontrada")
    return {
        "id": t.id, "nombre": t.nombre, "ciudad": t.ciudad,
        "direccion": t.direccion, "lat": t.lat, "lng": t.lng,
        "telefono": t.telefono,
        "servicios": [
            {
                "id": s.id, "tipo": s.tipo.value, "nombre": s.nombre,
                "descripcion": s.descripcion, "horario": s.horario,
                "lat": s.lat, "lng": s.lng
            }
            for s in t.services if s.activo
        ]
    }