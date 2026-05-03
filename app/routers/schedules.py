from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Schedule, Route, Bus, Seat, Ticket, Terminal, EstadoHorario
from datetime import datetime

router = APIRouter()

@router.get("/")
def search_schedules(
    origen: str = Query(None),
    destino: str = Query(None),
    fecha: str = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Schedule).options(
        joinedload(Schedule.route).joinedload(Route.terminal_origen),
        joinedload(Schedule.route).joinedload(Route.terminal_destino),
        joinedload(Schedule.bus).joinedload(Bus.company),
    ).filter(Schedule.estado == EstadoHorario.programado)

    if fecha:
        try:
            d = datetime.strptime(fecha, "%Y-%m-%d").date()
            q = q.filter(
                Schedule.hora_salida >= datetime.combine(d, datetime.min.time()),
                Schedule.hora_salida <  datetime.combine(d, datetime.max.time())
            )
        except:
            pass

    schedules = q.order_by(Schedule.hora_salida).limit(100).all()

    if origen:
        origen_lower = origen.lower()
        schedules = [s for s in schedules if origen_lower in s.route.terminal_origen.ciudad.lower()]
    if destino:
        destino_lower = destino.lower()
        schedules = [s for s in schedules if destino_lower in s.route.terminal_destino.ciudad.lower()]

    result = []
    for s in schedules:
        empresa_nombre = s.bus.company.nombre if s.bus.company else "Sin empresa"
        empresa_color  = s.bus.company.color_flota if s.bus.company else "#1B2A6B"
        result.append({
            "id": s.id,
            "hora_salida": s.hora_salida.isoformat(),
            "hora_llegada_est": s.hora_llegada_est.isoformat() if s.hora_llegada_est else None,
            "precio_base": s.precio_base,
            "asientos_disponibles": s.asientos_disponibles,
            "estado": s.estado.value,
            "ruta": {
                "id": s.route.id,
                "nombre": s.route.nombre,
                "distancia_km": s.route.distancia_km,
                "duracion_min": s.route.duracion_min,
                "origen": s.route.terminal_origen.ciudad,
                "destino": s.route.terminal_destino.ciudad,
            },
            "empresa": {
                "nombre": empresa_nombre,
                "color":  empresa_color,
            },
            "bus": {
                "placa": s.bus.placa,
                "tipo":  s.bus.tipo.value,
                "total_asientos": s.bus.total_asientos,
            }
        })
    return result


@router.get("/{schedule_id}/seats")
def get_seats(schedule_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    from app.models import Booking

    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    seats = db.query(Seat).filter(Seat.bus_id == schedule.bus_id).all()

    # Traer tickets con pasajero y booking
    from app.models import Booking
    bookings = db.query(Booking).filter(Booking.schedule_id == schedule_id).all()
    booking_ids = [b.id for b in bookings]
    booking_map = {b.id: b.codigo_reserva for b in bookings}

    tickets = db.query(Ticket).filter(Ticket.booking_id.in_(booking_ids)).all()

    # Mapa seat_id -> info del pasajero
    seat_info = {}
    for t in tickets:
        seat_info[t.seat_id] = {
            "codigo_reserva": booking_map.get(t.booking_id),
            "pasajero_nombre": t.pasajero_nombre,
            "pasajero_ci": t.pasajero_ci,
        }

    return [
        {
            "id": s.id,
            "numero": s.numero,
            "fila": s.fila,
            "columna": s.columna,
            "tipo": s.tipo.value,
            "piso": s.piso,
            "disponible": s.id not in seat_info,
            "codigo_reserva": seat_info.get(s.id, {}).get("codigo_reserva"),
            "pasajero_nombre": seat_info.get(s.id, {}).get("pasajero_nombre"),
            "pasajero_ci": seat_info.get(s.id, {}).get("pasajero_ci"),
        }
        for s in seats
    ]

