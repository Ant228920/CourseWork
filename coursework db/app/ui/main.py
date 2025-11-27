import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthService

from ui.queries import QueriesFrame
from ui.crud import CRUDFrame
from ui.view import ViewFrame
from ui.hierarchy_view import HierarchyTree

# ========================================================
# ПРАВА ДОСТУПУ
# ========================================================
ROLES = {
    "Administrator": {"users": True, "crud": True, "queries": True, "view": True, "schedule": True},
    "Operator": {"users": False, "crud": True, "queries": True, "view": True, "schedule": True},
    "Authorized": {"users": False, "crud": False, "queries": True, "view": True, "schedule": True},
    "Guest": {"users": False, "crud": False, "queries": False, "view": True, "schedule": False},
}

# ========================================================
# ТЕКСТИ ДЛЯ ДОВІДКИ (F1)
# ========================================================
HELP_TEXTS = {
    "Guest": """👋 ВІТАЄМО (Гість)

Ваші права обмежені режимом читання.

✅ ВАМ ДОСТУПНО:
📂 Вкладка "Перегляд": Ви можете переглядати лише загальні довідкові таблиці (наприклад, довідники звань чи типів техніки).

⛔ НЕДОСТУПНО:
- Аналітичні запити та звіти.
- Перегляд ієрархії підрозділів.
- Будь-яке редагування даних.
""",

    "Authorized": """✅ КОРИСТУВАЧ (Authorized)

Ви маєте доступ до перегляду та аналізу даних.

✅ ВАМ ДОСТУПНО:
📂 Вкладка "Перегляд": Повний доступ до перегляду всіх таблиць.
📊 Вкладка "Запити": Виконання складних аналітичних звітів (фільтрація даних).
📅 Вкладка "Графік": Перегляд структури підрозділів у вигляді ієрархічного дерева.
👤 Профіль: Зміна власного пароля.

⛔ НЕДОСТУПНО:
- Редагування, додавання або видалення даних.
""",

    "Operator": """🛠 ОПЕРАТОР

Ви маєте права на ведення бази даних.

✅ ВАМ ДОСТУПНО:
Все, що доступно звичайному користувачу (Перегляд, Запити, Графік), ПЛЮС:

✏️ Вкладка "Редагування" (CRUD):
- Створення нових записів.
- Редагування існуючих даних.
- Видалення записів.

Ваша задача — підтримувати актуальність даних у системі.
""",

    "Administrator": """👑 АДМІНІСТРАТОР

Повний доступ до управління системою.

✅ ВАМ ДОСТУПНО:
Всі функції Оператора (CRUD, Аналітика, Ієрархія), ПЛЮС:

🛡️ Вкладка "Адмін-панель":
1. Заявки: Підтвердження реєстрації нових користувачів та зміна їх ролей.
2. Користувачі: Перегляд списку всіх акаунтів.
3. SQL Консоль: Виконання прямих SQL-запитів до бази даних (для технічного обслуговування).
"""
}


class MainFrame(tk.Frame):
    def __init__(self, master, db, user, on_logout):
        super().__init__(master)
        self.db = db
        self.user = user
        self.on_logout = on_logout

        # Прив'язка клавіші F1
        self.master.bind('<F1>', self._show_help)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- TOOLBAR ---
        toolbar = ttk.Frame(self, padding=(10, 10))
        toolbar.grid(row=0, column=0, sticky="ew")

        role = user.get("role", "Guest")
        caps = ROLES.get(role, ROLES["Guest"])

        # Ліва частина (Навігація)
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side=tk.LEFT)

        if caps["view"]:
            ttk.Button(nav_frame, text="📂 Перегляд", command=self._show_view).pack(side=tk.LEFT, padx=5)
        if caps["crud"]:
            ttk.Button(nav_frame, text="✏️ Редагування", command=self._show_crud).pack(side=tk.LEFT, padx=5)
        if caps["queries"]:
            ttk.Button(nav_frame, text="📊 Запити", command=self._show_queries).pack(side=tk.LEFT, padx=5)
        if caps.get("schedule"):
            ttk.Button(nav_frame, text="📅 Графік", command=self._show_schedule).pack(side=tk.LEFT, padx=5)
        if caps["users"]:
            ttk.Button(nav_frame, text="🛡️ Адмін-панель", command=self._show_users).pack(side=tk.LEFT, padx=5)

        ttk.Button(nav_frame, text="❓ Допомога (F1)", command=self._show_help).pack(side=tk.LEFT, padx=15)

        # Права частина (Профіль)
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.RIGHT)

        ttk.Label(user_frame, text=f"{role}", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Separator(user_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5, pady=2)
        ttk.Button(user_frame, text="👤 Профіль", command=self._show_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text="🚪 Вийти", command=self._logout).pack(side=tk.LEFT, padx=5)

        # Основний контейнер
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._current = None
        self._show_view()

    def _swap(self, frame):
        if self._current:
            self._current.destroy()
        self._current = frame
        self._current.grid(row=0, column=0, sticky="nsew")

    def _show_view(self):
        self._swap(ViewFrame(self.container, self.db))

    def _show_crud(self):
        self._swap(CRUDFrame(self.container, self.db))

    def _show_queries(self):
        self._swap(QueriesFrame(self.container, self.db))

    def _show_schedule(self):
        self._swap(HierarchyTree(self.container, self.db))

    def _show_profile(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=30)
        self._swap(f)

        ttk.Label(f, text="👤 Профіль користувача", font=("Segoe UI", 24, "bold")).pack(pady=(0, 20))

        if self.user.get("role") == "Guest":
            info_frame = ttk.Frame(f, padding=20)
            info_frame.pack(fill=tk.X, pady=20)
            ttk.Label(info_frame, text="⛔ Обмежений доступ", font=("Segoe UI", 14, "bold"), foreground="red").pack(
                pady=10)
            msg = "У гостьовому режимі профіль користувача відсутній.\nБудь ласка, зареєструйтеся."
            ttk.Label(info_frame, text=msg, font=("Segoe UI", 11), justify="center").pack(pady=10)
            ttk.Button(info_frame, text="📝 Вийти та Зареєструватися", command=self._logout, width=30).pack(pady=20,
                                                                                                           ipady=5)
            return

        box = ttk.LabelFrame(f, text=" Дані акаунту ", padding=20)
        box.pack(fill=tk.X, pady=10)
        ttk.Label(box, text=f"Логін: {self.user['login']}", font=("Segoe UI", 12)).pack(anchor="w")
        ttk.Label(box, text=f"Роль: {self.user['role']}", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        pass_box = ttk.LabelFrame(f, text=" Безпека ", padding=20)
        pass_box.pack(fill=tk.X, pady=10)
        ttk.Label(pass_box, text="Новий пароль:", font=("Segoe UI", 10)).pack(anchor="w")
        new_pass_entry = ttk.Entry(pass_box, show="*", width=30)
        new_pass_entry.pack(anchor="w", pady=5)

        def change_pass():
            try:
                np = new_pass_entry.get().strip()
                if len(np) < 4:
                    messagebox.showwarning("Помилка", "Мін. 4 символи.")
                    return
                AuthService(self.db).change_password(self.user["login"], np)
                messagebox.showinfo("Успіх", "Пароль змінено!")
                new_pass_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(pass_box, text="💾 Зберегти", command=change_pass).pack(pady=10, anchor="e")

    # =====================================================
    # АДМІН ПАНЕЛЬ (ВИПРАВЛЕНО ВІДСТУПИ)
    # =====================================================
    def _show_users(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=10)
        self._swap(f)

        ttk.Label(f, text="Панель Адміністратора", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))
        notebook = ttk.Notebook(f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: ЗАЯВКИ ---
        tab_req = ttk.Frame(notebook, padding=10)
        notebook.add(tab_req, text="Заявки")

        cols = ("id", "user_id", "login", "request_type", "status", "created_at")
        tree = ttk.Treeview(tab_req, columns=cols, show="headings", height=15)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True)  # 🔥 Виніс з циклу

        def load_requests():
            try:
                for i in tree.get_children(): tree.delete(i)
                sql = "SELECT id, user_id, login, request_type, status, created_at FROM requests WHERE status = 'pending'"
                rows = self.db.query(sql)
                for r in rows:
                    tree.insert("", tk.END, values=(r["id"], r["user_id"], r["login"], r["request_type"], r["status"],
                                                    r["created_at"]))
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        load_requests()

        btn_frame = ttk.Frame(tab_req, padding=(0, 10))
        btn_frame.pack(fill=tk.X)

        def process_request(action):
            item = tree.focus()
            if not item: return
            rid = tree.item(item)["values"][0]
            try:
                srv = AuthService(self.db)
                if action == 'approve':
                    srv.admin_approve_request(rid)
                    messagebox.showinfo("Успіх", "Схвалено!")
                else:
                    srv.admin_reject_request(rid)
                    messagebox.showinfo("Успіх", "Відхилено.")
                load_requests()
                load_users()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(btn_frame, text="✅ Схвалити", command=lambda: process_request('approve')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Відхилити", command=lambda: process_request('reject')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Оновити", command=load_requests).pack(side=tk.RIGHT)

        # --- TAB 2: КОРИСТУВАЧІ ---
        tab_users = ttk.Frame(notebook, padding=10)
        notebook.add(tab_users, text="Користувачі")

        cols_u = ("id", "login", "role")
        tree_u = ttk.Treeview(tab_users, columns=cols_u, show="headings", height=15)
        for c in cols_u: tree_u.heading(c, text=c)
        tree_u.pack(fill=tk.BOTH, expand=True)

        def load_users():
            try:
                for i in tree_u.get_children(): tree_u.delete(i)
                sql = "SELECT u.id, k.login, r.name as role FROM users u JOIN keys k ON k.user_id = u.id JOIN roles r ON k.role_id = r.id ORDER BY u.id"
                for r in self.db.query(sql):
                    tree_u.insert("", tk.END, values=(r["id"], r["login"], r["role"]))
            except Exception:
                pass

        load_users()
        ttk.Button(tab_users, text="🔄 Оновити", command=load_users).pack(pady=5, anchor="e")

        # --- TAB 3: SQL КОНСОЛЬ ---
        tab_sql = ttk.Frame(notebook, padding=10)
        notebook.add(tab_sql, text="SQL Консоль")

        top_f = ttk.Frame(tab_sql)
        top_f.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(top_f, text="SQL Query:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        sql_text = tk.Text(top_f, height=5, font=("Consolas", 10))
        sql_text.pack(fill=tk.X, pady=5)

        res_f = ttk.Frame(tab_sql)
        res_f.pack(fill=tk.BOTH, expand=True)
        sc_y = ttk.Scrollbar(res_f);
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)
        sc_x = ttk.Scrollbar(res_f, orient=tk.HORIZONTAL);
        sc_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree_sql = ttk.Treeview(res_f, show="headings", yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        sc_y.config(command=tree_sql.yview);
        sc_x.config(command=tree_sql.xview)
        tree_sql.pack(fill=tk.BOTH, expand=True)

        lbl_status = ttk.Label(top_f, text="Ready", font=("Segoe UI", 9))
        lbl_status.pack(anchor="w")

        def run_sql():
            q = sql_text.get("1.0", tk.END).strip()
            if not q: return
            tree_sql.delete(*tree_sql.get_children())
            tree_sql["columns"] = []
            try:
                if q.upper().startswith("SELECT"):
                    if hasattr(self.db, 'query_with_columns'):
                        cols, rows = self.db.query_with_columns(q)
                    else:
                        rows = self.db.query(q)
                        cols = list(rows[0].keys()) if rows else ["Result"]

                    tree_sql["columns"] = cols
                    for c in cols: tree_sql.heading(c, text=c); tree_sql.column(c, width=100)
                    for r in rows: tree_sql.insert("", tk.END,
                                                   values=tuple(r) if isinstance(r, (list, tuple)) else tuple(
                                                       r.values()))
                    lbl_status.config(text=f"Rows: {len(rows)}", foreground="green")
                else:
                    af = self.db.execute(q)
                    lbl_status.config(text=f"Affected: {af}", foreground="blue")
            except Exception as e:
                lbl_status.config(text=f"Error: {e}", foreground="red")
                messagebox.showerror("SQL Error", str(e))

        ttk.Button(top_f, text="▶ Run", command=run_sql).pack(anchor="e")

    def _show_help(self, event=None):
        role = self.user.get("role", "Guest")
        text = HELP_TEXTS.get(role, "")
        win = tk.Toplevel(self)
        win.title("Довідка")
        win.geometry("600x400")
        t = tk.Text(win, wrap=tk.WORD, padx=10, pady=10);
        t.pack(fill=tk.BOTH, expand=True)
        t.insert("1.0", text);
        t.config(state=tk.DISABLED)

    def _logout(self):
        if messagebox.askyesno("Вихід", "Вийти з системи?"):
            self.master.unbind('<F1>')
            self.on_logout()