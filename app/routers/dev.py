from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Booking, Schedule
from app.models.user import RolUsuario
from app.routers.deps import get_current_user
import httpx, datetime

router = APIRouter(prefix="/dev", tags=["developer"])

def require_developer(current_user: User = Depends(get_current_user)):
    if current_user.rol != RolUsuario.developer:
        raise HTTPException(status_code=403, detail="Acceso solo para desarrolladores")
    return current_user

@router.get("/me")
def dev_me(dev: User = Depends(require_developer)):
    return {
        "id": dev.id,
        "nombre": dev.nombre,
        "email": dev.email,
        "rol": dev.rol,
        "mensaje": "Acceso total al sistema Bolivia Bus"
    }

@router.get("/health")
def dev_health(dev: User = Depends(require_developer), db: Session = Depends(get_db)):
    servicios = {}

    # Backend
    servicios["backend"] = {"status": "online", "url": "http://localhost:8000", "version": "1.0.0"}

    # PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        servicios["postgres"] = {"status": "online", "users": result}
    except Exception as e:
        servicios["postgres"] = {"status": "offline", "error": str(e)}

    # Frontend Pasajero
    try:
        r = httpx.get("http://localhost:5173", timeout=2)
        servicios["frontend_pasajero"] = {"status": "online", "url": "http://localhost:5173", "code": r.status_code}
    except:
        servicios["frontend_pasajero"] = {"status": "offline", "url": "http://localhost:5173"}

    # Panel Admin
    try:
        r = httpx.get("http://localhost:5174", timeout=2)
        servicios["panel_admin"] = {"status": "online", "url": "http://localhost:5174", "code": r.status_code}
    except:
        servicios["panel_admin"] = {"status": "offline", "url": "http://localhost:5174"}

    # App Chofer
    try:
        r = httpx.get("http://localhost:5175", timeout=2)
        servicios["app_chofer"] = {"status": "online", "url": "http://localhost:5175", "code": r.status_code}
    except:
        servicios["app_chofer"] = {"status": "offline", "url": "http://localhost:5175"}

    total = len(servicios)
    online = sum(1 for s in servicios.values() if s["status"] == "online")

    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sistema": "Bolivia Bus",
        "servicios": servicios,
        "resumen": {"total": total, "online": online, "offline": total - online}
    }

@router.get("/stats")
def dev_stats(dev: User = Depends(require_developer), db: Session = Depends(get_db)):
    stats = {}
    tablas = ["users", "companies", "routes", "buses", "seats", "schedules",
              "bookings", "tickets", "payments", "drivers", "terminals", "gps_tracking"]
    for tabla in tablas:
        try:
            count = db.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            stats[tabla] = count
        except:
            stats[tabla] = "error"

    # Ingresos totales
    try:
        ingresos = db.execute(text("SELECT COALESCE(SUM(precio_total), 0) FROM bookings WHERE estado = 'pagada'")).scalar()
        stats["ingresos_pagados"] = float(ingresos)
    except:
        stats["ingresos_pagados"] = 0

    # Reservas por estado
    try:
        estados = db.execute(text("SELECT estado, COUNT(*) FROM bookings GROUP BY estado")).fetchall()
        stats["bookings_por_estado"] = {str(e[0]): e[1] for e in estados}
    except:
        stats["bookings_por_estado"] = {}

    # Tamano BD
    try:
        size = db.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))")).scalar()
        stats["db_size"] = size
    except:
        stats["db_size"] = "unknown"

    return {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "stats": stats}

@router.get("/users")
def dev_users(dev: User = Depends(require_developer), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "email": u.email,
            "rol": u.rol,
            "activo": u.activo,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.patch("/users/{user_id}/rol")
def dev_cambiar_rol(
    user_id: str,
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    nuevo_rol = body.get("rol")
    try:
        user.rol = RolUsuario(nuevo_rol)
        db.commit()
        return {"ok": True, "user_id": user_id, "nuevo_rol": nuevo_rol}
    except:
        raise HTTPException(status_code=400, detail="Rol invalido")

@router.patch("/users/{user_id}/activo")
def dev_toggle_activo(
    user_id: str,
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = body.get("activo", True)
    db.commit()
    return {"ok": True, "user_id": user_id, "activo": user.activo}

@router.get("/logs/recientes")
def dev_logs_recientes(dev: User = Depends(require_developer), db: Session = Depends(get_db)):
    try:
        bookings = db.execute(text("""
            SELECT b.codigo_reserva, b.estado, b.precio_total, b.created_at,
                   u.email, u.nombre
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC LIMIT 50
        """)).fetchall()
        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "eventos": [
                {
                    "tipo": "booking",
                    "codigo": str(r[0]),
                    "estado": str(r[1]),
                    "monto": float(r[2]),
                    "fecha": r[3].isoformat() if r[3] else None,
                    "usuario_email": str(r[4]),
                    "usuario_nombre": str(r[5])
                }
                for r in bookings
            ]
        }
    except Exception as e:
        return {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "eventos": [], "error": str(e)}


# ─── SOPORTE / TICKETS ────────────────────────────────────────────────────────

from app.models.support import SupportTicket, SupportMessage

@router.get("/tickets")
def dev_tickets(
    estado: str = None,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    q = db.execute(text("""
        SELECT t.id, t.titulo, t.descripcion, t.sistema, t.prioridad, t.estado,
               t.nota_interna, t.created_at, t.updated_at,
               u.nombre as user_nombre, u.email as user_email,
               (SELECT COUNT(*) FROM support_messages m WHERE m.ticket_id = t.id) as total_mensajes
        FROM support_tickets t
        LEFT JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    """)).fetchall()
    tickets = []
    for r in q:
        if estado and str(r[5]) != estado:
            continue
        tickets.append({
            "id": str(r[0]), "titulo": str(r[1]), "descripcion": str(r[2]),
            "sistema": str(r[3]), "prioridad": str(r[4]), "estado": str(r[5]),
            "nota_interna": str(r[6]) if r[6] else None,
            "created_at": r[7].isoformat() if r[7] else None,
            "updated_at": r[8].isoformat() if r[8] else None,
            "user_nombre": str(r[9]) if r[9] else "Anonimo",
            "user_email": str(r[10]) if r[10] else None,
            "total_mensajes": int(r[11])
        })
    return tickets

@router.post("/tickets")
def dev_crear_ticket(
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    ticket_id = db.execute(text("""
        INSERT INTO support_tickets (titulo, descripcion, sistema, prioridad, estado)
        VALUES (:titulo, :descripcion, :sistema, :prioridad, 'abierto')
        RETURNING id
    """), {
        "titulo": body.get("titulo", "Sin titulo"),
        "descripcion": body.get("descripcion", ""),
        "sistema": body.get("sistema", "general"),
        "prioridad": body.get("prioridad", "media"),
    }).scalar()
    db.commit()
    if body.get("mensaje"):
        db.execute(text("""
            INSERT INTO support_messages (ticket_id, autor_id, autor_nombre, autor_rol, mensaje)
            VALUES (:tid, :aid, :nombre, 'developer', :msg)
        """), {"tid": str(ticket_id), "aid": str(dev.id), "nombre": dev.nombre, "msg": body["mensaje"]})
        db.commit()
    return {"ok": True, "ticket_id": str(ticket_id)}

@router.get("/tickets/{ticket_id}")
def dev_ticket_detalle(
    ticket_id: str,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    t = db.execute(text("""
        SELECT t.id, t.titulo, t.descripcion, t.sistema, t.prioridad, t.estado,
               t.nota_interna, t.created_at, t.updated_at,
               u.nombre as user_nombre, u.email as user_email
        FROM support_tickets t
        LEFT JOIN users u ON t.user_id = u.id
        WHERE t.id = :id
    """), {"id": ticket_id}).fetchone()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    msgs = db.execute(text("""
        SELECT id, autor_nombre, autor_rol, mensaje, es_nota_interna, created_at
        FROM support_messages WHERE ticket_id = :id ORDER BY created_at ASC
    """), {"id": ticket_id}).fetchall()
    return {
        "id": str(t[0]), "titulo": str(t[1]), "descripcion": str(t[2]),
        "sistema": str(t[3]), "prioridad": str(t[4]), "estado": str(t[5]),
        "nota_interna": str(t[6]) if t[6] else None,
        "created_at": t[7].isoformat() if t[7] else None,
        "updated_at": t[8].isoformat() if t[8] else None,
        "user_nombre": str(t[9]) if t[9] else "Anonimo",
        "user_email": str(t[10]) if t[10] else None,
        "mensajes": [
            {
                "id": str(m[0]), "autor_nombre": str(m[1]), "autor_rol": str(m[2]),
                "mensaje": str(m[3]), "es_nota_interna": bool(m[4]),
                "created_at": m[5].isoformat() if m[5] else None
            } for m in msgs
        ]
    }

@router.post("/tickets/{ticket_id}/mensajes")
def dev_agregar_mensaje(
    ticket_id: str,
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    db.execute(text("""
        INSERT INTO support_messages (ticket_id, autor_id, autor_nombre, autor_rol, mensaje, es_nota_interna)
        VALUES (:tid, :aid, :nombre, 'developer', :msg, :nota)
    """), {
        "tid": ticket_id, "aid": str(dev.id), "nombre": dev.nombre,
        "msg": body.get("mensaje", ""), "nota": body.get("es_nota_interna", False)
    })
    db.execute(text("UPDATE support_tickets SET updated_at = now() WHERE id = :id"), {"id": ticket_id})
    db.commit()
    return {"ok": True}

@router.patch("/tickets/{ticket_id}")
def dev_actualizar_ticket(
    ticket_id: str,
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    campos = []
    params = {"id": ticket_id}
    if "estado" in body:
        campos.append("estado = :estado"); params["estado"] = body["estado"]
    if "prioridad" in body:
        campos.append("prioridad = :prioridad"); params["prioridad"] = body["prioridad"]
    if "nota_interna" in body:
        campos.append("nota_interna = :nota"); params["nota"] = body["nota_interna"]
    if campos:
        campos.append("updated_at = now()")
        db.execute(text(f"UPDATE support_tickets SET {', '.join(campos)} WHERE id = :id"), params)
        db.commit()
    return {"ok": True}
