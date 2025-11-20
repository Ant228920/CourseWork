import tkinter as tk
from tkinter import ttk, messagebox
# Використовуємо правильний шлях імпорту
from auth import AuthService


class LoginFrame(tk.Frame):
    def __init__(self, master, db, on_login):
        super().__init__(master)
        self.db = db
        self.auth = AuthService(db)
        self.on_login = on_login
        self.pack(fill="both", expand=True, padx=20, pady=20)

        # ОДРАЗУ показуємо форму входу
        self.show_login_form()

    def show_login_form(self):
        """Головний екран входу"""
        for w in self.winfo_children(): w.destroy()

        ttk.Label(self, text="Вхід до системи", font=("Arial", 16, "bold")).pack(pady=20)

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Логін:").pack(anchor="w")
        login_entry = ttk.Entry(input_frame, width=30)
        login_entry.pack(pady=5)

        ttk.Label(input_frame, text="Пароль:").pack(anchor="w")
        password_entry = ttk.Entry(input_frame, show="*", width=30)
        password_entry.pack(pady=5)

        def do_login():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            user = self.auth.login(login, password)
            if user:
                messagebox.showinfo("Успіх", f"Вітаю, {login}!")
                self.on_login(user)
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль")

        def do_guest_login():
            user = self.auth.login_as_guest()
            if user:
                messagebox.showinfo("Вхід", "Ви увійшли як Гість")
                self.on_login(user)
            else:
                messagebox.showerror("Помилка", "Не вдалося увійти як гість")

        # Основна кнопка входу
        ttk.Button(self, text="УВІЙТИ", command=do_login).pack(pady=10, fill=tk.X, padx=40)

        # Додаткові посилання (в один ряд)
        links_frame = ttk.Frame(self)
        links_frame.pack(pady=5)

        # Кнопка переходу на реєстрацію
        ttk.Button(links_frame, text="📝 Реєстрація", command=self.show_register_form).pack(side=tk.LEFT, padx=5)
        # Кнопка відновлення пароля
        ttk.Button(links_frame, text="❓ Забули пароль?", command=self.show_forgot_password).pack(side=tk.LEFT, padx=5)

        # Розділювач і вхід як гість
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(self, text="👤 Увійти як Гість", command=do_guest_login).pack(pady=5)

    def show_register_form(self):
        """Екран реєстрації"""
        for w in self.winfo_children(): w.destroy()

        ttk.Label(self, text="Реєстрація", font=("Arial", 16, "bold")).pack(pady=10)

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=5)

        ttk.Label(input_frame, text="Логін:").pack(anchor="w")
        login_entry = ttk.Entry(input_frame, width=30)
        login_entry.pack(pady=2)

        ttk.Label(input_frame, text="Пароль:").pack(anchor="w")
        password_entry = ttk.Entry(input_frame, show="*", width=30)
        password_entry.pack(pady=2)

        ttk.Label(input_frame, text="Email:").pack(anchor="w")
        email_entry = ttk.Entry(input_frame, width=30)
        email_entry.pack(pady=2)

        ttk.Label(input_frame, text="Роль:").pack(anchor="w", pady=(10, 0))

        # Ролі (відображення -> значення в БД)
        role_map = {
            "Користувач (Authorized)": "Authorized",
            "Оператор (Потрібне підтвердження)": "Operator",
            "Адміністратор": "Administrator"
        }
        role_combo = ttk.Combobox(input_frame, values=list(role_map.keys()), state="readonly", width=27)
        role_combo.current(0)
        role_combo.pack(pady=5)

        def do_register():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip() or None

            # Отримуємо англійську назву ролі для БД
            target_role = role_map[role_combo.get()]

            if not login or not password:
                messagebox.showwarning("Увага", "Введіть логін і пароль")
                return

            try:
                if target_role == "Operator":
                    self.auth.register_with_request(login, password, target_role, email)
                    messagebox.showinfo("Увага", "Ваш акаунт створено як 'Гість'.\nЗапит на права Оператора надіслано.")
                else:
                    self.auth.create_user(login, password, target_role, email)
                    messagebox.showinfo("Успіх", "Акаунт створено! Тепер увійдіть.")

                self.show_login_form()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(self, text="ЗАРЕЄСТРУВАТИСЯ", command=do_register).pack(pady=15, fill=tk.X, padx=40)

        # Кнопка повернення на Логін
        ttk.Button(self, text="⬅ Вже маю акаунт (Увійти)", command=self.show_login_form).pack(pady=5)

    def show_forgot_password(self):
        """Екран відновлення пароля"""
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
            login = login_entry.get().strip()
            if not login:
                status_lbl.config(text="Введіть логін!", foreground="red")
                return
            msg = self.auth.create_password_reset_request(login)
            status_lbl.config(text=msg, foreground="blue")
            check_status_logic()

        def save_new_password(new_pass):
            login = login_entry.get().strip()
            if len(new_pass) < 4:
                messagebox.showwarning("Помилка", "Пароль закороткий")
                return
            try:
                self.auth.user_finalize_reset(login, new_pass)
                messagebox.showinfo("Успіх", "Пароль змінено! Увійдіть.")
                self.show_login_form()
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        def check_status_logic():
            login = login_entry.get().strip()
            if not login:
                status_lbl.config(text="Введіть логін", foreground="red")
                return

            status = self.auth.check_reset_status_simple(login)
            clear_action_frame()

            if status == 'not_found':
                status_lbl.config(text="Заявок немає.", foreground="orange")
                ttk.Button(action_frame, text="📤 Подати заявку", command=request_reset).pack()
            elif status == 'pending':
                status_lbl.config(text="⏳ На розгляді.", foreground="orange")
                ttk.Button(action_frame, text="🔄 Оновити статус", command=check_status_logic).pack()
            elif status == 'approved':
                status_lbl.config(text="✅ Схвалено! Введіть новий пароль:", foreground="green")
                ttk.Label(action_frame, text="Новий пароль:").pack(anchor="w")
                pass_entry = ttk.Entry(action_frame, show="*", width=30)
                pass_entry.pack(pady=5)
                ttk.Button(action_frame, text="💾 Зберегти", command=lambda: save_new_password(pass_entry.get())).pack(
                    pady=5)
            elif status == 'rejected':
                status_lbl.config(text="❌ Відхилено.", foreground="red")
                ttk.Button(action_frame, text="🔄 Подати знову",
                           command=lambda: [self.auth.resubmit_request(login), check_status_logic()]).pack()

        ttk.Button(action_frame, text="🔍 Перевірити статус / Подати", command=check_status_logic).pack()

        # Кнопка повернення на Логін
        ttk.Button(self, text="⬅ Назад до входу", command=self.show_login_form).pack(side=tk.BOTTOM, pady=20)