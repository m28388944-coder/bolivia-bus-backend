from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SeatResponse(BaseModel):
    id: UUID
    seat_number: str
    floor: int
    row: int
    column: int
    status: str
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    schedule_id: UUID
    seat_id: UUID
    passenger_name: str
    passenger_ci: str

class BookingResponse(BaseModel):
    id: UUID
    passenger_name: str
    passenger_ci: str
    base_price: float
    terminal_fee: float
    total_price: float
    status: str
    qr_token: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
