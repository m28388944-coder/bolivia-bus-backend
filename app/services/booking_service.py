from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from app.models.booking import Booking, BookingStatus
from app.models.seat import Seat, SeatStatus
from app.models.schedule import Schedule
from app.core.security import create_access_token
import uuid

def get_seats_by_schedule(db: Session, schedule_id: UUID):
    return db.query(Seat).filter(Seat.schedule_id == schedule_id).all()

def create_booking(db: Session, schedule_id: UUID, seat_id: UUID,
                   passenger_name: str, passenger_ci: str, user_id: UUID):
    seat = db.query(Seat).filter(
        Seat.id == seat_id,
        Seat.status == SeatStatus.AVAILABLE
    ).first()
    if not seat:
        return None, "Asiento no disponible"
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        return None, "Horario no encontrado"
    price_map = {
        "normal": schedule.price_normal,
        "semicama": schedule.price_semicama,
        "cama": schedule.price_cama,
    }
    base_price = price_map.get(schedule.bus.bus_type.value, schedule.price_normal)
    total = base_price + schedule.terminal_fee
    booking = Booking(
        id=uuid.uuid4(),
        user_id=user_id,
        schedule_id=schedule_id,
        seat_id=seat_id,
        passenger_name=passenger_name,
        passenger_ci=passenger_ci,
        base_price=base_price,
        terminal_fee=schedule.terminal_fee,
        total_price=total,
        status=BookingStatus.CONFIRMED,
    )
    qr_data = {"booking_id": str(booking.id), "ci": passenger_ci}
    booking.qr_token = create_access_token(qr_data)
    seat.status = SeatStatus.OCCUPIED
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking, None
