from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.services.ticket_service import get_ticket
from app.utils.pdf_generator import generate_ticket_pdf
from app.utils.qr_generator import validate_qr_token
from app.models.booking import Booking, BookingStatus

router = APIRouter()

@router.get("/{booking_id}")
def get_ticket_info(booking_id: UUID, db: Session = Depends(get_db)):
    result = get_ticket(db, booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return result

@router.get("/{booking_id}/pdf")
def download_pdf(booking_id: UUID, db: Session = Depends(get_db)):
    result = get_ticket(db, booking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    pdf = generate_ticket_pdf(result)
    filename = f"ticket_{booking_id}.pdf"
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.post("/validate")
def validate_ticket(token: str, db: Session = Depends(get_db)):
    payload = validate_qr_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Token invalido")
    booking = db.query(Booking).filter(Booking.id == UUID(payload["booking_id"])).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if booking.is_used:
        raise HTTPException(status_code=400, detail="Ticket ya usado")
    booking.is_used = True
    booking.status = BookingStatus.USED
    db.commit()
    return {"message": "Ticket validado", "passenger": booking.passenger_name}
