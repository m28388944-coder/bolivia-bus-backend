with open("app/routers/bookings.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
@router.get("/all")
def all_bookings(db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    bookings = db.query(Booking).options(
        joinedload(Booking.schedule).joinedload(Schedule.route)
    ).order_by(Booking.created_at.desc()).limit(100).all()
    return [
        {
            "id": b.id,
            "codigo_reserva": b.codigo_reserva,
            "estado": b.estado.value,
            "precio_total": b.precio_total,
            "created_at": b.created_at.isoformat(),
            "ruta": b.schedule.route.nombre,
            "hora_salida": b.schedule.hora_salida.isoformat(),
            "tickets": len(b.tickets) if b.tickets else 0,
        }
        for b in bookings
    ]
"""

content += new_endpoint
with open("app/routers/bookings.py", "w", encoding="utf-8") as f:
    f.write(content)
print("OK: /bookings/all agregado")