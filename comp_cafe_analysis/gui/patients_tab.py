import tkinter as tk
from tkinter import ttk, messagebox
from validators import PatientValidator

class PatientsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        # Форма информации о пациенте
        form_frame = ttk.LabelFrame(self.frame, text="Информация о пациенте")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.p_first_name = ttk.Entry(form_frame, width=20)
        self.p_first_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Фамилия:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.p_last_name = ttk.Entry(form_frame, width=20)
        self.p_last_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.p_dob = ttk.Entry(form_frame, width=20)
        self.p_dob.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Пол:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.p_gender = ttk.Combobox(form_frame, values=['Мужской', 'Женский'], width=17)  # Убрал "Другой"
        self.p_gender.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.p_phone = ttk.Entry(form_frame, width=20)
        self.p_phone.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.p_email = ttk.Entry(form_frame, width=20)
        self.p_email.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Адрес:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.p_address = tk.Text(form_frame, width=50, height=3)
        self.p_address.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Страховка:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.p_insurance = ttk.Entry(form_frame, width=20)
        self.p_insurance.grid(row=4, column=1, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить пациента", command=self.add_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить пациента", command=self.update_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить пациента", command=self.delete_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список пациентов
        list_frame = ttk.LabelFrame(self.frame, text="Список пациентов")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Имя', 'Фамилия', 'Дата рождения', 'Пол', 'Телефон', 'Email')
        self.patients_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.patients_tree.heading(col, text=col)
            self.patients_tree.column(col, width=100)
        
        self.patients_tree.pack(fill='both', expand=True)
        self.patients_tree.bind('<<TreeviewSelect>>', self.on_patient_select)
        
        # Загрузка пациентов
        self.load_patients()
    
    def load_patients(self):
        """Загрузка пациентов в дерево"""
        try:
            for item in self.patients_tree.get_children():
                self.patients_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT patient_id, first_name, last_name, date_of_birth, gender, phone, email 
                FROM patients ORDER BY last_name, first_name
            """)
            
            for row in result:
                self.patients_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пациентов: {e}")
    
    def add_patient(self):
        """Добавление нового пациента с валидацией"""
        try:
            # Валидация данных
            if not PatientValidator.validate_patient_data(
                self.p_first_name.get(),
                self.p_last_name.get(),
                self.p_dob.get(),
                self.p_gender.get(),
                self.p_phone.get(),
                self.p_email.get()
            ):
                return
                
            query = """
                INSERT INTO patients (first_name, last_name, date_of_birth, gender, phone, email, address, insurance_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.p_first_name.get(),
                self.p_last_name.get(),
                self.p_dob.get(),
                self.p_gender.get(),
                self.p_phone.get(),
                self.p_email.get(),
                self.p_address.get("1.0", tk.END).strip(),
                self.p_insurance.get()
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Пациент успешно добавлен")
            self.clear_form()
            self.load_patients()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пациента: {e}")
    
    def update_patient(self):
        """Обновление выбранного пациента с валидацией"""
        selected = self.patients_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите пациента для обновления")
            return
        
        try:
            # Валидация данных
            if not PatientValidator.validate_patient_data(
                self.p_first_name.get(),
                self.p_last_name.get(),
                self.p_dob.get(),
                self.p_gender.get(),
                self.p_phone.get(),
                self.p_email.get()
            ):
                return
                
            patient_id = self.patients_tree.item(selected[0])['values'][0]
            query = """
                UPDATE patients SET first_name=%s, last_name=%s, date_of_birth=%s, gender=%s, 
                phone=%s, email=%s, address=%s, insurance_number=%s WHERE patient_id=%s
            """
            params = (
                self.p_first_name.get(),
                self.p_last_name.get(),
                self.p_dob.get(),
                self.p_gender.get(),
                self.p_phone.get(),
                self.p_email.get(),
                self.p_address.get("1.0", tk.END).strip(),
                self.p_insurance.get(),
                patient_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Пациент успешно обновлен")
            self.load_patients()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить пациента: {e}")
    
    def delete_patient(self):
        """Удаление выбранного пациента"""
        selected = self.patients_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите пациента для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пациента?"):
            try:
                patient_id = self.patients_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
                messagebox.showinfo("Успех", "Пациент успешно удален")
                self.clear_form()
                self.load_patients()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить пациента: {e}")
    
    def on_patient_select(self, event):
        """Заполнение формы при выборе пациента"""
        selected = self.patients_tree.selection()
        if selected:
            patient_data = self.patients_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM patients WHERE patient_id=%s", (patient_data[0],)
            )
            
            if result:
                patient = result[0]
                self.p_first_name.delete(0, tk.END)
                self.p_first_name.insert(0, patient[1])
                self.p_last_name.delete(0, tk.END)
                self.p_last_name.insert(0, patient[2])
                self.p_dob.delete(0, tk.END)
                self.p_dob.insert(0, patient[3])
                self.p_gender.set(patient[4])
                self.p_phone.delete(0, tk.END)
                self.p_phone.insert(0, patient[5] or '')
                self.p_email.delete(0, tk.END)
                self.p_email.insert(0, patient[6] or '')
                self.p_address.delete("1.0", tk.END)
                self.p_address.insert("1.0", patient[7] or '')
                self.p_insurance.delete(0, tk.END)
                self.p_insurance.insert(0, patient[8] or '')
    
    def clear_form(self):
        """Очистка полей формы"""
        self.p_first_name.delete(0, tk.END)
        self.p_last_name.delete(0, tk.END)
        self.p_dob.delete(0, tk.END)
        self.p_gender.set('')
        self.p_phone.delete(0, tk.END)
        self.p_email.delete(0, tk.END)
        self.p_address.delete("1.0", tk.END)
        self.p_insurance.delete(0, tk.END)
