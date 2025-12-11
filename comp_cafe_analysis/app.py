import tkinter as tk
from tkinter import ttk
import sys
import os
import signal
from database import InternetCafeDatabase
from gui.sessions_tab import SessionsTab
from gui.tariffs_tab import TariffsTab
from gui.receipts_tab import ReceiptsTab
from gui.analysis_tab import AnalysisTab

class InternetCafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления интернет-кафе")
        self.root.geometry("1400x800")
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Увеличиваем масштаб приложения
        self.setup_styles()
        
        # Инициализация базы данных
        self.db = InternetCafeDatabase()
        
        self.setup_ui()

    def setup_styles(self):
        """Настройка стилей для увеличения масштаба"""
        style = ttk.Style()
        
        # Увеличиваем размер шрифта для всех элементов
        style.configure('.', font=('Arial', 11))
        
        # Увеличиваем размер шрифта для Treeview
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))
        
        # Увеличиваем размер шрифта для кнопок
        style.configure('TButton', font=('Arial', 11))
        
        # Увеличиваем размер шрифта для Label
        style.configure('TLabel', font=('Arial', 11))
        
        # Увеличиваем размер шрифта для Entry
        style.configure('TEntry', font=('Arial', 11))
        
        # Увеличиваем размер шрифта для Combobox
        style.configure('TCombobox', font=('Arial', 11))
        
        # Увеличиваем размер шрифта для LabelFrame
        style.configure('TLabelframe', font=('Arial', 12, 'bold'))
        style.configure('TLabelframe.Label', font=('Arial', 12, 'bold'))
        
        # Увеличиваем размер шрифта для Notebook
        style.configure('TNotebook', font=('Arial', 11))
        style.configure('TNotebook.Tab', font=('Arial', 11, 'bold'), padding=[15, 5])

    def setup_ui(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка сеансов
        self.sessions_tab = SessionsTab(notebook, self.db)
        notebook.add(self.sessions_tab.frame, text="Сеансы")
        
        # Вкладка тарифов
        self.tariffs_tab = TariffsTab(notebook, self.db)
        notebook.add(self.tariffs_tab.frame, text="Тарифы")
        
        # Вкладка квитанций
        self.receipts_tab = ReceiptsTab(notebook, self.db)
        notebook.add(self.receipts_tab.frame, text="Квитанции")

        # Вкладка анализа эффективности
        self.analysis_tab = AnalysisTab(notebook, self.db)
        notebook.add(self.analysis_tab.frame, text="Анализ эффективности")

    def on_closing(self):
        """Обработчик закрытия приложения"""
        print("Завершение работы приложения...")
        
        try:
            # Закрываем соединение с базой данных
            if hasattr(self, 'db') and self.db:
                self.db.close()
                print("Соединение с базой данных закрыто")
        except Exception as e:
            print(f"Ошибка при закрытии соединения: {e}")
        
        # Принудительно завершаем процесс
        self.root.quit()
        self.root.destroy()
        
        # Завершаем процесс Python
        os._exit(0)

def main():
    # Устанавливаем обработчик сигналов для корректного завершения
    def signal_handler(signum, frame):
        print("Получен сигнал завершения...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    root = tk.Tk()
    app = InternetCafeApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Приложение прервано пользователем")
    finally:
        print("Приложение завершено")

if __name__ == "__main__":
    main()
