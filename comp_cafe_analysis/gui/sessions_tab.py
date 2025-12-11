import tkinter as tk
from tkinter import ttk, messagebox
from validators import SessionValidator

class SessionsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        # Форма информации о сеансе
        form_frame = ttk.LabelFrame(self.frame, text="Информация о сеансе")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Номер компьютера:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.s_computer = ttk.Entry(form_frame, width=20)
        self.s_computer.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="IP-адрес:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.s_ip = ttk.Entry(form_frame, width=20)
        self.s_ip.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата соединения (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.s_date = ttk.Entry(form_frame, width=20)
        self.s_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Время начала (ЧЧ:ММ):").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.s_start = ttk.Entry(form_frame, width=20)
        self.s_start.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Время окончания (ЧЧ:ММ):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.s_end = ttk.Entry(form_frame, width=20)
        self.s_end.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить сеанс", command=self.add_session).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить сеанс", command=self.update_session).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить сеанс", command=self.delete_session).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список сеансов
        list_frame = ttk.LabelFrame(self.frame, text="Список сеансов")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Компьютер', 'IP-адрес', 'Дата', 'Начало', 'Окончание', 'Длительность (мин)')
        self.sessions_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=100)
        
        self.sessions_tree.pack(fill='both', expand=True)
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_select)
        
        # Загрузка сеансов
        self.load_sessions()
    
    def load_sessions(self):
        """Загрузка сеансов в дерево"""
        try:
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT session_id, computer_number, ip_address, connection_date, 
                       start_time, end_time,
                       EXTRACT(EPOCH FROM (end_time - start_time))/60 as duration_minutes
                FROM sessions 
                ORDER BY connection_date DESC, start_time DESC
            """)
            
            for row in result:
                # Форматируем длительность
                formatted_row = list(row)
                if row[6]:
                    formatted_row[6] = f"{int(row[6])} мин"
                self.sessions_tree.insert('', 'end', values=formatted_row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сеансы: {e}")
    
    def add_session(self):
        """Добавление нового сеанса с валидацией"""
        try:
            # Валидация данных
            if not SessionValidator.validate_session_data(
                self.s_computer.get(),
                self.s_ip.get(),
                self.s_date.get(),
                self.s_start.get(),
                self.s_end.get()
            ):
                return
                
            query = """
                INSERT INTO sessions (computer_number, ip_address, connection_date, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                int(self.s_computer.get()),
                self.s_ip.get(),
                self.s_date.get(),
                self.s_start.get(),
                self.s_end.get()
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Сеанс успешно добавлен")
            self.clear_form()
            self.load_sessions()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить сеанс: {e}")
    
    def update_session(self):
        """Обновление выбранного сеанса с валидацией"""
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите сеанс для обновления")
            return
        
        try:
            # Валидация данных
            if not SessionValidator.validate_session_data(
                self.s_computer.get(),
                self.s_ip.get(),
                self.s_date.get(),
                self.s_start.get(),
                self.s_end.get()
            ):
                return
                
            session_id = self.sessions_tree.item(selected[0])['values'][0]
            query = """
                UPDATE sessions SET computer_number=%s, ip_address=%s, connection_date=%s, 
                start_time=%s, end_time=%s WHERE session_id=%s
            """
            params = (
                int(self.s_computer.get()),
                self.s_ip.get(),
                self.s_date.get(),
                self.s_start.get(),
                self.s_end.get(),
                session_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Сеанс успешно обновлен")
            self.load_sessions()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить сеанс: {e}")
    
    def delete_session(self):
        """Удаление выбранного сеанса"""
        selected = self.sessions_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите сеанс для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот сеанс?"):
            try:
                session_id = self.sessions_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM sessions WHERE session_id=%s", (session_id,))
                messagebox.showinfo("Успех", "Сеанс успешно удален")
                self.clear_form()
                self.load_sessions()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить сеанс: {e}")
    
    def on_session_select(self, event):
        """Заполнение формы при выборе сеанса"""
        selected = self.sessions_tree.selection()
        if selected:
            session_data = self.sessions_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM sessions WHERE session_id=%s", (session_data[0],)
            )
            
            if result:
                session = result[0]
                self.s_computer.delete(0, tk.END)
                self.s_computer.insert(0, session[1])
                self.s_ip.delete(0, tk.END)
                self.s_ip.insert(0, session[2])
                self.s_date.delete(0, tk.END)
                self.s_date.insert(0, session[3])
                self.s_start.delete(0, tk.END)
                self.s_start.insert(0, session[4].strftime('%H:%M') if session[4] else '')
                self.s_end.delete(0, tk.END)
                self.s_end.insert(0, session[5].strftime('%H:%M') if session[5] else '')
    
    def clear_form(self):
        """Очистка полей формы"""
        self.s_computer.delete(0, tk.END)
        self.s_ip.delete(0, tk.END)
        self.s_date.delete(0, tk.END)
        self.s_start.delete(0, tk.END)
        self.s_end.delete(0, tk.END)
