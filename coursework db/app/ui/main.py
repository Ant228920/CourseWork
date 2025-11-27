import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

from ui.queries import QueriesFrame
from ui.crud import CRUDFrame
from ui.view import ViewFrame
from ui.hierarchy_view import HierarchyTree
from auth import AuthService

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
# ТЕКСТИ ДЛЯ F1
# ========================================================
HELP_TEXTS = {
    "Guest": "Гостьовий доступ…",
    "Authorized": "Авторизований користувач…",
    "Operator": "Оператор…",
    "Administrator": "Адміністратор…"
}


# ======================================================================
# ГОЛОВНИЙ КЛАС ІНТЕРФЕЙСУ
# ======================================================================
class MainFrame(tk.Frame):
    def __init__(self, master, db, user, on_logout):
        super().__init__(master)
        self.db = db
        self.user = user
        self.on_logout = on_logout

        self.master.bind('<F1>', self._show_help)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # =====================================================
        # ВЕРХНЯ ПАНЕЛЬ
        # =====================================================
        toolbar = ttk.Frame(self, padding=(10, 10))
        toolbar.grid(row=0, column=0, sticky="ew")

        role = user.get("role", "Guest")
        caps = ROLES.get(role, ROLES["Guest"])

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

        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.RIGHT)

        ttk.Label(user_frame, text=f"{role}", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(user_frame, text="👤 Профіль", command=self._show_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text="🚪 Вийти", command=self._logout).pack(side=tk.LEFT, padx=5)

        # Основний контейнер
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._current = None
        self._show_view()

    # =====================================================
    # НАВІГАЦІЯ
    # =====================================================
    def _swap(self, frame):
        if self._current:
            self._current.destroy()
        self._current = frame
        self._current.grid(row=0, column=0, sticky="nsew")

    def _show_view(self):
        try:
            self._swap(ViewFrame(self.container, self.db))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити перегляд.\n{e}")

    def _show_crud(self):
        try:
            self._swap(CRUDFrame(self.container, self.db))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити редагування.\n{e}")

    def _show_queries(self):
        try:
            self._swap(QueriesFrame(self.container, self.db))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити запити.\n{e}")

    def _show_schedule(self):
        try:
            self._swap(HierarchyTree(self.container, self.db))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити графік.\n{e}")

    # =====================================================
    # ПРОФІЛЬ
    # =====================================================
    def _show_profile(self):
        try:
            if self._current:
                self._current.destroy()

            f = ttk.Frame(self.container, padding=30)
            self._swap(f)

            ttk.Label(f, text="👤 Профіль користувача", font=("Segoe UI", 26, "bold")).pack(pady=(0, 20))

            # -------------------- ІНФОРМАЦІЯ --------------------
            box = ttk.LabelFrame(f, text=" Інформація ", padding=20)
            box.pack(fill=tk.X, pady=10)

            ttk.Label(box, text=f"Логін: {self.user['login']}", font=("Segoe UI", 14)).pack(anchor="w")
            ttk.Label(box, text=f"Роль: {self.user['role']}", font=("Segoe UI", 14)).pack(anchor="w")

            # -------------------- ЗМІНА ПАРОЛЯ --------------------
            pass_box = ttk.LabelFrame(f, text=" Змінити пароль ", padding=20)
            pass_box.pack(fill=tk.X, pady=10)

            ttk.Label(pass_box, text="Новий пароль:", font=("Segoe UI", 12)).pack(anchor="w")

            new_pass_entry = ttk.Entry(pass_box, show="*", width=30)
            new_pass_entry.pack(anchor="w", pady=5)

            def change_pass():
                try:
                    new_pass = new_pass_entry.get().strip()

                    if len(new_pass) < 6:
                        messagebox.showwarning("Помилка", "Пароль має містити мінімум 6 символів.")
                        return

                    AuthService(self.db).change_password(self.user["login"], new_pass)

                    messagebox.showinfo("Успіх", "Пароль успішно змінено!")
                    new_pass_entry.delete(0, tk.END)

                except Exception as e:
                    messagebox.showerror("Помилка", f"Не вдалося змінити пароль.\n{e}")

            ttk.Button(pass_box, text="Змінити пароль", command=change_pass).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити профіль.\n{e}")

    # =====================================================
    # АДМІНІСТРАТОР: ЗАЯВКИ
    # =====================================================
    def _show_users(self):
        if self._current:
            self._current.destroy()

        f = ttk.Frame(self.container, padding=10)
        self._swap(f)

        ttk.Label(f, text="Панель адміністратора", font=("Segoe UI", 20, "bold")).pack(anchor="w")

        notebook = ttk.Notebook(f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # TAB 1 — заявки
        tab_req = ttk.Frame(notebook, padding=10)
        notebook.add(tab_req, text="Заявки")

        cols = ("id", "user_id", "login", "request_type", "status", "created_at")
        tree = ttk.Treeview(tab_req, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120)

        tree.pack(fill=tk.BOTH, expand=True)

        def load_requests():
            try:
                for i in tree.get_children():
                    tree.delete(i)

                sql = """
                    SELECT id, user_id, login, request_type, status, created_at
                    FROM requests
                    WHERE status = 'pending'
                """
                rows = self.db.query(sql)

                for r in rows:
                    tree.insert("", tk.END, values=(
                        r["id"], r["user_id"], r["login"], r["request_type"],
                        r["status"], r["created_at"]
                    ))
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося завантажити заявки.\n{e}")

        load_requests()

        # ---------- КНОПКИ ----------
        btn_frame = ttk.Frame(tab_req)
        btn_frame.pack(fill=tk.X, pady=10)

        def approve():
            try:
                item = tree.focus()
                if not item:
                    messagebox.showwarning("Увага", "Оберіть заявку.")
                    return

                rid, user_id, login, rtype, status, created_at = tree.item(item)["values"]

                if rtype == "change_password":
                    new_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    AuthService(self.db).change_password(login, new_pass)
                    messagebox.showinfo("Успіх", f"Пароль змінено!\nНовий пароль: {new_pass}")

                elif rtype in ("change_role", "register"):
                    self.db.execute("UPDATE users SET role='Authorized' WHERE id=%s", (user_id,))
                    messagebox.showinfo("Успіх", "Роль користувача оновлено.")

                self.db.execute("UPDATE requests SET status='approved', processed_at=NOW() WHERE id=%s", (rid,))
                load_requests()
                messagebox.showinfo("Готово", "Заявку схвалено.")

            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося схвалити заявку.\n{e}")

        def reject():
            try:
                item = tree.focus()
                if not item:
                    messagebox.showwarning("Увага", "Оберіть заявку.")
                    return

                rid = tree.item(item)["values"][0]
                self.db.execute("UPDATE requests SET status='rejected', processed_at=NOW() WHERE id=%s", (rid,))
                load_requests()
                messagebox.showinfo("Готово", "Заявку відхилено.")

            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відхилити заявку.\n{e}")

        ttk.Button(btn_frame, text="✅ Підтвердити", command=approve).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Відхилити", command=reject).pack(side=tk.LEFT, padx=5)

        # TAB 2 — Користувачі
        tab_users = ttk.Frame(notebook, padding=10)
        notebook.add(tab_users, text="Користувачі")

        cols_u = ("id", "login", "role")
        tree_u = ttk.Treeview(tab_users, columns=cols_u, show="headings")
        for c in cols_u:
            tree_u.heading(c, text=c)

        tree_u.pack(fill=tk.BOTH, expand=True)

        def load_users():
            try:
                for i in tree_u.get_children():
                    tree_u.delete(i)

                sql = """
                      SELECT users.id,
                             keys.login,
                             roles.name AS role
                      FROM users
                      JOIN keys ON keys.user_id = users.id
                      JOIN roles ON roles.id = keys.role_id
                      ORDER BY users.id;
                      """
                for r in self.db.query(sql):
                    tree_u.insert("", tk.END, values=(r["id"], r["login"], r["role"]))

            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося завантажити список користувачів.\n{e}")

        load_users()

    # =====================================================
    # ДОВІДКА
    # =====================================================
    def _show_help(self, event=None):
        role = self.user.get("role", "Guest")
        text = HELP_TEXTS.get(role, "Довідка недоступна.")

        win = tk.Toplevel(self)
        win.title("Довідка")
        win.geometry("600x400")

        t = tk.Text(win, wrap=tk.WORD)
        t.pack(fill=tk.BOTH, expand=True)
        t.insert("1.0", text)
        t.config(state=tk.DISABLED)

    # =====================================================
    # ВИХІД
    # =====================================================
    def _logout(self):
        self.master.unbind('<F1>')
        self.on_logout()
