from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from datetime import datetime
from num2words import num2words
import uuid
import os
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Убедись, что файл шрифта 'arial.ttf' лежит в корне проекта
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

contract_counter = 1

RUSSIAN_MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

class ContractRequest(BaseModel):
    city: str
    signing_date: str
    client_name: str
    client_inn: str
    client_kpp: str = ""
    client_bank: str = ""
    client_account: str
    executor_type: str
    executor_name: str
    executor_inn: str
    executor_bank: str = ""
    executor_account: str
    executor_kpp: str = ""
    executor_passport: str = ""
    service_type: str
    deadline: str
    price: int
    additional_terms: str = "Нет"
    client_penalty: float = 0.0
    executor_penalty: float = 0.0

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/generate-pdf-contract")
def generate_pdf_contract(data: ContractRequest):
    global contract_counter
    unique_filename = f"contract_{uuid.uuid4().hex}.pdf"
    
    try:
        if data.signing_date:
            d = datetime.strptime(data.signing_date, '%Y-%m-%d')
            day_str, month_name, year_str = d.strftime('%d'), RUSSIAN_MONTHS[d.month], d.strftime('%Y')
            contract_number = f"№ {contract_counter:03d}/Д-{d.strftime('%d.%m')}"
        else:
            now = datetime.now()
            day_str, month_name, year_str = now.strftime('%d'), RUSSIAN_MONTHS[now.month], now.strftime('%Y')
            contract_number = f"№ {contract_counter:03d}/Д-б/д"

        contract_counter += 1
        
        doc = SimpleDocTemplate(
            unique_filename, 
            pagesize=A4, 
            rightMargin=1.5*cm, 
            leftMargin=1.5*cm, 
            topMargin=1.5*cm, 
            bottomMargin=1.5*cm
        )
        
        styles = getSampleStyleSheet()
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Arial', fontSize=10, leading=14, spaceAfter=6)
        bold_style = ParagraphStyle('BoldStyle', parent=body_style, fontName='Arial', fontSize=10, leading=14, spaceAfter=4)
        title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Arial', fontSize=13, leading=16, alignment=1, spaceAfter=4)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontName='Arial', fontSize=11, leading=14, alignment=1, spaceAfter=12)

        story = []
        
        header_data = [[
            Paragraph(f"г. {data.city if data.city else '________________'}", body_style), 
            Paragraph(f"«{day_str}» {month_name} {year_str} г.", ParagraphStyle('RightDate', parent=body_style, alignment=2))
        ]]
        header_table = Table(header_data, colWidths=[9*cm, 9*cm])
        story.append(header_table)
        story.append(Spacer(1, 8))
        
        story.append(Paragraph("<b>ДОГОВОР ОКАЗАНИЯ УСЛУГ</b>", title_style))
        story.append(Paragraph(f"<b>{contract_number}</b>", subtitle_style))
        
        exec_desc = f"{data.executor_type} {data.executor_name}"
        story.append(Paragraph(
            f"<b>{data.client_name}</b>, именуемый(ое) в дальнейшем «Заказчик», с одной стороны, и "
            f"<b>{exec_desc}</b>, именуемый(ое) в дальнейшем «Исполнитель», с другой стороны, "
            f"совместно именуемые «Стороны», заключили настоящий Договор о нижеследующем:", body_style
        ))
        
        story.append(Paragraph("<b>1. ПРЕДМЕТ ДОГОВОРА И СРОКИ</b>", bold_style))
        story.append(Paragraph(f"1.1. Исполнитель обязуется по заданию Заказчика оказать следующие услуги: <b>{data.service_type}</b>, а Заказчик обязуется принять и оплатить эти услуги.", body_style))
        story.append(Paragraph(f"1.2. Срок выполнения работ/оказания услуг: <b>{data.deadline}</b> с момента подписания настоящего Договора.", body_style))
        story.append(Paragraph("1.3. Исполнитель оказывает услуги лично либо с привлечением третьих лиц, оставаясь ответственным за их действия перед Заказчиком.", body_style))

        story.append(Paragraph("<b>2. ПРАВА И ОБЯЗАННОСТИ СТОРОН</b>", bold_style))
        story.append(Paragraph("2.1. <b>Исполнитель обязуется:</b> оказать услуги качественно, в полном объеме и в сроки, согласованные Сторонами в настоящем Договоре.", body_style))
        story.append(Paragraph("2.2. <b>Заказчик обязуется:</b> предоставить Исполнителю информацию и материалы, необходимые для оказания услуг, и своевременно оплатить оказанные услуги.", body_style))

        story.append(Paragraph("<b>3. ПОРЯДОК СДАЧИ И ПРИЕМКИ УСЛУГ</b>", bold_style))
        story.append(Paragraph("3.1. По завершении оказания услуг Исполнитель предоставляет Заказчику Акт об оказанных услугах.", body_style))
        story.append(Paragraph("3.2. Заказчик в течение 3 (трех) рабочих дней с момента получения Акта обязан подписать его либо направить мотивированный отказ.", body_style))

        story.append(Paragraph("<b>4. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЕТОВ</b>", bold_style))
        formatted_price = "{:,}".format(data.price).replace(',', ' ')
        try:
            price_words = num2words(data.price, lang='ru')
        except Exception:
            price_words = ""
        price_str = f"{formatted_price} руб. ({price_words} рублей)" if price_words else f"{formatted_price} рублей"
        
        story.append(Paragraph(f"4.1. Общая стоимость услуг по настоящему Договору составляет: <b>{price_str}</b>.", body_style))
        story.append(Paragraph("4.2. Оплата производится путем перечисления денежных средств на расчетный счет Исполнителя.", body_style))

        story.append(Paragraph("<b>5. ОТВЕТСТВЕННОСТЬ СТОРОН</b>", bold_style))
        c_pen = data.client_penalty if data.client_penalty else 0.0
        e_pen = data.executor_penalty if data.executor_penalty else 0.0
        story.append(Paragraph(f"5.1. За нарушение сроков оплаты Заказчик уплачивает пеню в размере <b>{c_pen}%</b> от суммы задолженности за каждый день просрочки.", body_style))
        story.append(Paragraph(f"5.2. За нарушение сроков оказания услуг Исполнитель уплачивает пеню в размере <b>{e_pen}%</b> от стоимости услуг за каждый день просрочки.", body_style))

        story.append(Paragraph("<b>6. ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ И ОСОБЫЕ УСЛОВИЯ</b>", bold_style))
        terms = data.additional_terms if data.additional_terms.strip() else "Нет"
        story.append(Paragraph(f"6.1. Дополнительные условия: <b>{terms}</b>", body_style))
        story.append(Paragraph("6.2. Споры и разногласия разрешаются путем переговоров, а при недостижении согласия — в судебном порядке в соответствии с законодательством РФ.", body_style))

        story.append(Spacer(1, 10))
        
        story.append(Paragraph("<b>7. АДРЕСА, РЕКВИЗИТЫ И ПОДПИСИ СТОРОН</b>", bold_style))
        
        client_kpp_str = f"<br/>КПП: {data.client_kpp}" if data.client_kpp else ""
        client_bank_str = f"<br/>Банк: {data.client_bank}" if data.client_bank else ""
        
        client_details = (
            f"<b>ЗАКАЗЧИК:</b><br/>"
            f"<b>{data.client_name}</b><br/>"
            f"ИНН: {data.client_inn}{client_kpp_str}"
            f"{client_bank_str}<br/>"
            f"р/сч: {data.client_account}<br/><br/>"
            f"Подпись: ______________________"
        )

        exec_kpp_str = f"<br/>КПП: {data.executor_kpp}" if data.executor_kpp else ""
        exec_pass_str = f"<br/>Паспорт: {data.executor_passport}" if data.executor_passport else ""
        exec_bank_str = f"<br/>Банк: {data.executor_bank}" if data.executor_bank else ""

        exec_details = (
            f"<b>ИСПОЛНИТЕЛЬ:</b><br/>"
            f"<b>{data.executor_name}</b> ({data.executor_type})<br/>"
            f"ИНН: {data.executor_inn}{exec_kpp_str}{exec_pass_str}"
            f"{exec_bank_str}<br/>"
            f"р/сч: {data.executor_account}<br/><br/>"
            f"Подпись: ______________________"
        )

        req_table = Table([[Paragraph(client_details, body_style), Paragraph(exec_details, body_style)]], colWidths=[9*cm, 9*cm])
        req_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(req_table)
        
        doc.build(story)
        
        # Функция обратного вызова, которая удалит временный файл после отправки пользователю
        def cleanup():
            if os.path.exists(unique_filename):
                try:
                    os.remove(unique_filename)
                except Exception:
                    pass

        return FileResponse(unique_filename, media_type="application/pdf", filename="Dogovor.pdf", background=cleanup)
        
    except Exception as e:
        if os.path.exists(unique_filename):
            try:
                os.remove(unique_filename)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
