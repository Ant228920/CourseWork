import tkinter as tk
from tkinter import ttk, messagebox


class ViewFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Верхня панель: Вибір таблиці
        top_panel = ttk.Frame(self, padding=5)
        top_panel.grid(row=0, column=0, sticky="ew")

        ttk.Label(top_panel, text="Оберіть таблицю для перегляду:").pack(side=tk.LEFT, padx=5)

        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(top_panel, textvariable=self.entity_var, state="readonly", width=30)
        self.entity_combo.pack(side=tk.LEFT, padx=5)
        self.entity_combo.bind("<<ComboboxSelected>>", self._on_entity_select)

        # Основна область контенту
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=1)  # Treeview розтягується

        # Конфігурація сутностей (Така ж як у CRUD, але можна скоротити)
        self.entities = {
            "Військові Округи": {
                "table": "military_districts",
                "display_fields": ["name", "code"],
                "headers": ["Назва", "Код"]
            },
            "Армії": {
                "table": "armies",
                "display_fields": ["number", "name"],
                "headers": ["Номер", "Назва"]
            },
            "Військові Частини": {
                "table": "military_units",
                "display_fields": ["number", "name"],
                "headers": ["Номер в/ч", "Назва"]
            },
            "Військовослужбовці": {
                "table": "military_personnel",
                "display_fields": ["last_name", "first_name", "middle_name"],
                "headers": ["Прізвище", "Ім'я", "По батькові"]
            },
            "Техніка": {
                "table": "equipment",
                "display_fields": ["model", "serial_number", "condition"],
                "headers": ["Модель", "Серійний номер", "Стан"]
            },
            "Озброєння": {
                "table": "weapons",
                "display_fields": ["model", "serial_number", "caliber"],
                "headers": ["Модель", "Номер", "Калібр"]
            }
        }

        # Заповнюємо комбобокс
        self.entity_combo['values'] = list(self.entities.keys())
        if self.entities:
            self.entity_combo.current(0)
            self._on_entity_select(None)

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name: return

        config = self.entities[entity_name]
        self._create_table_interface(config)

    def _create_table_interface(self, config):
        # Очищення попереднього вмісту
        for w in self.content_frame.winfo_children(): w.destroy()

        # 1. Панель пошуку
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ttk.Label(search_frame, text="Пошук:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self._search(config))

        ttk.Button(search_frame, text="🔄 Оновити", command=lambda: self._load_data(config)).pack(side=tk.RIGHT)

        # 2. Таблиця
        cols = config["display_fields"]
        headers = config.get("headers", cols)

        self.tree = ttk.Treeview(self.content_frame, columns=cols, show="headings")

        for col, header in zip(cols, headers):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=100)

        # Скролбари
        vsb = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.content_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        # Завантаження даних
        self._load_data(config)

    def _load_data(self, config):
        table = config["table"]
        fields = ", ".join(config["display_fields"])
        sql = f"SELECT {fields} FROM {table} ORDER BY id LIMIT 100"

        try:
            # Очищення
            for i in self.tree.get_children(): self.tree.delete(i)

            rows = self.db.query(sql)
            # rows - це список словників (DictCursor) або список кортежів
            for row in rows:
                # Якщо DictCursor
                vals = [row[f] for f in config["display_fields"]]
                self.tree.insert("", tk.END, values=vals)
        except Exception as e:
            print(f"Error loading view: {e}")

    def _search(self, config):
        query_text = self.search_var.get().strip()
        if not query_text:
            self._load_data(config)
            return

        table = config["table"]
        fields = config["display_fields"]

        # Будуємо WHERE clause для всіх полів (TEXT)
        where_parts = [f"{f}::text ILIKE %s" for f in fields]
        where_sql = " OR ".join(where_parts)

        sql = f"SELECT {', '.join(fields)} FROM {table} WHERE {where_sql} LIMIT 50"
        params = [f"%{query_text}%"] * len(fields)

        try:
            for i in self.tree.get_children(): self.tree.delete(i)
            rows = self.db.query(sql, params)
            for row in rows:
                vals = [row[f] for f in fields]
                self.tree.insert("", tk.END, values=vals)
        except Exception as e:
            print(f"Search error: {e}")