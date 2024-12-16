import sqlite3
from typing import List, Tuple
import os.path

class BudgetTracker:
    def __init__(self, db_name: str):
        not_exist = not os.path.isfile(db_name)
        self.conn = sqlite3.connect(db_name)
        
        if (not_exist):
            self.create_users_table()

    def create_users_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    expense TEXT
                )
            ''')
        self.conn.commit()

    def create_user_table(self, user_id: int):
        if not self.user_exists(user_id):
            table_name = f'user_{user_id}'
            with self.conn:
                self.conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        balance REAL,
                        date TEXT
                    )
                ''')
                self.conn.execute('''
                    INSERT INTO users (id, expense) VALUES (?, ?)
                ''', (user_id, table_name))
            self.conn.commit()

    def user_exists(self, user_id: int) -> bool:
        cursor = self.conn.execute('''
            SELECT 1 FROM users WHERE id = ?
        ''', (user_id,))
        return cursor.fetchone() is not None

    def add_balance(self, user_id: int, balance: float, date: str):
        if self.user_exists(user_id):
            table_name = self.get_user_table(user_id)
            with self.conn:
                self.conn.execute(f'''
                    INSERT INTO {table_name} (balance, date) VALUES (?, ?)
                ''', (balance, date))
            self.conn.commit()

    def update_balance(self, user_id: int, balance: float, date: str):
        if self.user_exists(user_id):
            table_name = self.get_user_table(user_id)
            with self.conn:
                self.conn.execute(f'''
                    UPDATE {table_name} SET balance = ? WHERE date = ?
                ''', (balance, date))
            self.conn.commit()

    def get_user_table(self, user_id: int) -> str:
        cursor = self.conn.execute('''
            SELECT expense FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def extract_data(self, user_id: int, start_date: str, end_date: str) -> List[Tuple[float, str]]:
        if self.user_exists(user_id):
            table_name = self.get_user_table(user_id)
            cursor = self.conn.execute(f'''
                SELECT balance, date FROM {table_name} WHERE date BETWEEN ? AND ?
            ''', (start_date, end_date))
            return cursor.fetchall()
        else:
            return []
    
    def extract_all_data(self, user_id: int) -> List[Tuple[float, str]]:
        if self.user_exists(user_id):
            table_name = self.get_user_table(user_id)
            cursor = self.conn.execute(f'''
                SELECT balance, date FROM {table_name} ''')
            return cursor.fetchall()
        else:
            return []
    
    def record_exists(self, user_id: int, date: str) -> bool:
        if (not self.user_exists(user_id)):
            return False
        table_name = self.get_user_table(user_id)
            
        cursor = self.conn.execute(f'''
            SELECT 1 FROM {table_name} WHERE date = ?
        ''', (date,))

        return cursor.fetchone() is not None
    
    def get_record(self, user_id: int, date: str) -> float:
        if (not self.user_exists(user_id)):
            return 0
        table_name = self.get_user_table(user_id)

        cursor = self.conn.execute(f'''
            SELECT balance FROM {table_name} WHERE date = ?
        ''', (date,))
        fetch = cursor.fetchall()
        return 0 if (fetch is None or len(fetch) == 0) else fetch[0][0]

if __name__ == '__main__':
    tracker = BudgetTracker('budget_tracker.db')
    # tracker.create_users_table()
    # # Создание таблицы для нового пользователя
    # tracker.create_user_table(1)

    # # Проверка существования пользователя
    # print(tracker.user_exists(1))  # True
    # print(tracker.user_exists(1471703209))  # False

    # # Добавление баланса
    # tracker.add_balance(1, 100.0, '2023-10-01')
    # tracker.add_balance(1, 150.0, '2023-10-02')

    # print(tracker.get_record(1471703209, '2024-12-16'))
    # # Обновление баланса
    # tracker.update_balance(1, 200.0, '2023-10-01')
    # print(tracker.get_record(1, '2023-10-01'))
    # # Извлечение данных
    # data = tracker.extract_data(1, '2022-10-01', '2024-10-02')
    # print(data)
