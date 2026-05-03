from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Booking, Ticket, Payment, Schedule, Seat, User
from app.models import EstadoReserva, EstadoTicket, EstadoPago, MetodoPago
from app.models.notification import Notification
from app.services.notifications import notificar_pasajero
from pydantic import BaseModel
from typing import List
import random, string

router = APIRouter()

def gen_codigo():
    return "BB" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

class PasajeroIn(BaseModel):
    seat_id: str
    nombre: str
    ci: str

class BookingIn(BaseModel):
    schedule_id: str
    pasajeros: List[PasajeroIn]
    metodo_pago: str = "efectivo"
    contacto_email: str = None
    contacto_telefono: str = None

@router.post("/")
def create_booking(req: BookingIn, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == req.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    seats = db.query(Seat).filter(Seat.id.in_([p.seat_id for p in req.pasajeros])).all()
    if len(seats) != len(req.pasajeros):
        raise HTTPException(status_code=400, detail="Asientos invalidos")

    user = db.query(User).filter(User.email == "admin@boliviabus.bo").first()
    if not user:
        raise HTTPException(status_code=500, detail="Usuario no encontrado")

    precio_total = schedule.precio_base * len(req.pasajeros)
    booking = Booking(
        user_id=user.id,
        schedule_id=schedule.id,
        codigo_reserva=gen_codigo(),
        estado=EstadoReserva.pagada,
        precio_total=precio_total
    )
    db.add(booking)
    db.flush()

    for pasajero in req.pasajeros:
        ticket = Ticket(
            booking_id=booking.id,
            seat_id=pasajero.seat_id,
            pasajero_nombre=pasajero.nombre,
            pasajero_ci=pasajero.ci,
            precio=schedule.precio_base,
            estado=EstadoTicket.activo
        )
        db.add(ticket)

    payment = Payment(
        booking_id=booking.id,
        metodo=MetodoPago(req.metodo_pago),
        monto=precio_total,
        estado=EstadoPago.completado
    )
    db.add(payment)

    schedule.asientos_disponibles = max(0, (schedule.asientos_disponibles or 0) - len(req.pasajeros))
    db.commit()
    db.refresh(booking)

    return {
        "id": booking.id,
        "codigo_reserva": booking.codigo_reserva,
        "precio_total": booking.precio_total,
        "estado": booking.estado.value
    }

@router.get("/my")
def my_bookings(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "admin@boliviabus.bo").first()
    if not user:
        return []
    from app.models import Bus
    bookings = db.query(Booking).options(
        joinedload(Booking.schedule).joinedload(Schedule.route),
        joinedload(Booking.schedule).joinedload(Schedule.bus),
        joinedload(Booking.tickets)
    ).filter(Booking.user_id == user.id).order_by(Booking.created_at.desc()).all()
    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "codigo_reserva": b.codigo_reserva,
            "estado": b.estado.value,
            "precio_total": b.precio_total,
            "created_at": b.created_at.isoformat(),
            "ruta": b.schedule.route.nombre,
            "hora_salida": b.schedule.hora_salida.isoformat(),
            "hora_llegada": b.schedule.hora_llegada_est.isoformat() if b.schedule.hora_llegada_est else None,
            "tickets": len(b.tickets),
            "placa": b.schedule.bus.placa if b.schedule.bus else None,
        })
    return result

@router.get("/all")
def all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).options(
        joinedload(Booking.schedule).joinedload(Schedule.route),
        joinedload(Booking.tickets).joinedload(Ticket.seat)
    ).order_by(Booking.created_at.desc()).limit(100).all()
    result = []
    for b in bookings:
        for t in (b.tickets or []):
            result.append({
                "id": t.id,
                "booking_id": b.id,
                "schedule_id": b.schedule_id,
                "codigo_reserva": b.codigo_reserva,
                "estado": b.estado.value,
                "precio_total": b.precio_total,
                "created_at": b.created_at.isoformat(),
                "ruta": b.schedule.route.nombre,
                "hora_salida": b.schedule.hora_salida.isoformat(),
                "passenger_name": t.pasajero_nombre,
                "passenger_ci": t.pasajero_ci,
                "seat_number": t.seat.numero if t.seat else None,
                "total_price": t.precio,
                "status": t.estado.value,
            })
    return result




