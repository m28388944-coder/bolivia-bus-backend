from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nombre = Column(String(120), nullable=False)
    ruc = Column(String(20), unique=True)
    logo_url = Column(String(300))
    color_flota = Column(String(7), default="#1a56db")
    telefono = Column(String(20))
    email = Column(String(120))
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    routes = relationship("Route", back_populates="company")
    buses = relationship("Bus", back_populates="company")
    drivers = relationship("Driver", back_populates="company")