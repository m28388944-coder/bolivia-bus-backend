from sqlalchemy import Column, String, Boolean, Float, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class TipoServicio(str, enum.Enum):
    cajero = "cajero"
    consultorio = "consultorio"
    food_court = "food_court"
    gimnasio = "gimnasio"
    comercio = "comercio"
    preembarque = "preembarque"
    bano = "bano"
    informacion = "informacion"

class Terminal(Base):
    __tablename__ = "terminals"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nombre = Column(String(120), nullable=False)
    ciudad = Column(String(80), nullable=False)
    direccion = Column(String(200))
    lat = Column(Float)
    lng = Column(Float)
    telefono = Column(String(20))
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    services = relationship("TerminalService", back_populates="terminal")
    routes_origen = relationship("Route", foreign_keys="Route.terminal_origen_id", back_populates="terminal_origen")
    routes_destino = relationship("Route", foreign_keys="Route.terminal_destino_id", back_populates="terminal_destino")

class TerminalService(Base):
    __tablename__ = "terminal_services"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    terminal_id = Column(UUID(as_uuid=False), __import__("sqlalchemy").ForeignKey("terminals.id"), nullable=False)
    tipo = Column(Enum(TipoServicio), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text)
    horario = Column(String(80))
    lat = Column(Float)
    lng = Column(Float)
    activo = Column(Boolean, default=True)
    terminal = relationship("Terminal", back_populates="services")