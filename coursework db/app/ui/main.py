import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Додаємо поточну директорію до шляху Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from queries import QueriesFrame

ROLES = {
	"Адміністратор": {"users": True, "crud": True, "queries": True, "view": True},
	"Оператор": {"users": False, "crud": True, "queries": True, "view": True},
	"Авторизований": {"users": False, "crud": False, "queries": True, "view": True},
	"Гість": {"users": False, "crud": False, "queries": False, "view": True},
}

class MainFrame(tk.Frame):
	def __init__(self, master, db, user, on_logout):
		super().__init__(master)
		self.db = db
		self.user = user
		self.on_logout = on_logout

		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		toolbar = ttk.Frame(self, padding=6)
		toolbar.grid(row=0, column=0, sticky="ew")

		role = user.get("role")
		caps = ROLES.get(role, ROLES["Гість"]) 

		btn_view = ttk.Button(toolbar, text="Перегляд", command=self._show_view)
		btn_view.pack(side=tk.LEFT, padx=2)

		self.btn_crud = ttk.Button(toolbar, text="CRUD", command=self._show_crud, state=(tk.NORMAL if caps["crud"] else tk.DISABLED))
		self.btn_crud.pack(side=tk.LEFT, padx=2)

		self.btn_queries = ttk.Button(toolbar, text="Запити", command=self._show_queries, state=(tk.NORMAL if caps["queries"] else tk.DISABLED))
		self.btn_queries.pack(side=tk.LEFT, padx=2)

		self.btn_users = ttk.Button(toolbar, text="Користувачі", command=self._show_users, state=(tk.NORMAL if caps["users"] else tk.DISABLED))
		self.btn_users.pack(side=tk.LEFT, padx=2)

		ttk.Label(toolbar, text=f"Роль: {role}").pack(side=tk.RIGHT)

		btn_logout = ttk.Button(toolbar, text="Вийти", command=self._logout)
		btn_logout.pack(side=tk.RIGHT, padx=2)

		self.container = ttk.Frame(self)
		self.container.grid(row=1, column=0, sticky="nsew")
		self.container.columnconfigure(0, weight=1)
		self.container.rowconfigure(0, weight=1)

		self._current = None
		self._show_view()

	def _swap(self, frame: tk.Frame):
		if self._current is not None:
			self._current.destroy()
		self._current = frame
		self._current.grid(row=0, column=0, sticky="nsew")

	def _show_view(self):
		f = ttk.Frame(self.container, padding=12)
		ttk.Label(f, text="Перегляд довідників і основних сутностей (readonly)").pack(anchor="w")
		self._swap(f)

	def _show_crud(self):
		f = ttk.Frame(self.container, padding=12)
		ttk.Label(f, text="CRUD: додати/редагувати/видалити/пошук (тимчасово недоступно)").pack(anchor="w")
		self._swap(f)

	def _show_queries(self):
		f = QueriesFrame(self.container, self.db)
		self._swap(f)

	def _show_users(self):
		f = ttk.Frame(self.container, padding=12)
		ttk.Label(f, text="Користувачі: додавання/права/заявки гостей (буде додано)").pack(anchor="w")
		self._swap(f)

	def _logout(self):
		self.on_logout()
