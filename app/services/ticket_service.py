from sqlalchemy.orm import Session
from uuid import UUID
from app.models.booking import Booking
from app.models.seat import Seat
from app.models.schedule import Schedule
from app.models.route import Route
from app.models.bus import Bus

def get_ticket(db: Session, booking_id: UUID):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return None
    schedule = db.query(Schedule).filter(Schedule.id == booking.schedule_id).first()
    route = db.query(Route).filter(Route.id == schedule.route_id).first()
    bus = db.query(Bus).filter(Bus.id == schedule.bus_id).first()
    seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
    return {
        "booking_id": booking.id,
        "passenger_name": booking.passenger_name,
        "passenger_ci": booking.passenger_ci,
        "origin": route.origin,
        "destination": route.destination,
        "departure_time": schedule.departure_time,
        "seat_number": seat.seat_number,
        "floor": seat.floor,
        "bus_type": bus.bus_type.value,
        "company": bus.company,
        "base_price": booking.base_price,
        "terminal_fee": booking.terminal_fee,
        "total_price": booking.total_price,
        "qr_token": booking.qr_token,
        "status": booking.status.value,
    }
