import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
import empirical_functions as ef
import sys

# НАСТРОЙКИ МАСШТАБИРОВАНИЯ - ДОБАВЛЕНО ДЛЯ УВЕЛИЧЕНИЯ ШРИФТА
SCALE_FACTOR = 1.8  # Увеличиваем масштаб на 30%

class EmpiricalApp:
    def __init__(self, root):
        self.root = root
        
        # ПРИМЕНЯЕМ МАСШТАБИРОВАНИЕ - ДОБАВЛЕНО
        self.root.tk.call('tk', 'scaling', SCALE_FACTOR)
        
        self.root.title("Подбор оптимальной эмпирической функции")
#        self.root.geometry("1250x1000")  # Слегка увеличено для лучшего отображения
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Данные по умолчанию (вариант 18)
        self.default_x = [1, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8, 3.1, 3.4, 3.7, 4]
        self.default_y = [1.000, 1.428, 2.090, 2.968, 4.052, 5.334, 6.810, 8.479, 10.336, 12.382, 14.614]
        
        self.current_results = None
        self.create_widgets()
        self.load_default_data()
    
    def create_widgets(self):
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка ввода данных
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="Ввод данных")
        
        # Вкладка результатов
        result_frame = ttk.Frame(notebook)
        notebook.add(result_frame, text="Результаты")
        
        # Вкладка графиков
        plot_frame = ttk.Frame(notebook)
        notebook.add(plot_frame, text="Графики")
        
        # Настройка вкладок
        self.setup_input_tab(input_frame)
        self.setup_result_tab(result_frame)
        self.setup_plot_tab(plot_frame)
    
    def setup_input_tab(self, parent):
        # Заголовок - увеличен шрифт
        title_label = ttk.Label(parent, text="Ввод данных для подбора эмпирической функции", 
                               font=('Arial', 14, 'bold'))  # Увеличено с 12 до 14
        title_label.pack(pady=15)  # Увеличено pady
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=15)  # Увеличено pady
        
        # Кнопки с увеличенными отступами
        ttk.Button(button_frame, text="Загрузить вариант 18", 
                  command=self.load_default_data).pack(side='left', padx=8, pady=5)
        ttk.Button(button_frame, text="Очистить данные", 
                  command=self.clear_data).pack(side='left', padx=8, pady=5)
        ttk.Button(button_frame, text="Добавить строку", 
                  command=self.add_row).pack(side='left', padx=8, pady=5)
        ttk.Button(button_frame, text="Удалить строку", 
                  command=self.delete_row).pack(side='left', padx=8, pady=5)
        ttk.Button(button_frame, text="Выполнить подбор функций", 
                  command=self.calculate_functions).pack(side='left', padx=8, pady=5)
        
        # Создаем стиль для выделенной кнопки
        style = ttk.Style()
        style.configure('Accent.TButton', foreground='white', background='#0078D7')
        
        # Фрейм для таблицы данных
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True, padx=15, pady=15)  # Увеличены отступы
        
        # Создаем таблицу для ввода данных
        self.create_data_table(table_frame)
    
    def create_data_table(self, parent):
        # Создаем Treeview как таблицу
        columns = ('index', 'x', 'y')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)  # Увеличена высота
        
        # Настраиваем заголовки с увеличенным шрифтом
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))  # Увеличиваем шрифт заголовков
        style.configure("Treeview", font=('Arial', 10), rowheight=25)  # Увеличиваем шрифт и высоту строк
        
        self.tree.heading('index', text='№')
        self.tree.heading('x', text='x значение')
        self.tree.heading('y', text='y значение')
        
        # Увеличиваем ширину колонок
        self.tree.column('index', width=70)
        self.tree.column('x', width=200)
        self.tree.column('y', width=200)
        
        # Полосы прокрутки
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Привязываем обработчик двойного клика для редактирования
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def setup_result_tab(self, parent):
        # Заголовок с увеличенным шрифтом
        title_label = ttk.Label(parent, text="Результаты подбора эмпирических функций", 
                               font=('Arial', 14, 'bold'))  # Увеличено с 12 до 14
        title_label.pack(pady=15)  # Увеличено pady
        
        # Фрейм для лучшей модели
        best_model_frame = ttk.LabelFrame(parent, text="НАИЛУЧШАЯ МОДЕЛЬ", padding=15)  # Увеличено padding
        best_model_frame.pack(fill='x', padx=15, pady=10)  # Увеличены отступы
        
        self.best_model_text = scrolledtext.ScrolledText(best_model_frame, height=10,  # Увеличена высота
                                                        wrap=tk.WORD, font=('Courier', 11))  # Увеличено с 9 до 11
        self.best_model_text.pack(fill='both', expand=True)
        
        # Фрейм для всех моделей
        all_models_frame = ttk.LabelFrame(parent, text="ВСЕ МОДЕЛИ (отсортированы по качеству)", padding=15)  # Увеличено padding
        all_models_frame.pack(fill='both', expand=True, padx=15, pady=10)  # Увеличены отступы
        
        self.all_models_text = scrolledtext.ScrolledText(all_models_frame, wrap=tk.WORD, 
                                                        font=('Courier', 11))  # Увеличено с 9 до 11
        self.all_models_text.pack(fill='both', expand=True)
    
    def setup_plot_tab(self, parent):
        # Заголовок с увеличенным шрифтом
        title_label = ttk.Label(parent, text="Графическое представление результатов", 
                               font=('Arial', 14, 'bold'))  # Увеличено с 12 до 14
        title_label.pack(pady=15)  # Увеличено pady
        
        # Фрейм для управления графиком
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', padx=15, pady=10)  # Увеличены отступы
        
        ttk.Label(control_frame, text="Показать на графике:", font=('Arial', 11)).pack(side='left')  # Увеличен шрифт
        
        self.plot_var = tk.StringVar(value="best")
        ttk.Radiobutton(control_frame, text="Только лучшую модель", 
                       variable=self.plot_var, value="best", 
                       command=self.update_plot).pack(side='left', padx=15)  # Увеличено padx
        ttk.Radiobutton(control_frame, text="Все модели", 
                       variable=self.plot_var, value="all", 
                       command=self.update_plot).pack(side='left', padx=15)  # Увеличено padx
        
        # Фрейм для графика
        self.plot_frame = ttk.Frame(parent)
        self.plot_frame.pack(fill='both', expand=True, padx=15, pady=15)  # Увеличены отступы
        
        # Создаем фигуру matplotlib с увеличенным размером
        self.fig, self.ax = plt.subplots(figsize=(10, 7), dpi=80)  # Увеличено с (8,6) до (10,7)
        
        # Увеличиваем шрифты на графике
        plt.rcParams.update({'font.size': 12})  # Увеличиваем базовый размер шрифта
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Начальный текст на графике с увеличенным шрифтом
        self.ax.text(0.5, 0.5, 'График появится после расчета', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=14)  # Увеличено с 12 до 14
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.set_title('Подбор эмпирической функции', fontsize=14)
        self.canvas.draw()
    
    def load_default_data(self):
        """Загружает данные варианта 18 по умолчанию"""
        self.clear_data()
        
        for i, (x_val, y_val) in enumerate(zip(self.default_x, self.default_y)):
            self.tree.insert('', 'end', values=(i+1, x_val, y_val))
    
    def clear_data(self):
        """Очищает таблицу данных"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_row(self):
        """Добавляет новую строку в таблицу"""
        next_index = len(self.tree.get_children()) + 1
        self.tree.insert('', 'end', values=(next_index, 0.0, 0.0))
    
    def delete_row(self):
        """Удаляет выбранную строку из таблицы"""
        selected = self.tree.selection()
        if selected:
            self.tree.delete(selected)
        else:
            messagebox.showwarning("Предупреждение", "Выберите строку для удаления")
    
    def on_double_click(self, event):
        """Обработчик двойного клика для редактирования ячейки"""
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        
        if column == '#2':  # колонка x
            self.edit_cell(item, 'x')
        elif column == '#3':  # колонка y
            self.edit_cell(item, 'y')
    
    def edit_cell(self, item, column_name):
        """Редактирование ячейки"""
        values = self.tree.item(item, 'values')
        col_index = 1 if column_name == 'x' else 2
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование {column_name}")
        edit_window.geometry("350x120")  # Увеличено окно
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Увеличиваем шрифт в окне редактирования
        ttk.Label(edit_window, text=f"Введите новое значение {column_name}:", 
                 font=('Arial', 11)).pack(pady=8)  # Увеличен шрифт и отступы
        
        entry_var = tk.StringVar(value=values[col_index])
        entry = ttk.Entry(edit_window, textvariable=entry_var, width=25, font=('Arial', 11))  # Увеличен шрифт
        entry.pack(pady=8)  # Увеличены отступы
        entry.focus()
        
        def save_value():
            try:
                new_value = float(entry_var.get())
                new_values = list(values)
                new_values[col_index] = new_value
                self.tree.item(item, values=tuple(new_values))
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное числовое значение")
        
        ttk.Button(edit_window, text="Сохранить", command=save_value).pack(pady=8)  # Увеличены отступы
        entry.bind('<Return>', lambda e: save_value())
    
    def get_data_from_table(self):
        """Извлекает данные из таблицы"""
        x_data = []
        y_data = []
        
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            try:
                x_val = float(values[1])
                y_val = float(values[2])
                x_data.append(x_val)
                y_data.append(y_val)
            except ValueError:
                continue
        
        return np.array(x_data), np.array(y_data)
    
    def calculate_functions(self):
        """Выполняет подбор всех эмпирических функций"""
        x, y = self.get_data_from_table()
        
        if len(x) < 2:
            messagebox.showerror("Ошибка", "Недостаточно данных для расчета. Нужно как минимум 2 точки.")
            return
        
        try:
            # Выполняем подбор функций
            self.current_results = ef.fit_models(x, y)
            
            if not self.current_results:
                messagebox.showerror("Ошибка", "Не удалось подобрать ни одну функцию")
                return
            
            # Обновляем текстовые результаты
            self.update_results_text()
            
            # Обновляем график
            self.update_plot()
            
            # Переключаемся на вкладку результатов
            notebook = self.root.winfo_children()[0]
            notebook.select(1)
            
            messagebox.showinfo("Успех", f"Подобрано {len(self.current_results)} функций!\n"
                                      f"Лучшая модель: {self.current_results[0]['name']}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при расчете: {str(e)}")
    
    def update_results_text(self):
        """Обновляет текстовые результаты"""
        best_model = ef.get_best_model(self.current_results)
        
        # Обновляем текст лучшей модели
        self.best_model_text.delete(1.0, tk.END)
        if best_model:
            best_text = "★ ЛУЧШАЯ МОДЕЛЬ ★\n\n"
            best_text += ef.format_model_result(best_model)
            self.best_model_text.insert(1.0, best_text)
        
        # Обновляем текст всех моделей
        self.all_models_text.delete(1.0, tk.END)
        all_text = "Сравнение всех моделей (от лучшей к худшей):\n\n"
        for i, result in enumerate(self.current_results, 1):
            all_text += f"МЕСТО #{i}:\n"
            all_text += ef.format_model_result(result)
        self.all_models_text.insert(1.0, all_text)
    
    def update_plot(self):
        """Обновляет график"""
        if self.current_results is None:
            return
        
        x, y = self.get_data_from_table()
        
        # Очищаем график
        self.ax.clear()
        
        # Увеличиваем шрифты на осях и легенде
        self.ax.tick_params(axis='both', which='major', labelsize=11)
        
        # Отображаем экспериментальные точки
        self.ax.scatter(x, y, color='black', s=60, label='Экспериментальные точки', zorder=5)  # Увеличены точки
        
        # Создаем точки для гладкого графика
        x_plot = np.linspace(min(x) * 0.9, max(x) * 1.1, 200)
        
        if self.plot_var.get() == "best":
            # Только лучшая модель
            best_model = self.current_results[0]
            y_plot = best_model['function'](x_plot, *best_model['parameters'])
            self.ax.plot(x_plot, y_plot, 'red', linewidth=2.5,  # Увеличена толщина линии
                        label=f"{best_model['name']} (R²={best_model['r_squared']:.4f})")
        else:
            # Все модели
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
            for i, result in enumerate(self.current_results):
                if i < len(colors):
                    try:
                        y_plot = result['function'](x_plot, *result['parameters'])
                        self.ax.plot(x_plot, y_plot, color=colors[i], linewidth=2.0,  # Увеличена толщина линии
                                   label=f"{result['name']} (R²={result['r_squared']:.4f})")
                    except:
                        continue
        
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.set_title('Подбор эмпирической функции методом наименьших квадратов', fontsize=13)
        self.ax.legend(fontsize=11)  # Увеличен шрифт легенды
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def on_closing(self):
        """Корректное завершение работы приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            # Закрываем фигуру matplotlib
            plt.close('all')
            # Уничтожаем окно
            self.root.destroy()
            # Принудительно завершаем процесс
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmpiricalApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        plt.close('all')
        root.destroy()
        sys.exit()
