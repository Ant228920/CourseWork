from typing import Optional, Dict, List
from passlib.hash import pbkdf2_sha256


class AuthService:
    def __init__(self, db):
        self.db = db

    def hash_password(self, raw_password: str) -> str:
        return pbkdf2_sha256.hash(raw_password)

    def verify(self, raw_password: str, hashed: str) -> bool:
        try:
            return pbkdf2_sha256.verify(raw_password, hashed)
        except Exception:
            return False

    def get_key_by_login(self, login: str) -> Optional[Dict]:
        # Отримуємо дані тільки з таблиці ключів
        sql = """
              SELECT k.id, k.login, k.password, k.role_id, r.name AS role, k.user_id
              FROM keys k
                       JOIN roles r ON r.id = k.role_id
              WHERE k.login = %s \
              """
        rows = self.db.query(sql, [login])
        return dict(rows[0]) if rows else None

    def get_all_keys_unsafe(self) -> List[Dict]:
        return self.db.query('SELECT login, password FROM keys')

    def create_user(self, login: str, password: str, role_name: str, email: Optional[str] = None) -> int:
        # 1. Знаходимо роль
        role = self.db.query('SELECT id FROM roles WHERE name=%s', [role_name])
        if not role: raise ValueError(f"Role '{role_name}' not found")
        role_id = role[0][0]

        # 2. Створюємо профіль в users (тільки email і статус)
        user_sql = 'INSERT INTO users (email, confirmed) VALUES (%s, %s) RETURNING id'
        user_id = self.db.query(user_sql, [email, True])[0][0]

        # 3. Створюємо ключі в keys (логін, пароль, роль)
        pwd = self.hash_password(password)
        keys_sql = 'INSERT INTO keys (login, password, role_id, user_id) VALUES (%s, %s, %s, %s)'
        self.db.execute(keys_sql, [login, pwd, role_id, user_id])

        return user_id

    def register_with_request(self, login: str, password: str, target_role: str, email: Optional[str] = None):
        # Створення Гостя (через метод create_user)
        user_id = self.create_user(login, password, "Guest", email)

        # Створення запиту
        req_type = 'role_operator' if target_role == 'Operator' else 'role_authorized'
        self.create_request(user_id, login, req_type)

    def login(self, login: str, password: str) -> Optional[Dict]:
        key = self.get_key_by_login(login)
        if not key: return None

        # Перевірка пароля
        if not self.verify(password, key['password']): return None

        # Перевірка статусу в таблиці users
        user_data = self.db.query('SELECT confirmed, email FROM users WHERE id=%s', [key['user_id']])
        if not user_data or not user_data[0]['confirmed']: return None

        session = key.copy()
        session['email'] = user_data[0]['email']
        return session

    def login_as_guest(self) -> Optional[Dict]:
        guest = self.get_key_by_login('guest')
        if not guest:
            # Автоматично створюємо системного гостя, якщо немає
            self.create_user('guest', 'guest', 'Guest', 'guest@system')
            guest = self.get_key_by_login('guest')

        # Перевіряємо чи існує профіль
        user_data = self.db.query('SELECT email FROM users WHERE id=%s', [guest['user_id']])

        session = guest.copy()
        session['email'] = user_data[0]['email'] if user_data else ''
        return session

    def change_password(self, login: str, new_pass: str):
        h = self.hash_password(new_pass)
        self.db.execute("UPDATE keys SET password=%s WHERE login=%s", [h, login])

    # --- REQUESTS ---
    def create_request(self, uid, login, rtype):
        exists = self.db.query("SELECT id FROM requests WHERE login=%s AND request_type=%s AND status='pending'",
                               [login, rtype])
        if exists: return "Заявка вже існує."
        self.db.execute("INSERT INTO requests (user_id, login, request_type, status) VALUES (%s, %s, %s, 'pending')",
                        [uid, login, rtype])
        return "Заявку створено."

    def create_password_reset_request(self, login: str) -> str:
        key = self.get_key_by_login(login)
        if not key: return "Користувача не знайдено."
        return self.create_request(key['user_id'], login, 'password_reset')

    def check_reset_status_simple(self, login: str) -> str:
        row = self.db.query(
            "SELECT status FROM requests WHERE login=%s AND request_type='password_reset' ORDER BY created_at DESC LIMIT 1",
            [login])
        return row[0]['status'] if row else "not_found"

    def resubmit_request(self, login: str):
        self.create_password_reset_request(login)

    def admin_approve_request(self, req_id: int):
        self.admin_process_request(req_id, 'approve')

    def admin_reject_request(self, req_id: int):
        self.admin_process_request(req_id, 'reject')

    def admin_process_request(self, req_id: int, action: str):
        req = self.db.query("SELECT * FROM requests WHERE id=%s", [req_id])[0]
        status = 'approved' if action == 'approve' else 'rejected'

        if status == 'approved' and req['request_type'].startswith('role_'):
            new_role_name = 'Operator' if req['request_type'] == 'role_operator' else 'Authorized'
            rid = self.db.query("SELECT id FROM roles WHERE name=%s", [new_role_name])[0][0]

            # Оновлюємо роль тільки в таблиці ключів!
            self.db.execute("UPDATE keys SET role_id=%s WHERE login=%s", [rid, req['login']])
            status = 'completed'

        self.db.execute("UPDATE requests SET status=%s, processed_at=NOW() WHERE id=%s", [status, req_id])

    def user_finalize_reset(self, login: str, new_pass: str):
        if self.check_reset_status_simple(login) != 'approved': raise ValueError("Немає дозволу")
        self.change_password(login, new_pass)
        self.db.execute("DELETE FROM requests WHERE login=%s AND request_type='password_reset'", [login])