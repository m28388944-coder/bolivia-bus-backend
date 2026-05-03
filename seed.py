import sys
sys.path.insert(0, ".")
from app.database import SessionLocal
from app.models import (
    Company, Terminal, TerminalService, Route,
    Bus, Seat, User, Driver, Schedule,
    TipoBus, TipoAsiento, TipoServicio, RolUsuario, EstadoHorario
)
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid, random

pwd = CryptContext(schemes=["bcrypt"])
db = SessionLocal()

print("Limpiando datos anteriores...")
db.query(Schedule).delete()
db.query(Driver).delete()
db.query(Seat).delete()
db.query(Bus).delete()
db.query(Route).delete()
db.query(TerminalService).delete()
db.query(Terminal).delete()
db.query(User).delete()
db.query(Company).delete()
db.commit()

print("Creando empresas...")
empresas = [
    Company(nombre="Flota Bolivar", color_flota="#E63946", telefono="22312345", email="info@flotabolivar.bo"),
    Company(nombre="Trans Copacabana", color_flota="#1D3557", telefono="22387654", email="info@transcopacabana.bo"),
    Company(nombre="Flota Cosmos", color_flota="#2A9D8F", telefono="22456789", email="info@flotacosmos.bo"),
    Company(nombre="Concordia", color_flota="#E9C46A", telefono="22567890", email="info@concordia.bo"),
    Company(nombre="Bolivia Bus Express", color_flota="#6A0572", telefono="22678901", email="info@boliviabusexpress.bo"),
]
for e in empresas:
    db.add(e)
db.commit()
for e in empresas:
    db.refresh(e)
print(f"  {len(empresas)} empresas creadas")

print("Creando terminales...")
t_elalto = Terminal(
    nombre="Terminal Metropolitana El Alto",
    ciudad="El Alto",
    direccion="Av. 6 de Marzo, Ciudad Satélite, El Alto",
    lat=-16.5054,
    lng=-68.1936,
    telefono="22810000"
)
t_lapaz = Terminal(
    nombre="Terminal de Buses La Paz",
    ciudad="La Paz",
    direccion="Av. Peru esq. Av. Montes, La Paz",
    lat=-16.4897,
    lng=-68.1193,
    telefono="22228177"
)
t_oruro = Terminal(
    nombre="Terminal de Buses Oruro",
    ciudad="Oruro",
    direccion="Av. Galvarro esq. Aroma, Oruro",
    lat=-17.9643,
    lng=-67.1103,
    telefono="52529000"
)
t_cbba = Terminal(
    nombre="Terminal de Buses Cochabamba",
    ciudad="Cochabamba",
    direccion="Av. Ayacucho esq. Aroma, Cochabamba",
    lat=-17.3935,
    lng=-66.1568,
    telefono="44223456"
)
t_scz = Terminal(
    nombre="Terminal Bimodal Santa Cruz",
    ciudad="Santa Cruz",
    direccion="Av. Cañoto esq. Irala, Santa Cruz",
    lat=-17.7863,
    lng=-63.1812,
    telefono="33367890"
)
terminales = [t_elalto, t_lapaz, t_oruro, t_cbba, t_scz]
for t in terminales:
    db.add(t)
db.commit()
for t in terminales:
    db.refresh(t)
print(f"  {len(terminales)} terminales creadas")

print("Creando servicios Terminal El Alto...")
servicios_elalto = [
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="BCP", descripcion="Banco de Credito Bolivia", horario="08:00-20:00", lat=-16.5052, lng=-68.1934),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="BNB", descripcion="Banco Nacional de Bolivia", horario="08:00-20:00", lat=-16.5053, lng=-68.1935),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="BancoSol", descripcion="Banco Solidario", horario="08:30-19:30", lat=-16.5055, lng=-68.1937),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Banco Union", descripcion="Banco Union S.A.", horario="08:00-18:00", lat=-16.5056, lng=-68.1938),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Banco Ganadero", descripcion="Banco Ganadero S.A.", horario="09:00-18:00", lat=-16.5057, lng=-68.1939),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Banco Fie", descripcion="Banco Fie S.A.", horario="08:30-19:00", lat=-16.5058, lng=-68.1940),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Bisa", descripcion="Banco Bisa S.A.", horario="09:00-19:00", lat=-16.5059, lng=-68.1941),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Mercantil Santa Cruz", descripcion="Banco Mercantil Santa Cruz", horario="08:00-20:00", lat=-16.5060, lng=-68.1942),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.cajero, nombre="Banco Economico", descripcion="Banco Economico S.A.", horario="09:00-18:00", lat=-16.5061, lng=-68.1943),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.consultorio, nombre="Consultorio Medico Terminal", descripcion="Atencion medica general, primeros auxilios", horario="07:00-22:00", lat=-16.5062, lng=-68.1933),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.food_court, nombre="Patio de Comidas", descripcion="Restaurantes y snacks tipicos bolivianos", horario="06:00-23:00", lat=-16.5063, lng=-68.1932),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.gimnasio, nombre="Gimnasio Terminal", descripcion="Gimnasio equipado para viajeros", horario="06:00-22:00", lat=-16.5064, lng=-68.1931),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.comercio, nombre="Galerias Comerciales", descripcion="Tiendas de ropa, artesanias y souvenirs", horario="08:00-21:00", lat=-16.5065, lng=-68.1930),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.preembarque, nombre="Sala de Preembarque", descripcion="Sala de espera VIP con WiFi y carga USB", horario="05:00-24:00", lat=-16.5066, lng=-68.1929),
    TerminalService(terminal_id=t_elalto.id, tipo=TipoServicio.informacion, nombre="Informaciones", descripcion="Punto de informacion turistica y de servicios", horario="06:00-22:00", lat=-16.5067, lng=-68.1928),
]
for s in servicios_elalto:
    db.add(s)
db.commit()
print(f"  {len(servicios_elalto)} servicios Terminal El Alto")

print("Creando rutas...")
rutas_data = [
    (empresas[0], t_elalto, t_oruro, "El Alto - Oruro", 228, 180, 25.0),
    (empresas[1], t_elalto, t_cbba, "El Alto - Cochabamba", 393, 270, 35.0),
    (empresas[2], t_elalto, t_scz, "El Alto - Santa Cruz", 900, 480, 80.0),
    (empresas[3], t_lapaz, t_oruro, "La Paz - Oruro", 230, 190, 25.0),
    (empresas[4], t_lapaz, t_cbba, "La Paz - Cochabamba", 395, 280, 40.0),
    (empresas[0], t_oruro, t_cbba, "Oruro - Cochabamba", 208, 180, 20.0),
    (empresas[1], t_cbba, t_scz, "Cochabamba - Santa Cruz", 495, 300, 55.0),
]
rutas = []
for emp, orig, dest, nombre, dist, dur, precio in rutas_data:
    r = Route(
        company_id=emp.id,
        terminal_origen_id=orig.id,
        terminal_destino_id=dest.id,
        nombre=nombre,
        distancia_km=dist,
        duracion_min=dur,
        activa=True
    )
    db.add(r)
    rutas.append((r, precio))
db.commit()
for r, p in rutas:
    db.refresh(r)
print(f"  {len(rutas)} rutas creadas")

print("Creando buses y asientos...")
buses_data = [
    (empresas[0], "B-1234", TipoBus.semicama, 40, "Mercedes Benz OF-1721", 2020),
    (empresas[1], "B-5678", TipoBus.cama, 24, "Volvo B420R", 2021),
    (empresas[2], "B-9012", TipoBus.normal, 50, "Scania K360", 2019),
    (empresas[3], "B-3456", TipoBus.semicama, 40, "Mercedes Benz OF-1721", 2022),
    (empresas[4], "B-7890", TipoBus.cama, 24, "Volvo B420R", 2023),
    (empresas[0], "B-2468", TipoBus.normal, 50, "Scania K310", 2020),
    (empresas[1], "B-1357", TipoBus.semicama, 40, "Mercedes Benz OF-1721", 2021),
]
buses = []
for emp, placa, tipo, total, modelo, anio in buses_data:
    b = Bus(company_id=emp.id, placa=placa, tipo=tipo, total_asientos=total, modelo=modelo, anio=anio)
    db.add(b)
    buses.append(b)
db.commit()
for b in buses:
    db.refresh(b)

for bus in buses:
    filas = bus.total_asientos // 4
    for fila_num in range(1, filas + 1):
        fila = chr(64 + fila_num)
        for col in range(1, 5):
            num = f"{fila}{col}"
            tipo_asiento = TipoAsiento.cama if bus.tipo == TipoBus.cama else (TipoAsiento.semicama if bus.tipo == TipoBus.semicama else TipoAsiento.normal)
            s = Seat(bus_id=bus.id, numero=num, fila=fila, columna=col, tipo=tipo_asiento, piso=1)
            db.add(s)
db.commit()
print(f"  {len(buses)} buses y asientos creados")

print("Creando usuarios y choferes...")
usuarios_choferes = [
    ("Juan Carlos Mamani", "jcmamani@boliviabus.bo", "77123456", "1234567LP", empresas[0], "B-1234-LP", "1234"),
    ("Pedro Quispe Condori", "pquispe@transcopacabana.bo", "77234567", "2345678LP", empresas[1], "B-5678-OR", "5678"),
    ("Luis Flores Tarqui", "lflores@cosmos.bo", "77345678", "3456789CB", empresas[2], "B-9012-CB", "9012"),
    ("Mario Gutierrez Paz", "mgutierrez@concordia.bo", "77456789", "4567890LP", empresas[3], "B-3456-LP", "3456"),
    ("Carlos Ticona Apaza", "cticona@boliviabusexpress.bo", "77567890", "5678901LP", empresas[4], "B-7890-SC", "7890"),
]
choferes = []
for nombre, email, tel, ci, emp, lic, pin in usuarios_choferes:
    u = User(
        nombre=nombre, email=email, telefono=tel, ci=ci,
        password_hash=pwd.hash("chofer1234"),
        rol=RolUsuario.chofer
    )
    db.add(u)
    db.flush()
    d = Driver(user_id=u.id, company_id=emp.id, licencia=lic, pin_hash=pwd.hash(pin))
    db.add(d)
    db.flush()
    choferes.append(d)

admin = User(
    nombre="Administrador Bolivia Bus", email="admin@boliviabus.bo",
    telefono="22000000", ci="9999999LP",
    password_hash=pwd.hash("admin1234"),
    rol=RolUsuario.admin
)
db.add(admin)
db.commit()
for c in choferes:
    db.refresh(c)
print(f"  {len(choferes)} choferes + 1 admin creados")

print("Creando horarios proximos 7 dias...")
count_schedules = 0
base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
horarios_salida = [6, 8, 10, 14, 18, 22]
for dia in range(7):
    fecha = base_date + timedelta(days=dia)
    for idx, (ruta, precio) in enumerate(rutas):
        chofer = choferes[idx % len(choferes)]
        bus = buses[idx % len(buses)]
        for hora in random.sample(horarios_salida, 3):
            salida = fecha + timedelta(hours=hora)
            llegada = salida + timedelta(minutes=ruta.duracion_min)
            sch = Schedule(
                route_id=ruta.id,
                bus_id=bus.id,
                driver_id=chofer.id,
                hora_salida=salida,
                hora_llegada_est=llegada,
                precio_base=precio,
                estado=EstadoHorario.programado,
                asientos_disponibles=bus.total_asientos
            )
            db.add(sch)
            count_schedules += 1
db.commit()
print(f"  {count_schedules} horarios creados")

db.close()
print("")
print("Seed completado exitosamente.")
print("  Empresas  :", len(empresas))
print("  Terminales:", len(terminales))
print("  Rutas     :", len(rutas))
print("  Buses     :", len(buses))
print("  Choferes  :", len(choferes))
print("  Horarios  :", count_schedules)