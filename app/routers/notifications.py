from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import User, Booking
from app.models.notification import Notification
from app.routers.deps import get_current_user
from app.models.user import RolUsuario
from app.services.notifications import notificar_pasajero
import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])

def require_developer(current_user: User = Depends(get_current_user)):
    if current_user.rol != RolUsuario.developer:
        raise HTTPException(status_code=403, detail="Solo desarrolladores")
    return current_user

# ── ENVIAR NOTIFICACION MANUAL ────────────────────────────────────────────────
@router.post("/enviar")
def enviar_notificacion(
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    user_id    = body.get("user_id")
    booking_id = body.get("booking_id")
    titulo     = body.get("titulo", "Notificacion Bolivia Bus")
    mensaje    = body.get("mensaje", "")
    canales    = body.get("canales", ["email", "sms", "whatsapp"])

    if not user_id or not mensaje:
        raise HTTPException(status_code=400, detail="Faltan user_id y mensaje")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos_ticket = None
    if booking_id:
        row = db.execute(text("""
            SELECT b.codigo_reserva, b.precio_total,
                   r.origen, r.destino,
                   s.fecha_salida
            FROM bookings b
            LEFT JOIN schedules s ON b.schedule_id = s.id
            LEFT JOIN routes r ON s.route_id = r.id
            WHERE b.id = :bid
        """), {"bid": booking_id}).fetchone()
        if row:
            datos_ticket = {
                "codigo_reserva": str(row[0]),
                "precio": round(float(row[1]), 2),
                "ruta": f"{row[2]} -> {row[3]}" if row[2] else None,
                "fecha_salida": row[4].strftime("%d/%m/%Y %H:%M") if row[4] else None,
            }

    resultado = notificar_pasajero(
        email=user.email,
        telefono=user.telefono or "",
        nombre=user.nombre,
        titulo=titulo,
        mensaje_corto=mensaje,
        datos_ticket=datos_ticket,
        canales=canales,
    )

    # Guardar en BD
    notif = Notification(
        user_id=user_id,
        booking_id=booking_id,
        tipo="manual",
        mensaje=f"[{','.join(canales)}] {titulo}: {mensaje}",
        leida=False,
    )
    db.add(notif)
    db.commit()

    return {"ok": resultado["ok"], "resultados": resultado["resultados"], "exitosos": resultado["exitosos"]}

# ── NOTIFICAR POR BOOKING ─────────────────────────────────────────────────────
@router.post("/booking/{booking_id}")
def notificar_booking(
    booking_id: str,
    body: dict,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    row = db.execute(text("""
        SELECT b.codigo_reserva, b.precio_total, b.user_id,
               u.nombre, u.email, u.telefono,
               r.origen, r.destino, s.fecha_salida
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        LEFT JOIN schedules s ON b.schedule_id = s.id
        LEFT JOIN routes r ON s.route_id = r.id
        WHERE b.id = :bid
    """), {"bid": booking_id}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Booking no encontrado")

    datos_ticket = {
        "codigo_reserva": str(row[0]),
        "precio": round(float(row[1]), 2),
        "ruta": f"{row[6]} -> {row[7]}" if row[6] else None,
        "fecha_salida": row[8].strftime("%d/%m/%Y %H:%M") if row[8] else None,
    }

    titulo  = body.get("titulo", "Tu reserva en Bolivia Bus")
    mensaje = body.get("mensaje", f"Tu reserva {row[0]} ha sido confirmada.")
    canales = body.get("canales", ["email", "sms", "whatsapp"])

    resultado = notificar_pasajero(
        email=str(row[4]),
        telefono=str(row[5]) if row[5] else "",
        nombre=str(row[3]),
        titulo=titulo,
        mensaje_corto=mensaje,
        datos_ticket=datos_ticket,
        canales=canales,
    )

    notif = Notification(
        user_id=str(row[2]),
        booking_id=booking_id,
        tipo="booking",
        mensaje=f"[{','.join(canales)}] {titulo}",
        leida=False,
    )
    db.add(notif)
    db.commit()

    return {"ok": resultado["ok"], "resultados": resultado["resultados"], "datos_ticket": datos_ticket}

# ── HISTORIAL DE NOTIFICACIONES ───────────────────────────────────────────────
@router.get("/historial")
def historial(
    limit: int = 50,
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    rows = db.execute(text("""
        SELECT n.id, n.tipo, n.mensaje, n.leida, n.created_at,
               u.nombre, u.email, u.telefono,
               b.codigo_reserva
        FROM notifications n
        LEFT JOIN users u ON n.user_id = u.id
        LEFT JOIN bookings b ON n.booking_id = b.id
        ORDER BY n.created_at DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    return [
        {
            "id": str(r[0]),
            "tipo": str(r[1]),
            "mensaje": str(r[2]),
            "leida": bool(r[3]),
            "created_at": r[4].isoformat() if r[4] else None,
            "user_nombre": str(r[5]) if r[5] else None,
            "user_email": str(r[6]) if r[6] else None,
            "user_telefono": str(r[7]) if r[7] else None,
            "codigo_reserva": str(r[8]) if r[8] else None,
        }
        for r in rows
    ]

# ── BUSCAR USUARIOS/BOOKINGS ──────────────────────────────────────────────────
@router.get("/usuarios/buscar")
def buscar_usuarios(
    q: str = "",
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    rows = db.execute(text("""
        SELECT id, nombre, email, telefono
        FROM users
        WHERE rol = 'pasajero'
          AND (nombre ILIKE :q OR email ILIKE :q OR telefono ILIKE :q)
        ORDER BY nombre
        LIMIT 20
    """), {"q": f"%{q}%"}).fetchall()
    return [{"id": str(r[0]), "nombre": str(r[1]), "email": str(r[2]), "telefono": str(r[3]) if r[3] else ""} for r in rows]

@router.get("/bookings/buscar")
def buscar_bookings(
    q: str = "",
    dev: User = Depends(require_developer),
    db: Session = Depends(get_db)
):
    rows = db.execute(text("""
        SELECT b.id, b.codigo_reserva, b.estado, b.precio_total,
               u.nombre, u.email,
               r.origen, r.destino
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        LEFT JOIN schedules s ON b.schedule_id = s.id
        LEFT JOIN routes r ON s.route_id = r.id
        WHERE b.codigo_reserva ILIKE :q OR u.nombre ILIKE :q OR u.email ILIKE :q
        ORDER BY b.created_at DESC
        LIMIT 20
    """), {"q": f"%{q}%"}).fetchall()
    return [
        {
            "id": str(r[0]), "codigo_reserva": str(r[1]),
            "estado": str(r[2]), "precio_total": float(r[3]),
            "user_nombre": str(r[4]), "user_email": str(r[5]),
            "ruta": f"{r[6]} -> {r[7]}" if r[6] else "Sin ruta",
        }
        for r in rows
    ]
