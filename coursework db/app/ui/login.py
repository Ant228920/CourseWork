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
        for w in self.winfo_children():
            w.destroy()

        ttk.Label(self, text="Ласкаво просимо!", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Button(self, text="🔑 Увійти", command=self.show_login_form).pack(pady=5)
        ttk.Button(self, text="🆕 Створити новий акаунт", command=self.show_register_form).pack(pady=5)

    # ---------- LOGIN ----------
    def show_login_form(self):
        for w in self.winfo_children():
            w.destroy()

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

        ttk.Button(self, text="Увійти", command=do_login).pack(pady=10)
        ttk.Button(self, text="⬅ Назад", command=self.create_start_screen).pack()

    # ---------- REGISTER ----------
    def show_register_form(self):
        for w in self.winfo_children():
            w.destroy()

        ttk.Label(self, text="Реєстрація нового користувача", font=("Arial", 13, "bold")).pack(pady=10)

        ttk.Label(self, text="Логін:").pack()
        login_entry = ttk.Entry(self)
        login_entry.pack()

        ttk.Label(self, text="Пароль:").pack()
        password_entry = ttk.Entry(self, show="*")
        password_entry.pack()

        ttk.Label(self, text="Email (необов'язково):").pack()
        email_entry = ttk.Entry(self)
        email_entry.pack()

        # Вибір ролі
        ttk.Label(self, text="Хто ви?", font=("Arial", 11, "bold")).pack(pady=(10, 5))

        role_var = tk.StringVar(value="user")

        role_frame = ttk.Frame(self)
        role_frame.pack(pady=5)

        ttk.Radiobutton(
            role_frame,
            text="👤 Користувач",
            variable=role_var,
            value="user"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Radiobutton(
            role_frame,
            text="👑 Адміністратор",
            variable=role_var,
            value="admin"
        ).pack(side=tk.LEFT, padx=10)

        def do_register():
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip() or None
            selected_role = role_var.get()

            if not login or not password:
                messagebox.showwarning("Увага", "Введіть логін і пароль")
                return

            # Визначаємо role_id залежно від вибору
            if selected_role == "admin":
                role_id = 2
                role_name = "Адміністратор"
            else:
                role_id = 1
                role_name = "Авторизований"

            try:
                self.auth.create_user_with_role_id(login, password, role_id, email=email)
                messagebox.showinfo("Успіх", f"Користувач створений з роллю '{role_name}'!\nТепер увійдіть.")
                self.show_login_form()
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося створити користувача:\n{e}")

        ttk.Button(self, text="Зареєструватися", command=do_register).pack(pady=10)
        ttk.Button(self, text="⬅ Назад", command=self.create_start_screen).pack()