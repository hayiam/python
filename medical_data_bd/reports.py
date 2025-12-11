from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_russian_fonts()
    
    def setup_russian_fonts(self):
        """Настройка шрифтов для поддержки русского языка"""
        try:
            # Попробуем найти и зарегистрировать шрифт с поддержкой кириллицы
            font_paths = [
                "DejavuSans.ttf",
                "arial.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/times.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
                    print(f"Шрифт зарегистрирован: {font_path}")
                    return True
            
            # Если шрифты не найдены, используем стандартные
            print("Предупреждение: Русские шрифты не найдены. Используются стандартные шрифты.")
            return False
            
        except Exception as e:
            print(f"Ошибка при регистрации шрифтов: {e}")
            return False
    
    def create_russian_paragraph(self, text, style_name='Normal', **kwargs):
        """Создание параграфа с поддержкой русского текста"""
        try:
            # Создаем кастомный стиль с русским шрифтом
            russian_style = ParagraphStyle(
                f'Russian{style_name}',
                parent=self.styles[style_name],
                **kwargs
            )
            
            # Пытаемся использовать русский шрифт
            try:
                russian_style.fontName = 'DejaVuSans'
            except:
                pass  # Если шрифт не зарегистрирован, используем стандартный
                
            return Paragraph(text, russian_style)
        except Exception as e:
            print(f"Ошибка создания русского параграфа: {e}")
            return Paragraph(text, self.styles[style_name])
    
    def ensure_unicode(self, text):
        """Обеспечивает корректное отображение Unicode текста"""
        if text is None:
            return ""
        if isinstance(text, str):
            return text
        try:
            return str(text)
        except:
            return ""
    
    def generate_patient_report(self, patient_data, filename="patient_report.pdf"):
        """Генерация медицинского отчета пациента"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "МЕДИЦИНСКИЙ ОТЧЕТ - ИНФОРМАЦИЯ О ПАЦИЕНТЕ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Информация о пациенте
        patient_info = [
            ["ID пациента:", self.ensure_unicode(patient_data[0])],
            ["Имя:", self.ensure_unicode(patient_data[1])],
            ["Фамилия:", self.ensure_unicode(patient_data[2])],
            ["Дата рождения:", patient_data[3].strftime('%Y-%m-%d')],
            ["Пол:", self.ensure_unicode(patient_data[4])],
            ["Телефон:", self.ensure_unicode(patient_data[5]) or "Н/Д"],
            ["Email:", self.ensure_unicode(patient_data[6]) or "Н/Д"],
            ["Адрес:", self.ensure_unicode(patient_data[7]) or "Н/Д"],
            ["Страховой номер:", self.ensure_unicode(patient_data[8]) or "Н/Д"]
        ]
        
        # Создаем таблицу с ячейками как Paragraph для поддержки Unicode
        table_data = []
        for row in patient_info:
            table_row = []
            for cell in row:
                table_row.append(self.create_russian_paragraph(cell, 'Normal', fontSize=10))
            table_data.append(table_row)
        
        patient_table = Table(table_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Для английского текста
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Подвал отчета
        footer = self.create_russian_paragraph(
            f"Сгенерировано {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            'Normal',
            fontSize=8,
            textColor=colors.gray,
            alignment=2
        )
        story.append(Spacer(1, 30))
        story.append(footer)
        
        doc.build(story)
        return filename

    def generate_all_patients_report(self, patients_data, filename="all_patients_report.pdf"):
        """Генерация отчета по всем пациентам"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "ОТЧЕТ ПО ВСЕМ ПАЦИЕНТАМ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Заголовки таблицы
        header_row = [
            'ID пациента', 'Имя', 'Фамилия', 'Дата рождения', 'Пол', 'Телефон'
        ]
        
        # Создаем данные таблицы с поддержкой Unicode
        table_data = []
        
        # Заголовок таблицы
        header_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=10) for text in header_row]
        table_data.append(header_cells)
        
        # Данные пациентов
        for patient in patients_data:
            row_data = [
                self.ensure_unicode(patient[0]),
                self.ensure_unicode(patient[1]),
                self.ensure_unicode(patient[2]),
                patient[3].strftime('%Y-%m-%d') if patient[3] else 'Н/Д',
                self.ensure_unicode(patient[4]),
                self.ensure_unicode(patient[5]) or 'Н/Д'
            ]
            
            row_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=9) for text in row_data]
            table_data.append(row_cells)
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Сводка
        total = len(patients_data)
        summary_text = f"Всего пациентов: {total}"
        summary = self.create_russian_paragraph(
            summary_text, 
            'Normal',
            fontSize=10,
            spaceBefore=20
        )
        story.append(summary)
        
        doc.build(story)
        return filename

    def generate_all_doctors_report(self, doctors_data, filename="all_doctors_report.pdf"):
        """Генерация отчета по всем врачам"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "ОТЧЕТ ПО ВСЕМ ВРАЧАМ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Заголовки таблицы
        header_row = [
            'ID врача', 'Имя', 'Фамилия', 'Специализация', 'Телефон', 'Email'
        ]
        
        # Создаем данные таблицы с поддержкой Unicode
        table_data = []
        
        # Заголовок таблицы
        header_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=10) for text in header_row]
        table_data.append(header_cells)
        
        # Данные врачей
        for doctor in doctors_data:
            row_data = [
                self.ensure_unicode(doctor[0]),
                self.ensure_unicode(doctor[1]),
                self.ensure_unicode(doctor[2]),
                self.ensure_unicode(doctor[3]),
                self.ensure_unicode(doctor[4]) or 'Н/Д',
                self.ensure_unicode(doctor[5]) or 'Н/Д'
            ]
            
            row_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=9) for text in row_data]
            table_data.append(row_cells)
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Сводка
        total = len(doctors_data)
        summary_text = f"Всего врачей: {total}"
        summary = self.create_russian_paragraph(
            summary_text, 
            'Normal',
            fontSize=10,
            spaceBefore=20
        )
        story.append(summary)
        
        doc.build(story)
        return filename
    
    def generate_appointments_report(self, appointments_data, filename="appointments_report.pdf"):
        """Генерация отчета по назначениям"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "ОТЧЕТ ПО НАЗНАЧЕНИЯМ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Заголовки таблицы
        header_row = [
            'ID назначения', 'Пациент', 'Врач', 'Дата', 'Статус', 'Диагноз'
        ]
        
        # Создаем данные таблицы с поддержкой Unicode
        table_data = []
        
        # Заголовок таблицы
        header_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=10) for text in header_row]
        table_data.append(header_cells)
        
        # Данные назначений
        for appointment in appointments_data:
            row_data = [
                self.ensure_unicode(appointment[0]),
                f"{self.ensure_unicode(appointment[1])} {self.ensure_unicode(appointment[2])}",
                f"Доктор {self.ensure_unicode(appointment[3])}",
                appointment[4].strftime('%Y-%m-%d %H:%M'),
                self.ensure_unicode(appointment[5]),
                self.ensure_unicode(appointment[6]) or 'Н/Д'
            ]
            
            row_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=9) for text in row_data]
            table_data.append(row_cells)
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Сводка
        total = len(appointments_data)
        completed = len([a for a in appointments_data if a[5] in ['Completed', 'Завершено']])
        pending = total - completed
        
        summary_text = f"Всего назначений: {total} | Завершено: {completed} | Ожидают: {pending}"
        summary = self.create_russian_paragraph(
            summary_text, 
            'Normal',
            fontSize=10,
            spaceBefore=20
        )
        story.append(summary)
        
        doc.build(story)
        return filename

    def generate_doctor_report(self, doctor_data, filename="doctor_report.pdf"):
        """Генерация отчета по врачу"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "ОТЧЕТ ПО ВРАЧУ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Информация о враче
        doctor_info = [
            ["ID врача:", self.ensure_unicode(doctor_data[0])],
            ["Имя:", self.ensure_unicode(doctor_data[1])],
            ["Фамилия:", self.ensure_unicode(doctor_data[2])],
            ["Специализация:", self.ensure_unicode(doctor_data[3])],
            ["Телефон:", self.ensure_unicode(doctor_data[4]) or "Н/Д"],
            ["Email:", self.ensure_unicode(doctor_data[5]) or "Н/Д"],
            ["Номер лицензии:", self.ensure_unicode(doctor_data[6]) or "Н/Д"],
            ["Дата приема:", doctor_data[7].strftime('%Y-%m-%d') if doctor_data[7] else "Н/Д"],
            ["Зарплата:", f"{doctor_data[8]:.2f}" if doctor_data[8] else "Н/Д"]
        ]
        
        # Создаем таблицу с ячейками как Paragraph
        table_data = []
        for row in doctor_info:
            table_row = []
            for cell in row:
                table_row.append(self.create_russian_paragraph(cell, 'Normal', fontSize=10))
            table_data.append(table_row)
        
        doctor_table = Table(table_data, colWidths=[2*inch, 4*inch])
        doctor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(doctor_table)
        story.append(Spacer(1, 20))
        
        # Подвал отчета
        footer = self.create_russian_paragraph(
            f"Сгенерировано {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            'Normal',
            fontSize=8,
            textColor=colors.gray,
            alignment=2
        )
        story.append(Spacer(1, 30))
        story.append(footer)
        
        doc.build(story)
        return filename

    def generate_medical_records_report(self, medical_records_data, filename="medical_records_report.pdf"):
        """Генерация отчета по медицинским картам"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Заголовок
        title = self.create_russian_paragraph(
            "ОТЧЕТ ПО МЕДИЦИНСКИМ КАРТАМ", 
            'Heading1',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        # Заголовки таблицы
        header_row = [
            'ID записи', 'Пациент', 'Врач', 'Дата визита', 'Диагноз', 'Лечение'
        ]
        
        # Создаем данные таблицы с поддержкой Unicode
        table_data = []
        
        # Заголовок таблицы
        header_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=10) for text in header_row]
        table_data.append(header_cells)
        
        # Данные медицинских записей
        for record in medical_records_data:
            row_data = [
                self.ensure_unicode(record[0]),
                self.ensure_unicode(record[1]),
                self.ensure_unicode(record[2]),
                record[3].strftime('%Y-%m-%d') if record[3] else 'Н/Д',
                self.ensure_unicode(record[4]) or 'Н/Д',
                self.ensure_unicode(record[5]) or 'Н/Д'
            ]
            
            row_cells = [self.create_russian_paragraph(text, 'Normal', fontSize=9) for text in row_data]
            table_data.append(row_cells)
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Сводка
        total = len(medical_records_data)
        summary_text = f"Всего медицинских записей: {total}"
        summary = self.create_russian_paragraph(
            summary_text, 
            'Normal',
            fontSize=10,
            spaceBefore=20
        )
        story.append(summary)
        
        doc.build(story)
        return filename

    def generate_comprehensive_report(self, patients_data, doctors_data, appointments_data, medical_records_data, filename="comprehensive_report.pdf"):
        """Генерация комплексного отчета"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # Титульная страница
        title = self.create_russian_paragraph(
            "КОМПЛЕКСНЫЙ МЕДИЦИНСКИЙ ОТЧЕТ", 
            'Heading1',
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        story.append(title)
        
        subtitle = self.create_russian_paragraph(
            f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
            'Heading2',
            fontSize=12,
            spaceAfter=100,
            alignment=1
        )
        story.append(subtitle)
        
        story.append(PageBreak())
        
        # Раздел пациентов
        patients_title = self.create_russian_paragraph(
            "1. СТАТИСТИКА ПО ПАЦИЕНТАМ", 
            'Heading2',
            fontSize=14,
            spaceAfter=20
        )
        story.append(patients_title)
        
        patients_count = len(patients_data)
        patients_summary = self.create_russian_paragraph(
            f"Всего пациентов в системе: {patients_count}", 
            'Normal',
            fontSize=12,
            spaceAfter=10
        )
        story.append(patients_summary)
        
        # Раздел врачей
        doctors_title = self.create_russian_paragraph(
            "2. СТАТИСТИКА ПО ВРАЧАМ", 
            'Heading2',
            fontSize=14,
            spaceAfter=20
        )
        story.append(doctors_title)
        
        doctors_count = len(doctors_data)
        doctors_summary = self.create_russian_paragraph(
            f"Всего врачей в системе: {doctors_count}", 
            'Normal',
            fontSize=12,
            spaceAfter=10
        )
        story.append(doctors_summary)
        
        # Раздел назначений
        appointments_title = self.create_russian_paragraph(
            "3. СТАТИСТИКА ПО НАЗНАЧЕНИЯМ", 
            'Heading2',
            fontSize=14,
            spaceAfter=20
        )
        story.append(appointments_title)
        
        appointments_count = len(appointments_data)
        completed_appointments = len([a for a in appointments_data if a[5] in ['Completed', 'Завершено']])
        pending_appointments = appointments_count - completed_appointments
        
        appointments_summary = self.create_russian_paragraph(
            f"Всего назначений: {appointments_count} | Завершено: {completed_appointments} | Ожидают: {pending_appointments}", 
            'Normal',
            fontSize=12,
            spaceAfter=10
        )
        story.append(appointments_summary)
        
        # Раздел медицинских записей
        records_title = self.create_russian_paragraph(
            "4. СТАТИСТИКА ПО МЕДИЦИНСКИМ ЗАПИСЯМ", 
            'Heading2',
            fontSize=14,
            spaceAfter=20
        )
        story.append(records_title)
        
        records_count = len(medical_records_data)
        records_summary = self.create_russian_paragraph(
            f"Всего медицинских записей: {records_count}", 
            'Normal',
            fontSize=12,
            spaceAfter=10
        )
        story.append(records_summary)
        
        story.append(PageBreak())
        
        # Общая сводка
        summary_title = self.create_russian_paragraph(
            "ОБЩАЯ СВОДКА", 
            'Heading2',
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(summary_title)
        
        summary_data = [
            ["Показатель", "Количество"],
            ["Пациенты", str(patients_count)],
            ["Врачи", str(doctors_count)],
            ["Назначения", str(appointments_count)],
            ["Медицинские записи", str(records_count)],
            ["Завершенные назначения", str(completed_appointments)],
            ["Ожидающие назначения", str(pending_appointments)]
        ]
        
        summary_table_data = []
        for row in summary_data:
            table_row = []
            for cell in row:
                table_row.append(self.create_russian_paragraph(cell, 'Normal', fontSize=10))
            summary_table_data.append(table_row)
        
        summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        
        doc.build(story)
        return filename
