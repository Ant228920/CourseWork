import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthService


class LoginFrame(tk.Frame):
    def __init__(self, master, db, on_login):
        super().__init__(master)
        self.db = db
        self.auth = AuthService(db)
        self.on_login = on_login

        # Розтягуємо фрейм на все вікно
        self.pack(fill="both", expand=True)

        # Створюємо центральний контейнер для контенту
        self.center_frame = ttk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.create_start_screen()

    def _clear(self):
        """Очищення центрального контейнера"""
        for w in self.center_frame.winfo_children():
            w.destroy()

    def create_start_screen(self):
        """Початковий екран (Титульна сторінка)"""
        self._clear()

        # Заголовок
        ttk.Label(self.center_frame, text="Ласкаво просимо!", font=("Segoe UI", 24, "bold")).pack(pady=(0, 10))
        ttk.Label(self.center_frame, text="Інформаційна система військового округу", font=("Segoe UI", 12),
                  foreground="gray").pack(pady=(0, 30))

        btn_frame = ttk.Frame(self.center_frame)
        btn_frame.pack(pady=10)

        # Основні кнопки
        ttk.Button(btn_frame, text="🔑 Вхід до системи", width=30, command=self.show_login_form,
                   style="Accent.TButton").pack(pady=10, ipady=5)
        ttk.Button(btn_frame, text="📝 Реєстрація нового користувача", width=30, command=self.show_register_form).pack(
            pady=10, ipady=5)

        # Розділювач
        ttk.Separator(self.center_frame, orient='horizontal').pack(fill='x', pady=25)

        # Вхід як гість
        ttk.Button(self.center_frame, text="👤 Продовжити як Гість", width=30, command=self.do_guest_login).pack(pady=5,
                                                                                                                ipady=5)

    def do_guest_login(self):
        user = self.auth.login_as_guest()
        if user:
            messagebox.showinfo("Вхід", "Ви увійшли як Гість (обмежений доступ)")
            self.on_login(user)
        else:
            messagebox.showerror("Помилка", "Не вдалося увійти як гість")

    def show_login_form(self):
        """Форма входу"""
        self._clear()

        ttk.Label(self.center_frame, text="Вхід до системи", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        input_frame = ttk.Frame(self.center_frame, padding=20)
        input_frame.pack(fill="x")

        # Поля вводу
        ttk.Label(input_frame, text="Логін", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        login_entry = ttk.Entry(input_frame, width=35, font=("Segoe UI", 11))
        login_entry.pack(pady=(0, 15))

        ttk.Label(input_frame, text="Пароль", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        password_entry = ttk.Entry(input_frame, show="*", width=35, font=("Segoe UI", 11))
        password_entry.pack(pady=(0, 20))

        def do_login():
            login = login_entry.get().strip()
            password = password_entry.get().strip()

            user = self.auth.login(login, password)

            if user:
                # Фікс для адміна (на випадок проблем з БД)
                if user['login'] == 'admin':
                    user['role'] = 'Administrator'

                messagebox.showinfo("Успіх", f"Вітаю, {user['login']}!\nВаша роль: {user['role']}")
                self.on_login(user)
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль")

        # Кнопки дій
        ttk.Button(self.center_frame, text="УВІЙТИ", command=do_login, style="Accent.TButton", width=30).pack(pady=10,
                                                                                                              ipady=5)

        ttk.Button(self.center_frame, text="Забули пароль?", command=self.show_forgot_password).pack(pady=5)

        ttk.Button(self.center_frame, text="⬅ На головну", command=self.create_start_screen).pack(pady=20)

    def show_register_form(self):
        """Форма реєстрації"""
        self._clear()

        ttk.Label(self.center_frame, text="Реєстрація", font=("Segoe UI", 20, "bold")).pack(pady=(0, 15))

        input_frame = ttk.Frame(self.center_frame)
        input_frame.pack(fill="x")

        # Поля
        ttk.Label(input_frame, text="Логін:", font=("Segoe UI", 10)).pack(anchor="w")
        login_entry = ttk.Entry(input_frame, width=35)
        login_entry.pack(pady=(5, 10))

        ttk.Label(input_frame, text="Пароль:", font=("Segoe UI", 10)).pack(anchor="w")
        password_entry = ttk.Entry(input_frame, show="*", width=35)
        password_entry.pack(pady=(5, 10))

        ttk.Label(input_frame, text="Email:", font=("Segoe UI", 10)).pack(anchor="w")
        email_entry = ttk.Entry(input_frame, width=35)
        email_entry.pack(pady=(5, 10))

        ttk.Label(input_frame, text="Оберіть роль:", font=("Segoe UI", 10)).pack(anchor="w")

        role_map = {
            "Користувач (Authorized)": "Authorized",
            "Оператор (Потрібне підтвердження)": "Operator"
        }
        role_combo = ttk.Combobox(input_frame, values=list(role_map.keys()), state="readonly", width=33)
        role_combo.current(0)
        role_combo.pack(pady=(5, 15))

        def do_register():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip() or None

            target_role = role_map[role_combo.get()]

            if not login or not password:
                messagebox.showwarning("Увага", "Введіть логін і пароль")
                return

            try:
                if target_role == "Operator":
                    self.auth.register_with_request(login, password, target_role, email)
                    messagebox.showinfo("Увага",
                                        "Ваш акаунт створено як 'Гість'.\nЗапит на роль Оператора надіслано адміністратору.")
                else:
                    self.auth.create_user(login, password, target_role, email)
                    messagebox.showinfo("Успіх", "Акаунт створено! Тепер увійдіть.")

                self.show_login_form()  # Повертаємось на логін після успіху
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(self.center_frame, text="ЗАРЕЄСТРУВАТИСЯ", command=do_register, style="Accent.TButton",
                   width=30).pack(pady=10, ipady=5)
        ttk.Button(self.center_frame, text="⬅ Назад", command=self.create_start_screen).pack(pady=10)

    def show_forgot_password(self):
        """Екран відновлення пароля"""
        self._clear()

        ttk.Label(self.center_frame, text="Відновлення доступу", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20))

        ttk.Label(self.center_frame, text="Введіть ваш логін для перевірки:", font=("Segoe UI", 10)).pack(anchor="w")
        login_entry = ttk.Entry(self.center_frame, width=35)
        login_entry.pack(pady=10)

        status_lbl = ttk.Label(self.center_frame, text="", font=("Segoe UI", 10), wraplength=300)
        status_lbl.pack(pady=10)

        action_frame = ttk.Frame(self.center_frame)
        action_frame.pack(pady=5, fill=tk.X)

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
                messagebox.showwarning("Помилка", "Пароль занадто короткий")
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
                status_lbl.config(text="Активних заявок не знайдено.", foreground="orange")
                ttk.Button(action_frame, text="📤 Подати заявку на відновлення", command=request_reset, width=30).pack(
                    pady=5)
            elif status == 'pending':
                status_lbl.config(text="⏳ Заявка на розгляді у адміністратора.", foreground="orange")
                ttk.Button(action_frame, text="🔄 Оновити статус", command=check_status_logic).pack(pady=5)
            elif status == 'approved':
                status_lbl.config(text="✅ Схвалено! Введіть новий пароль:", foreground="green")

                ttk.Label(action_frame, text="Новий пароль:").pack(anchor="w")
                pass_entry = ttk.Entry(action_frame, show="*", width=35)
                pass_entry.pack(pady=5)

                ttk.Button(action_frame, text="💾 Зберегти новий пароль", style="Accent.TButton",
                           command=lambda: save_new_password(pass_entry.get())).pack(pady=10, ipady=5)
            elif status == 'rejected':
                status_lbl.config(text="❌ Заявку відхилено.", foreground="red")
                ttk.Button(action_frame, text="🔄 Подати знову",
                           command=lambda: [self.auth.resubmit_request(login), check_status_logic()]).pack(pady=5)

        ttk.Button(self.center_frame, text="🔍 Перевірити статус", command=check_status_logic, width=30).pack(pady=5)

        ttk.Button(self.center_frame, text="⬅ Назад до входу", command=self.show_login_form).pack(pady=20)