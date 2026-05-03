from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class RolUsuario(str, enum.Enum):
    pasajero = "pasajero"
    admin = "admin"
    chofer = "chofer"
    developer = "developer"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nombre = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    telefono = Column(String(20))
    ci = Column(String(20))
    password_hash = Column(String(200), nullable=False)
    rol = Column(Enum(RolUsuario), default=RolUsuario.pasajero)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bookings = relationship("Booking", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    driver_profile = relationship("Driver", back_populates="user", uselist=False)

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id"), nullable=False)
    licencia = Column(String(20))
    pin_hash = Column(String(200))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="driver_profile")
    company = relationship("Company", back_populates="drivers")
    schedules = relationship("Schedule", back_populates="driver")
