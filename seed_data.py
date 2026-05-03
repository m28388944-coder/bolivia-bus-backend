import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["DATABASE_URL"] = "postgresql://boliviabus:boliviabus123@localhost:5432/boliviabus_db"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from app.models.user import RolUsuario
from app.models.schedule import Schedule
from app.models.route import Route
from app.models.terminal import Terminal
from app.models.bus import Bus
from app.models.company import Company
from passlib.context import CryptContext
import uuid, datetime

engine = create_engine("postgresql://boliviabus:boliviabus123@localhost:5432/boliviabus_db")
Session = sessionmaker(bind=engine)
db = Session()
pwd = CryptContext(schemes=["bcrypt"])

print("Creando tablas...")
Base.metadata.create_all(engine)

print("Limpiando datos...")
for tabla in ["gps_tracking","support_messages","support_tickets","notifications",
              "payments","tickets","bookings","schedules","drivers","buses","routes",
              "terminal_services","terminals","companies"]:
    db.execute(text(f"DELETE FROM {tabla}"))
db.execute(text("DELETE FROM users WHERE email NOT IN ('dev@boliviabus.bo','admin@boliviabus.bo')"))
db.commit()

print("Creando empresa...")
empresa = Company(
    id=str(uuid.uuid4()), nombre="Trans Bolivia Express",
    ruc="1234567", telefono="22345678",
    email="info@transbolivia.bo", activa=True
)
db.add(empresa)
db.flush()

print("Creando terminales...")
term_lpz  = Terminal(id=str(uuid.uuid4()), nombre="Terminal La Paz",       ciudad="La Paz",       direccion="Villa Fatima",  activa=True)
term_cbba = Terminal(id=str(uuid.uuid4()), nombre="Terminal Cochabamba",   ciudad="Cochabamba",   direccion="Av. Ayacucho",  activa=True)
term_scz  = Terminal(id=str(uuid.uuid4()), nombre="Terminal Santa Cruz",   ciudad="Santa Cruz",   direccion="Av. Canoto",    activa=True)
term_oru  = Terminal(id=str(uuid.uuid4()), nombre="Terminal Oruro",        ciudad="Oruro",        direccion="Calle Aldana",  activa=True)
db.add_all([term_lpz, term_cbba, term_scz, term_oru])
db.flush()

print("Creando rutas...")
rutas_data = [
    ("La Paz - Cochabamba",  "La Paz",      "Cochabamba", 380, 360,  45.0, term_lpz,  term_cbba),
    ("La Paz - Santa Cruz",  "La Paz",      "Santa Cruz", 860, 720,  90.0, term_lpz,  term_scz),
    ("Cochabamba - Santa Cruz","Cochabamba","Santa Cruz", 500, 480,  65.0, term_cbba, term_scz),
    ("La Paz - Oruro",       "La Paz",      "Oruro",      230, 180,  30.0, term_lpz,  term_oru),
]
rutas = []
for nombre, origen, destino, km, min, precio, torig, tdest in rutas_data:
    r = Route(
        id=str(uuid.uuid4()), company_id=empresa.id,
        nombre=nombre, distancia_km=km, duracion_min=min,
        terminal_origen_id=torig.id, terminal_destino_id=tdest.id,
        activa=True
    )
    rutas.append((r, precio, origen, destino))
    db.add(r)
db.flush()

print("Creando bus...")
bus = Bus(
    id=str(uuid.uuid4()), company_id=empresa.id,
    placa="BOL-1234", modelo="Mercedes Benz O-500",
    total_asientos=40, activo=True
)
db.add(bus)
db.flush()

print("Creando horarios para los proximos 7 dias...")
hoy = datetime.date.today()
horarios = []
for i, (ruta, precio, origen, destino) in enumerate(rutas):
    for d in range(0, 7):
        fecha = hoy + datetime.timedelta(days=d)
        hora = datetime.time(6 + i*3, 0)
        salida = datetime.datetime.combine(fecha, hora)
        llegada = salida + datetime.timedelta(minutes=ruta.duracion_min)
        sch = Schedule(
            id=str(uuid.uuid4()),
            route_id=ruta.id, bus_id=bus.id,
            hora_salida=salida, hora_llegada_est=llegada,
            precio_base=precio, asientos_disponibles=40,
            estado="programado"
        )
        horarios.append(sch)
        db.add(sch)
db.flush()

print("Creando usuarios...")
for email, nombre, rol, tel in [
    ("pasajero@test.bo", "Juan Mamani",    "pasajero", "71234567"),
    ("admin@boliviabus.bo", "Administrador", "admin",  None),
]:
    existe = db.execute(text("SELECT id FROM users WHERE email=:e"), {"e": email}).fetchone()
    if not existe:
        db.add(User(
            id=str(uuid.uuid4()), nombre=nombre, email=email,
            telefono=tel, password_hash=pwd.hash("test1234"),
            rol=RolUsuario(rol), activo=True
        ))

db.commit()
print("SEED OK!")
print(f"  Rutas: {len(rutas)} | Horarios: {len(horarios)} | Bus: {bus.placa}")
print("  pasajero@test.bo / test1234")
print("  admin@boliviabus.bo / test1234")
db.close()
