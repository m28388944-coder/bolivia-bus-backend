with open('app/utils/pdf_generator.py', 'w', encoding='utf-8') as f:
    f.write('''from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import qrcode

NAVY = colors.HexColor("#1B2A6B")
GOLD = colors.HexColor("#D4AF37")

def generate_ticket_pdf(t: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    lbl = ParagraphStyle("lbl", parent=styles["Normal"], textColor=NAVY, fontSize=9, fontName="Helvetica-Bold")
    val = ParagraphStyle("val", parent=styles["Normal"], textColor=colors.black, fontSize=11)
    ctr = ParagraphStyle("ctr", parent=styles["Normal"], textColor=colors.white, fontSize=20, alignment=TA_CENTER)
    sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=GOLD, fontSize=12, alignment=TA_CENTER)
    elems = []
    hdr = Table([[Paragraph("BOLIVIA BUS", ctr)], [Paragraph("Ticket de Viaje", sub)]], colWidths=[17*cm])
    hdr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12)]))
    elems.append(hdr)
    elems.append(Spacer(1, 0.5*cm))
    rows = [
        [Paragraph("PASAJERO", lbl), Paragraph(str(t.get("passenger_name","")).upper(), val)],
        [Paragraph("CI", lbl), Paragraph(str(t.get("passenger_ci","")), val)],
        [Paragraph("RUTA", lbl), Paragraph(str(t.get("origin","")) + " -> " + str(t.get("destination","")), val)],
        [Paragraph("SALIDA", lbl), Paragraph(str(t.get("departure_time","")), val)],
        [Paragraph("ASIENTO", lbl), Paragraph(str(t.get("seat_number","")) + " Piso " + str(t.get("floor","")), val)],
        [Paragraph("EMPRESA", lbl), Paragraph(str(t.get("company","")) + " - " + str(t.get("bus_type","")), val)],
        [Paragraph("PRECIO BASE", lbl), Paragraph("Bs. " + str(round(t.get("base_price",0),2)), val)],
        [Paragraph("TERMINAL", lbl), Paragraph("Bs. " + str(round(t.get("terminal_fee",0),2)), val)],
        [Paragraph("TOTAL", lbl), Paragraph("Bs. " + str(round(t.get("total_price",0),2)), val)],
    ]
    tbl = Table(rows, colWidths=[5*cm, 12*cm])
    tbl.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.lightgrey),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F0F4FF")),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),10)]))
    elems.append(tbl)
    elems.append(Spacer(1, 0.5*cm))
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(t.get("qr_token",""))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qb = BytesIO()
    qr_img.save(qb, format="PNG")
    qb.seek(0)
    qr_rl = Image(qb, width=4*cm, height=4*cm)
    qt = Table([[qr_rl, Paragraph("Presenta este QR al conductor para validar tu pasaje.", ParagraphStyle("qt", parent=styles["Normal"], fontSize=10, textColor=NAVY))]], colWidths=[5*cm, 12*cm])
    qt.setStyle(TableStyle([("ALIGN",(0,0),(0,0),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),1,NAVY),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    elems.append(qt)
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph("Bolivia Bus | boliviabus.bo", ParagraphStyle("ft", parent=styles["Normal"], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    doc.build(elems)
    buf.seek(0)
    return buf.getvalue()
''')
print('OK: pdf_generator.py')