import tkinter as tk
from tkinter import ttk, messagebox
from validators import DoctorValidator

class DoctorsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        # Форма информации о враче
        form_frame = ttk.LabelFrame(self.frame, text="Информация о враче")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.d_first_name = ttk.Entry(form_frame, width=20)
        self.d_first_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Фамилия:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.d_last_name = ttk.Entry(form_frame, width=20)
        self.d_last_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Специализация:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.d_specialization = ttk.Combobox(form_frame, values=[
            'Кардиология', 'Педиатрия', 'Ортопедия', 'Дерматология', 
            'Неврология', 'Онкология', 'Психиатрия', 'Хирургия', 'Терапия'
        ], width=18)
        self.d_specialization.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Телефон:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.d_phone = ttk.Entry(form_frame, width=20)
        self.d_phone.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.d_email = ttk.Entry(form_frame, width=20)
        self.d_email.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Номер лицензии:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.d_license = ttk.Entry(form_frame, width=20)
        self.d_license.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата приема (ГГГГ-ММ-ДД):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.d_hire_date = ttk.Entry(form_frame, width=20)
        self.d_hire_date.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Зарплата:").grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.d_salary = ttk.Entry(form_frame, width=20)
        self.d_salary.grid(row=3, column=3, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить врача", command=self.add_doctor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить врача", command=self.update_doctor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить врача", command=self.delete_doctor).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список врачей
        list_frame = ttk.LabelFrame(self.frame, text="Список врачей")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Имя', 'Фамилия', 'Специализация', 'Телефон', 'Email', 'Лицензия')
        self.doctors_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.doctors_tree.heading(col, text=col)
            self.doctors_tree.column(col, width=100)
        
        self.doctors_tree.pack(fill='both', expand=True)
        self.doctors_tree.bind('<<TreeviewSelect>>', self.on_doctor_select)
        
        # Загрузка врачей
        self.load_doctors()
    
    def load_doctors(self):
        """Загрузка врачей в дерево"""
        try:
            for item in self.doctors_tree.get_children():
                self.doctors_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT doctor_id, first_name, last_name, specialization, phone, email, license_number 
                FROM doctors ORDER BY last_name, first_name
            """)
            
            for row in result:
                self.doctors_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить врачей: {e}")
    
   
    def add_doctor(self):
        """Добавление нового врача с валидацией"""
        try:
            # Валидация данных
            if not DoctorValidator.validate_doctor_data(
                self.d_first_name.get(),
                self.d_last_name.get(),
                self.d_specialization.get(),
                self.d_phone.get(),
                self.d_email.get(),
                self.d_license.get(),
                self.d_hire_date.get(),
                self.d_salary.get()
            ):
                return
                
            query = """
                INSERT INTO doctors (first_name, last_name, specialization, phone, email, license_number, hire_date, salary)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.d_first_name.get(),
                self.d_last_name.get(),
                self.d_specialization.get(),
                self.d_phone.get(),
                self.d_email.get(),
                self.d_license.get(),
                self.d_hire_date.get(),
                float(self.d_salary.get()) if self.d_salary.get() else 0
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Врач успешно добавлен")
            self.clear_form()
            self.load_doctors()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить врача: {e}")
    
    def update_doctor(self):
        """Обновление выбранного врача с валидацией"""
        selected = self.doctors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите врача для обновления")
            return
        
        try:
            # Валидация данных
            if not DoctorValidator.validate_doctor_data(
                self.d_first_name.get(),
                self.d_last_name.get(),
                self.d_specialization.get(),
                self.d_phone.get(),
                self.d_email.get(),
                self.d_license.get(),
                self.d_hire_date.get(),
                self.d_salary.get()
            ):
                return
                
            doctor_id = self.doctors_tree.item(selected[0])['values'][0]
            query = """
                UPDATE doctors SET first_name=%s, last_name=%s, specialization=%s, phone=%s, 
                email=%s, license_number=%s, hire_date=%s, salary=%s WHERE doctor_id=%s
            """
            params = (
                self.d_first_name.get(),
                self.d_last_name.get(),
                self.d_specialization.get(),
                self.d_phone.get(),
                self.d_email.get(),
                self.d_license.get(),
                self.d_hire_date.get(),
                float(self.d_salary.get()) if self.d_salary.get() else 0,
                doctor_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Врач успешно обновлен")
            self.load_doctors()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить врача: {e}")
    
    def delete_doctor(self):
        """Удаление выбранного врача"""
        selected = self.doctors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите врача для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого врача?"):
            try:
                doctor_id = self.doctors_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM doctors WHERE doctor_id=%s", (doctor_id,))
                messagebox.showinfo("Успех", "Врач успешно удален")
                self.clear_form()
                self.load_doctors()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить врача: {e}")
    
    def on_doctor_select(self, event):
        """Заполнение формы при выборе врача"""
        selected = self.doctors_tree.selection()
        if selected:
            doctor_data = self.doctors_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM doctors WHERE doctor_id=%s", (doctor_data[0],)
            )
            
            if result:
                doctor = result[0]
                self.d_first_name.delete(0, tk.END)
                self.d_first_name.insert(0, doctor[1])
                self.d_last_name.delete(0, tk.END)
                self.d_last_name.insert(0, doctor[2])
                self.d_specialization.set(doctor[3])
                self.d_phone.delete(0, tk.END)
                self.d_phone.insert(0, doctor[4] or '')
                self.d_email.delete(0, tk.END)
                self.d_email.insert(0, doctor[5] or '')
                self.d_license.delete(0, tk.END)
                self.d_license.insert(0, doctor[6] or '')
                self.d_hire_date.delete(0, tk.END)
                self.d_hire_date.insert(0, doctor[7])
                self.d_salary.delete(0, tk.END)
                self.d_salary.insert(0, str(doctor[8]) if doctor[8] else '')
    
    def clear_form(self):
        """Очистка полей формы"""
        self.d_first_name.delete(0, tk.END)
        self.d_last_name.delete(0, tk.END)
        self.d_specialization.set('')
        self.d_phone.delete(0, tk.END)
        self.d_email.delete(0, tk.END)
        self.d_license.delete(0, tk.END)
        self.d_hire_date.delete(0, tk.END)
        self.d_salary.delete(0, tk.END)
