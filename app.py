from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

if os.path.exists('arial.ttf'):
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.get("/form/{contract_type}", response_class=HTMLResponse)
def contract_form(request: Request, contract_type: str):
    # Динамически ищет шаблон конкретного договора, например form_rent.html
    template_name = f"form_{contract_type}.html"
    return templates.TemplateResponse(request, template_name, {"request": request, "contract_type": contract_type})

@app.post("/generate-pdf")
def generate_pdf(
    contract_type: str = Form(...),
    city: str = Form(...),
    date: str = Form(...),
    party1_name: str = Form(...),
    party1_id: str = Form(""),
    party2_name: str = Form(...),
    party2_id: str = Form(""),
    specific_field_1: str = Form(""),
    specific_field_2: str = Form(""),
    price: str = Form("0"),
    deadline: str = Form("Не указано")
):
    filename = "contract.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    c.setFont(font_name, 11)
    
    y = 750
    c.drawString(50, y, f"ДОГОВОР ({contract_type.upper()})")
    y -= 30
    c.drawString(50, y, f"г. {city}, от {date}")
    y -= 40
    
    c.drawString(50, y, f"Сторона 1: {party1_name} (ИНН/Паспорт: {party1_id})")
    y -= 20
    c.drawString(50, y, f"Сторона 2: {party2_name} (ИНН/Паспорт: {party2_id})")
    y -= 30
    
    c.drawString(50, y, f"1. Специфика договора: {specific_field_1}")
    y -= 20
    c.drawString(50, y, f"2. Дополнительные условия: {specific_field_2}")
    y -= 20
    c.drawString(50, y, f"3. Сумма / Оплата: {price} руб.")
    y -= 20
    c.drawString(50, y, f"4. Срок выполнения: {deadline}")
    
    c.save()
    return FileResponse(filename, media_type='application/pdf', filename=filename)
