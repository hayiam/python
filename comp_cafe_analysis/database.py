import psycopg2
from psycopg2 import sql
import os
from datetime import datetime, date, time
from data.sample_data import SampleData
import random
from decimal import Decimal

class InternetCafeDatabase:
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
                database=os.getenv('DB_NAME', 'internet_cafe_db'),
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
            
            # Таблица сеансов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id SERIAL PRIMARY KEY,
                    computer_number INTEGER NOT NULL,
                    ip_address VARCHAR(15) NOT NULL,
                    connection_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица тарифов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tariffs (
                    tariff_id SERIAL PRIMARY KEY,
                    effective_date DATE NOT NULL,
                    cost_per_minute DECIMAL(10,2) NOT NULL,
                    discount_evening DECIMAL(10,2) NOT NULL,
                    discount_night DECIMAL(10,2) NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица квитанций
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_id SERIAL PRIMARY KEY,
                    organization_name VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    receipt_date DATE NOT NULL,
                    total_minutes INTEGER NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    operator_name VARCHAR(100) NOT NULL,
                    shift_number INTEGER NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица связи квитанций и сеансов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipt_sessions (
                    id SERIAL PRIMARY KEY,
                    receipt_id INTEGER REFERENCES receipts(receipt_id) ON DELETE CASCADE,
                    session_id INTEGER REFERENCES sessions(session_id) ON DELETE CASCADE,
                    session_minutes INTEGER NOT NULL,
                    session_cost DECIMAL(10,2) NOT NULL
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
            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]
            
            if sessions_count == 0:
                sample_data = SampleData()
                
                print("Добавление демонстрационных данных...")
                
                # Вставка сеансов
                cursor.executemany("""
                    INSERT INTO sessions (computer_number, ip_address, connection_date, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, sample_data.sessions)
                print(f"Добавлено {len(sample_data.sessions)} сеансов")
                
                # Вставка тарифов
                cursor.executemany("""
                    INSERT INTO tariffs (effective_date, cost_per_minute, discount_evening, discount_night)
                    VALUES (%s, %s, %s, %s)
                """, sample_data.tariffs)
                print(f"Добавлено {len(sample_data.tariffs)} тарифов")
                
                # Вставка квитанций
                cursor.executemany("""
                    INSERT INTO receipts (organization_name, address, phone, receipt_date, 
                    total_minutes, total_amount, operator_name, shift_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, sample_data.receipts)
                print(f"Добавлено {len(sample_data.receipts)} квитанций")
                
                # Создаем связи между квитанциями и сеансами
                self.create_receipt_sessions_links(cursor)
                
                self.connection.commit()
                print("Демонстрационные данные успешно добавлены")
            
            cursor.close()
            
        except Exception as e:
            print(f"Ошибка добавления демонстрационных данных: {e}")
            if self.connection:
                self.connection.rollback()
    
    def create_receipt_sessions_links(self, cursor):
        """Создание связей между квитанциями и сеансами"""
        try:
            # Получаем все квитанции
            cursor.execute("SELECT receipt_id, receipt_date, total_amount FROM receipts")
            receipts = cursor.fetchall()
            
            # Получаем все сеансы
            cursor.execute("SELECT session_id, connection_date FROM sessions ORDER BY connection_date")
            sessions = cursor.fetchall()
            
            session_index = 0
            
            for receipt in receipts:
                receipt_id, receipt_date, total_amount = receipt
                
                # Добавляем 1-3 сеанса в каждую квитанцию
                num_sessions = random.randint(1, 3)
                receipt_remaining = float(total_amount)  # Преобразуем Decimal в float
                
                for i in range(num_sessions):
                    if session_index >= len(sessions):
                        break
                    
                    session_id, session_date = sessions[session_index]
                    
                    # Пропускаем сеансы, которые были после даты квитанции
                    while session_index < len(sessions) - 1 and session_date > receipt_date:
                        session_index += 1
                        session_id, session_date = sessions[session_index]
                    
                    if session_date <= receipt_date:
                        # Распределяем стоимость
                        if i == num_sessions - 1:  # Последний сеанс получает остаток
                            session_cost = receipt_remaining
                        else:
                            session_cost = round(float(total_amount) * random.uniform(0.2, 0.5), 2)  # Преобразуем в float
                            receipt_remaining -= session_cost
                        
                        # Расчет минут (примерно 1.5-3 руб/минута)
                        session_minutes = int(session_cost / random.uniform(1.5, 3.0))
                        
                        cursor.execute("""
                            INSERT INTO receipt_sessions (receipt_id, session_id, session_minutes, session_cost)
                            VALUES (%s, %s, %s, %s)
                        """, (receipt_id, session_id, session_minutes, Decimal(str(session_cost))))  # Преобразуем обратно в Decimal
                    
                    session_index += 1
            
            print("Созданы связи между квитанциями и сеансами")
            
        except Exception as e:
            print(f"Ошибка создания связей: {e}")
            raise
    
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
            if self.connection:
                self.connection.rollback()
            return None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
