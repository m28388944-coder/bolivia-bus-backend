from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TicketResponse(BaseModel):
    booking_id: UUID
    passenger_name: str
    passenger_ci: str
    origin: str
    destination: str
    departure_time: datetime
    seat_number: str
    floor: int
    bus_type: str
    company: str
    base_price: float
    terminal_fee: float
    total_price: float
    qr_token: str
    status: str
