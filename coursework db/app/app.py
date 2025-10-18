import tkinter as tk
from tkinter import ttk
from db import Database
from ui.login import LoginFrame
from app.ui.main import MainFrame  # твій головний екран після логіну

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Military DB")
        self.geometry("600x400")
        self.db = Database()

        self._current = None
        self.show_login_screen()

    def _swap(self, frame):
        if self._current:
            self._current.destroy()
        self._current = frame
        self._current.pack(fill="both", expand=True)

    def show_login_screen(self):
        self._swap(LoginFrame(self, self.db, on_login=self.show_main_screen))

    def show_main_screen(self, user):
        from app.ui.main import MainFrame
        self._swap(MainFrame(self, self.db, user, on_logout=self.show_login_screen))


if __name__ == "__main__":
    app = App()
    app.mainloop()
