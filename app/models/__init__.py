from app.database import Base
from app.models.company import Company
from app.models.terminal import Terminal, TerminalService, TipoServicio
from app.models.route import Route
from app.models.bus import Bus, Seat, TipoBus, TipoAsiento
from app.models.user import User, Driver, RolUsuario
from app.models.schedule import Schedule, EstadoHorario
from app.models.booking import Booking, Ticket, Payment, EstadoReserva, EstadoTicket, EstadoPago, MetodoPago
from app.models.gps import GpsTracking
from app.models.notification import Notification
from app.models.support import SupportTicket, SupportMessage, PrioridadSoporte, EstadoSoporte

