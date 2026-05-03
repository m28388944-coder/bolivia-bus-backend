with open('app/api/v1/endpoints/bookings.py', 'r', encoding='utf-8') as f:
    content = f.read()

extra = '''
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
'''

with open('app/api/v1/endpoints/bookings.py', 'w', encoding='utf-8') as f:
    f.write(content + extra)
print('OK: bookings.py actualizado')