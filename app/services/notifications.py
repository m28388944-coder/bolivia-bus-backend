import os, emails, logging
from emails.template import JinjaTemplate
from twilio.rest import Client
from datetime import datetime

logger = logging.getLogger(__name__)

# ── CONFIG (desde .env) ──────────────────────────────────────────────────────
TWILIO_SID        = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_PHONE = os.getenv("TWILIO_PHONE_FROM", "")
TWILIO_WA_FROM    = os.getenv("TWILIO_WA_FROM", "")
SMTP_HOST         = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT         = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER         = os.getenv("SMTP_USER", "")
SMTP_PASS         = os.getenv("SMTP_PASS", "")
EMAIL_FROM        = os.getenv("EMAIL_FROM", "noreply@boliviabus.bo")
EMAIL_FROM_NAME   = os.getenv("EMAIL_FROM_NAME", "Bolivia Bus")

# ── PLANTILLA EMAIL HTML ─────────────────────────────────────────────────────
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin:0; padding:0; background:#f0f4f8; font-family:'Segoe UI',Arial,sans-serif; }
  .wrap { max-width:580px; margin:32px auto; background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08); }
  .header { background:linear-gradient(135deg,#1B2A6B,#2d45a8); padding:32px 36px; text-align:center; }
  .header h1 { color:#D4AF37; margin:0; font-size:26px; font-weight:800; letter-spacing:-0.5px; }
  .header p { color:rgba(255,255,255,0.7); margin:6px 0 0; font-size:14px; }
  .body { padding:32px 36px; }
  .body h2 { color:#1B2A6B; font-size:20px; margin:0 0 16px; }
  .body p { color:#475569; font-size:15px; line-height:1.7; margin:0 0 16px; }
  .ticket-box { background:#f8fafc; border:2px solid #E2E8F0; border-radius:12px; padding:20px 24px; margin:20px 0; }
  .ticket-box .row { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #E2E8F0; }
  .ticket-box .row:last-child { border-bottom:none; }
  .ticket-box .label { color:#94A3B8; font-size:13px; font-weight:600; }
  .ticket-box .value { color:#1B2A6B; font-size:14px; font-weight:700; }
  .codigo { text-align:center; background:linear-gradient(135deg,#1B2A6B,#2d45a8); color:#D4AF37; font-size:28px; font-weight:800; letter-spacing:6px; padding:18px; border-radius:10px; margin:20px 0; }
  .footer { background:#f8fafc; padding:20px 36px; text-align:center; color:#94A3B8; font-size:12px; border-top:1px solid #E2E8F0; }
  .btn { display:inline-block; background:#D4AF37; color:#1B2A6B; font-weight:800; font-size:15px; padding:14px 32px; border-radius:10px; text-decoration:none; margin:16px 0; }
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>🚌 Bolivia Bus</h1>
    <p>Sistema de transporte interprovincial</p>
  </div>
  <div class="body">
    <h2>{{titulo}}</h2>
    <p>Hola <strong>{{nombre}}</strong>,</p>
    <p>{{mensaje}}</p>
    {% if codigo_reserva %}
    <div class="ticket-box">
      {% if ruta %}<div class="row"><span class="label">Ruta</span><span class="value">{{ruta}}</span></div>{% endif %}
      {% if fecha_salida %}<div class="row"><span class="label">Fecha</span><span class="value">{{fecha_salida}}</span></div>{% endif %}
      {% if asiento %}<div class="row"><span class="label">Asiento</span><span class="value">{{asiento}}</span></div>{% endif %}
      {% if precio %}<div class="row"><span class="label">Total</span><span class="value">Bs. {{precio}}</span></div>{% endif %}
    </div>
    <div class="codigo">{{codigo_reserva}}</div>
    <p style="text-align:center;color:#94A3B8;font-size:13px;">Presenta este codigo al abordar</p>
    {% endif %}
    {% if url_accion %}
    <div style="text-align:center;">
      <a href="{{url_accion}}" class="btn">{{texto_accion or "Ver mi ticket"}}</a>
    </div>
    {% endif %}
  </div>
  <div class="footer">
    Bolivia Bus &copy; {{anio}} &mdash; Sistema de transporte interprovincial<br>
    Este mensaje fue enviado automaticamente, no responder.
  </div>
</div>
</body>
</html>
"""

def _twilio_client():
    if not TWILIO_SID or not TWILIO_TOKEN:
        raise ValueError("Twilio no configurado — falta TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN en .env")
    return Client(TWILIO_SID, TWILIO_TOKEN)

# ── EMAIL ────────────────────────────────────────────────────────────────────
def enviar_email(destinatario_email: str, destinatario_nombre: str,
                 titulo: str, mensaje: str, datos: dict = None) -> dict:
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP no configurado — email no enviado")
        return {"ok": False, "canal": "email", "error": "SMTP no configurado"}
    try:
        ctx = {
            "titulo": titulo,
            "nombre": destinatario_nombre,
            "mensaje": mensaje,
            "anio": datetime.now().year,
            **(datos or {})
        }
        m = emails.Message(
            subject=titulo,
            html=JinjaTemplate(EMAIL_TEMPLATE),
            mail_from=(EMAIL_FROM_NAME, EMAIL_FROM),
        )
        r = m.send(
            to=(destinatario_nombre, destinatario_email),
            render=ctx,
            smtp={"host": SMTP_HOST, "port": SMTP_PORT,
                  "user": SMTP_USER, "password": SMTP_PASS, "tls": True}
        )
        ok = r.status_code == 250
        logger.info(f"Email {'OK' if ok else 'FAIL'} -> {destinatario_email}")
        return {"ok": ok, "canal": "email", "status": r.status_code}
    except Exception as e:
        logger.error(f"Email error: {e}")
        return {"ok": False, "canal": "email", "error": str(e)}

# ── SMS ──────────────────────────────────────────────────────────────────────
def enviar_sms(telefono: str, mensaje: str) -> dict:
    if not TWILIO_FROM_PHONE:
        logger.warning("SMS no configurado — falta TWILIO_PHONE_FROM en .env")
        return {"ok": False, "canal": "sms", "error": "SMS no configurado"}
    try:
        tel = telefono.strip()
        if not tel.startswith("+"):
            tel = "+591" + tel.lstrip("0")
        client = _twilio_client()
        msg = client.messages.create(body=mensaje, from_=TWILIO_FROM_PHONE, to=tel)
        logger.info(f"SMS OK -> {tel} SID={msg.sid}")
        return {"ok": True, "canal": "sms", "sid": msg.sid}
    except Exception as e:
        logger.error(f"SMS error: {e}")
        return {"ok": False, "canal": "sms", "error": str(e)}

# ── WHATSAPP ─────────────────────────────────────────────────────────────────
def enviar_whatsapp(telefono: str, mensaje: str) -> dict:
    if not TWILIO_WA_FROM:
        logger.warning("WhatsApp no configurado — falta TWILIO_WA_FROM en .env")
        return {"ok": False, "canal": "whatsapp", "error": "WhatsApp no configurado"}
    try:
        tel = telefono.strip()
        if not tel.startswith("+"):
            tel = "+591" + tel.lstrip("0")
        client = _twilio_client()
        msg = client.messages.create(
            body=mensaje,
            from_="whatsapp:" + TWILIO_WA_FROM,
            to="whatsapp:" + tel
        )
        logger.info(f"WhatsApp OK -> {tel} SID={msg.sid}")
        return {"ok": True, "canal": "whatsapp", "sid": msg.sid}
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return {"ok": False, "canal": "whatsapp", "error": str(e)}

# ── ENVIO MULTIPLE (los 3 canales) ───────────────────────────────────────────
def notificar_pasajero(
    email: str, telefono: str, nombre: str,
    titulo: str, mensaje_corto: str,
    datos_ticket: dict = None,
    canales: list = None
) -> dict:
    if canales is None:
        canales = ["email", "sms", "whatsapp"]

    resultados = {}

    if "email" in canales and email:
        resultados["email"] = enviar_email(email, nombre, titulo, mensaje_corto, datos_ticket)

    texto_sms = f"Bolivia Bus: {titulo}\n{mensaje_corto}"
    if datos_ticket and datos_ticket.get("codigo_reserva"):
        texto_sms += f"\nCodigo: {datos_ticket['codigo_reserva']}"

    if "sms" in canales and telefono:
        resultados["sms"] = enviar_sms(telefono, texto_sms)

    if "whatsapp" in canales and telefono:
        wa_msg = f"*Bolivia Bus* 🚌\n\n*{titulo}*\n\n{mensaje_corto}"
        if datos_ticket and datos_ticket.get("codigo_reserva"):
            wa_msg += f"\n\n*Codigo de reserva:* `{datos_ticket['codigo_reserva']}`"
        if datos_ticket and datos_ticket.get("ruta"):
            wa_msg += f"\n*Ruta:* {datos_ticket['ruta']}"
        resultados["whatsapp"] = enviar_whatsapp(telefono, wa_msg)

    exitosos = sum(1 for r in resultados.values() if r.get("ok"))
    logger.info(f"Notificacion enviada: {exitosos}/{len(resultados)} canales OK")
    return {"ok": exitosos > 0, "resultados": resultados, "exitosos": exitosos, "total": len(resultados)}
