import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Додаємо кореневу папку в шляхи, щоб Python бачив модуль 'app'
sys.path.append(os.getcwd())

try:
    from app.db import Database
    from app.ui.login import LoginFrame
    from app.ui.main import MainFrame
except ImportError:
    # Якщо запускаємо з папки app/, то імпорти будуть інакші (але краще запускати з кореня)
    from db import Database
    from ui.login import LoginFrame
    from ui.main import MainFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # 1. Налаштування вікна
        self.title("Інформаційна система 'Військовий округ'")
        self.geometry("1100x700")  # Більший розмір для зручності таблиць

        # 2. Центрування вікна на екрані
        self._center_window(1100, 700)

        # 3. Покращення вигляду (тема)
        style = ttk.Style()
        try:
            style.theme_use('clam')  # Виглядає краще стандартного
        except tk.TclError:
            pass  # Якщо теми немає, використовуємо стандартну

        # 4. Підключення до БД
        try:
            self.db = Database()
            self.db.connect()  # Перевіряємо з'єднання одразу
        except Exception as e:
            messagebox.showerror("Критична помилка", f"Не вдалося підключитися до БД:\n{e}")
            self.destroy()
            return

        # Обробка закриття вікна (хрестик)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._current_frame = None
        self.show_login_screen()

    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _swap(self, frame):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = frame
        self._current_frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        self._swap(LoginFrame(self, self.db, on_login=self.show_main_screen))

    def show_main_screen(self, user):
        self._swap(MainFrame(self, self.db, user, on_logout=self.show_login_screen))

    def on_closing(self):
        """Коректне закриття з'єднання з БД при виході"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()