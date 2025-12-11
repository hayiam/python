import tkinter as tk
from tkinter import ttk, messagebox
from validators import AppointmentValidator

class AppointmentsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
        self.load_patient_doctor_comboboxes()
    
    def setup_ui(self):
        # Форма информации о назначении
        form_frame = ttk.LabelFrame(self.frame, text="Информация о назначении")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Пациент:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.a_patient = ttk.Combobox(form_frame, width=20)
        self.a_patient.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Врач:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.a_doctor = ttk.Combobox(form_frame, width=20)
        self.a_doctor.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.a_datetime = ttk.Entry(form_frame, width=20)
        self.a_datetime.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Статус:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.a_status = ttk.Combobox(form_frame, values=['Запланировано', 'Завершено', 'Отменено', 'Неявка'], width=18)
        self.a_status.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Диагноз:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.a_diagnosis = tk.Text(form_frame, width=50, height=3)
        self.a_diagnosis.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Рецепт:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.a_prescription = tk.Text(form_frame, width=50, height=3)
        self.a_prescription.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Примечания:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.a_notes = tk.Text(form_frame, width=50, height=3)
        self.a_notes.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить назначение", command=self.add_appointment).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить назначение", command=self.update_appointment).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить назначение", command=self.delete_appointment).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список назначений
        list_frame = ttk.LabelFrame(self.frame, text="Список назначений")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Пациент', 'Врач', 'Дата', 'Статус', 'Диагноз')
        self.appointments_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=100)
        
        self.appointments_tree.pack(fill='both', expand=True)
        self.appointments_tree.bind('<<TreeviewSelect>>', self.on_appointment_select)
        
        # Загрузка назначений
        self.load_appointments()
    
    def load_patient_doctor_comboboxes(self):
        """Загрузка имен пациентов и врачей в комбобоксы"""
        try:
            # Загрузка пациентов
            patients_result, _ = self.db.execute_query(
                "SELECT patient_id, first_name, last_name FROM patients ORDER BY last_name, first_name"
            )
            patient_names = [f"{p[1]} {p[2]} (ID: {p[0]})" for p in patients_result]
            self.a_patient['values'] = patient_names
            
            # Загрузка врачей
            doctors_result, _ = self.db.execute_query(
                "SELECT doctor_id, first_name, last_name FROM doctors ORDER BY last_name, first_name"
            )
            doctor_names = [f"Доктор {d[1]} {d[2]} (ID: {d[0]})" for d in doctors_result]
            self.a_doctor['values'] = doctor_names
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные комбобоксов: {e}")
    
    def load_appointments(self):
        """Загрузка назначений в дерево"""
        try:
            for item in self.appointments_tree.get_children():
                self.appointments_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT a.appointment_id, p.first_name || ' ' || p.last_name, 
                       d.first_name || ' ' || d.last_name, a.appointment_date, 
                       a.status, a.diagnosis
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors d ON a.doctor_id = d.doctor_id
                ORDER BY a.appointment_date DESC
            """)
            
            for row in result:
                self.appointments_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить назначения: {e}")

    def add_appointment(self):
        """Добавление нового назначения с валидацией"""
        try:
            # Валидация данных
            if not AppointmentValidator.validate_appointment_data(
                self.a_patient.get(),
                self.a_doctor.get(),
                self.a_datetime.get(),
                self.a_status.get(),
                self.a_diagnosis.get("1.0", tk.END).strip()
            ):
                return
                
            # Извлечение ID пациента и врача из выбора комбобокса
            patient_text = self.a_patient.get()
            doctor_text = self.a_doctor.get()
            
            patient_id = int(patient_text.split('(ID: ')[1].rstrip(')')) if patient_text else None
            doctor_id = int(doctor_text.split('(ID: ')[1].rstrip(')')) if doctor_text else None
            
            query = """
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, diagnosis, prescription, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                patient_id,
                doctor_id,
                self.a_datetime.get(),
                self.a_status.get(),
                self.a_diagnosis.get("1.0", tk.END).strip(),
                self.a_prescription.get("1.0", tk.END).strip(),
                self.a_notes.get("1.0", tk.END).strip()
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Назначение успешно добавлено")
            self.clear_form()
            self.load_appointments()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить назначение: {e}")
    
    def update_appointment(self):
        """Обновление выбранного назначения с валидацией"""
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите назначение для обновления")
            return
        
        try:
            # Валидация данных
            if not AppointmentValidator.validate_appointment_data(
                self.a_patient.get(),
                self.a_doctor.get(),
                self.a_datetime.get(),
                self.a_status.get(),
                self.a_diagnosis.get("1.0", tk.END).strip()
            ):
                return
                
            appointment_id = self.appointments_tree.item(selected[0])['values'][0]
            
            # Извлечение ID пациента и врача из выбора комбобокса
            patient_text = self.a_patient.get()
            doctor_text = self.a_doctor.get()
            
            patient_id = int(patient_text.split('(ID: ')[1].rstrip(')')) if patient_text else None
            doctor_id = int(doctor_text.split('(ID: ')[1].rstrip(')')) if doctor_text else None
            
            query = """
                UPDATE appointments SET patient_id=%s, doctor_id=%s, appointment_date=%s, 
                status=%s, diagnosis=%s, prescription=%s, notes=%s WHERE appointment_id=%s
            """
            params = (
                patient_id,
                doctor_id,
                self.a_datetime.get(),
                self.a_status.get(),
                self.a_diagnosis.get("1.0", tk.END).strip(),
                self.a_prescription.get("1.0", tk.END).strip(),
                self.a_notes.get("1.0", tk.END).strip(),
                appointment_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Назначение успешно обновлено")
            self.load_appointments()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить назначение: {e}")
    
    def delete_appointment(self):
        """Удаление выбранного назначения"""
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите назначение для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это назначение?"):
            try:
                appointment_id = self.appointments_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM appointments WHERE appointment_id=%s", (appointment_id,))
                messagebox.showinfo("Успех", "Назначение успешно удалено")
                self.clear_form()
                self.load_appointments()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить назначение: {e}")
    
    def on_appointment_select(self, event):
        """Заполнение формы при выборе назначения"""
        selected = self.appointments_tree.selection()
        if selected:
            appointment_data = self.appointments_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM appointments WHERE appointment_id=%s", (appointment_data[0],)
            )
            
            if result:
                appointment = result[0]
                # Получение имен пациента и врача для комбобоксов
                patient_result, _ = self.db.execute_query(
                    "SELECT first_name, last_name FROM patients WHERE patient_id=%s", (appointment[1],)
                )
                doctor_result, _ = self.db.execute_query(
                    "SELECT first_name, last_name FROM doctors WHERE doctor_id=%s", (appointment[2],)
                )
                
                if patient_result:
                    patient_name = f"{patient_result[0][0]} {patient_result[0][1]} (ID: {appointment[1]})"
                    self.a_patient.set(patient_name)
                
                if doctor_result:
                    doctor_name = f"Доктор {doctor_result[0][0]} {doctor_result[0][1]} (ID: {appointment[2]})"
                    self.a_doctor.set(doctor_name)
                
                self.a_datetime.delete(0, tk.END)
                self.a_datetime.insert(0, appointment[3].strftime('%Y-%m-%d %H:%M') if appointment[3] else '')
                self.a_status.set(appointment[4] or '')
                self.a_diagnosis.delete("1.0", tk.END)
                self.a_diagnosis.insert("1.0", appointment[5] or '')
                self.a_prescription.delete("1.0", tk.END)
                self.a_prescription.insert("1.0", appointment[6] or '')
                self.a_notes.delete("1.0", tk.END)
                self.a_notes.insert("1.0", appointment[7] or '')
    
    def clear_form(self):
        """Очистка полей формы"""
        self.a_patient.set('')
        self.a_doctor.set('')
        self.a_datetime.delete(0, tk.END)
        self.a_status.set('')
        self.a_diagnosis.delete("1.0", tk.END)
        self.a_prescription.delete("1.0", tk.END)
        self.a_notes.delete("1.0", tk.END)
