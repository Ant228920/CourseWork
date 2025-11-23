import tkinter as tk
from tkinter import ttk, messagebox
from ui.queries import QueriesFrame
from ui.crud import CRUDFrame
from auth import AuthService

# НАЛАШТУВАННЯ ПРАВ ДОСТУПУ
# True = кнопка є, False = кнопки немає
ROLES = {
    "Administrator": {"users": True, "crud": True, "queries": True, "view": True},
    "Operator": {"users": False, "crud": True, "queries": True, "view": True},
    "Authorized": {"users": False, "crud": False, "queries": True, "view": True},
    "Guest": {"users": False, "crud": False, "queries": False, "view": True},
}


class MainFrame(tk.Frame):
    def __init__(self, master, db, user, on_logout):
        super().__init__(master)
        self.db = db
        self.user = user
        self.on_logout = on_logout

        # Діагностика (можна прибрати потім)
        print(f"LOGIN DEBUG: User={user.get('login')}, Role={user.get('role')}")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Панель інструментів
        toolbar = ttk.Frame(self, padding=6)
        toolbar.grid(row=0, column=0, sticky="ew")

        # Отримуємо права
        role = user.get("role")
        # Якщо раптом роль прийшла 'Адміністратор' (укр), а в словнику 'Administrator' (англ),
        # то get поверне Guest. Тому важливо, щоб в базі були англійські назви.
        # Але про всяк випадок додамо fallback:
        if role not in ROLES:
            print(f"WARNING: Role '{role}' not found in config, defaulting to Guest")
            caps = ROLES["Guest"]
        else:
            caps = ROLES[role]

        # --- ЛІВА ЧАСТИНА (ФУНКЦІОНАЛ) ---

        # 1. Перегляд
        if caps["view"]:
            ttk.Button(toolbar, text="Перегляд", command=self._show_view).pack(side=tk.LEFT, padx=2)

        # 2. CRUD
        if caps["crud"]:
            self.btn_crud = ttk.Button(toolbar, text="CRUD", command=self._show_crud)
            self.btn_crud.pack(side=tk.LEFT, padx=2)

        # 3. Запити
        if caps["queries"]:
            self.btn_queries = ttk.Button(toolbar, text="Запити", command=self._show_queries)
            self.btn_queries.pack(side=tk.LEFT, padx=2)

        # 4. Адмінка
        if caps["users"]:
            self.btn_users = ttk.Button(toolbar, text="Користувачі", command=self._show_users)
            self.btn_users.pack(side=tk.LEFT, padx=2)

        # --- ПРАВА ЧАСТИНА (СИСТЕМНА) ---

        ttk.Label(toolbar, text=f"Роль: {role}").pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="Вийти", command=self._logout).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="👤 Мій профіль", command=self._show_profile).pack(side=tk.RIGHT, padx=2)

        # Основний контент
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._current = None
        self._show_view()

    def _swap(self, frame):
        if self._current: self._current.destroy()
        self._current = frame
        self._current.grid(row=0, column=0, sticky="nsew")

    def _show_view(self):
        # Спробуємо використати ViewFrame, якщо він є. Якщо ні - заглушка.
        try:
            from ui.view import ViewFrame
            f = ViewFrame(self.container, self.db)
        except ImportError:
            f = ttk.Frame(self.container, padding=12)
            ttk.Label(f, text="Ласкаво просимо до системи військового округу", font=("Arial", 14)).pack(pady=20)
            if self.user.get('role') == 'Guest':
                ttk.Label(f, text="Ваш статус: Гість. Функціонал обмежено.", foreground="grey").pack()

        self._swap(f)

    def _show_crud(self):
        self._swap(CRUDFrame(self.container, self.db))

    def _show_queries(self):
        self._swap(QueriesFrame(self.container, self.db))

    def _show_profile(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=20)
        self._swap(f)

        current_login = self.user.get('login')
        current_role = self.user.get('role')
        current_email = self.user.get('email') or "Не вказано"

        ttk.Label(f, text=f"Профіль користувача: {current_login}", font=("Arial", 16, "bold")).pack(pady=(0, 10),
                                                                                                    anchor="w")

        # Логіка для ГOСТЯ
        if current_role == 'Guest':
            info_frame = ttk.LabelFrame(f, text="Статус акаунта", padding=15)
            info_frame.pack(fill=tk.X, pady=10)
            ttk.Label(info_frame, text="Ви використовуєте тимчасовий гостьовий доступ.", font=("Arial", 11)).pack(
                anchor="w", pady=(0, 10))
            ttk.Button(info_frame, text="📝 Зареєструватися (Вихід)", command=self._logout).pack(anchor="w", pady=5)
            return

        # Логіка для ПОВНОЦІННИХ юзерів
        info_frame = ttk.LabelFrame(f, text="Інформація", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        ttk.Label(info_frame, text=f"Роль: {current_role}", font=("Arial", 11)).pack(anchor="w")
        ttk.Label(info_frame, text=f"Email: {current_email}", font=("Arial", 11)).pack(anchor="w")

        pass_frame = ttk.LabelFrame(f, text="Зміна пароля", padding=15)
        pass_frame.pack(fill=tk.X, pady=20)
        ttk.Label(pass_frame, text="Новий пароль:").grid(row=0, column=0, sticky="w", pady=5)
        entry_new_pass = ttk.Entry(pass_frame, show="*", width=30)
        entry_new_pass.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        def save_new_password():
            new_p = entry_new_pass.get().strip()
            if len(new_p) < 4:
                messagebox.showwarning("Помилка", "Пароль надто короткий!")
                return
            try:
                # from app.auth import AuthService
                AuthService(self.db).change_password(current_login, new_p)
                messagebox.showinfo("Успіх", "Ваш пароль змінено!")
                entry_new_pass.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(pass_frame, text="💾 Зберегти", command=save_new_password).grid(row=1, column=1, sticky="e", pady=10)

    def _show_users(self):
        # АДМІН-ПАНЕЛЬ
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=10)
        self._swap(f)

        notebook = ttk.Notebook(f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: ЗАЯВКИ (Реєстрація) ---
        tab_req = ttk.Frame(notebook)
        notebook.add(tab_req, text="Реєстрація / Ролі")

        cols_req = ("id", "login", "status", "type")
        tree_req = ttk.Treeview(tab_req, columns=cols_req, show="headings")
        tree_req.heading("id", text="ID")
        tree_req.heading("login", text="Логін")
        tree_req.heading("status", text="Статус")
        tree_req.heading("type", text="Тип запиту")
        tree_req.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_req():
            for i in tree_req.get_children(): tree_req.delete(i)
            # Показуємо запити на роль (role_operator, role_authorized)
            sql = "SELECT id, login, status, request_type FROM requests WHERE status='pending' AND request_type LIKE 'role_%'"
            for r in self.db.query(sql):
                tree_req.insert("", tk.END, values=(r['id'], r['login'], r['status'], r['request_type']))

        btn_fr_req = ttk.Frame(tab_req)
        btn_fr_req.pack(fill=tk.X, pady=5)

        def process_role(action):
            sel = tree_req.selection()
            if not sel: return
            rid = tree_req.item(sel[0])['values'][0]
            try:
                # from app.auth import AuthService
                AuthService(self.db).admin_process_request(rid, action)
                refresh_req()
                messagebox.showinfo("ОК", "Оброблено")
            except Exception as e:
                messagebox.showerror("ERR", str(e))

        ttk.Button(btn_fr_req, text="✅ Схвалити", command=lambda: process_role('approve')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_req, text="❌ Відхилити", command=lambda: process_role('reject')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_req, text="🔄 Оновити", command=refresh_req).pack(side=tk.RIGHT)
        refresh_req()

        # --- TAB 2: ВІДНОВЛЕННЯ ПАРОЛІВ ---
        tab_res = ttk.Frame(notebook)
        notebook.add(tab_res, text="Відновлення паролів")

        cols_res = ("id", "login", "status", "date")
        tree_res = ttk.Treeview(tab_res, columns=cols_res, show="headings")
        tree_res.heading("id", text="ID")
        tree_res.heading("login", text="Логін")
        tree_res.heading("status", text="Статус")
        tree_res.heading("date", text="Дата")
        tree_res.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_res():
            for i in tree_res.get_children(): tree_res.delete(i)
            sql = "SELECT id, login, status, created_at FROM requests WHERE status='pending' AND request_type='password_reset'"
            for r in self.db.query(sql):
                vals = list(r.values()) if isinstance(r, dict) else r
                tree_res.insert("", tk.END, values=vals)

        btn_fr_res = ttk.Frame(tab_res)
        btn_fr_res.pack(fill=tk.X, pady=5)

        def process_pass(action):
            sel = tree_res.selection()
            if not sel: return
            rid = tree_res.item(sel[0])['values'][0]
            try:
                # from app.auth import AuthService
                AuthService(self.db).admin_process_request(rid, action)
                refresh_res()
                msg = "Дозволено зміну" if action == 'approve' else "Відхилено"
                messagebox.showinfo("ОК", msg)
            except Exception as e:
                messagebox.showerror("ERR", str(e))

        ttk.Button(btn_fr_res, text="✅ Дозволити зміну", command=lambda: process_pass('approve')).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(btn_fr_res, text="❌ Відхилити", command=lambda: process_pass('reject')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_res, text="🔄 Оновити", command=refresh_res).pack(side=tk.RIGHT)
        refresh_res()

        # --- TAB 3: ВСІ КОРИСТУВАЧІ ---
        tab_users = ttk.Frame(notebook)
        notebook.add(tab_users, text="Всі користувачі")

        cols_usr = ("id", "login", "role")
        tree_usr = ttk.Treeview(tab_users, columns=cols_usr, show="headings")
        for c in cols_usr: tree_usr.heading(c, text=c.capitalize())
        tree_usr.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_users():
            for i in tree_usr.get_children(): tree_usr.delete(i)
            # Показуємо користувачів та їхні ролі з таблиці keys
            sql = "SELECT k.id, k.login, r.name FROM keys k JOIN roles r ON r.id=k.role_id ORDER BY k.id"
            for r in self.db.query(sql):
                vals = list(r.values()) if isinstance(r, dict) else r
                tree_usr.insert("", tk.END, values=vals)

        ttk.Button(tab_users, text="🔄 Оновити", command=refresh_users).pack(pady=5)
        refresh_users()

    def _logout(self):
        self.on_logout()