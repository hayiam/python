import re
from datetime import datetime
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
    def validate_email(email):
        """Проверка формата email"""
        if email and email.strip():
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                messagebox.showerror("Ошибка валидации", "Неверный формат email")
                return False
        return True

    @staticmethod
    def validate_phone(phone):
        """Проверка формата телефона"""
        if phone and phone.strip():
            # Разрешаем форматы: +7 XXX XXX XX XX, 8 XXX XXX XX XX, XXX XXX XX XX
            pattern = r'^(\+7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            if not re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                messagebox.showerror("Ошибка валидации", "Неверный формат телефона")
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
    def validate_datetime(datetime_string):
        """Проверка формата даты и времени (ГГГГ-ММ-ДД ЧЧ:ММ)"""
        if datetime_string and datetime_string.strip():
            try:
                datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
                return True
            except ValueError:
                messagebox.showerror("Ошибка валидации", "Неверный формат даты и времени. Используйте ГГГГ-ММ-ДД ЧЧ:ММ")
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
    def validate_selection(value, field_name):
        """Проверка выбора из комбобокса"""
        if not value or str(value).strip() == '':
            messagebox.showerror("Ошибка валидации", f"Необходимо выбрать значение в поле '{field_name}'")
            return False
        return True

    @staticmethod
    def validate_gender(gender):
        """Проверка выбора пола"""
        if not gender or gender.strip() == '':
            messagebox.showerror("Ошибка валидации", "Необходимо выбрать пол")
            return False
        if gender not in ['Мужской', 'Женский']:
            messagebox.showerror("Ошибка валидации", "Неверное значение пола. Допустимые значения: Мужской, Женский")
            return False
        return True

class PatientValidator:
    @staticmethod
    def validate_patient_data(first_name, last_name, dob, gender, phone, email):
        """Валидация данных пациента"""
        validator = FieldValidator()
        
        if not validator.validate_required(first_name, "Имя"):
            return False
        if not validator.validate_required(last_name, "Фамилия"):
            return False
        if not validator.validate_required(dob, "Дата рождения"):
            return False
        if not validator.validate_date(dob, "Дата рождения"):
            return False
        if not validator.validate_gender(gender):
            return False
        if phone and not validator.validate_phone(phone):
            return False
        if email and not validator.validate_email(email):
            return False
            
        return True

class DoctorValidator:
    @staticmethod
    def validate_doctor_data(first_name, last_name, specialization, phone, email, license, hire_date, salary):
        """Валидация данных врача"""
        validator = FieldValidator()
        
        if not validator.validate_required(first_name, "Имя"):
            return False
        if not validator.validate_required(last_name, "Фамилия"):
            return False
        if not validator.validate_required(specialization, "Специализация"):
            return False
        if phone and not validator.validate_phone(phone):
            return False
        if email and not validator.validate_email(email):
            return False
        if not validator.validate_required(license, "Номер лицензии"):
            return False
        if not validator.validate_required(hire_date, "Дата приема"):
            return False
        if not validator.validate_date(hire_date, "Дата приема"):
            return False
        if salary and not validator.validate_number(salary, "Зарплата", min_value=0):
            return False
            
        return True

class AppointmentValidator:
    @staticmethod
    def validate_appointment_data(patient, doctor, datetime, status, diagnosis):
        """Валидация данных назначения"""
        validator = FieldValidator()
        
        if not validator.validate_selection(patient, "Пациент"):
            return False
        if not validator.validate_selection(doctor, "Врач"):
            return False
        if not validator.validate_required(datetime, "Дата и время"):
            return False
        if not validator.validate_datetime(datetime):
            return False
        if not validator.validate_required(status, "Статус"):
            return False
        if not validator.validate_required(diagnosis, "Диагноз"):
            return False
            
        return True

class MedicalRecordValidator:
    @staticmethod
    def validate_medical_record_data(patient, doctor, visit_date, diagnosis):
        """Валидация данных медицинской записи"""
        validator = FieldValidator()
        
        if not validator.validate_selection(patient, "Пациент"):
            return False
        if not validator.validate_selection(doctor, "Врач"):
            return False
        if not validator.validate_required(visit_date, "Дата визита"):
            return False
        if not validator.validate_date(visit_date, "Дата визита"):
            return False
        if not validator.validate_required(diagnosis, "Диагноз"):
            return False
            
        return True
