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
    titles = {
        "services": "Договор оказания услуг",
        "construction": "Договор строительного подряда",
        "sale": "Договор купли-продажи",
        "rent": "Договор аренды помещения",
        "loan": "Договор займа",
        "employment": "Трудовой договор",
        "supply": "Договор поставки",
        "storage": "Договор хранения",
        "license": "Лицензионный договор"
    }
    return templates.TemplateResponse(request, "form.html", {
        "request": request,
        "contract_type": contract_type,
        "contract_title": titles.get(contract_type, "Договор")
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
    deadline: str = Form("Не указано"),
    price: str = Form(...),
    extra_terms: str = Form(""),
    penalty_customer: str = Form("0.1"),
    penalty_contractor: str = Form("0.1")
):
    filename = "contract.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    c.setFont(font_name, 11)
    
    y = 750
    titles = {
        "services": "ДОГОВОР УСЛУГ", 
        "construction": "ДОГОВОР ПОДРЯДА", 
        "sale": "ДОГОВОР КУПЛИ-продажи",
        "rent": "ДОГОВОР АРЕНДЫ",
        "loan": "ДОГОВОР ЗАЙМА",
        "employment": "ТРУДОВОЙ ДОГОВОР",
        "supply": "ДОГОВОР ПОСТАВКИ",
        "storage": "ДОГОВОР ХРАНЕНИЯ",
        "license": "ЛИЦЕНЗИОННЫЙ ДОГОВОР"
    }
    c.drawString(50, y, titles.get(contract_type, "ДОГОВОР"))
    
    y -= 30
    c.drawString(50, y, f"г. {city}, {date}")
    y -= 40
    
    # Гибкая настройка сторон в зависимости от типа
    if contract_type == "employment":
        c.drawString(50, y, f"Работодатель: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Работник: {customer_name}")
    elif contract_type == "loan":
        c.drawString(50, y, f"Займодавец: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Заемщик: {customer_name}")
    elif contract_type == "rent":
        c.drawString(50, y, f"Арендодатель: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Арендатор: {customer_name}")
    elif contract_type == "supply":
        c.drawString(50, y, f"Поставщик: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Покупатель: {customer_name}")
    elif contract_type == "storage":
        c.drawString(50, y, f"Хранитель: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Поклажедатель: {customer_name}")
    elif contract_type == "license":
        c.drawString(50, y, f"Лицензиар: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Лицензиат: {customer_name}")
    else:
        c.drawString(50, y, f"Сторона 1: {contractor_name}")
        y -= 20
        c.drawString(50, y, f"Сторона 2: {customer_name}")
        
    y -= 30
    c.drawString(50, y, f"1. Предмет / Обязанности: {subject}")
    y -= 20
    c.drawString(50, y, f"2. Сумма / Вознаграждение: {price} руб.")
    y -= 20
    c.drawString(50, y, f"3. Срок / Период действия: {deadline}")
    
    c.save()
    return FileResponse(filename, media_type='application/pdf', filename=filename)
