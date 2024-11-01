from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Client
from datetime import datetime
from django.utils import timezone

def generate_pdf(request, start_date=None, end_date=None):
    # Parse the date range if provided
    if start_date and end_date:
        start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
        clients = Client.objects.filter(date__range=[start_date, end_date])
    elif start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        clients = Client.objects.filter(date__date=start_date)
    else:
        # If no date provided, return all clients
        clients = Client.objects.all()

    # Create a HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clients.pdf"'

    # Create the PDF object, using the response object as its "file."
    pdf = canvas.Canvas(response, pagesize=A4)

    # Set up some basic PDF settings
    width, height = A4
    pdf.setFont("Helvetica", 12)
    y_position = height - 50  # start position for the first line

    # Title
    pdf.drawString(200, y_position, "Client Contacts Report")
    y_position -= 30

    # Headers
    pdf.drawString(20, y_position, "Name")
    pdf.drawString(250, y_position, "Phone Number 1")
    pdf.drawString(380, y_position, "Phone Number 2")
    pdf.drawString(500, y_position, "Date")
    y_position -= 20

    # Iterate through the clients and add them to the PDF
    for client in clients:
        pdf.drawString(20, y_position, client.name)
        pdf.drawString(250, y_position, client.phoneNumber1)
        pdf.drawString(380, y_position, client.phoneNumber2 if client.phoneNumber2 else "")
        pdf.drawString(500, y_position, client.date.strftime('%Y-%m-%d %H:%M:%S'))
        y_position -= 20

        # Check if the content goes out of the page
        if y_position <= 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = height - 50

    # Close the PDF object cleanly.
    pdf.save()

    return response
