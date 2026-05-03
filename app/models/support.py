from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum

def gen_uuid():
    return str(uuid.uuid4())

class PrioridadSoporte(str, enum.Enum):
    baja   = "baja"
    media  = "media"
    alta   = "alta"
    critica = "critica"

class EstadoSoporte(str, enum.Enum):
    abierto    = "abierto"
    en_proceso = "en_proceso"
    resuelto   = "resuelto"
    cerrado    = "cerrado"

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    titulo      = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    sistema     = Column(String(50), default="general")
    prioridad   = Column(Enum(PrioridadSoporte), default=PrioridadSoporte.media)
    estado      = Column(Enum(EstadoSoporte), default=EstadoSoporte.abierto)
    user_id     = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    nota_interna = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    mensajes    = relationship("SupportMessage", back_populates="ticket", order_by="SupportMessage.created_at")

class SupportMessage(Base):
    __tablename__ = "support_messages"
    id         = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    ticket_id  = Column(UUID(as_uuid=False), ForeignKey("support_tickets.id"), nullable=False)
    autor_id   = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    autor_nombre = Column(String(120), default="Sistema")
    autor_rol  = Column(String(20), default="developer")
    mensaje    = Column(Text, nullable=False)
    es_nota_interna = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ticket     = relationship("SupportTicket", back_populates="mensajes")

