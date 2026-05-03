from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class RouteResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    distance_km: float
    duration_hours: float
    is_active: bool
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    origin: str
    destination: str
    date: str
    passengers: int = 1

class ScheduleResponse(BaseModel):
    id: UUID
    route_id: UUID
    bus_id: UUID
    departure_time: datetime
    arrival_time: datetime
    price_normal: float
    price_semicama: float
    price_cama: float
    terminal_fee: float
    status: str
    available_seats: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    company: Optional[str] = None
    bus_type: Optional[str] = None
    duration_hours: Optional[float] = None
    class Config:
        from_attributes = True
