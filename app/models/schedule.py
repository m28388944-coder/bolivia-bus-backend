from sqlalchemy import Column, Float, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class EstadoHorario(str, enum.Enum):
    programado = "programado"
    en_ruta = "en_ruta"
    completado = "completado"
    cancelado = "cancelado"

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    route_id = Column(UUID(as_uuid=False), ForeignKey("routes.id"), nullable=False)
    bus_id = Column(UUID(as_uuid=False), ForeignKey("buses.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"))
    hora_salida = Column(DateTime(timezone=True), nullable=False)
    hora_llegada_est = Column(DateTime(timezone=True))
    precio_base = Column(Float, nullable=False)
    estado = Column(Enum(EstadoHorario), default=EstadoHorario.programado)
    asientos_disponibles = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    route = relationship("Route", back_populates="schedules")
    bus = relationship("Bus", back_populates="schedules")
    driver = relationship("Driver", back_populates="schedules")
    bookings = relationship("Booking", back_populates="schedule")
    gps_tracking = relationship("GpsTracking", back_populates="schedule")