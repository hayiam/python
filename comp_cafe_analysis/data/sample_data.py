from datetime import date, time, timedelta
import random

class SampleData:
    def __init__(self):
        # Генерируем расширенные данные для анализа за 2023-2025 годы
        self.sessions = self.generate_sessions()
        self.tariffs = self.generate_tariffs()
        self.receipts = self.generate_receipts()
    
    def generate_tariffs(self):
        """Генерация тарифов за весь период"""
        return [
            (date(2023, 1, 1), 2.30, 1.60, 1.00),
            (date(2023, 6, 1), 2.40, 1.70, 1.10),
            (date(2024, 1, 1), 2.50, 1.80, 1.20),
            (date(2024, 2, 2), 2.70, 2.00, 1.40),
            (date(2024, 3, 1), 2.90, 2.20, 1.60),
            (date(2024, 9, 1), 3.10, 2.40, 1.80),
            (date(2025, 1, 1), 3.30, 2.60, 2.00),
            (date(2025, 6, 1), 3.50, 2.80, 2.20)
        ]
    
    def generate_sessions(self):
        """Генерация сеансов за 2023-2025 годы"""
        sessions = []
        
        # Компьютеры в кафе
        computers = [1, 2, 3, 4, 5, 6, 7, 8]
        ip_base = "192.168.1.10"
        
        # Генерируем сеансы с 2023 по ноябрь 2025
        start_date = date(2023, 1, 1)
        end_date = date(2025, 11, 30)
        current_date = start_date
        
        while current_date <= end_date:
            # Количество сеансов зависит от дня недели и сезона
            if current_date.weekday() >= 5:  # Выходные
                daily_sessions = random.randint(25, 35)
            else:  # Будни
                daily_sessions = random.randint(15, 25)
            
            # Летом и зимой больше посетителей
            if current_date.month in [6, 7, 8, 12, 1]:
                daily_sessions = int(daily_sessions * 1.3)
            
            for _ in range(daily_sessions):
                computer = random.choice(computers)
                ip_address = f"{ip_base}{computer}"
                
                # Время начала между 8:00 и 23:00
                start_hour = random.randint(8, 23)
                start_minute = random.choice([0, 15, 30, 45])
                start_time_obj = time(start_hour, start_minute)
                
                # Длительность от 30 минут до 4 часов
                duration_minutes = random.choice([30, 45, 60, 90, 120, 180, 240])
                end_time_obj = self.add_minutes_to_time(start_time_obj, duration_minutes)
                
                sessions.append((
                    computer,
                    ip_address,
                    current_date,
                    start_time_obj,
                    end_time_obj
                ))
            
            current_date += timedelta(days=1)
        
        return sessions
    
    def generate_receipts(self):
        """Генерация квитанций за 2023-2025 годы"""
        receipts = []
        
        organizations = [
            "ООО 'ТехноСервис'", "ИП Иванов А.С.", "ООО 'Компьютерный Мир'", 
            "ИП Петрова М.К.", "ООО 'ИТ Решения'", "ИП Сидоров В.П.",
            "ООО 'ГеймЛэнд'", "ИП Козлов Д.В.", "ООО 'КиберЗона'", "ИП Николаева Е.С."
        ]
        
        addresses = [
            "г. Москва, ул. Ленина, д. 10", "г. Москва, пр. Мира, д. 25",
            "г. Москва, ул. Пушкина, д. 15", "г. Москва, б-р Космонавтов, д. 8",
            "г. Москва, ул. Гагарина, д. 33", "г. Москва, ул. Тверская, д. 20"
        ]
        
        operators = ["Иванова А.И.", "Петров С.М.", "Сидорова Е.К.", "Козлов Д.В.", "Николаева С.П."]
        
        # Генерируем квитанции с 2023 по ноябрь 2025
        start_date = date(2023, 1, 1)
        end_date = date(2025, 11, 30)
        current_date = start_date
        
        while current_date <= end_date:
            # 1-4 квитанции в день
            daily_receipts = random.randint(1, 4)
            
            # В выходные и праздники больше квитанций
            if current_date.weekday() >= 5:
                daily_receipts = random.randint(2, 5)
            
            for _ in range(daily_receipts):
                organization = random.choice(organizations)
                address = random.choice(addresses)
                phone = f"+7 9{random.randint(10, 99)} {random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
                operator = random.choice(operators)
                shift = random.randint(1, 3)
                
                # Сумма квитанции увеличивается со временем (инфляция + рост бизнеса)
                base_year = 2023
                year_factor = 1.0 + (current_date.year - base_year) * 0.15
                base_amount = random.uniform(600, 6000) * year_factor
                total_amount = round(base_amount, 2)
                total_minutes = int(total_amount / random.uniform(1.8, 3.2))
                
                receipts.append((
                    organization,
                    address,
                    phone,
                    current_date,
                    total_minutes,
                    total_amount,
                    operator,
                    shift
                ))
            
            current_date += timedelta(days=1)
        
        return receipts
    
    def add_minutes_to_time(self, time_obj, minutes):
        """Добавляет минуты к времени"""
        total_minutes = time_obj.hour * 60 + time_obj.minute + minutes
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        return time(new_hour, new_minute)
