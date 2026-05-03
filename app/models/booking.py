from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class EstadoReserva(str, enum.Enum):
    pendiente = "pendiente"
    pagada = "pagada"
    cancelada = "cancelada"
    completada = "completada"

class EstadoTicket(str, enum.Enum):
    activo = "activo"
    usado = "usado"
    cancelado = "cancelado"

class EstadoPago(str, enum.Enum):
    pendiente = "pendiente"
    completado = "completado"
    fallido = "fallido"
    reembolsado = "reembolsado"

class MetodoPago(str, enum.Enum):
    efectivo = "efectivo"
    qr = "qr"
    tarjeta = "tarjeta"
    transferencia = "transferencia"

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    schedule_id = Column(UUID(as_uuid=False), ForeignKey("schedules.id"), nullable=False)
    codigo_reserva = Column(String(12), unique=True, nullable=False)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.pendiente)
    precio_total = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="bookings")
    schedule = relationship("Schedule", back_populates="bookings")
    tickets = relationship("Ticket", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")
    notifications = relationship("Notification", back_populates="booking")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    booking_id = Column(UUID(as_uuid=False), ForeignKey("bookings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=False), ForeignKey("seats.id"), nullable=False)
    pasajero_nombre = Column(String(120), nullable=False)
    pasajero_ci = Column(String(20))
    precio = Column(Float, nullable=False)
    qr_code = Column(String(500))
    estado = Column(Enum(EstadoTicket), default=EstadoTicket.activo)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    booking = relationship("Booking", back_populates="tickets")
    seat = relationship("Seat", back_populates="tickets")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    booking_id = Column(UUID(as_uuid=False), ForeignKey("bookings.id"), nullable=False)
    metodo = Column(Enum(MetodoPago), nullable=False)
    monto = Column(Float, nullable=False)
    estado = Column(Enum(EstadoPago), default=EstadoPago.pendiente)
    referencia_ext = Column(String(100))
    pagado_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    booking = relationship("Booking", back_populates="payments")