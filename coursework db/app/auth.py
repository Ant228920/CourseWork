from typing import Optional, Dict
from passlib.hash import bcrypt

class AuthService:
	def __init__(self, db):
		self.db = db

	def hash_password(self, raw_password: str) -> str:
		return bcrypt.hash(raw_password)

	def verify(self, raw_password: str, hashed: str) -> bool:
		return raw_password == hashed

	def get_user_by_login(self, login: str) -> Optional[Dict]:
		rows = self.db.query('SELECT u.id, u.login, u.password, u.role_id, u.confirmed, r.name AS role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.login=%s', [login])
		return dict(rows[0]) if rows else None

	def create_user(self, login: str, password: str, role_name: str, email: Optional[str] = None, confirmed: bool = True) -> int:
		role = self.db.query('SELECT id FROM roles WHERE name=%s', [role_name])
		if not role:
			raise ValueError("Role not found")
		role_id = role[0][0]
		pwd = self.hash_password(password)
		return self.db.execute('INSERT INTO users (login,password,role_id,email,confirmed) VALUES (%s,%s,%s,%s,%s)', [login, pwd, role_id, email, confirmed])

	def request_access_as_guest(self, user_id: int, comment: Optional[str] = None) -> int:
		return self.db.execute('INSERT INTO access_requests (user_id,comment) VALUES (%s,%s)', [user_id, comment])

	def login(self, login: str, password: str) -> Optional[Dict]:
		user = self.get_user_by_login(login)
		if not user:
			return None
		if not user.get('confirmed'):
			return None
		if not self.verify(password, user['password']):
			return None
		return user
