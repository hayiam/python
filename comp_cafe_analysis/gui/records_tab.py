import tkinter as tk
from tkinter import ttk, messagebox
from validators import MedicalRecordValidator

class RecordsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
        self.load_record_comboboxes()
    
    def setup_ui(self):
        # Форма медицинской записи
        form_frame = ttk.LabelFrame(self.frame, text="Медицинская запись")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Пациент:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.r_patient = ttk.Combobox(form_frame, width=20)
        self.r_patient.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Врач:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.r_doctor = ttk.Combobox(form_frame, width=20)
        self.r_doctor.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата визита (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.r_visit_date = ttk.Entry(form_frame, width=20)
        self.r_visit_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Следующий визит (ГГГГ-ММ-ДД):").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.r_next_visit = ttk.Entry(form_frame, width=20)
        self.r_next_visit.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Симптомы:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.r_symptoms = tk.Text(form_frame, width=50, height=3)
        self.r_symptoms.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Диагноз:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.r_diagnosis = tk.Text(form_frame, width=50, height=3)
        self.r_diagnosis.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Лечение:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.r_treatment = tk.Text(form_frame, width=50, height=3)
        self.r_treatment.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Медикаменты:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.r_medications = tk.Text(form_frame, width=50, height=3)
        self.r_medications.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить запись", command=self.add_medical_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить запись", command=self.update_medical_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить запись", command=self.delete_medical_record).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список медицинских записей
        list_frame = ttk.LabelFrame(self.frame, text="Медицинские записи")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Пациент', 'Врач', 'Дата визита', 'Диагноз')
        self.records_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.records_tree.heading(col, text=col)
            self.records_tree.column(col, width=100)
        
        self.records_tree.pack(fill='both', expand=True)
        self.records_tree.bind('<<TreeviewSelect>>', self.on_record_select)
        
        # Загрузка медицинских записей
        self.load_medical_records()
    
    def load_record_comboboxes(self):
        """Загрузка имен пациентов и врачей в комбобоксы медицинских записей"""
        try:
            # Загрузка пациентов
            patients_result, _ = self.db.execute_query(
                "SELECT patient_id, first_name, last_name FROM patients ORDER BY last_name, first_name"
            )
            patient_names = [f"{p[1]} {p[2]} (ID: {p[0]})" for p in patients_result]
            self.r_patient['values'] = patient_names
            
            # Загрузка врачей
            doctors_result, _ = self.db.execute_query(
                "SELECT doctor_id, first_name, last_name FROM doctors ORDER BY last_name, first_name"
            )
            doctor_names = [f"Доктор {d[1]} {d[2]} (ID: {d[0]})" for d in doctors_result]
            self.r_doctor['values'] = doctor_names
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные комбобоксов: {e}")
    
    def load_medical_records(self):
        """Загрузка медицинских записей в дерево"""
        try:
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT mr.record_id, p.first_name || ' ' || p.last_name, 
                       d.first_name || ' ' || d.last_name, mr.visit_date, mr.diagnosis
                FROM medical_records mr
                JOIN patients p ON mr.patient_id = p.patient_id
                JOIN doctors d ON mr.doctor_id = d.doctor_id
                ORDER BY mr.visit_date DESC
            """)
            
            for row in result:
                self.records_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить медицинские записи: {e}")
    

    def add_medical_record(self):
        """Добавление новой медицинской записи с валидацией"""
        try:
            # Валидация данных
            if not MedicalRecordValidator.validate_medical_record_data(
                self.r_patient.get(),
                self.r_doctor.get(),
                self.r_visit_date.get(),
                self.r_diagnosis.get("1.0", tk.END).strip()
            ):
                return
                
            # Извлечение ID пациента и врача из выбора комбобокса
            patient_text = self.r_patient.get()
            doctor_text = self.r_doctor.get()
            
            patient_id = int(patient_text.split('(ID: ')[1].rstrip(')')) if patient_text else None
            doctor_id = int(doctor_text.split('(ID: ')[1].rstrip(')')) if doctor_text else None
            
            query = """
                INSERT INTO medical_records (patient_id, doctor_id, visit_date, symptoms, 
                diagnosis, treatment, medications, next_visit_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                patient_id,
                doctor_id,
                self.r_visit_date.get(),
                self.r_symptoms.get("1.0", tk.END).strip(),
                self.r_diagnosis.get("1.0", tk.END).strip(),
                self.r_treatment.get("1.0", tk.END).strip(),
                self.r_medications.get("1.0", tk.END).strip(),
                self.r_next_visit.get() or None
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Медицинская запись успешно добавлена")
            self.clear_form()
            self.load_medical_records()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить медицинскую запись: {e}")
    
    def update_medical_record(self):
        """Обновление выбранной медицинской записи с валидацией"""
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите медицинскую запись для обновления")
            return
        
        try:
            # Валидация данных
            if not MedicalRecordValidator.validate_medical_record_data(
                self.r_patient.get(),
                self.r_doctor.get(),
                self.r_visit_date.get(),
                self.r_diagnosis.get("1.0", tk.END).strip()
            ):
                return
                
            record_id = self.records_tree.item(selected[0])['values'][0]
            
            # Извлечение ID пациента и врача из выбора комбобокса
            patient_text = self.r_patient.get()
            doctor_text = self.r_doctor.get()
            
            patient_id = int(patient_text.split('(ID: ')[1].rstrip(')')) if patient_text else None
            doctor_id = int(doctor_text.split('(ID: ')[1].rstrip(')')) if doctor_text else None
            
            query = """
                UPDATE medical_records SET patient_id=%s, doctor_id=%s, visit_date=%s, 
                symptoms=%s, diagnosis=%s, treatment=%s, medications=%s, next_visit_date=%s 
                WHERE record_id=%s
            """
            params = (
                patient_id,
                doctor_id,
                self.r_visit_date.get(),
                self.r_symptoms.get("1.0", tk.END).strip(),
                self.r_diagnosis.get("1.0", tk.END).strip(),
                self.r_treatment.get("1.0", tk.END).strip(),
                self.r_medications.get("1.0", tk.END).strip(),
                self.r_next_visit.get() or None,
                record_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Медицинская запись успешно обновлена")
            self.load_medical_records()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить медицинскую запись: {e}")
    
    def delete_medical_record(self):
        """Удаление выбранной медицинской записи"""
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите медицинскую запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту медицинскую запись?"):
            try:
                record_id = self.records_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM medical_records WHERE record_id=%s", (record_id,))
                messagebox.showinfo("Успех", "Медицинская запись успешно удалена")
                self.clear_form()
                self.load_medical_records()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить медицинскую запись: {e}")
    
    def on_record_select(self, event):
        """Заполнение формы при выборе медицинской записи"""
        selected = self.records_tree.selection()
        if selected:
            record_data = self.records_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM medical_records WHERE record_id=%s", (record_data[0],)
            )
            
            if result:
                record = result[0]
                # Получение имен пациента и врача для комбобоксов
                patient_result, _ = self.db.execute_query(
                    "SELECT first_name, last_name FROM patients WHERE patient_id=%s", (record[1],)
                )
                doctor_result, _ = self.db.execute_query(
                    "SELECT first_name, last_name FROM doctors WHERE doctor_id=%s", (record[7],)
                )
                
                if patient_result:
                    patient_name = f"{patient_result[0][0]} {patient_result[0][1]} (ID: {record[1]})"
                    self.r_patient.set(patient_name)
                
                if doctor_result:
                    doctor_name = f"Доктор {doctor_result[0][0]} {doctor_result[0][1]} (ID: {record[7]})"
                    self.r_doctor.set(doctor_name)
                
                self.r_visit_date.delete(0, tk.END)
                self.r_visit_date.insert(0, record[2])
                self.r_symptoms.delete("1.0", tk.END)
                self.r_symptoms.insert("1.0", record[3] or '')
                self.r_diagnosis.delete("1.0", tk.END)
                self.r_diagnosis.insert("1.0", record[4] or '')
                self.r_treatment.delete("1.0", tk.END)
                self.r_treatment.insert("1.0", record[5] or '')
                self.r_medications.delete("1.0", tk.END)
                self.r_medications.insert("1.0", record[6] or '')
                self.r_next_visit.delete(0, tk.END)
                self.r_next_visit.insert(0, record[8] or '')
    
    def clear_form(self):
        """Очистка полей формы"""
        self.r_patient.set('')
        self.r_doctor.set('')
        self.r_visit_date.delete(0, tk.END)
        self.r_next_visit.delete(0, tk.END)
        self.r_symptoms.delete("1.0", tk.END)
        self.r_diagnosis.delete("1.0", tk.END)
        self.r_treatment.delete("1.0", tk.END)
        self.r_medications.delete("1.0", tk.END)
