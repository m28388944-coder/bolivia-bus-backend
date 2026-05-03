from sqlalchemy import Column, String, Boolean, Float, Integer, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


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


class EstadoHorario(str, enum.Enum):
    programado = "programado"
    en_ruta = "en_ruta"
    completado = "completado"
    cancelado = "cancelado"


class RolUsuario(str, enum.Enum):
    pasajero = "pasajero"
    admin = "admin"
    chofer = "chofer"


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


class TipoServicio(str, enum.Enum):
    cajero = "cajero"
    consultorio = "consultorio"
    food_court = "food_court"
    gimnasio = "gimnasio"
    comercio = "comercio"
    preembarque = "preembarque"
    bano = "bano"
    informacion = "informacion"


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
    terminal_id = Column(UUID(as_uuid=False), ForeignKey("terminals.id"), nullable=False)
    tipo = Column(Enum(TipoServicio), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text)
    horario = Column(String(80))
    lat = Column(Float)
    lng = Column(Float)
    activo = Column(Boolean, default=True)
    terminal = relationship("Terminal", back_populates="services")


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


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=False), ForeignKey("bookings.id"))
    tipo = Column(String(40), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="notifications")
    booking = relationship("Booking", back_populates="notifications")
