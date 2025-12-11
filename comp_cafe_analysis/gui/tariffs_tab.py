import tkinter as tk
from tkinter import ttk, messagebox
from validators import TariffValidator

class TariffsTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        # Форма информации о тарифе
        form_frame = ttk.LabelFrame(self.frame, text="Информация о тарифе")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата действия (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.t_date = ttk.Entry(form_frame, width=20)
        self.t_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Стоимость минуты (руб):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.t_cost = ttk.Entry(form_frame, width=20)
        self.t_cost.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Льготная стоимость 20:00-02:00 (руб):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.t_evening = ttk.Entry(form_frame, width=20)
        self.t_evening.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Льготная стоимость 02:00-06:00 (руб):").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.t_night = ttk.Entry(form_frame, width=20)
        self.t_night.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Добавить тариф", command=self.add_tariff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить тариф", command=self.update_tariff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить тариф", command=self.delete_tariff).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side='left', padx=5)
        
        # Список тарифов
        list_frame = ttk.LabelFrame(self.frame, text="Список тарифов")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Дата действия', 'Стоимость минуты', 'Льгота 20:00-02:00', 'Льгота 02:00-06:00')
        self.tariffs_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tariffs_tree.heading(col, text=col)
            self.tariffs_tree.column(col, width=120)
        
        self.tariffs_tree.pack(fill='both', expand=True)
        self.tariffs_tree.bind('<<TreeviewSelect>>', self.on_tariff_select)
        
        # Загрузка тарифов
        self.load_tariffs()
    
    def load_tariffs(self):
        """Загрузка тарифов в дерево"""
        try:
            for item in self.tariffs_tree.get_children():
                self.tariffs_tree.delete(item)
            
            result, columns = self.db.execute_query("""
                SELECT tariff_id, effective_date, cost_per_minute, discount_evening, discount_night
                FROM tariffs 
                ORDER BY effective_date DESC
            """)
            
            for row in result:
                self.tariffs_tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить тарифы: {e}")
    
    def add_tariff(self):
        """Добавление нового тарифа с валидацией"""
        try:
            # Валидация данных
            if not TariffValidator.validate_tariff_data(
                self.t_date.get(),
                self.t_cost.get(),
                self.t_evening.get(),
                self.t_night.get()
            ):
                return
                
            query = """
                INSERT INTO tariffs (effective_date, cost_per_minute, discount_evening, discount_night)
                VALUES (%s, %s, %s, %s)
            """
            params = (
                self.t_date.get(),
                float(self.t_cost.get()),
                float(self.t_evening.get()),
                float(self.t_night.get())
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Тариф успешно добавлен")
            self.clear_form()
            self.load_tariffs()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить тариф: {e}")
    
    def update_tariff(self):
        """Обновление выбранного тарифа с валидацией"""
        selected = self.tariffs_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите тариф для обновления")
            return
        
        try:
            # Валидация данных
            if not TariffValidator.validate_tariff_data(
                self.t_date.get(),
                self.t_cost.get(),
                self.t_evening.get(),
                self.t_night.get()
            ):
                return
                
            tariff_id = self.tariffs_tree.item(selected[0])['values'][0]
            query = """
                UPDATE tariffs SET effective_date=%s, cost_per_minute=%s, 
                discount_evening=%s, discount_night=%s WHERE tariff_id=%s
            """
            params = (
                self.t_date.get(),
                float(self.t_cost.get()),
                float(self.t_evening.get()),
                float(self.t_night.get()),
                tariff_id
            )
            
            self.db.execute_query(query, params)
            messagebox.showinfo("Успех", "Тариф успешно обновлен")
            self.load_tariffs()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить тариф: {e}")
    
    def delete_tariff(self):
        """Удаление выбранного тарифа"""
        selected = self.tariffs_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите тариф для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот тариф?"):
            try:
                tariff_id = self.tariffs_tree.item(selected[0])['values'][0]
                self.db.execute_query("DELETE FROM tariffs WHERE tariff_id=%s", (tariff_id,))
                messagebox.showinfo("Успех", "Тариф успешно удален")
                self.clear_form()
                self.load_tariffs()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить тариф: {e}")
    
    def on_tariff_select(self, event):
        """Заполнение формы при выборе тарифа"""
        selected = self.tariffs_tree.selection()
        if selected:
            tariff_data = self.tariffs_tree.item(selected[0])['values']
            
            result, columns = self.db.execute_query(
                "SELECT * FROM tariffs WHERE tariff_id=%s", (tariff_data[0],)
            )
            
            if result:
                tariff = result[0]
                self.t_date.delete(0, tk.END)
                self.t_date.insert(0, tariff[1])
                self.t_cost.delete(0, tk.END)
                self.t_cost.insert(0, str(tariff[2]))
                self.t_evening.delete(0, tk.END)
                self.t_evening.insert(0, str(tariff[3]))
                self.t_night.delete(0, tk.END)
                self.t_night.insert(0, str(tariff[4]))
    
    def clear_form(self):
        """Очистка полей формы"""
        self.t_date.delete(0, tk.END)
        self.t_cost.delete(0, tk.END)
        self.t_evening.delete(0, tk.END)
        self.t_night.delete(0, tk.END)
