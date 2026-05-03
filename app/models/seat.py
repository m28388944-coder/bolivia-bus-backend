from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.db.base import Base


class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    BLOCKED = "blocked"


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False)
    seat_number = Column(String(5), nullable=False)
    floor = Column(Integer, nullable=False, default=1)
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE)
    reserved_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    schedule = relationship("Schedule", back_populates="seats")
    booking = relationship("Booking", back_populates="seat", uselist=False)
