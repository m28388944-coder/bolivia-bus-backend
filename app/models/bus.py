from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class TipoBus(str, enum.Enum):
    normal = "normal"
    semicama = "semicama"
    cama = "cama"
    doble_piso = "doble_piso"

class TipoAsiento(str, enum.Enum):
    normal = "normal"
    semicama = "semicama"
    cama = "cama"

class Bus(Base):
    __tablename__ = "buses"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    placa = Column(String(10), unique=True, nullable=False)
    tipo = Column(Enum(TipoBus), default=TipoBus.normal)
    total_asientos = Column(Integer, nullable=False)
    modelo = Column(String(80))
    anio = Column(Integer)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    company = relationship("Company", back_populates="buses")
    seats = relationship("Seat", back_populates="bus")
    schedules = relationship("Schedule", back_populates="bus")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    bus_id = Column(UUID(as_uuid=False), ForeignKey("buses.id"), nullable=False)
    numero = Column(String(5), nullable=False)
    fila = Column(String(3), nullable=False)
    columna = Column(Integer, nullable=False)
    tipo = Column(Enum(TipoAsiento), default=TipoAsiento.normal)
    piso = Column(Integer, default=1)
    disponible = Column(Boolean, default=True)
    bus = relationship("Bus", back_populates="seats")
    tickets = relationship("Ticket", back_populates="seat")