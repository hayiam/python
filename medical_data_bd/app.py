import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import MedicalDatabase
from reports import PDFReportGenerator
from gui.patients_tab import PatientsTab
from gui.doctors_tab import DoctorsTab
from gui.appointments_tab import AppointmentsTab
from gui.records_tab import RecordsTab
from gui.reports_tab import ReportsTab
import os

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления медицинской организацией")
        self.root.geometry("1200x700")
        
        # Инициализация базы данных и генератора PDF
        self.db = MedicalDatabase()
        self.pdf_generator = PDFReportGenerator()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка пациентов
        self.patients_tab = PatientsTab(notebook, self.db)
        notebook.add(self.patients_tab.frame, text="Пациенты")
        
        # Вкладка врачей
        self.doctors_tab = DoctorsTab(notebook, self.db)
        notebook.add(self.doctors_tab.frame, text="Врачи")
        
        # Вкладка назначений
        self.appointments_tab = AppointmentsTab(notebook, self.db)
        notebook.add(self.appointments_tab.frame, text="Назначения")
        
        # Вкладка медицинских записей
        self.records_tab = RecordsTab(notebook, self.db)
        notebook.add(self.records_tab.frame, text="Медкарты")
        
        # Вкладка отчетов
        self.reports_tab = ReportsTab(notebook, self.db, self.pdf_generator)
        notebook.add(self.reports_tab.frame, text="Отчеты")

def main():
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
