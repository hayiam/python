import psycopg2
from psycopg2 import sql
import os
from datetime import datetime, date
from data.sample_data import SampleData

class MedicalDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
        self.prefill_data()
    
    def connect(self):
        """Подключение к PostgreSQL базе данных"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'medical_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'magnususer'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("Подключение к PostgreSQL установлено")
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
    
    def create_tables(self):
        """Создание всех необходимых таблиц"""
        try:
            cursor = self.connection.cursor()
            
            # Таблица пациентов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    address TEXT,
                    insurance_number VARCHAR(50),
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица врачей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id SERIAL PRIMARY KEY,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    specialization VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    license_number VARCHAR(50) UNIQUE,
                    hire_date DATE,
                    salary DECIMAL(10,2)
                )
            """)
            
            # Таблица назначений с каскадным удалением
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id SERIAL PRIMARY KEY,
                    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
                    doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
                    appointment_date TIMESTAMP NOT NULL,
                    status VARCHAR(20) DEFAULT 'Scheduled',
                    diagnosis TEXT,
                    prescription TEXT,
                    notes TEXT
                )
            """)
            
            # Таблица медицинских записей с каскадным удалением
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medical_records (
                    record_id SERIAL PRIMARY KEY,
                    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,
                    visit_date DATE NOT NULL,
                    symptoms TEXT,
                    diagnosis TEXT,
                    treatment TEXT,
                    medications TEXT,
                    doctor_id INTEGER REFERENCES doctors(doctor_id) ON DELETE CASCADE,
                    next_visit_date DATE
                )
            """)
            
            self.connection.commit()
            cursor.close()
            print("Таблицы успешно созданы")
            
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")

    def prefill_data(self):
        """Заполнение базы данных демонстрационными данными"""
        try:
            cursor = self.connection.cursor()
            
            # Проверка существования данных
            cursor.execute("SELECT COUNT(*) FROM patients")
            patient_count = cursor.fetchone()[0]
            
            if patient_count == 0:
                sample_data = SampleData()
                
                # Вставка пациентов
                cursor.executemany("""
                    INSERT INTO patients (first_name, last_name, date_of_birth, gender, phone, email, address, insurance_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, sample_data.patients)
                
                # Вставка врачей
                cursor.executemany("""
                    INSERT INTO doctors (first_name, last_name, specialization, phone, email, license_number, hire_date, salary)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, sample_data.doctors)
                
                # Получаем ID вставленных пациентов и врачей
                cursor.execute("SELECT patient_id FROM patients ORDER BY patient_id")
                patient_ids = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT doctor_id FROM doctors ORDER BY doctor_id")
                doctor_ids = [row[0] for row in cursor.fetchall()]
                
                # Вставка назначений - используем реальные ID
                appointments_data = []
                for i, appointment in enumerate(sample_data.appointments):
                    if i < len(patient_ids) and i < len(doctor_ids):
                        appointments_data.append((
                            patient_ids[i],  # patient_id
                            doctor_ids[i],   # doctor_id
                            appointment[2],  # appointment_date
                            appointment[3],  # status
                            appointment[4],  # diagnosis
                            appointment[5],  # prescription
                            appointment[6]   # notes
                        ))
                
                cursor.executemany("""
                    INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, diagnosis, prescription, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, appointments_data)
                
                # Вставка медицинских записей - используем реальные ID
                medical_records_data = []
                for i, record in enumerate(sample_data.medical_records):
                    if i < len(patient_ids) and i < len(doctor_ids):
                        medical_records_data.append((
                            patient_ids[i],  # patient_id
                            record[1],       # visit_date
                            record[2],       # symptoms
                            record[3],       # diagnosis
                            record[4],       # treatment
                            record[5],       # medications
                            doctor_ids[i],   # doctor_id
                            record[7]        # next_visit_date
                        ))
                
                cursor.executemany("""
                    INSERT INTO medical_records (patient_id, visit_date, symptoms, diagnosis, treatment, medications, doctor_id, next_visit_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, medical_records_data)
                
                self.connection.commit()
                print("Демонстрационные данные успешно добавлены")
            
            cursor.close()
            
        except Exception as e:
            print(f"Ошибка добавления демонстрационных данных: {e}")
            # Важно: откатываем транзакцию при ошибке
            if self.connection:
                self.connection.rollback() 
        
    def execute_query(self, query, params=None):
        """Выполнение запроса и возврат результатов"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                return result, columns
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            # Откатываем транзакцию при ошибке
            if self.connection:
                self.connection.rollback()
            return None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
