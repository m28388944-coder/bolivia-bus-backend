from app.database import SessionLocal
from app.models import Schedule
from datetime import datetime, timedelta
import uuid

db = SessionLocal()

route_id = "5eb03fdf-c5bf-4510-a7b6-b691b5e73001"
fecha = "2026-05-02"
duracion_min = 280

horarios = [
    {"bus_id": "972bfb33-a406-4c50-97cb-c32c90f173f2", "hora": "07:00", "precio": 35},
    {"bus_id": "972bfb33-a406-4c50-97cb-c32c90f173f2", "hora": "13:00", "precio": 35},
    {"bus_id": "20c4d091-0dd2-475b-9211-ecf1ab79ab7b", "hora": "08:30", "precio": 45},
    {"bus_id": "20c4d091-0dd2-475b-9211-ecf1ab79ab7b", "hora": "20:00", "precio": 45},
    {"bus_id": "3b086a57-89d1-49d8-a8a3-a5aa27785b3b", "hora": "06:30", "precio": 25},
    {"bus_id": "3b086a57-89d1-49d8-a8a3-a5aa27785b3b", "hora": "14:00", "precio": 25},
    {"bus_id": "e0714f78-7903-417c-949e-efaa2a9fdf04", "hora": "09:00", "precio": 38},
    {"bus_id": "e0714f78-7903-417c-949e-efaa2a9fdf04", "hora": "21:00", "precio": 38},
]

for h in horarios:
    salida = datetime.fromisoformat(fecha + "T" + h["hora"] + ":00+00:00")
    llegada = salida + timedelta(minutes=duracion_min)
    s = Schedule(
        id=str(uuid.uuid4()),
        route_id=route_id,
        bus_id=h["bus_id"],
        hora_salida=salida,
        hora_llegada_est=llegada,
        precio_base=h["precio"],
        estado="programado",
    )
    db.add(s)

db.commit()
print("OK - " + str(len(horarios)) + " horarios agregados para 4 empresas")
