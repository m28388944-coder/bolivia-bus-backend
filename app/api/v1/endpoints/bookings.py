from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking
from app.services.seat_service import release_expired_seats
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=BookingResponse)
def book(data: BookingCreate, db: Session = Depends(get_db)):
    release_expired_seats(db)
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    booking, error = create_booking(
        db=db,
        schedule_id=data.schedule_id,
        seat_id=data.seat_id,
        passenger_name=data.passenger_name,
        passenger_ci=data.passenger_ci,
        user_id=user_id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return booking

@router.get("/{booking_id}")
def get_booking(booking_id: UUID, db: Session = Depends(get_db)):
    from app.models.booking import Booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return booking

@router.get("/schedule/{schedule_id}")
def get_bookings_by_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    from app.models.booking import Booking
    from app.models.seat import Seat
    bookings = db.query(Booking).filter(Booking.schedule_id == schedule_id).all()
    result = []
    for b in bookings:
        seat = db.query(Seat).filter(Seat.id == b.seat_id).first()
        result.append({
            "id": str(b.id),
            "passenger_name": b.passenger_name,
            "passenger_ci": b.passenger_ci,
            "seat_number": seat.seat_number if seat else "-",
            "floor": seat.floor if seat else 0,
            "base_price": b.base_price,
            "terminal_fee": b.terminal_fee,
            "total_price": b.total_price,
            "status": b.status.value,
            "created_at": b.created_at.isoformat(),
        })
    return {"bookings": result, "total": len(result)}

@router.get("/all")
def get_all_bookings(db: Session = Depends(get_db)):
    from app.models.booking import Booking
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(50).all()
    return {"bookings": [{"id": str(b.id), "passenger_name": b.passenger_name, "status": b.status.value, "total_price": b.total_price} for b in bookings]}
