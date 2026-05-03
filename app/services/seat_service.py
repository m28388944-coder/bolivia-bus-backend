from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timedelta
from app.models.seat import Seat, SeatStatus
from app.models.schedule import Schedule

def get_seat_map(db: Session, schedule_id: UUID):
    seats = db.query(Seat).filter(Seat.schedule_id == schedule_id).order_by(Seat.floor, Seat.row, Seat.column).all()
    floor1 = []
    floor2 = []
    for s in seats:
        data = {
            "id": str(s.id),
            "seat_number": s.seat_number,
            "floor": s.floor,
            "row": s.row,
            "column": s.column,
            "status": s.status.value,
        }
        if s.floor == 1:
            floor1.append(data)
        else:
            floor2.append(data)
    return {"floor_1": floor1, "floor_2": floor2, "total": len(seats)}

def reserve_seat_with_lock(db: Session, seat_id: UUID, minutes: int = 15):
    seat = db.query(Seat).filter(Seat.id == seat_id).with_for_update().first()
    if not seat:
        return None, "Asiento no encontrado"
    if seat.status != SeatStatus.AVAILABLE:
        return None, "Asiento no disponible"
    seat.status = SeatStatus.RESERVED
    seat.reserved_until = datetime.utcnow() + timedelta(minutes=minutes)
    db.commit()
    db.refresh(seat)
    return seat, None

def release_expired_seats(db: Session):
    now = datetime.utcnow()
    expired = db.query(Seat).filter(
        Seat.status == SeatStatus.RESERVED,
        Seat.reserved_until < now
    ).all()
    count = 0
    for seat in expired:
        seat.status = SeatStatus.AVAILABLE
        seat.reserved_until = None
        count += 1
    db.commit()
    return count
