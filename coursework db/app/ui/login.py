import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthService


class LoginFrame(tk.Frame):
    def __init__(self, master, db, on_login):
        super().__init__(master)
        self.db = db
        self.auth = AuthService(db)
        self.on_login = on_login
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.create_start_screen()

    def create_start_screen(self):
        """Початковий екран"""
        for w in self.winfo_children(): w.destroy()

        ttk.Label(self, text="Ласкаво просимо!", font=("Arial", 14, "bold")).pack(pady=10)

        # Тільки основні кнопки
        ttk.Button(self, text="🔑 Увійти", command=self.show_login_form).pack(pady=5)
        ttk.Button(self, text="🆕 Реєстрація", command=self.show_register_form).pack(pady=5)

    def show_login_form(self):
        """Форма входу з полями та відновленням пароля"""
        for w in self.winfo_children(): w.destroy()

        ttk.Label(self, text="Вхід до системи", font=("Arial", 13, "bold")).pack(pady=10)

        ttk.Label(self, text="Логін:").pack()
        login_entry = ttk.Entry(self)
        login_entry.pack()

        ttk.Label(self, text="Пароль:").pack()
        password_entry = ttk.Entry(self, show="*")
        password_entry.pack()

        def do_login():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            user = self.auth.login(login, password)
            if user:
                messagebox.showinfo("Успіх", f"Вітаю, {login}!")
                self.on_login(user)
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль")

        # Кнопка входу
        ttk.Button(self, text="Увійти", command=do_login).pack(pady=10)

        # Кнопка відновлення пароля
        ttk.Button(self, text="❓ Забули пароль?", command=self.show_forgot_password).pack(pady=2)

        ttk.Button(self, text="⬅ Назад", command=self.create_start_screen).pack(pady=10)

    def show_forgot_password(self):
        """Екран відновлення пароля (статус заявки / зміна)"""
        for w in self.winfo_children(): w.destroy()

        ttk.Label(self, text="Відновлення доступу", font=("Arial", 14, "bold")).pack(pady=10)

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=5)

        ttk.Label(input_frame, text="Ваш логін:").pack(anchor="w")
        login_entry = ttk.Entry(input_frame, width=30)
        login_entry.pack(pady=5)

        status_lbl = ttk.Label(self, text="", font=("Arial", 10), foreground="blue", wraplength=400)
        status_lbl.pack(pady=10)

        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5, fill=tk.X, padx=20)

        def clear_action_frame():
            for widget in action_frame.winfo_children(): widget.destroy()

        def request_reset():
            """Подати нову заявку"""
            login = login_entry.get().strip()
            if not login:
                status_lbl.config(text="Введіть логін!", foreground="red")
                return
            msg = self.auth.create_password_reset_request(login)
            status_lbl.config(text=msg, foreground="blue")
            check_status_logic()

        def save_new_password(new_pass):
            """Зберегти новий пароль (якщо дозволено)"""
            login = login_entry.get().strip()
            if len(new_pass) < 4:
                messagebox.showwarning("Помилка", "Пароль занадто короткий")
                return
            try:
                self.auth.user_finalize_reset(login, new_pass)
                messagebox.showinfo("Успіх", "Пароль успішно змінено! Тепер увійдіть.")
                self.show_login_form()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        def check_status_logic():
            """Перевірка статусу заявки"""
            login = login_entry.get().strip()
            if not login:
                status_lbl.config(text="Введіть логін для перевірки", foreground="red")
                return

            status = self.auth.check_reset_status_simple(login)
            clear_action_frame()

            if status == 'not_found':
                status_lbl.config(text="Заявок не знайдено. Подайте нову.", foreground="orange")
                ttk.Button(action_frame, text="📤 Подати заявку", command=request_reset).pack()

            elif status == 'pending':
                status_lbl.config(text="⏳ Заявка на розгляді. Очікуйте рішення адміністратора.", foreground="orange")
                ttk.Button(action_frame, text="🔄 Оновити статус", command=check_status_logic).pack()

            elif status == 'rejected':
                status_lbl.config(text="❌ Вашу заявку відхилено адміністратором.", foreground="red")

                def resubmit():
                    self.auth.resubmit_request(login)
                    check_status_logic()

                ttk.Button(action_frame, text="🔄 Подати запит знову", command=resubmit).pack()

            elif status == 'approved':
                status_lbl.config(text="✅ Заявку схвалено! Придумайте новий пароль.", foreground="green")

                ttk.Label(action_frame, text="Новий пароль:").pack(anchor="w")
                pass_entry = ttk.Entry(action_frame, show="*", width=30)
                pass_entry.pack(pady=5)

                ttk.Button(action_frame, text="💾 Зберегти новий пароль",
                           command=lambda: save_new_password(pass_entry.get())).pack(pady=10)

        ttk.Button(action_frame, text="🔍 Перевірити статус / Подати заявку", command=check_status_logic).pack()

        back_frame = ttk.Frame(self)
        back_frame.pack(side=tk.BOTTOM, pady=20)
        ttk.Button(back_frame, text="⬅ Назад до входу", command=self.show_login_form).pack()

    def show_register_form(self):
        for w in self.winfo_children(): w.destroy()
        ttk.Label(self, text="Реєстрація", font=("Arial", 13, "bold")).pack(pady=10)

        ttk.Label(self, text="Логін:").pack()
        login_entry = ttk.Entry(self)
        login_entry.pack()

        ttk.Label(self, text="Пароль:").pack()
        password_entry = ttk.Entry(self, show="*")
        password_entry.pack()

        ttk.Label(self, text="Email:").pack()
        email_entry = ttk.Entry(self)
        email_entry.pack()

        ttk.Label(self, text="Роль:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        role_var = tk.StringVar(value="user")

        role_frame = ttk.Frame(self)
        role_frame.pack(pady=5)

        # Радіокнопки відображаються українською, але значення передають 'user'/'admin'
        ttk.Radiobutton(role_frame, text="👤 Користувач", variable=role_var, value="user").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(role_frame, text="👑 Адміністратор", variable=role_var, value="admin").pack(side=tk.LEFT,
                                                                                                   padx=10)

        def do_register():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip() or None

            # !!! ВИПРАВЛЕННЯ ТУТ !!!
            # Ми використовуємо англійські назви ролей, тому що саме вони записані в базі даних (таблиця roles)
            role_name = "Administrator" if role_var.get() == "admin" else "Authorized"

            if not login or not password:
                messagebox.showwarning("Увага", "Введіть логін і пароль")
                return

            try:
                self.auth.create_user(login, password, role_name, email=email)
                messagebox.showinfo("Успіх", f"Користувач створений! Тепер увійдіть.")
                self.show_login_form()
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося створити користувача:\n{e}")

        ttk.Button(self, text="Зареєструватися", command=do_register).pack(pady=10)
        ttk.Button(self, text="⬅ Назад", command=self.create_start_screen).pack()