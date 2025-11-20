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

    # --- АВТОРИЗАЦІЯ ---
    def get_key_by_login(self, login: str) -> Optional[Dict]:
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
        role = self.db.query('SELECT id FROM roles WHERE name=%s', [role_name])
        if not role:
            raise ValueError("Role not found")
        role_id = role[0][0]

        pwd = self.hash_password(password)

        user_sql = 'INSERT INTO users (email, confirmed, role_id, login, password) VALUES (%s, %s, %s, %s, %s) RETURNING id'
        user_id = self.db.query(user_sql, [email, True, role_id, login, pwd])[0][0]

        keys_sql = 'INSERT INTO keys (login, password, role_id, user_id) VALUES (%s, %s, %s, %s)'
        self.db.execute(keys_sql, [login, pwd, role_id, user_id])
        return user_id

    def register_with_request(self, login: str, password: str, target_role: str, email: Optional[str] = None):
        """Спеціальна реєстрація для Оператора: створює як Guest + запит на підвищення"""
        # 1. Спочатку створюємо як 'Guest'
        guest_role_id = self.db.query("SELECT id FROM roles WHERE name='Guest'")[0][0]
        pwd = self.hash_password(password)

        user_sql = 'INSERT INTO users (email, confirmed, role_id, login, password) VALUES (%s, %s, %s, %s, %s) RETURNING id'
        user_id = self.db.query(user_sql, [email, True, guest_role_id, login, pwd])[0][0]

        self.db.execute(
            'INSERT INTO keys (login, password, role_id, user_id) VALUES (%s, %s, %s, %s)',
            [login, pwd, guest_role_id, user_id]
        )

        # 2. Створюємо запит на роль Оператора
        req_type = 'role_operator'  # Тільки для оператора
        self.create_request(user_id, login, req_type)

    def login(self, login: str, password: str) -> Optional[Dict]:
        key_data = self.get_key_by_login(login)
        if not key_data: return None

        user_data = self.db.query('SELECT confirmed, email FROM users WHERE id=%s', [key_data['user_id']])
        if not user_data or not user_data[0]['confirmed']: return None

        if not self.verify(password, key_data['password']): return None

        session_user = key_data.copy()
        session_user['role'] = key_data['role']
        session_user['email'] = user_data[0]['email']
        return session_user

    def login_as_guest(self) -> Optional[Dict]:
        """Знаходить або створює користувача guest для швидкого входу"""
        # Спробуємо знайти існуючого гостя
        guest = self.get_key_by_login('guest')

        if not guest:
            # Якщо немає - створимо його автоматично
            try:
                self.create_user('guest', 'guest', 'Guest', 'guest@system.local')
                guest = self.get_key_by_login('guest')
            except Exception as e:
                print(f"Guest creation error: {e}")
                return None

        # Повертаємо дані гостя (без перевірки пароля)
        session_user = guest.copy()
        session_user['role'] = 'Guest'
        session_user['email'] = 'guest@system.local'
        return session_user

    def change_password(self, login: str, new_password: str):
        hashed = self.hash_password(new_password)
        self.db.execute("UPDATE keys SET password=%s WHERE login=%s", [hashed, login])
        self.db.execute("UPDATE users SET password=%s WHERE login=%s", [hashed, login])

    # --- ЗАПИТИ (Requests) ---

    def create_request(self, user_id: Optional[int], login: str, req_type: str) -> str:
        existing = self.db.query(
            "SELECT id FROM requests WHERE login=%s AND request_type=%s AND status='pending'",
            [login, req_type]
        )
        if existing:
            return "Заявка вже існує."

        self.db.execute(
            "INSERT INTO requests (user_id, login, request_type, status) VALUES (%s, %s, %s, 'pending')",
            [user_id, login, req_type]
        )
        return "Заявку створено."

    def create_password_reset_request(self, login: str) -> str:
        if not self.get_key_by_login(login): return "Користувача не знайдено."
        return self.create_request(None, login, 'password_reset')

    def check_reset_status_simple(self, login: str) -> str:
        # Перевіряємо статус (для пароля або для ролі - залежить від контексту, тут для пароля)
        # Але краще зробити універсально, якщо ви використовуєте це для ролей теж.
        # Для простоти повертаємо статус останнього запиту будь-якого типу або конкретно пароля
        rows = self.db.query("SELECT status FROM requests WHERE login=%s ORDER BY created_at DESC LIMIT 1", [login])
        return rows[0]['status'] if rows else "not_found"

    def resubmit_request(self, login: str):
        self.create_request(None, login, 'password_reset')  # Спрощено

    def admin_approve_request(self, request_id: int):
        self.admin_process_request(request_id, 'approve')

    def admin_reject_request(self, request_id: int):
        self.admin_process_request(request_id, 'reject')

    def admin_process_request(self, req_id: int, action: str):
        req = self.db.query("SELECT * FROM requests WHERE id=%s", [req_id])[0]
        login, rtype = req['login'], req['request_type']
        new_status = 'approved' if action == 'approve' else 'rejected'

        if new_status == 'approved':
            if rtype == 'role_operator':
                # Підвищуємо до Оператора
                op_role = self.db.query("SELECT id FROM roles WHERE name='Operator'")[0][0]
                self.db.execute("UPDATE keys SET role_id=%s WHERE login=%s", [op_role, login])
                self.db.execute("UPDATE users SET role_id=%s WHERE login=%s", [op_role, login])
                new_status = 'completed'

        self.db.execute("UPDATE requests SET status=%s, processed_at=NOW() WHERE id=%s", [new_status, req_id])

    def user_finalize_reset(self, login: str, new_password: str):
        # Метод для зміни пароля юзером після схвалення (використовує check_reset_status_simple)
        # ... (код аналогічний попередньому, але звертається до requests)
        # Для стислості:
        hashed = self.hash_password(new_password)
        self.db.execute("UPDATE keys SET password=%s WHERE login=%s", [hashed, login])
        self.db.execute("UPDATE users SET password=%s WHERE login=%s", [hashed, login])
        self.db.execute("DELETE FROM requests WHERE login=%s AND request_type='password_reset'", [login])