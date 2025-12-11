import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time, timedelta
from validators import ReceiptValidator

class ReceiptsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
        self.load_sessions_combobox()
    
    def setup_ui(self):
        # Форма информации о квитанции
        form_frame = ttk.LabelFrame(self.frame, text="Информация о квитанции")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Организация
        ttk.Label(form_frame, text="Название организации:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.r_org = ttk.Entry(form_frame, width=30)
        self.r_org.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Адрес:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.r_address = tk.Text(form_frame, width=50, height=2)
        self.r_address.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.r_phone = ttk.Entry(form_frame, width=20)
        self.r_phone.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата квитанции (ГГГГ-ММ-ДД):").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.r_date = ttk.Entry(form_frame, width=20)
        self.r_date.grid(row=2, column=3, padx=5, pady=5)
        
        # Оператор
        ttk.Label(form_frame, text="ФИО оператора:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.r_operator = ttk.Entry(form_frame, width=20)
        self.r_operator.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Номер смены:").grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.r_shift = ttk.Entry(form_frame, width=20)
        self.r_shift.grid(row=3, column=3, padx=5, pady=5)
        
        # Выбор сеансов
        ttk.Label(form_frame, text="Выберите сеансы:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.r_sessions = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, width=50, height=6)
        self.r_sessions.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky='we')
        
        # Информация о стоимости
        ttk.Label(form_frame, text="Общее количество минут:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.r_total_minutes = ttk.Label(form_frame, text="0", background="white")
        self.r_total_minutes.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(form_frame, text="Общая сумма (руб):").grid(row=5, column=2, padx=5, pady=5, sticky='w')
        self.r_total_amount = ttk.Label(form_frame, text="0.00", background="white")
        self.r_total_amount.grid(row=5, column=3, padx=5, pady=5, sticky='w')
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Рассчитать стоимость", command=self.calculate_cost).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Создать квитанцию", command=self.create_receipt).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить квитанцию", command=self.delete_receipt).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список квитанций
        list_frame = ttk.LabelFrame(self.frame, text="Список квитанций")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Организация', 'Дата', 'Минуты', 'Сумма', 'Оператор', 'Смена')
        self.receipts_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.receipts_tree.heading(col, text=col)
            self.receipts_tree.column(col, width=100)
        
        self.receipts_tree.pack(fill='both', expand=True)
        self.receipts_tree.bind('<<TreeviewSelect>>', self.on_receipt_select)
        
        # Загрузка квитанций
        self.load_receipts()
    
    def load_sessions_combobox(self):
        """Загрузка сеансов в список"""
        try:
            self.r_sessions.delete(0, tk.END)
            
            result, columns = self.db.execute_query("""
                SELECT s.session_id, s.computer_number, s.connection_date, s.start_time, s.end_time
                FROM sessions s
                LEFT JOIN receipt_sessions rs ON s.session_id = rs.session_id
                WHERE rs.session_id IS NULL
                ORDER BY s.connection_date DESC, s.start_time DESC
            """)
            
            for row in result:
                session_text = f"Компьютер {row[1]} | {row[2]} | {row[3].strftime('%H:%M')}-{row[4].strftime('%H:%M')} (ID: {row[0]})"
                self.r_sessions.insert(tk.END, session_text)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сеансы: {e}")
    
    def load_receipts(self):
        """Загрузка квитанций в дерево"""
        try:
            for item in self.receipts_tree.get_children():
                self.receipts_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT receipt_id, organization_name, receipt_date, total_minutes, total_amount, operator_name, shift_number
                FROM receipts 
                ORDER BY receipt_date DESC
            """)
            
            for row in result:
                self.receipts_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить квитанции: {e}")
    
    def calculate_session_cost(self, session_id, connection_date, start_time, end_time):
        """Расчет стоимости сеанса на основе тарифов"""
        try:
            # Находим действующий тариф на дату сеанса
            result, columns = self.db.execute_query("""
                SELECT cost_per_minute, discount_evening, discount_night
                FROM tariffs 
                WHERE effective_date <= %s
                ORDER BY effective_date DESC 
                LIMIT 1
            """, (connection_date,))
            
            if not result:
                messagebox.showerror("Ошибка", f"Не найден тариф для даты {connection_date}")
                return 0, 0
            
            tariff = result[0]
            cost_per_minute = tariff[0]
            discount_evening = tariff[1]
            discount_night = tariff[2]
            
            # Расчет продолжительности в минутах
            start_dt = datetime.combine(connection_date, start_time)
            end_dt = datetime.combine(connection_date, end_time)
            
            # Если время окончания раньше времени начала, значит сеанс перешел на следующий день
            if end_time < start_time:
                end_dt = datetime.combine(connection_date + timedelta(days=1), end_time)
            
            total_minutes = int((end_dt - start_dt).total_seconds() / 60)
            
            # Расчет стоимости по периодам
            total_cost = 0
            current_dt = start_dt
            
            for minute in range(total_minutes):
                hour = current_dt.time().hour
                
                # Определяем тарифный период
                if 6 <= hour < 20:
                    rate = cost_per_minute
                elif 20 <= hour < 24 or 0 <= hour < 2:
                    rate = discount_evening
                else:  # 2 <= hour < 6
                    rate = discount_night
                
                total_cost += rate
                current_dt = current_dt + timedelta(minutes=1)
            
            return total_minutes, round(total_cost, 2)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета стоимости: {e}")
            return 0, 0
    
    def calculate_cost(self):
        """Расчет общей стоимости выбранных сеансов"""
        try:
            selected_indices = self.r_sessions.curselection()
            if not selected_indices:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы один сеанс")
                return
            
            total_minutes = 0
            total_cost = 0
            
            for index in selected_indices:
                session_text = self.r_sessions.get(index)
                session_id = int(session_text.split('(ID: ')[1].rstrip(')'))
                
                # Получаем данные сеанса
                result, columns = self.db.execute_query(
                    "SELECT connection_date, start_time, end_time FROM sessions WHERE session_id=%s",
                    (session_id,)
                )
                
                if result:
                    session_data = result[0]
                    minutes, cost = self.calculate_session_cost(
                        session_id, session_data[0], session_data[1], session_data[2]
                    )
                    total_minutes += minutes
                    total_cost += cost
            
            self.r_total_minutes.config(text=str(total_minutes))
            self.r_total_amount.config(text=f"{total_cost:.2f}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {e}")
    
    def create_receipt(self):
        """Создание квитанции"""
        try:
            # Валидация данных
            if not ReceiptValidator.validate_receipt_data(
                self.r_org.get(),
                self.r_address.get("1.0", tk.END).strip(),
                self.r_phone.get(),
                self.r_date.get(),
                self.r_operator.get(),
                self.r_shift.get()
            ):
                return
            
            selected_indices = self.r_sessions.curselection()
            if not selected_indices:
                messagebox.showwarning("Предупреждение", "Выберите хотя бы один сеанс")
                return
            
            total_minutes = int(self.r_total_minutes.cget("text"))
            total_cost = float(self.r_total_amount.cget("text"))
            
            if total_minutes == 0:
                messagebox.showwarning("Предупреждение", "Нет данных для создания квитанции")
                return
            
            # Создаем квитанцию
            query = """
                INSERT INTO receipts (organization_name, address, phone, receipt_date, 
                total_minutes, total_amount, operator_name, shift_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING receipt_id
            """
            params = (
                self.r_org.get(),
                self.r_address.get("1.0", tk.END).strip(),
                self.r_phone.get(),
                self.r_date.get(),
                total_minutes,
                total_cost,
                self.r_operator.get(),
                int(self.r_shift.get())
            )
            
            result = self.db.execute_query(query, params)
            if result:
                # Получаем ID созданной квитанции
                receipt_id_result, _ = self.db.execute_query("SELECT lastval()")
                receipt_id = receipt_id_result[0][0] if receipt_id_result else None
                
                if receipt_id:
                    # Добавляем связи с сеансами
                    for index in selected_indices:
                        session_text = self.r_sessions.get(index)
                        session_id = int(session_text.split('(ID: ')[1].rstrip(')'))
                        
                        # Получаем данные сеанса для расчета стоимости
                        session_result, _ = self.db.execute_query(
                            "SELECT connection_date, start_time, end_time FROM sessions WHERE session_id=%s",
                            (session_id,)
                        )
                        
                        if session_result:
                            session_data = session_result[0]
                            minutes, cost = self.calculate_session_cost(
                                session_id, session_data[0], session_data[1], session_data[2]
                            )
                            
                            # Создаем связь
                            link_query = """
                                INSERT INTO receipt_sessions (receipt_id, session_id, session_minutes, session_cost)
                                VALUES (%s, %s, %s, %s)
                            """
                            self.db.execute_query(link_query, (receipt_id, session_id, minutes, cost))
            
            messagebox.showinfo("Успех", "Квитанция успешно создана")
            self.clear_form()
            self.load_receipts()
            self.load_sessions_combobox()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать квитанцию: {e}")
    
    def delete_receipt(self):
        """Удаление выбранной квитанции"""
        selected = self.receipts_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите квитанцию для удаления")
            return
        
        receipt_data = self.receipts_tree.item(selected[0])['values']
        receipt_id = receipt_data[0]
        organization = receipt_data[1]
        receipt_date = receipt_data[2]
        
        if messagebox.askyesno("Подтверждение удаления", 
                              f"Вы уверены, что хотите удалить квитанцию?\n"
                              f"Организация: {organization}\n"
                              f"Дата: {receipt_date}"):
            try:
                # Удаляем квитанцию (связи удалятся каскадно благодаря ON DELETE CASCADE)
                self.db.execute_query("DELETE FROM receipts WHERE receipt_id=%s", (receipt_id,))
                messagebox.showinfo("Успех", "Квитанция успешно удалена")
                self.clear_form()
                self.load_receipts()
                self.load_sessions_combobox()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить квитанцию: {e}")
    
    def on_receipt_select(self, event):
        """Заполнение формы при выборе квитанции"""
        selected = self.receipts_tree.selection()
        if selected:
            receipt_data = self.receipts_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM receipts WHERE receipt_id=%s", (receipt_data[0],)
            )
            
            if result:
                receipt = result[0]
                self.r_org.delete(0, tk.END)
                self.r_org.insert(0, receipt[1])
                self.r_address.delete("1.0", tk.END)
                self.r_address.insert("1.0", receipt[2] or '')
                self.r_phone.delete(0, tk.END)
                self.r_phone.insert(0, receipt[3] or '')
                self.r_date.delete(0, tk.END)
                self.r_date.insert(0, receipt[4])
                self.r_operator.delete(0, tk.END)
                self.r_operator.insert(0, receipt[7] or '')
                self.r_shift.delete(0, tk.END)
                self.r_shift.insert(0, str(receipt[8]) if receipt[8] else '')
                
                # Загружаем связанные сеансы
                self.load_receipt_sessions(receipt_data[0])
    
    def load_receipt_sessions(self, receipt_id):
        """Загрузка сеансов для выбранной квитанции"""
        try:
            result, columns = self.db.execute_query("""
                SELECT s.session_id, s.computer_number, s.connection_date, s.start_time, s.end_time,
                       rs.session_minutes, rs.session_cost
                FROM receipt_sessions rs
                JOIN sessions s ON rs.session_id = s.session_id
                WHERE rs.receipt_id = %s
            """, (receipt_id,))
            
            total_minutes = 0
            total_cost = 0
            
            for row in result:
                total_minutes += row[5]
                total_cost += row[6]
            
            self.r_total_minutes.config(text=str(total_minutes))
            self.r_total_amount.config(text=f"{total_cost:.2f}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сеансы квитанции: {e}")
    
    def clear_form(self):
        """Очистка полей формы"""
        self.r_org.delete(0, tk.END)
        self.r_address.delete("1.0", tk.END)
        self.r_phone.delete(0, tk.END)
        self.r_date.delete(0, tk.END)
        self.r_operator.delete(0, tk.END)
        self.r_shift.delete(0, tk.END)
        self.r_total_minutes.config(text="0")
        self.r_total_amount.config(text="0.00")
        self.r_sessions.selection_clear(0, tk.END)
