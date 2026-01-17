import sqlite3
from config import PLANNED_WORK, ALLOWANCE


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('car_logger.db')
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mileage INTEGER NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def add_record(self, mileage, date, type_, description):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO logs (mileage, date, type, description) VALUES (?, ?, ?, ?)",
            (mileage, date, type_, description)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_records(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY date DESC, mileage DESC")
        return cursor.fetchall()
    
    def get_last_service(self, description):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT mileage FROM logs WHERE description = ? ORDER BY mileage DESC LIMIT 1",
            (description,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def check_services(self, current_mileage):
        results = []
        for work_desc, period in PLANNED_WORK:
            last_mileage = self.get_last_service(work_desc)
            next_service = last_mileage + period
            admission = int(period * ALLOWANCE / 100)
            
            if current_mileage >= next_service - admission:
                status = "СРОЧНО!" if current_mileage >= next_service else "Скоро потребуется"
                results.append((work_desc, last_mileage, next_service, status))
        
        return results
    
    def delete_record(self, record_id):
        """Удаляет запись по ID"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id = ?", (record_id,))
        self.conn.commit()
        return cursor.rowcount  # Возвращает количество удаленных строк
    
    def close(self):
        self.conn.close()