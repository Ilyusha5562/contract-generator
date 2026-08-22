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

# Безопасная регистрация шрифта
if os.path.exists('arial.ttf'):
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.get("/form/{contract_type}", response_class=HTMLResponse)
def contract_form(request: Request, contract_type: str):
    titles = {
        "services": "Договор оказания услуг",
        "construction": "Договор строительного подряда"
    }
    contract_title = titles.get(contract_type, "Договор")
    return templates.TemplateResponse(request, "form.html", {
        "contract_type": contract_type,
        "contract_title": contract_title
    })

@app.post("/generate-pdf")
def generate_pdf(
    contract_type: str = Form(...),
    city: str = Form(...),
    date: str = Form(...),
    customer_name: str = Form(...),
    customer_inn: str = Form(...),
    contractor_name: str = Form(...),
    contractor_inn: str = Form(...),
    subject: str = Form(...),
    deadline: str = Form(...),
    price: str = Form(...),
    extra_terms: str = Form(""),
    penalty_customer: str = Form("0.1"),
    penalty_contractor: str = Form("0.1")
):
    filename = "contract.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    c.setFont(font_name, 11)
    
    y = height - 40
    title = "ДОГОВОР ОКАЗАНИЯ УСЛУГ" if contract_type == "services" else "ДОГОВОР СТРОИТЕЛЬНОГО ПОДРЯДА"
    
    c.drawString(50, y, f"{title} № 1")
    y -= 25
    c.drawString(50, y, f"г. {city}                                                                          Дата: {date}")
    y -= 35
    
    c.drawString(50, y, f"Заказчик: {customer_name}, ИНН: {customer_inn}")
    y -= 20
    contractor_label = "Исполнитель" if contract_type == "services" else "Подрядчик"
    c.drawString(50, y, f"{contractor_label}: {contractor_name}, ИНН: {contractor_inn}")
    y -= 30
    
    c.drawString(50, y, f"1. Предмет: {subject}")
    y -= 20
    c.drawString(50, y, f"2. Срок: {deadline}")
    y -= 20
    c.drawString(50, y, f"3. Стоимость: {price} руб.")
    y -= 25
    
    if extra_terms:
        c.drawString(50, y, f"4. Доп. условия: {extra_terms}")
        y -= 25

    c.drawString(50, y, f"5. Ответственность: пени {penalty_customer}% / {penalty_contractor}%")
    
    c.save()
    return FileResponse(filename, media_type='application/pdf', filename=filename)
