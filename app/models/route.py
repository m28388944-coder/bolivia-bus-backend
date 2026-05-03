from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Route(Base):
    __tablename__ = "routes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    terminal_origen_id = Column(UUID(as_uuid=False), ForeignKey("terminals.id"), nullable=False)
    terminal_destino_id = Column(UUID(as_uuid=False), ForeignKey("terminals.id"), nullable=False)
    nombre = Column(String(120), nullable=False)
    distancia_km = Column(Float)
    duracion_min = Column(Integer)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    company = relationship("Company", back_populates="routes")
    terminal_origen = relationship("Terminal", foreign_keys=[terminal_origen_id], back_populates="routes_origen")
    terminal_destino = relationship("Terminal", foreign_keys=[terminal_destino_id], back_populates="routes_destino")
    schedules = relationship("Schedule", back_populates="route")