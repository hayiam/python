import re
from datetime import datetime, time
from tkinter import messagebox

class FieldValidator:
    @staticmethod
    def validate_required(value, field_name):
        """Проверка обязательного поля"""
        if not value or str(value).strip() == '':
            messagebox.showerror("Ошибка валидации", f"Поле '{field_name}' обязательно для заполнения")
            return False
        return True

    @staticmethod
    def validate_ip_address(ip):
        """Проверка формата IP-адреса"""
        if ip and ip.strip():
            pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(pattern, ip):
                messagebox.showerror("Ошибка валидации", "Неверный формат IP-адреса")
                return False
            
            # Проверка, что каждый октет в диапазоне 0-255
            octets = ip.split('.')
            for octet in octets:
                if not (0 <= int(octet) <= 255):
                    messagebox.showerror("Ошибка валидации", "Неверный диапазон IP-адреса")
                    return False
        return True

    @staticmethod
    def validate_date(date_string, field_name):
        """Проверка формата даты (ГГГГ-ММ-ДД)"""
        if date_string and date_string.strip():
            try:
                datetime.strptime(date_string, '%Y-%m-%d')
                return True
            except ValueError:
                messagebox.showerror("Ошибка валидации", f"Неверный формат даты в поле '{field_name}'. Используйте ГГГГ-ММ-ДД")
                return False
        return True

    @staticmethod
    def validate_time(time_string, field_name):
        """Проверка формата времени (ЧЧ:ММ)"""
        if time_string and time_string.strip():
            try:
                datetime.strptime(time_string, '%H:%M')
                return True
            except ValueError:
                messagebox.showerror("Ошибка валидации", f"Неверный формат времени в поле '{field_name}'. Используйте ЧЧ:ММ")
                return False
        return True

    @staticmethod
    def validate_number(value, field_name, min_value=None, max_value=None):
        """Проверка числового поля"""
        if value and str(value).strip():
            try:
                num = float(value)
                if min_value is not None and num < min_value:
                    messagebox.showerror("Ошибка валидации", f"Значение поля '{field_name}' не может быть меньше {min_value}")
                    return False
                if max_value is not None and num > max_value:
                    messagebox.showerror("Ошибка валидации", f"Значение поля '{field_name}' не может быть больше {max_value}")
                    return False
                return True
            except ValueError:
                messagebox.showerror("Ошибка валидации", f"Поле '{field_name}' должно содержать числовое значение")
                return False
        return True

    @staticmethod
    def validate_phone(phone):
        """Проверка формата телефона"""
        if phone and phone.strip():
            pattern = r'^(\+7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            if not re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                messagebox.showerror("Ошибка валидации", "Неверный формат телефона")
                return False
        return True

class SessionValidator:
    @staticmethod
    def validate_session_data(computer_number, ip_address, connection_date, start_time, end_time):
        """Валидация данных сеанса"""
        validator = FieldValidator()
        
        if not validator.validate_required(computer_number, "Номер компьютера"):
            return False
        if not validator.validate_number(computer_number, "Номер компьютера", min_value=1):
            return False
        if not validator.validate_required(ip_address, "IP-адрес"):
            return False
        if not validator.validate_ip_address(ip_address):
            return False
        if not validator.validate_required(connection_date, "Дата соединения"):
            return False
        if not validator.validate_date(connection_date, "Дата соединения"):
            return False
        if not validator.validate_required(start_time, "Время начала"):
            return False
        if not validator.validate_time(start_time, "Время начала"):
            return False
        if not validator.validate_required(end_time, "Время окончания"):
            return False
        if not validator.validate_time(end_time, "Время окончания"):
            return False
            
        # Проверка, что время окончания позже времени начала
        try:
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
            if end <= start:
                messagebox.showerror("Ошибка валидации", "Время окончания должно быть позже времени начала")
                return False
        except:
            pass
            
        return True

class TariffValidator:
    @staticmethod
    def validate_tariff_data(effective_date, cost_per_minute, discount_evening, discount_night):
        """Валидация данных тарифа"""
        validator = FieldValidator()
        
        if not validator.validate_required(effective_date, "Дата действия"):
            return False
        if not validator.validate_date(effective_date, "Дата действия"):
            return False
        if not validator.validate_required(cost_per_minute, "Стоимость минуты"):
            return False
        if not validator.validate_number(cost_per_minute, "Стоимость минуты", min_value=0):
            return False
        if not validator.validate_required(discount_evening, "Льготная стоимость (20:00-02:00)"):
            return False
        if not validator.validate_number(discount_evening, "Льготная стоимость (20:00-02:00)", min_value=0):
            return False
        if not validator.validate_required(discount_night, "Льготная стоимость (02:00-06:00)"):
            return False
        if not validator.validate_number(discount_night, "Льготная стоимость (02:00-06:00)", min_value=0):
            return False
            
        return True

class ReceiptValidator:
    @staticmethod
    def validate_receipt_data(organization_name, address, phone, receipt_date, operator_name, shift_number):
        """Валидация данных квитанции"""
        validator = FieldValidator()
        
        if not validator.validate_required(organization_name, "Название организации"):
            return False
        if not validator.validate_required(address, "Адрес"):
            return False
        if not validator.validate_required(phone, "Телефон"):
            return False
        if not validator.validate_phone(phone):
            return False
        if not validator.validate_required(receipt_date, "Дата квитанции"):
            return False
        if not validator.validate_date(receipt_date, "Дата квитанции"):
            return False
        if not validator.validate_required(operator_name, "ФИО оператора"):
            return False
        if not validator.validate_required(shift_number, "Номер смены"):
            return False
        if not validator.validate_number(shift_number, "Номер смены", min_value=1):
            return False
            
        return True
