from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
    
    # Настраиваем документ с отступами (в пунктах)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    font_name = 'Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    
    # Стили текста с поддержкой переносов и правильным шрифтом
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=10
    )
    
    story = []
    
    # Добавляем элементы в документ
    story.append(Paragraph(f"<b>ДОГОВОР ({contract_type.upper()})</b>", title_style))
    story.append(Paragraph(f"г. {city}, от {date}", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>Сторона 1:</b> {party1_name} (ИНН/Паспорт: {party1_id})", body_style))
    story.append(Paragraph(f"<b>Сторона 2:</b> {party2_name} (ИНН/Паспорт: {party2_id})", body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>1. Специфика договора:</b> {specific_field_1}", body_style))
    story.append(Paragraph(f"<b>2. Дополнительные условия:</b> {specific_field_2}", body_style))
    story.append(Paragraph(f"<b>3. Сумма / Оплата:</b> {price} руб.", body_style))
    story.append(Paragraph(f"<b>4. Срок выполнения:</b> {deadline}", body_style))

    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    # Добавляем небольшой отступ перед подписями
    story.append(Spacer(1, 40))
    
    # Данные для таблицы подписей
    signature_data = [
        [Paragraph("<b>Продавец:</b>", body_style), Paragraph("<b>Покупатель:</b>", body_style)],
        [Paragraph(f"{party1_name}", body_style), Paragraph(f"{party2_name}", body_style)],
        [Paragraph("<br/><br/>___________________ / ___________________", body_style), 
         Paragraph("<br/><br/>___________________ / ___________________", body_style)]
    ]
    
    # Создаем табличку шириной 500 пунктов (под ширину полей страницы)
    sig_table = Table(signature_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(sig_table)
    
    # Компилируем PDF
    doc.build(story)
    
    # Отправляем файл для предпросмотра в браузере (disposition='inline')
    return FileResponse(
        filename, 
        media_type='application/pdf', 
        filename=filename, 
        content_disposition_type='inline'
    )
