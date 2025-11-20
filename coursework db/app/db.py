import os
import psycopg2
import psycopg2.extras
from typing import Any, Iterable, Optional, Tuple, List
from dotenv import load_dotenv

# ✅ Завантажуємо змінні середовища з .env
load_dotenv()


class Database:
    def __init__(self):
        self._conn = None

    def connect(self):
        """Підключення до бази даних PostgreSQL"""
        if self._conn is None or self._conn.closed:
            try:
                self._conn = psycopg2.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", "5432")),
                    database=os.getenv("DB_NAME", "military"),
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASSWORD", "postgres"),
                    cursor_factory=psycopg2.extras.DictCursor
                )
                print(f"✅ Підключено до БД '{os.getenv('DB_NAME')}' на {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
            except Exception as e:
                print(f"❌ Помилка підключення до БД ({os.getenv('DB_NAME')}): {e}")
                raise
        return self._conn

    def query(self, sql: str, params: Optional[Iterable[Any]] = None):
        """Виконати SELECT-запит і повернути результат"""
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            try:
                rows = cur.fetchall()
                return rows
            except psycopg2.ProgrammingError:
                return []

    def query_with_columns(self, sql: str, params: Optional[Iterable[Any]] = None) -> Tuple[List[str], list]:
        """Виконати SELECT-запит і повернути (імена колонок, дані)"""
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            try:
                rows = cur.fetchall()
                cols = [desc.name for desc in cur.description]
                return cols, rows
            except psycopg2.ProgrammingError:
                return [], []

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """Виконати INSERT/UPDATE/DELETE"""
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount

    # --- НОВИЙ МЕТОД ---
    def execute_file(self, filepath: str):
        """Виконує SQL-скрипт із вказаного файлу."""
        if not os.path.exists(filepath):
            print(f"❌ Файл не знайдено: {filepath}")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_script = f.read()
        except Exception as e:
             print(f"❌ Помилка читання файлу '{filepath}': {e}")
             return

        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql_script)
                conn.commit()
                print(f"✅ Скрипт '{filepath}' успішно виконано!")
        except Exception as e:
            conn.rollback()
            print(f"❌ Помилка при виконанні SQL з '{filepath}':\n{e}")
    # -------------------

    def close(self):
        """Закрити підключення"""
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
            self._conn = None
            print("🔒 Підключення до БД закрито")

    def __del__(self):
        """Автоматичне закриття при видаленні об’єкта"""
        self.close()