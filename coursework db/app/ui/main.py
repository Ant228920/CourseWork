import tkinter as tk
from tkinter import ttk, messagebox
from ui.queries import QueriesFrame
from ui.crud import CRUDFrame
from auth import AuthService

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

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self, padding=6)
        toolbar.grid(row=0, column=0, sticky="ew")

        role = user.get("role")
        caps = ROLES.get(role, ROLES["Guest"])

        ttk.Button(toolbar, text="Перегляд", command=self._show_view).pack(side=tk.LEFT, padx=2)

        self.btn_crud = ttk.Button(toolbar, text="CRUD", command=self._show_crud,
                                   state=(tk.NORMAL if caps["crud"] else tk.DISABLED))
        self.btn_crud.pack(side=tk.LEFT, padx=2)

        self.btn_queries = ttk.Button(toolbar, text="Запити", command=self._show_queries,
                                      state=(tk.NORMAL if caps["queries"] else tk.DISABLED))
        self.btn_queries.pack(side=tk.LEFT, padx=2)

        self.btn_users = ttk.Button(toolbar, text="Користувачі", command=self._show_users,
                                    state=(tk.NORMAL if caps["users"] else tk.DISABLED))
        self.btn_users.pack(side=tk.LEFT, padx=2)

        ttk.Label(toolbar, text=f"Роль: {role}").pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="Вийти", command=self._logout).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="👤 Мій профіль", command=self._show_profile).pack(side=tk.RIGHT, padx=2)

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
        f = ttk.Frame(self.container, padding=12)
        ttk.Label(f, text="Ласкаво просимо до системи військового округу", font=("Arial", 14)).pack(pady=20)
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

        ttk.Label(f, text=f"Профіль: {current_login}", font=("Arial", 16, "bold")).pack(pady=(0, 10), anchor="w")

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
                AuthService(self.db).change_password(current_login, new_p)
                messagebox.showinfo("Успіх", "Ваш пароль змінено!")
                entry_new_pass.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(pass_frame, text="💾 Зберегти", command=save_new_password).grid(row=1, column=1, sticky="e", pady=10)

    def _show_users(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=10)
        self._swap(f)

        notebook = ttk.Notebook(f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: GUEST REQUESTS ---
        tab_requests = ttk.Frame(notebook)
        notebook.add(tab_requests, text="Заявки на реєстрацію")

        cols_req = ("id", "login", "status", "comment")
        tree_req = ttk.Treeview(tab_requests, columns=cols_req, show="headings")
        for c in cols_req: tree_req.heading(c, text=c.capitalize())
        tree_req.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_requests():
            for i in tree_req.get_children(): tree_req.delete(i)
            sql = "SELECT ar.id, k.login, ar.status, ar.comment FROM access_requests ar JOIN keys k ON k.user_id=ar.user_id WHERE ar.status='pending'"
            for r in self.db.query(sql): tree_req.insert("", tk.END, values=list(r.values()))

        btn_frame_req = ttk.Frame(tab_requests)
        btn_frame_req.pack(fill=tk.X, pady=5)

        def approve_guest():
            sel = tree_req.selection()
            if not sel: return
            item = tree_req.item(sel[0])
            rid, rlogin = item['values'][0], item['values'][1]
            try:
                self.db.execute("UPDATE access_requests SET status='approved' WHERE id=%s", [rid])
                self.db.execute("UPDATE keys SET role_id=3 WHERE login=%s", [rlogin])  # 3=Authorized
                self.db.execute("UPDATE users SET role_id=3 WHERE login=%s", [rlogin])
                refresh_requests()
                messagebox.showinfo("ОК", f"Доступ надано: {rlogin}")
            except Exception as e:
                messagebox.showerror("ERR", str(e))

        ttk.Button(btn_frame_req, text="✅ Надати доступ", command=approve_guest).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_req, text="🔄 Оновити", command=refresh_requests).pack(side=tk.RIGHT)
        refresh_requests()

        # --- TAB 2: PASSWORD RESETS ---
        tab_resets = ttk.Frame(notebook)
        notebook.add(tab_resets, text="Відновлення паролів")

        cols_res = ("id", "login", "status", "date")
        tree_res = ttk.Treeview(tab_resets, columns=cols_res, show="headings")
        for c in cols_res: tree_res.heading(c, text=c.capitalize())
        tree_res.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_resets():
            for i in tree_res.get_children(): tree_res.delete(i)
            sql = "SELECT id, login, status, created_at FROM password_resets WHERE status='pending' ORDER BY created_at DESC"
            for r in self.db.query(sql):
                vals = list(r.values()) if isinstance(r, dict) else r
                tree_res.insert("", tk.END, values=vals)

        btn_frame_res = ttk.Frame(tab_resets)
        btn_frame_res.pack(fill=tk.X, pady=5)

        def approve_reset():
            sel = tree_res.selection()
            if not sel: return
            req_id, req_login = tree_res.item(sel[0])['values'][0], tree_res.item(sel[0])['values'][1]
            if messagebox.askyesno("Підтвердження", f"Дозволити користувачу {req_login} змінити пароль?"):
                AuthService(self.db).admin_approve_request(req_id)
                refresh_resets()
                messagebox.showinfo("Успіх", "Заявку схвалено.")

        def deny_reset():
            sel = tree_res.selection()
            if not sel: return
            req_id = tree_res.item(sel[0])['values'][0]
            AuthService(self.db).admin_reject_request(req_id)
            refresh_resets()
            messagebox.showinfo("Відхилено", "Заявку відхилено.")

        ttk.Button(btn_frame_res, text="✅ Схвалити", command=approve_reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_res, text="❌ Відхилити", command=deny_reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_res, text="🔄 Оновити", command=refresh_resets).pack(side=tk.RIGHT)
        refresh_resets()

        # --- TAB 3: ALL USERS ---
        tab_users = ttk.Frame(notebook)
        notebook.add(tab_users, text="Всі користувачі")

        cols_usr = ("id", "login", "role")
        tree_usr = ttk.Treeview(tab_users, columns=cols_usr, show="headings")
        for c in cols_usr: tree_usr.heading(c, text=c.capitalize())
        tree_usr.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_users():
            for i in tree_usr.get_children(): tree_usr.delete(i)
            sql = "SELECT k.id, k.login, r.name FROM keys k JOIN roles r ON r.id=k.role_id ORDER BY k.id"
            for r in self.db.query(sql): tree_usr.insert("", tk.END, values=list(r.values()))

        ttk.Button(tab_users, text="🔄 Оновити", command=refresh_users).pack(pady=5)
        refresh_users()

    def _logout(self):
        self.on_logout()