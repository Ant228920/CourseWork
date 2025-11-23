import tkinter as tk
from tkinter import ttk, messagebox
from ui.queries import QueriesFrame
from ui.crud import CRUDFrame
from ui.view import ViewFrame
from auth import AuthService

# ========================================================
# НАЛАШТУВАННЯ ПРАВ ДОСТУПУ
# ========================================================
ROLES = {
    "Administrator": {"users": True, "crud": True, "queries": True, "view": True},
    "Operator": {"users": False, "crud": True, "queries": True, "view": True},
    "Authorized": {"users": False, "crud": False, "queries": True, "view": True},
    "Guest": {"users": False, "crud": False, "queries": False, "view": True},
}

# ========================================================
# ТЕКСТИ ІНСТРУКЦІЙ (ДЛЯ F1)
# ========================================================
HELP_TEXTS = {
    "Guest": """
👋 ВІТАЄМО В СИСТЕМІ! (Роль: Гість)

Ви увійшли з обмеженими правами перегляду.
Ваші можливості:
🔹 Перегляд: Доступ до загальних довідників (список округів, типи техніки).

⛔ Обмеження:
- Ви не можете бачити детальні дані про особовий склад.
- Ви не можете виконувати аналітичні запити.
- Ви не можете редагувати дані.

💡 Як отримати доступ?
Перейдіть у вкладку "👤 Мій профіль" та натисніть кнопку "Зареєструватися". 
Оберіть бажану роль (наприклад, Оператор) та очікуйте підтвердження адміністратора.
""",

    "Authorized": """
✅ ІНСТРУКЦІЯ КОРИСТУВАЧА (Роль: Авторизований)

Ви маєте доступ до перегляду та аналізу даних.
Ваші інструменти:

📊 Вкладка "Запити":
- Отримання списків офіцерського та рядового складу.
- Пошук техніки та озброєння за категоріями.
- Формування звітів про дислокацію частин.
- Експорт отриманих даних у CSV (Excel).

📂 Вкладка "Перегляд":
- Перегляд довідкової інформації про структуру округу.

👤 Мій профіль:
- Тут ви можете змінити свій пароль.

⛔ Ви не можете додавати або видаляти дані з бази.
""",

    "Operator": """
🛠 ІНСТРУКЦІЯ ОПЕРАТОРА

Ви маєте права на керування даними системи.
Основні функції:

✏️ Вкладка "CRUD" (Редагування):
- Додавання нових військових частин, особового складу, техніки.
- Редагування існуючих записів (наприклад, зміна звання, переміщення техніки).
- Видалення застарілих даних.
⚠️ Увага: Видалення частини або підрозділу може призвести до видалення пов'язаних даних (каскадне видалення)!

📊 Вкладка "Запити":
- Повний доступ до аналітичних звітів.
- Пошук інформації за складними критеріями.
- Експорт звітів.

👤 Безпека:
- Не передавайте свій пароль третім особам. Змінюйте його у профілі раз на місяць.
""",

    "Administrator": """
👑 ПАНЕЛЬ АДМІНІСТРАТОРА

Ви маєте повний контроль над системою.

🛡️ Вкладка "Адмін-панель":
1. Заявки на реєстрацію:
   - Схвалюйте нових Операторів та Авторизованих користувачів.
   - Відхиляйте підозрілі заявки.
2. Відновлення паролів:
   - Обробка запитів користувачів, які забули пароль.
3. Всі користувачі:
   - Перегляд списку всіх акаунтів та їх ролей.

🔧 Управління даними (CRUD):
- Ви маєте повний доступ до всіх таблиць, включно з системними довідниками.

📊 Аналітика:
- Доступ до всіх типів запитів та звітів.

⚠️ Відповідальність:
Ви відповідаєте за безпеку системи. Регулярно перевіряйте список користувачів.
"""
}


class MainFrame(tk.Frame):
    def __init__(self, master, db, user, on_logout):
        super().__init__(master)
        self.db = db
        self.user = user
        self.on_logout = on_logout

        # Прив'язка клавіші F1 до виклику довідки
        self.master.bind('<F1>', self._show_help)

        # Налаштування сітки
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- ПАНЕЛЬ ІНСТРУМЕНТІВ (ВЕРХНЄ МЕНЮ) ---
        toolbar = ttk.Frame(self, padding=(10, 10))
        toolbar.grid(row=0, column=0, sticky="ew")

        role = user.get("role")
        # Фікс, якщо роль з бази прийшла українською, а ключі англійською (або навпаки)
        # Але ми домовились, що в базі англійська.
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

        if caps["users"]:
            ttk.Button(nav_frame, text="🛡️ Адмін-панель", command=self._show_users).pack(side=tk.LEFT, padx=5)

        # Кнопка Довідки (для наочності, крім F1)
        ttk.Button(nav_frame, text="❓ Допомога (F1)", command=self._show_help).pack(side=tk.LEFT, padx=15)

        # Права частина (Юзер)
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.RIGHT)

        ttk.Label(user_frame, text=f"{role}", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Separator(user_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10, pady=2)

        ttk.Button(user_frame, text="👤 Профіль", command=self._show_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text="🚪 Вийти", command=self._logout).pack(side=tk.LEFT, padx=5)

        # --- ОСНОВНИЙ КОНТЕЙНЕР ---
        self.container = ttk.Frame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._current = None
        self._show_view()

    # --- ЛОГІКА ДОВІДКИ (F1) ---
    def _show_help(self, event=None):
        """Відкриває вікно з інструкцією для поточної ролі"""
        role = self.user.get("role", "Guest")
        help_text = HELP_TEXTS.get(role, HELP_TEXTS["Guest"])

        # Створюємо гарне спливаюче вікно
        help_win = tk.Toplevel(self)
        help_win.title(f"Довідка: {role}")
        help_win.geometry("600x500")

        # Центрування
        help_win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (500 // 2)
        help_win.geometry(f"+{x}+{y}")

        # Текстове поле з прокруткою
        f = ttk.Frame(help_win, padding=20)
        f.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(f, wrap=tk.WORD, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", relief="flat", padx=10, pady=10)
        # Якщо у вас світла тема, змініть bg/fg. Для sv_ttk dark це підходить.
        # Або просто використовуйте стандартні кольори від теми:
        if "sv_ttk" in str(ttk.Style().theme_names()):
            # sv_ttk автоматично стилізує Text, якщо не задавати кольори жорстко,
            # але іноді треба підказати. Спробуємо без жорстких кольорів:
            txt = tk.Text(f, wrap=tk.WORD, font=("Segoe UI", 11), relief="flat", padx=10, pady=10)

        scr = ttk.Scrollbar(f, command=txt.yview)
        txt.configure(yscrollcommand=scr.set)

        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr.pack(side=tk.RIGHT, fill=tk.Y)

        # Вставляємо текст
        txt.insert(tk.END, help_text)
        txt.config(state=tk.DISABLED)  # Тільки для читання

        ttk.Button(help_win, text="Зрозуміло", command=help_win.destroy, style="Accent.TButton").pack(pady=10)

    def _swap(self, frame):
        if self._current:
            self._current.destroy()
        self._current = frame
        self._current.grid(row=0, column=0, sticky="nsew")

    def _show_view(self):
        try:
            f = ViewFrame(self.container, self.db)
        except ImportError:
            f = ttk.Frame(self.container, padding=20)
            ttk.Label(f, text="Ласкаво просимо до ІС 'Військовий округ'", font=("Segoe UI", 20, "bold")).pack(pady=40)
            if self.user.get('role') == 'Guest':
                ttk.Label(f, text="Ваш статус: Гість. Функціонал обмежено.", foreground="grey").pack()
        self._swap(f)

    def _show_crud(self):
        self._swap(CRUDFrame(self.container, self.db))

    def _show_queries(self):
        self._swap(QueriesFrame(self.container, self.db))

    def _show_profile(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container)
        self._swap(f)

        content = ttk.Frame(f, padding=30)
        content.place(relx=0.5, rely=0.5, anchor="center")

        header_frame = ttk.Frame(content)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text=f"Вітаємо, {self.user.get('login')}", font=("Segoe UI", 24, "bold")).pack()
        ttk.Label(header_frame, text="Керування обліковим записом", font=("Segoe UI", 10), foreground="gray").pack()

        if self.user.get('role') == 'Guest':
            info_frame = ttk.LabelFrame(content, text=" Статус акаунта ", padding=20)
            info_frame.pack(fill=tk.X, pady=10)
            ttk.Label(info_frame, text="⚠️ Ви використовуєте тимчасовий гостьовий доступ.", font=("Segoe UI", 11)).pack(
                anchor="w")
            ttk.Label(info_frame, text="Щоб отримати повний доступ, будь ласка, зареєструйтеся.").pack(anchor="w",
                                                                                                       pady=(5, 20))
            ttk.Button(info_frame, text="📝 Зареєструватися (Вихід)", command=self._logout, width=30).pack()
        else:
            pass_frame = ttk.LabelFrame(content, text=" Безпека ", padding=20)
            pass_frame.pack(fill=tk.X, pady=10)

            ttk.Label(pass_frame, text="Зміна пароля", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))

            entry_frame = ttk.Frame(pass_frame)
            entry_frame.pack(fill=tk.X)

            ttk.Label(entry_frame, text="Новий пароль:").pack(anchor="w")
            entry_new_pass = ttk.Entry(entry_frame, show="*", width=40)
            entry_new_pass.pack(fill=tk.X, pady=5)

            def save_new_password():
                new_p = entry_new_pass.get().strip()
                if len(new_p) < 4:
                    messagebox.showwarning("Помилка", "Пароль надто короткий!")
                    return
                try:
                    from app.auth import AuthService
                    AuthService(self.db).change_password(self.user.get('login'), new_p)
                    messagebox.showinfo("Успіх", "Ваш пароль успішно змінено!")
                    entry_new_pass.delete(0, tk.END)
                except Exception as e:
                    messagebox.showerror("Помилка", str(e))

            ttk.Button(pass_frame, text="💾 Зберегти новий пароль", command=save_new_password).pack(pady=10, anchor="e")

    def _show_users(self):
        if self._current: self._current.destroy()
        f = ttk.Frame(self.container, padding=10)
        self._swap(f)

        ttk.Label(f, text="Панель Адміністратора", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))

        notebook = ttk.Notebook(f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # TAB 1
        tab_req = ttk.Frame(notebook, padding=10)
        notebook.add(tab_req, text="   Заявки на реєстрацію   ")

        cols_req = ("id", "login", "status", "type")
        tree_req = ttk.Treeview(tab_req, columns=cols_req, show="headings", height=10)
        tree_req.heading("id", text="ID");
        tree_req.column("id", width=50)
        tree_req.heading("login", text="Логін");
        tree_req.column("login", width=150)
        tree_req.heading("status", text="Статус");
        tree_req.column("status", width=100)
        tree_req.heading("type", text="Тип ролі");
        tree_req.column("type", width=150)
        tree_req.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        def refresh_requests():
            for i in tree_req.get_children(): tree_req.delete(i)
            sql = "SELECT id, login, status, request_type FROM requests WHERE status='pending' AND request_type LIKE 'role_%'"
            try:
                for r in self.db.query(sql):
                    tree_req.insert("", tk.END, values=(r['id'], r['login'], r['status'], r['request_type']))
            except:
                pass

        btn_fr_req = ttk.Frame(tab_req)
        btn_fr_req.pack(fill=tk.X)

        def process_role(action):
            sel = tree_req.selection()
            if not sel: return
            rid = tree_req.item(sel[0])['values'][0]
            try:
                from app.auth import AuthService
                AuthService(self.db).admin_process_request(rid, action)
                refresh_requests()
                messagebox.showinfo("Успіх", "Заявку оброблено")
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(btn_fr_req, text="✅ Схвалити", command=lambda: process_role('approve')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_req, text="❌ Відхилити", command=lambda: process_role('reject')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_req, text="🔄 Оновити", command=refresh_requests).pack(side=tk.RIGHT)
        refresh_requests()

        # TAB 2
        tab_res = ttk.Frame(notebook, padding=10)
        notebook.add(tab_res, text="   Відновлення паролів   ")
        cols_res = ("id", "login", "status", "date")
        tree_res = ttk.Treeview(tab_res, columns=cols_res, show="headings", height=10)
        tree_res.heading("id", text="ID");
        tree_res.heading("login", text="Логін");
        tree_res.heading("status", text="Статус");
        tree_res.heading("date", text="Дата")
        tree_res.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        def refresh_resets():
            for i in tree_res.get_children(): tree_res.delete(i)
            sql = "SELECT id, login, status, created_at FROM requests WHERE status='pending' AND request_type='password_reset' ORDER BY created_at DESC"
            for r in self.db.query(sql):
                vals = list(r.values()) if isinstance(r, dict) else r
                tree_res.insert("", tk.END, values=vals)

        btn_fr_res = ttk.Frame(tab_res)
        btn_fr_res.pack(fill=tk.X)

        def process_pass(action):
            sel = tree_res.selection()
            if not sel: return
            rid = tree_res.item(sel[0])['values'][0]
            try:
                from app.auth import AuthService
                AuthService(self.db).admin_process_request(rid, action)
                refresh_resets()
                msg = "Дозволено зміну" if action == 'approve' else "Відхилено"
                messagebox.showinfo("Успіх", msg)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(btn_fr_res, text="✅ Дозволити", command=lambda: process_pass('approve')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_res, text="❌ Відхилити", command=lambda: process_pass('reject')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_fr_res, text="🔄 Оновити", command=refresh_resets).pack(side=tk.RIGHT)
        refresh_resets()

        # TAB 3
        tab_users = ttk.Frame(notebook, padding=10)
        notebook.add(tab_users, text="   Всі користувачі   ")
        cols_usr = ("id", "login", "role")
        tree_usr = ttk.Treeview(tab_users, columns=cols_usr, show="headings")
        tree_usr.heading("id", text="ID");
        tree_usr.heading("login", text="Логін");
        tree_usr.heading("role", text="Роль")
        tree_usr.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        def refresh_users():
            for i in tree_usr.get_children(): tree_usr.delete(i)
            sql = "SELECT k.id, k.login, r.name FROM keys k JOIN roles r ON r.id=k.role_id ORDER BY k.id"
            for r in self.db.query(sql):
                vals = list(r.values()) if isinstance(r, dict) else r
                tree_usr.insert("", tk.END, values=vals)

        ttk.Button(tab_users, text="🔄 Оновити список", command=refresh_users).pack(anchor="e")
        refresh_users()

    def _logout(self):
        # Обов'язково відв'язуємо F1 при виході, щоб не дублювати події
        self.master.unbind('<F1>')
        self.on_logout()