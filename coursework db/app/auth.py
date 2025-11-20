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
        """Повертає всі логіни та хеші (для старого методу, якщо потрібно)"""
        return self.db.query('SELECT login, password FROM keys')

    def create_user(self, login: str, password: str, role_name: str, email: Optional[str] = None,
                    confirmed: bool = True) -> int:
        role = self.db.query('SELECT id FROM roles WHERE name=%s', [role_name])
        if not role:
            raise ValueError("Role not found")
        role_id = role[0][0]

        pwd = self.hash_password(password)

        # Створюємо user та key
        user_sql = 'INSERT INTO users (email, confirmed, role_id, login, password) VALUES (%s, %s, %s, %s, %s) RETURNING id'
        user_id = self.db.query(user_sql, [email, confirmed, role_id, login, pwd])[0][0]

        keys_sql = 'INSERT INTO keys (login, password, role_id, user_id) VALUES (%s, %s, %s, %s)'
        self.db.execute(keys_sql, [login, pwd, role_id, user_id])

        return user_id

    def create_user_with_role_id(self, login: str, password: str, role_id: int, email: Optional[str] = None,
                                 confirmed: bool = True) -> int:
        pwd = self.hash_password(password)
        user_sql = 'INSERT INTO users (email, confirmed, role_id, login, password) VALUES (%s, %s, %s, %s, %s) RETURNING id'
        user_id = self.db.query(user_sql, [email, confirmed, role_id, login, pwd])[0][0]
        keys_sql = 'INSERT INTO keys (login, password, role_id, user_id) VALUES (%s, %s, %s, %s)'
        self.db.execute(keys_sql, [login, pwd, role_id, user_id])
        return user_id

    def request_access_as_guest(self, user_id: int, comment: Optional[str] = None) -> int:
        return self.db.execute('INSERT INTO access_requests (user_id, comment) VALUES (%s,%s)', [user_id, comment])

    def login(self, login: str, password: str) -> Optional[Dict]:
        key_data = self.get_key_by_login(login)
        if not key_data:
            return None

        user_data = self.db.query('SELECT confirmed, email FROM users WHERE id=%s', [key_data['user_id']])
        if not user_data or not user_data[0]['confirmed']:
            return None

        if not self.verify(password, key_data['password']):
            return None

        session_user = key_data.copy()
        session_user['role'] = key_data['role']
        session_user['email'] = user_data[0]['email']
        return session_user

    def change_password(self, login: str, new_password: str):
        """Зміна пароля з профілю (без заявок)"""
        hashed = self.hash_password(new_password)
        self.db.execute("UPDATE keys SET password=%s WHERE login=%s", [hashed, login])
        self.db.execute("UPDATE users SET password=%s WHERE login=%s", [hashed, login])

    # --- ЛОГІКА ВІДНОВЛЕННЯ ПАРОЛЯ (ЗАЯВКИ) ---

    def create_password_reset_request(self, login: str) -> str:
        if not self.get_key_by_login(login):
            return "Користувача не знайдено."

        rows = self.db.query(
            "SELECT id, status FROM password_resets WHERE login=%s ORDER BY created_at DESC LIMIT 1",
            [login]
        )
        if rows:
            status = rows[0]['status']
            if status == 'pending':
                return "Заявка вже на розгляді."
            if status == 'approved':
                return "Заявку вже схвалено! Введіть новий пароль."

        self.db.execute("INSERT INTO password_resets (login, status, created_at) VALUES (%s, 'pending', NOW())",
                        [login])
        return "Заявку подано! Очікуйте рішення адміністратора."

    def check_reset_status_simple(self, login: str) -> str:
        rows = self.db.query(
            "SELECT status FROM password_resets WHERE login=%s ORDER BY created_at DESC LIMIT 1",
            [login]
        )
        if not rows:
            return "not_found"
        return rows[0]['status']

    def resubmit_request(self, login: str):
        self.db.execute("INSERT INTO password_resets (login, status, created_at) VALUES (%s, 'pending', NOW())",
                        [login])

    def admin_approve_request(self, request_id: int):
        self.db.execute("UPDATE password_resets SET status='approved', processed_at=NOW() WHERE id=%s", [request_id])

    def admin_reject_request(self, request_id: int):
        self.db.execute("UPDATE password_resets SET status='rejected', processed_at=NOW() WHERE id=%s", [request_id])

    def user_finalize_reset(self, login: str, new_password: str):
        status = self.check_reset_status_simple(login)
        if status != 'approved':
            raise ValueError("Немає дозволу на зміну пароля.")

        hashed = self.hash_password(new_password)
        self.db.execute("UPDATE keys SET password=%s WHERE login=%s", [hashed, login])
        self.db.execute("UPDATE users SET password=%s WHERE login=%s", [hashed, login])

        # ВИДАЛЯЄМО заявку після успішної зміни
        self.db.execute("DELETE FROM password_resets WHERE login=%s AND status='approved'", [login])