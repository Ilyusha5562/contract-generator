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
        "rent": "Договор аренды",
        "loan": "Договор займа",
        "employment": "Трудовой договор",
        "supply": "Договор поставки",
        "storage": "Договор хранения",
        "license": "Лицензионный договор",
        "carriage": "Договор перевозки",
        "gift": "Договор дарения",
        "agency": "Агентский договор",
        "commission": "Договор комиссии",
        "author": "Договор авторского заказа",
        "nda": "Соглашение о конфиденциальности (NDA)"
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
    # Заголовок для всех 15 типов
    c.drawString(50, y, "ДОГОВОР")
    y -= 30
    c.drawString(50, y, f"г. {city}, {date}")
    y -= 40
    
    # Динамические стороны
    roles = {
        "carriage": ("Перевозчик", "Заказчик"),
        "gift": ("Даритель", "Одаряемый"),
        "agency": ("Агент", "Принципал"),
        "commission": ("Комиссионер", "Комитент"),
        "author": ("Заказчик", "Автор"),
        "nda": ("Раскрывающая сторона", "Получающая сторона")
    }
    role1, role2 = roles.get(contract_type, ("Сторона 1", "Сторона 2"))
    
    c.drawString(50, y, f"{role1}: {contractor_name}")
    y -= 20
    c.drawString(50, y, f"{role2}: {customer_name}")
    
    y -= 30
    c.drawString(50, y, f"1. Предмет: {subject}")
    y -= 20
    c.drawString(50, y, f"2. Цена/Вознаграждение: {price} руб.")
    y -= 20
    c.drawString(50, y, f"3. Срок: {deadline}")
    
    c.save()
    return FileResponse(filename, media_type='application/pdf', filename=filename)
