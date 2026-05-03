from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.bus_location import BusLocation
from app.models.bus import Bus
from app.core.websocket import manager
from datetime import datetime
import uuid

router = APIRouter()

@router.websocket("/ws/tracking")
async def tracking_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/update")
async def update_location(
    bus_id: str,
    latitude: float,
    longitude: float,
    speed_kmh: float = 0.0,
    heading: float = 0.0,
    status: str = "en_ruta",
    db: Session = Depends(get_db)
):
    loc = BusLocation(
        id=uuid.uuid4(),
        bus_id=uuid.UUID(bus_id),
        latitude=latitude,
        longitude=longitude,
        speed_kmh=speed_kmh,
        heading=heading,
        status=status,
        timestamp=datetime.utcnow()
    )
    db.add(loc)
    db.commit()
    bus = db.query(Bus).filter(Bus.id == uuid.UUID(bus_id)).first()
    await manager.broadcast({
        "type": "location_update",
        "bus_id": bus_id,
        "company": bus.company if bus else "Desconocido",
        "bus_type": bus.bus_type.value if bus else "normal",
        "plate": bus.plate if bus else "",
        "latitude": latitude,
        "longitude": longitude,
        "speed_kmh": speed_kmh,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"ok": True}

@router.get("/latest")
def get_latest(db: Session = Depends(get_db)):
    buses = db.query(Bus).filter(Bus.is_active == True).all()
    result = []
    for bus in buses:
        loc = db.query(BusLocation).filter(
            BusLocation.bus_id == bus.id
        ).order_by(BusLocation.timestamp.desc()).first()
        if loc:
            result.append({
                "bus_id": str(bus.id),
                "company": bus.company,
                "bus_type": bus.bus_type.value,
                "plate": bus.plate,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "speed_kmh": loc.speed_kmh,
                "status": loc.status,
                "timestamp": loc.timestamp.isoformat()
            })
    return {"buses": result}
