from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.services.seat_service import get_seat_map, reserve_seat_with_lock, release_expired_seats

router = APIRouter()

@router.get("/map/{schedule_id}")
def seat_map(schedule_id: UUID, db: Session = Depends(get_db)):
    result = get_seat_map(db, schedule_id)
    if not result["total"]:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return result

@router.post("/reserve/{seat_id}")
def reserve_seat(seat_id: UUID, db: Session = Depends(get_db)):
    seat, error = reserve_seat_with_lock(db, seat_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "message": "Asiento reservado por 15 minutos",
        "seat_id": str(seat.id),
        "seat_number": seat.seat_number,
        "status": seat.status.value,
        "reserved_until": seat.reserved_until,
    }

@router.post("/release-expired")
def release_expired(db: Session = Depends(get_db)):
    count = release_expired_seats(db)
    return {"message": f"{count} asientos liberados"}
