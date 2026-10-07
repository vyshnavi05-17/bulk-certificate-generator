import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def draw_certificate_pdf(
    output_path: str,
    recipient_name: str,
    course_name: str,
    event_date: str,
    issuer: str,
    certificate_id: int
) -> str:
    """
    Renders a single predefined, professionally styled certificate PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    page_width, page_height = landscape(A4)  # 841.89 x 595.27 points
    c = canvas.Canvas(output_path, pagesize=landscape(A4))

    # Background subtle tint
    c.setFillColor(colors.HexColor("#FCFDFD"))
    c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Outer decorative border (Navy)
    c.setStrokeColor(colors.HexColor("#1A365D"))  # Deep Navy
    c.setLineWidth(4)
    c.rect(25, 25, page_width - 50, page_height - 50, fill=0, stroke=1)

    # Inner decorative border (Gold)
    c.setStrokeColor(colors.HexColor("#D69E2E"))  # Warm Gold
    c.setLineWidth(1.5)
    c.rect(33, 33, page_width - 66, page_height - 66, fill=0, stroke=1)

    # Header / Title
    c.setFillColor(colors.HexColor("#1A365D"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(page_width / 2, page_height - 100, "CERTIFICATE OF COMPLETION")

    # Decorative subtitle
    c.setFillColor(colors.HexColor("#718096"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_width / 2, page_height - 135, "THIS IS PROUDLY PRESENTED TO")

    # Recipient Name
    c.setFillColor(colors.HexColor("#2B6CB0"))  # Royal Blue
    c.setFont("Helvetica-Bold", 28)
    display_name = recipient_name.strip()
    if len(display_name) > 40:
        display_name = display_name[:37] + "..."
    c.drawCentredString(page_width / 2, page_height - 195, display_name)

    # Thin separator line under name
    c.setStrokeColor(colors.HexColor("#E2E8F0"))
    c.setLineWidth(1)
    c.line(page_width / 2 - 180, page_height - 210, page_width / 2 + 180, page_height - 210)

    # Purpose description
    c.setFillColor(colors.HexColor("#4A5568"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(
        page_width / 2,
        page_height - 245,
        "for successfully completing the course/event"
    )

    # Course Name
    c.setFillColor(colors.HexColor("#1A202C"))
    c.setFont("Helvetica-Bold", 22)
    display_course = course_name.strip()
    if len(display_course) > 50:
        display_course = display_course[:47] + "..."
    c.drawCentredString(page_width / 2, page_height - 285, display_course)

    # Footer Metadata: Left (Date & ID), Right (Issuer & Signature)
    # Left: Event Date & Certificate ID
    c.setFillColor(colors.HexColor("#4A5568"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(75, 125, f"Date: {event_date}")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#718096"))
    c.drawString(75, 105, f"Certificate ID: #{certificate_id}")

    # Right: Issuer & Signature line
    c.setStrokeColor(colors.HexColor("#4A5568"))
    c.setLineWidth(1)
    c.line(page_width - 275, 135, page_width - 75, 135)

    c.setFillColor(colors.HexColor("#2D3748"))
    c.setFont("Helvetica-Bold", 12)
    display_issuer = issuer.strip()
    if len(display_issuer) > 30:
        display_issuer = display_issuer[:27] + "..."
    c.drawCentredString(page_width - 175, 118, display_issuer)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#A0AEC0"))
    c.drawCentredString(page_width - 175, 102, "Authorized Signature")

    c.save()
    return output_path
