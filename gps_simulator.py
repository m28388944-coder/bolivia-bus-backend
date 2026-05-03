import asyncio
import httpx

RUTAS = {
    "La Paz - Cochabamba": [
        (-16.5000, -68.1500),
        (-16.6000, -68.0000),
        (-16.7500, -67.8000),
        (-16.9000, -67.5000),
        (-17.0500, -67.2000),
        (-17.1500, -66.8000),
        (-17.2500, -66.5000),
        (-17.3800, -66.1600),
    ],
    "La Paz - Oruro": [
        (-16.5000, -68.1500),
        (-16.7000, -68.0500),
        (-16.9000, -67.9500),
        (-17.1500, -67.8000),
        (-17.3800, -67.9000),
        (-17.5000, -67.8500),
        (-17.7200, -67.6500),
        (-17.9800, -67.1400),
    ],
    "Cochabamba - Santa Cruz": [
        (-17.3800, -66.1600),
        (-17.4500, -65.8000),
        (-17.5500, -65.4000),
        (-17.6500, -65.0000),
        (-17.7500, -64.6000),
        (-17.8000, -64.2000),
        (-17.8500, -63.8000),
        (-17.7800, -63.1800),
    ],
}

async def simulate_bus(bus_id: str, placa: str, route_name: str, interval: int = 4):
    points = RUTAS.get(route_name, list(RUTAS.values())[0])
    idx = 0
    direction = 1
    async with httpx.AsyncClient() as client:
        while True:
            lat, lng = points[idx]
            try:
                await client.post(
                    "http://localhost:8000/tracking/update",
                    params={
                        "bus_id": placa,
                        "latitude": lat,
                        "longitude": lng,
                        "speed_kmh": 85.0,
                        "status": "en_ruta"
                    }
                )
                print(f"Bus {placa} | {route_name} | punto {idx+1}/{len(points)}")
            except Exception as e:
                print(f"Error bus {placa}: {e}")
            idx += direction
            if idx >= len(points) - 1:
                direction = -1
            elif idx <= 0:
                direction = 1
            await asyncio.sleep(interval)

async def main():
    import sys
    sys.path.insert(0, ".")
    from app.db.session import SessionLocal
    from app.models.bus import Bus
    db = SessionLocal()
    buses = db.query(Bus).filter(Bus.activo == True).all()
    db.close()
    if not buses:
        print("No hay buses activos en la BD")
        return
    routes_list = list(RUTAS.keys())
    tasks = []
    for i, bus in enumerate(buses):
        route = routes_list[i % len(routes_list)]
        print(f"Simulando: {bus.placa} en {route}")
        tasks.append(simulate_bus(str(bus.id), bus.placa, route))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())