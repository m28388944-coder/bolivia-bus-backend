from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
from datetime import datetime

router = APIRouter()

# Almacen en memoria de ubicaciones
bus_locations: Dict[str, Any] = {}
active_connections = []

@router.post("/update")
async def update_location(bus_id: str, latitude: float, longitude: float, speed_kmh: float = 0, status: str = "en_ruta"):
    bus_locations[bus_id] = {
        "bus_id": bus_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed_kmh": speed_kmh,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    # Notificar a todos los clientes WebSocket
    msg = json.dumps({"type": "location_update", **bus_locations[bus_id]})
    dead = []
    for ws in active_connections:
        try:
            await ws.send_text(msg)
        except:
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)
    return {"ok": True}

@router.get("/latest")
def get_latest():
    return {"buses": list(bus_locations.values())}

@router.websocket("/ws")
async def websocket_tracking(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    # Enviar estado actual al conectarse
    for loc in bus_locations.values():
        await ws.send_text(json.dumps({"type": "location_update", **loc}))
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in active_connections:
            active_connections.remove(ws)