import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np
from datetime import date

class AnalysisTab:
    def __init__(self, notebook, db):
        self.db = db
        self.frame = ttk.Frame(notebook)
        self.setup_ui()
    
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Правая панель - визуализация
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Информация о критерии Гурвица
        info_frame = ttk.LabelFrame(left_frame, text="Критерий Гурвица")
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_text = tk.Text(info_frame, width=35, height=8, wrap=tk.WORD, font=('Arial', 9))
        info_text.pack(padx=5, pady=5, fill='both')
        info_text.insert(tk.END, 
            "Критерий Гурвица - компромисс между крайним оптимизмом и пессимизмом.\n\n"
            "Формула:\n"
            "H = α × max(доход) + (1-α) × min(доход)\n\n"
            "где:\n"
            "• α - коэффициент оптимизма (0-1)\n"
            "• max(доход) - максимальный доход\n"
            "• min(доход) - минимальный доход\n\n"
            "α=1: максимакс (оптимист)\n"
            "α=0: минимакс (пессимист)")
        info_text.config(state=tk.DISABLED)
        
        # Параметры анализа
        params_frame = ttk.LabelFrame(left_frame, text="Параметры анализа")
        params_frame.pack(fill='x', pady=(0, 10))
        
        # Период анализа
        ttk.Label(params_frame, text="Период анализа:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.period_var = tk.StringVar(value="365")
        period_combo = ttk.Combobox(params_frame, textvariable=self.period_var, width=15, state="readonly")
        period_combo['values'] = ('365 дней (1 год)', '730 дней (2 года)', '1095 дней (3 года)')
        period_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Коэффициент оптимизма
        ttk.Label(params_frame, text="Коэффициент оптимизма (α):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.alpha_var = tk.DoubleVar(value=0.5)
        alpha_scale = ttk.Scale(params_frame, from_=0, to=1, variable=self.alpha_var, 
                               orient='horizontal', length=150)
        alpha_scale.grid(row=1, column=1, padx=5, pady=5, sticky='we')
        
        self.alpha_label = ttk.Label(params_frame, text="0.50")
        self.alpha_label.grid(row=2, column=1, padx=5, pady=2)
        
        # Привязываем обновление метки к изменению слайдера
        alpha_scale.configure(command=self.update_alpha_label)
        
        # Кнопки управления
        button_frame = ttk.Frame(params_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Рассчитать", command=self.calculate_analysis).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить график", command=self.update_plot).pack(side='left', padx=5)
        
        # Результаты анализа
        results_frame = ttk.LabelFrame(left_frame, text="Результаты анализа")
        results_frame.pack(fill='x')
        
        # Показатели эффективности
        ttk.Label(results_frame, text="Максимальный доход:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.max_income_label = ttk.Label(results_frame, text="0.00 руб", foreground="green")
        self.max_income_label.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Минимальный доход:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.min_income_label = ttk.Label(results_frame, text="0.00 руб", foreground="red")
        self.min_income_label.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Средний доход:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.avg_income_label = ttk.Label(results_frame, text="0.00 руб")
        self.avg_income_label.grid(row=2, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Критерий Гурвица:").grid(row=3, column=0, padx=5, pady=2, sticky='w')
        self.hurwicz_label = ttk.Label(results_frame, text="0.00 руб", font=('Arial', 10, 'bold'))
        self.hurwicz_label.grid(row=3, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Всего дней:").grid(row=4, column=0, padx=5, pady=2, sticky='w')
        self.days_count_label = ttk.Label(results_frame, text="0")
        self.days_count_label.grid(row=4, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Период данных:").grid(row=5, column=0, padx=5, pady=2, sticky='w')
        self.data_period_label = ttk.Label(results_frame, text="-", wraplength=200)
        self.data_period_label.grid(row=5, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(results_frame, text="Рекомендация:").grid(row=6, column=0, padx=5, pady=2, sticky='w')
        self.recommendation_label = ttk.Label(results_frame, text="-", wraplength=200)
        self.recommendation_label.grid(row=6, column=1, padx=5, pady=2, sticky='w')
        
        # Область для графика
        self.setup_plot_area(right_frame)
        
        # Первоначальный расчет
        self.calculate_analysis()
    
    def setup_plot_area(self, parent):
        """Настройка области для графиков"""
        plot_frame = ttk.LabelFrame(parent, text="Анализ эффективности интернет-кафе")
        plot_frame.pack(fill='both', expand=True)
        
        # Создаем фигуру matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.fig.tight_layout(pad=3.0)
        
        # Встраиваем график в Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def update_alpha_label(self, event=None):
        """Обновление метки коэффициента оптимизма"""
        self.alpha_label.config(text=f"{self.alpha_var.get():.2f}")
    
    def get_period_days(self):
        """Получение количества дней из выбранного периода"""
        period_map = {
            '365 дней (1 год)': 365,
            '730 дней (2 года)': 730,
            '1095 дней (3 года)': 1095
        }
        return period_map.get(self.period_var.get(), 365)
    
    def get_income_data(self, period_days):
        """Получение данных о доходах за указанный период"""
        try:
            # Используем реальные данные из базы
            end_date = date(2025, 11, 30)  # Последняя дата в демо-данных
            start_date = end_date - timedelta(days=period_days)
            
            # Получаем данные о доходах по дням
            query = """
                SELECT receipt_date, SUM(total_amount) as daily_income
                FROM receipts 
                WHERE receipt_date BETWEEN %s AND %s
                GROUP BY receipt_date 
                ORDER BY receipt_date
            """
            result, columns = self.db.execute_query(query, (start_date, end_date))
            
            if not result:
                return [], []
            
            dates = [row[0] for row in result]
            incomes = [float(row[1]) for row in result]
            
            return dates, incomes
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return [], []
    
    def calculate_hurwicz(self, incomes, alpha):
        """Расчет критерия Гурвица"""
        if not incomes:
            return 0, 0, 0, 0
        
        max_income = max(incomes)
        min_income = min(incomes)
        avg_income = sum(incomes) / len(incomes)
        hurwicz_value = alpha * max_income + (1 - alpha) * min_income
        
        return max_income, min_income, avg_income, hurwicz_value
    
    def get_recommendation(self, hurwicz_value, avg_income, alpha, days_count):
        """Получение рекомендации на основе анализа"""
        if days_count == 0:
            return "Недостаточно данных для анализа"
            
        if hurwicz_value > avg_income * 1.2:
            if alpha > 0.7:
                return "Отличные результаты! Оптимистичный подход оправдан. Рекомендуется расширение."
            else:
                return "Стабильно высокие доходы. Можно увеличить инвестиции в развитие."
        elif hurwicz_value > avg_income:
            if alpha > 0.7:
                return "Хорошие перспективы. Оптимистичная стратегия может принести результаты."
            else:
                return "Стабильные показатели. Рекомендуется осторожное развитие."
        else:
            if alpha < 0.3:
                return "Консервативная стратегия. Рассмотрите более оптимистичные сценарии для роста."
            else:
                return "Требуется оптимизация процессов. Проанализируйте причины низкой эффективности."
    
    def calculate_analysis(self):
        """Основной расчет анализа"""
        try:
            period_days = self.get_period_days()
            alpha = self.alpha_var.get()
            
            # Получаем данные о доходах
            dates, incomes = self.get_income_data(period_days)
            
            if not incomes:
                # Сбрасываем показатели если нет данных
                self.max_income_label.config(text="0.00 руб")
                self.min_income_label.config(text="0.00 руб")
                self.avg_income_label.config(text="0.00 руб")
                self.hurwicz_label.config(text="0.00 руб")
                self.days_count_label.config(text="0")
                self.data_period_label.config(text="Нет данных")
                self.recommendation_label.config(text="Недостаточно данных для анализа")
                return
            
            # Рассчитываем критерий Гурвица
            max_income, min_income, avg_income, hurwicz_value = self.calculate_hurwicz(incomes, alpha)
            
            # Определяем период данных
            data_start = min(dates).strftime('%d.%m.%Y')
            data_end = max(dates).strftime('%d.%m.%Y')
            data_period = f"{data_start} - {data_end}"
            
            # Обновляем интерфейс
            self.max_income_label.config(text=f"{max_income:.2f} руб")
            self.min_income_label.config(text=f"{min_income:.2f} руб")
            self.avg_income_label.config(text=f"{avg_income:.2f} руб")
            self.hurwicz_label.config(text=f"{hurwicz_value:.2f} руб")
            self.days_count_label.config(text=str(len(incomes)))
            self.data_period_label.config(text=data_period)
            
            # Получаем рекомендацию
            recommendation = self.get_recommendation(hurwicz_value, avg_income, alpha, len(incomes))
            self.recommendation_label.config(text=recommendation)
            
            # Обновляем графики
            self.update_plots(dates, incomes, hurwicz_value, avg_income)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете анализа: {e}")
    
    def update_plots(self, dates, incomes, hurwicz_value, avg_income):
        """Обновление графиков"""
        try:
            # Очищаем графики
            self.ax1.clear()
            self.ax2.clear()
            
            alpha = self.alpha_var.get()
            
            # График 1: Динамика доходов
            self.ax1.plot(dates, incomes, 'b-', linewidth=1, label='Доходы', alpha=0.7, marker='o', markersize=2)
            self.ax1.axhline(y=avg_income, color='r', linestyle='--', label=f'Средний: {avg_income:.2f} руб')
            self.ax1.axhline(y=hurwicz_value, color='g', linestyle='--', 
                           label=f'Гурвиц (α={alpha:.2f}): {hurwicz_value:.2f} руб')
            
            self.ax1.set_title('Динамика ежедневных доходов интернет-кафе')
            self.ax1.set_ylabel('Доход, руб')
            self.ax1.legend()
            self.ax1.grid(True, alpha=0.3)
            self.ax1.tick_params(axis='x', rotation=45)
            
            # График 2: Сравнение критериев
            criteria_names = ['Максимальный', 'Минимальный', 'Средний', 'Гурвица']
            criteria_values = [max(incomes), min(incomes), avg_income, hurwicz_value]
            colors = ['green', 'red', 'blue', 'orange']
            
            bars = self.ax2.bar(criteria_names, criteria_values, color=colors, alpha=0.7)
            self.ax2.set_title('Сравнение критериев эффективности')
            self.ax2.set_ylabel('Доход, руб')
            self.ax2.grid(True, alpha=0.3)
            
            # Добавляем подписи значений на столбцах
            for bar, value in zip(bars, criteria_values):
                height = bar.get_height()
                self.ax2.text(bar.get_x() + bar.get_width()/2., height + max(criteria_values)*0.01,
                            f'{value:.2f}', ha='center', va='bottom', fontsize=9)
            
            # Автоматическое размещение подписей
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении графиков: {e}")
    
    def update_plot(self):
        """Обновление только графиков без пересчета данных"""
        try:
            period_days = self.get_period_days()
            dates, incomes = self.get_income_data(period_days)
            
            if incomes:
                alpha = self.alpha_var.get()
                max_income, min_income, avg_income, hurwicz_value = self.calculate_hurwicz(incomes, alpha)
                self.update_plots(dates, incomes, hurwicz_value, avg_income)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении графиков: {e}")
