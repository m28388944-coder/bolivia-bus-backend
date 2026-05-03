from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.schedule import Schedule
from app.models.route import Route
from app.models.bus import Bus
from app.models.seat import Seat, SeatStatus

DEPARTAMENTOS = [
    "La Paz", "Santa Cruz", "Cochabamba",
    "Oruro", "Potosi", "Sucre", "Tarija"
]

def search_schedules(db: Session, origin: str, destination: str, date: str):
    search_date = datetime.strptime(date, "%Y-%m-%d")
    results = db.query(Schedule).join(Route).join(Bus).filter(
        and_(
            Route.origin == origin,
            Route.destination == destination,
            Schedule.departure_time >= search_date,
            Schedule.status == "active"
        )
    ).all()
    output = []
    for s in results:
        available = db.query(Seat).filter(
            Seat.schedule_id == s.id,
            Seat.status == SeatStatus.AVAILABLE
        ).count()
        item = {
            "id": s.id,
            "route_id": s.route_id,
            "bus_id": s.bus_id,
            "departure_time": s.departure_time,
            "arrival_time": s.arrival_time,
            "price_normal": s.price_normal,
            "price_semicama": s.price_semicama,
            "price_cama": s.price_cama,
            "terminal_fee": s.terminal_fee,
            "status": s.status.value,
            "available_seats": available,
            "origin": s.route.origin,
            "destination": s.route.destination,
            "company": s.bus.company,
            "bus_type": s.bus.bus_type.value,
            "duration_hours": s.route.duration_hours,
        }
        output.append(item)
    return output

def get_departamentos():
    return DEPARTAMENTOS
