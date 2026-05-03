from sqlalchemy import Column, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class GpsTracking(Base):
    __tablename__ = "gps_tracking"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    schedule_id = Column(UUID(as_uuid=False), ForeignKey("schedules.id"), nullable=False)
    bus_id = Column(UUID(as_uuid=False), ForeignKey("buses.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    velocidad_kmh = Column(Float, default=0)
    rumbo = Column(Float, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    schedule = relationship("Schedule", back_populates="gps_tracking")