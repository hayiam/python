import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

class ReportsTab:
    def __init__(self, notebook, db, pdf_generator):
        self.db = db
        self.pdf_generator = pdf_generator
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        reports_frame = ttk.Frame(self.frame)
        reports_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Пациенты
        patients_frame = ttk.LabelFrame(reports_frame, text="Отчеты по пациентам", padding=10)
        patients_frame.pack(fill='x', pady=5)
        
        ttk.Button(patients_frame, text="Сгенерировать отчет по всем пациентам", 
                  command=self.generate_all_patients_report).pack(side='left', padx=5)
        
        # Врачи
        doctors_frame = ttk.LabelFrame(reports_frame, text="Отчеты по врачам", padding=10)
        doctors_frame.pack(fill='x', pady=5)
        
        ttk.Button(doctors_frame, text="Сгенерировать отчет по всем врачам", 
                  command=self.generate_all_doctors_report).pack(side='left', padx=5)
        
        # Назначения
        appointments_frame = ttk.LabelFrame(reports_frame, text="Отчеты по назначениям", padding=10)
        appointments_frame.pack(fill='x', pady=5)
        
        ttk.Button(appointments_frame, text="Сгенерировать отчет по всем назначениям", 
                  command=self.generate_appointments_report).pack(side='left', padx=5)
        
        # Медкарты
        records_frame = ttk.LabelFrame(reports_frame, text="Отчеты по медкартам", padding=10)
        records_frame.pack(fill='x', pady=5)
        
        ttk.Button(records_frame, text="Сгенерировать отчет по всем медкартам", 
                  command=self.generate_all_records_report).pack(side='left', padx=5)
        
        # Комплексный отчет
        comprehensive_frame = ttk.LabelFrame(reports_frame, text="Комплексные отчеты", padding=10)
        comprehensive_frame.pack(fill='x', pady=5)
        
        ttk.Button(comprehensive_frame, text="Сгенерировать комплексный отчет", 
                  command=self.generate_comprehensive_report).pack(side='left', padx=5)
    
    def safe_execute_query(self, query, params=None):
        """Безопасное выполнение запроса с обработкой ошибок"""
        try:
            if params:
                return self.db.execute_query(query, params)
            else:
                return self.db.execute_query(query)
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None, None
    
    def generate_all_patients_report(self):
        """Генерация отчета по всем пациентам"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF файлы", "*.pdf")],
                title="Сохранить отчет по всем пациентам как"
            )
            
            if filename:
                result = self.safe_execute_query("""
                    SELECT patient_id, first_name, last_name, date_of_birth, gender, phone
                    FROM patients ORDER BY last_name, first_name
                """)
                
                if result and result[0]:
                    self.pdf_generator.generate_all_patients_report(result[0], filename)
                    messagebox.showinfo("Успех", f"Отчет сгенерирован: {filename}")
                    os.startfile(filename)
                else:
                    messagebox.showwarning("Предупреждение", "Нет данных о пациентах")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать отчет: {e}")
    
    def generate_all_doctors_report(self):
        """Генерация отчета по всем врачам"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF файлы", "*.pdf")],
                title="Сохранить отчет по всем врачам как"
            )
            
            if filename:
                result = self.safe_execute_query("""
                    SELECT doctor_id, first_name, last_name, specialization, phone, email
                    FROM doctors ORDER BY last_name, first_name
                """)
                
                if result and result[0]:
                    self.pdf_generator.generate_all_doctors_report(result[0], filename)
                    messagebox.showinfo("Успех", f"Отчет сгенерирован: {filename}")
                    os.startfile(filename)
                else:
                    messagebox.showwarning("Предупреждение", "Нет данных о врачах")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать отчет: {e}")
    
    def generate_appointments_report(self):
        """Генерация PDF отчета по назначениям"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF файлы", "*.pdf")],
                title="Сохранить отчет по назначениям как"
            )
            
            if filename:
                result = self.safe_execute_query("""
                    SELECT a.appointment_id, p.first_name, p.last_name, d.first_name, 
                           a.appointment_date, a.status, a.diagnosis
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                    ORDER BY a.appointment_date DESC
                """)
                
                if result and result[0]:
                    self.pdf_generator.generate_appointments_report(result[0], filename)
                    messagebox.showinfo("Успех", f"Отчет сгенерирован: {filename}")
                    os.startfile(filename)
                else:
                    messagebox.showwarning("Предупреждение", "Нет данных о назначениях")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать отчет: {e}")
    
    def generate_all_records_report(self):
        """Генерация PDF отчета по всем медицинским записям"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF файлы", "*.pdf")],
                title="Сохранить отчет по всем медкартам как"
            )
            
            if filename:
                result = self.safe_execute_query("""
                    SELECT mr.record_id, p.first_name || ' ' || p.last_name as patient_name,
                           d.first_name || ' ' || d.last_name as doctor_name, mr.visit_date, 
                           mr.diagnosis, mr.treatment
                    FROM medical_records mr
                    JOIN patients p ON mr.patient_id = p.patient_id
                    JOIN doctors d ON mr.doctor_id = d.doctor_id
                    ORDER BY mr.visit_date DESC
                """)
                
                if result and result[0]:
                    self.pdf_generator.generate_medical_records_report(result[0], filename)
                    messagebox.showinfo("Успех", f"Отчет сгенерирован: {filename}")
                    os.startfile(filename)
                else:
                    messagebox.showwarning("Предупреждение", "Нет данных медицинских записей")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать отчет: {e}")
    
    def generate_comprehensive_report(self):
        """Генерация комплексного PDF отчета"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF файлы", "*.pdf")],
                title="Сохранить комплексный отчет как"
            )
            
            if filename:
                # Получаем данные для всех разделов
                patients_result = self.safe_execute_query("SELECT * FROM patients")
                doctors_result = self.safe_execute_query("SELECT * FROM doctors")
                appointments_result = self.safe_execute_query("""
                    SELECT a.appointment_id, p.first_name, p.last_name, d.first_name, 
                           a.appointment_date, a.status, a.diagnosis
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.patient_id
                    JOIN doctors d ON a.doctor_id = d.doctor_id
                """)
                records_result = self.safe_execute_query("""
                    SELECT mr.record_id, p.first_name || ' ' || p.last_name as patient_name,
                           d.first_name || ' ' || d.last_name as doctor_name, mr.visit_date, 
                           mr.diagnosis, mr.treatment
                    FROM medical_records mr
                    JOIN patients p ON mr.patient_id = p.patient_id
                    JOIN doctors d ON mr.doctor_id = d.doctor_id
                """)
                
                # Извлекаем только данные (первый элемент кортежа)
                patients_data = patients_result[0] if patients_result and patients_result[0] else []
                doctors_data = doctors_result[0] if doctors_result and doctors_result[0] else []
                appointments_data = appointments_result[0] if appointments_result and appointments_result[0] else []
                records_data = records_result[0] if records_result and records_result[0] else []
                
                if patients_data or doctors_data or appointments_data or records_data:
                    self.pdf_generator.generate_comprehensive_report(
                        patients_data, doctors_data, appointments_data, records_data, filename
                    )
                    messagebox.showinfo("Успех", f"Комплексный отчет сгенерирован: {filename}")
                    os.startfile(filename)
                else:
                    messagebox.showwarning("Предупреждение", "Нет данных для генерации отчета")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать комплексный отчет: {e}")
