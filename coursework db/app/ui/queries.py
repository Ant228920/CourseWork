import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from tkcalendar import DateEntry

# ===================================================================
# ГРУПОВАНА СТРУКТУРА ЗАПИТІВ (З РОЗУМНИМИ ПАРАМЕТРАМИ)
# ===================================================================

QUERY_GROUPS = {
    "1. Офіцерський склад": [
        {
            "name": "Загальний список",
            "sql": """
                   SELECT mp.last_name || ' ' || mp.first_name AS "Офіцер",
                          r.name                               AS "Звання",
                          mu.name                              AS "Частина"
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id = 1;
                   """,
            "params": []
        },
        {
            "name": "Пошук за званням",
            "sql": """
                   SELECT mp.last_name, mp.first_name, mu.name as "Частина"
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id = 1
                     AND r.id = %(rank_id)s;
                   """,
            # "source" вказує таблицю, "display" - що показувати людям
            "params": [{"name": "rank_id", "label": "Звання", "type": "db_combo",
                        "table": "ranks", "display": "name", "condition": "category_id=1"}]
        }
    ],
    "2. Рядовий та сержантський склад": [
        {
            "name": "Загальний список",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as "Звання", mu.name as "Частина"
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id IN (2, 3)
                   ORDER BY mp.last_name;
                   """,
            "params": []
        },
        {
            "name": "У конкретній частині",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as "Звання"
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                   WHERE r.category_id IN (2, 3)
                     AND mp.military_unit_id = %(unit_id)s;
                   """,
            "params": [{"name": "unit_id", "label": "Військова частина", "type": "db_combo",
                        "table": "military_units", "display": "name"}]
        }
    ],
    "3. Військова техніка": [
        {
            "name": "Наявність техніки (Всього)",
            "sql": """
                   SELECT et.name AS "Тип", et.category AS "Категорія", COUNT(e.id) AS "Кількість", mu.name AS "Частина"
                   FROM equipment e
                            JOIN equipment_types et ON e.equipment_type_id = et.id
                            JOIN military_units mu ON e.military_unit_id = mu.id
                   GROUP BY et.name, et.category, mu.name
                   ORDER BY mu.name;
                   """,
            "params": []
        },
        {
            "name": "Техніка в Армії (за категорією)",
            "sql": """
                   SELECT e.model, e.serial_number, mu.name as "Частина"
                   FROM equipment e
                            JOIN equipment_types et ON e.equipment_type_id = et.id
                            JOIN military_units mu ON e.military_unit_id = mu.id
                            LEFT JOIN divisions d ON mu.division_id = d.id
                            LEFT JOIN brigades b ON mu.brigade_id = b.id
                            LEFT JOIN corps c ON c.id = COALESCE(d.corps_id, b.corps_id)
                            LEFT JOIN armies a ON a.id = c.army_id
                   WHERE et.category = %(cat_name)s
                     AND a.id = %(army_id)s;
                   """,
            "params": [
                {"name": "cat_name", "label": "Категорія", "type": "manual_combo",
                 "values": ["Combat Vehicle", "Transport Vehicle"]},
                {"name": "army_id", "label": "Армія", "type": "db_combo",
                 "table": "armies", "display": "name"}
            ]
        }
    ],
    "4. Озброєння": [
        {
            "name": "Звіт по озброєнню (Округ)",
            "sql": """
                   SELECT wt.name AS "Зброя", COUNT(w.id) AS "Кількість", md.name AS "Округ"
                   FROM weapons w
                            JOIN weapon_types wt ON w.weapon_type_id = wt.id
                            JOIN military_units mu ON w.military_unit_id = mu.id
                            LEFT JOIN divisions d ON mu.division_id = d.id
                            LEFT JOIN brigades b ON mu.brigade_id = b.id
                            LEFT JOIN corps c ON c.id = COALESCE(d.corps_id, b.corps_id)
                            LEFT JOIN armies a ON a.id = c.army_id
                            LEFT JOIN military_districts md ON md.id = a.military_district_id
                   GROUP BY wt.name, md.name;
                   """,
            "params": []
        },
        {
            "name": "Озброєння частини",
            "sql": """
                   SELECT w.model, w.serial_number, w.caliber
                   FROM weapons w
                   WHERE w.military_unit_id = %(unit_id)s;
                   """,
            "params": [{"name": "unit_id", "label": "Частина", "type": "db_combo",
                        "table": "military_units", "display": "name"}]
        }
    ],
    "5. Статистика": [
        {
            "name": "Армія з найбільшою к-стю частин",
            "sql": """
                   SELECT a.name, COUNT(mu.id)
                   FROM armies a
                            JOIN corps c ON c.army_id = a.id
                            LEFT JOIN divisions d ON d.corps_id = c.id
                            LEFT JOIN brigades b ON b.corps_id = c.id
                            LEFT JOIN military_units mu ON (mu.division_id = d.id OR mu.brigade_id = b.id)
                   GROUP BY a.id, a.name
                   ORDER BY 2 DESC LIMIT 1;
                   """,
            "params": []
        }
    ],
    "6. Керівний склад": [
        {
            "name": "Командири частин (в Армії)",
            "sql": """
                   SELECT mu.name AS "Частина", mp.last_name AS "Командир", r.name AS "Звання"
                   FROM military_units mu
                            JOIN military_personnel mp ON mu.commander_id = mp.id
                            JOIN ranks r ON mp.rank_id = r.id
                            LEFT JOIN divisions d ON mu.division_id = d.id
                            LEFT JOIN brigades b ON mu.brigade_id = b.id
                            LEFT JOIN corps c ON c.id = COALESCE(d.corps_id, b.corps_id)
                            LEFT JOIN armies a ON a.id = c.army_id
                   WHERE a.id = %(army_id)s;
                   """,
            "params": [{"name": "army_id", "label": "Армія", "type": "db_combo",
                        "table": "armies", "display": "name"}]
        }
    ],
    "7. Дислокація": [
        {
            "name": "Локації частин округу",
            "sql": """
                   SELECT mu.name, loc.address
                   FROM military_units mu
                            JOIN locations loc ON mu.location_id = loc.id
                            LEFT JOIN divisions d ON mu.division_id = d.id
                            LEFT JOIN brigades b ON mu.brigade_id = b.id
                            LEFT JOIN corps c ON c.id = COALESCE(d.corps_id, b.corps_id)
                            LEFT JOIN armies a ON a.id = c.army_id
                            LEFT JOIN military_districts md ON md.id = a.military_district_id
                   WHERE md.id = %(dist_id)s;
                   """,
            "params": [{"name": "dist_id", "label": "Округ", "type": "db_combo",
                        "table": "military_districts", "display": "name"}]
        }
    ],
    "8. Пошук за кількістю": [
        {
            "name": "Частини з > N одиниць техніки (тип)",
            "sql": """
                   SELECT mu.name, COUNT(e.id)
                   FROM military_units mu
                            JOIN equipment e ON e.military_unit_id = mu.id
                            JOIN equipment_types et ON e.equipment_type_id = et.id
                   WHERE et.id = %(type_id)s
                   GROUP BY mu.id, mu.name
                   HAVING COUNT(e.id) >= %(min_count)s;
                   """,
            "params": [
                {"name": "type_id", "label": "Тип техніки", "type": "db_combo",
                 "table": "equipment_types", "display": "name"},
                {"name": "min_count", "label": "Мін. кількість", "type": "int"}
            ]
        }
    ],
    "9. Спеціальності": [
        {
            "name": "Військові спец. у підрозділі",
            "sql": """
                   SELECT mp.last_name, s.name AS "Спец."
                   FROM military_personnel mp
                            JOIN personnel_specialties ps ON mp.id = ps.personnel_id
                            JOIN specialties s ON ps.specialty_id = s.id
                   WHERE s.id = %(spec_id)s
                     AND mp.military_unit_id = %(unit_id)s;
                   """,
            "params": [
                {"name": "spec_id", "label": "Спеціальність", "type": "db_combo",
                 "table": "specialties", "display": "name"},
                {"name": "unit_id", "label": "Частина", "type": "db_combo",
                 "table": "military_units", "display": "name"}
            ]
        }
    ],
    "10. Інфраструктура": [
        {
            "name": "Споруди частини",
            "sql": "SELECT name, type, address FROM facilities WHERE military_unit_id = %(unit_id)s;",
            "params": [{"name": "unit_id", "label": "Частина", "type": "db_combo",
                        "table": "military_units", "display": "name"}]
        }
    ]
}


# ========================================
# QUERIES FRAME (Логіка інтерфейсу)
# ========================================

class QueriesFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.current_query_config = None
        self._param_widgets = []  # Список активних віджетів параметрів

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # --- БЛОК ВИБОРУ ---
        selection_frame = ttk.LabelFrame(self, text="Вибір запиту", padding=10)
        selection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        selection_frame.columnconfigure(1, weight=1)

        ttk.Label(selection_frame, text="Категорія:").grid(row=0, column=0, sticky="w", padx=5)
        self.cat_combo = ttk.Combobox(selection_frame, state="readonly", values=list(QUERY_GROUPS.keys()))
        self.cat_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.cat_combo.bind("<<ComboboxSelected>>", self._on_category_select)

        ttk.Label(selection_frame, text="Запит:").grid(row=1, column=0, sticky="w", padx=5)
        self.query_combo = ttk.Combobox(selection_frame, state="readonly")
        self.query_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.query_combo.bind("<<ComboboxSelected>>", self._on_query_select)

        # --- ПАРАМЕТРИ ---
        self.params_wrapper = ttk.LabelFrame(self, text="Параметри пошуку", padding=10)
        self.params_wrapper.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.params_frame = ttk.Frame(self.params_wrapper)
        self.params_frame.pack(fill=tk.X)

        # --- КНОПКИ ---
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.btn_run = ttk.Button(btn_frame, text="▶ Виконати", command=self._run, state=tk.DISABLED)
        self.btn_run.pack(side=tk.LEFT)
        self.btn_export = ttk.Button(btn_frame, text="💾 Експорт", command=self._export, state=tk.DISABLED)
        self.btn_export.pack(side=tk.RIGHT)

        # --- ТАБЛИЦЯ ---
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_frame, show="headings")
        sb_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        sb_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        sb_x.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_category_select(self, event):
        cat = self.cat_combo.get()
        queries = QUERY_GROUPS.get(cat, [])
        self.query_combo['values'] = [q['name'] for q in queries]
        if queries:
            self.query_combo.current(0)
            self._on_query_select(None)
        else:
            self.query_combo.set('')
            self._clear_params()

    def _on_query_select(self, event):
        cat = self.cat_combo.get()
        q_name = self.query_combo.get()
        queries = QUERY_GROUPS.get(cat, [])
        self.current_query_config = next((q for q in queries if q['name'] == q_name), None)

        if self.current_query_config:
            self.btn_run.config(state=tk.NORMAL)
            self._build_params(self.current_query_config)
        else:
            self.btn_run.config(state=tk.DISABLED)

    def _clear_params(self):
        # Очищаємо GUI
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        # Очищаємо логічний список
        self._param_widgets.clear()

    def _build_params(self, cfg):
        self._clear_params()
        params = cfg.get("params", [])

        if not params:
            ttk.Label(self.params_frame, text="Параметри не потрібні", foreground="gray").pack(anchor="w")
            return

        for p in params:
            row = ttk.Frame(self.params_frame)
            row.pack(fill=tk.X, pady=2)

            lbl_text = p.get("label", p["name"]) + ":"
            ttk.Label(row, text=lbl_text, width=20).pack(side=tk.LEFT)

            widget = None

            # 1. Випадаючий список з бази (DB Combo)
            if p["type"] == "db_combo":
                try:
                    table = p["table"]
                    display = p.get("display", "name")
                    cond = p.get("condition", "")
                    where_clause = f"WHERE {cond}" if cond else ""

                    query = f"SELECT id, {display} FROM {table} {where_clause} ORDER BY {display}"
                    data = self.db.query(query)

                    # Формат: "ID: Name"
                    values = [f"{r['id']}: {r[display]}" for r in data]
                    widget = ttk.Combobox(row, values=values, state="readonly", width=30)
                except Exception as e:
                    print(f"Error loading combo for {p['name']}: {e}")
                    widget = ttk.Entry(row)  # Fallback

            # 2. Ручний список (Manual Combo)
            elif p["type"] == "manual_combo":
                widget = ttk.Combobox(row, values=p["values"], state="readonly", width=30)

            # 3. Дата
            elif p["type"] == "date":
                widget = DateEntry(row, date_pattern="yyyy-mm-dd", width=25)

            # 4. Звичайний текст/число
            else:
                widget = ttk.Entry(row, width=30)

            widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Зберігаємо метадані про параметр разом із віджетом
            self._param_widgets.append({
                "meta": p,
                "widget": widget
            })

    def _run(self):
        if not self.current_query_config: return

        # Збір значень
        values = {}
        for item in self._param_widgets:
            meta = item["meta"]
            widget = item["widget"]
            raw_val = widget.get()

            if not raw_val:
                messagebox.showwarning("Увага", f"Заповніть поле '{meta.get('label', meta['name'])}'")
                return

            # Обробка значень
            final_val = raw_val

            if meta["type"] == "int":
                try:
                    final_val = int(raw_val)
                except:
                    messagebox.showerror("Помилка", "Потрібно ввести число")
                    return

            elif meta["type"] == "db_combo":
                # Витягуємо ID з рядка "ID: Name"
                try:
                    final_val = int(raw_val.split(":")[0])
                except:
                    return

            values[meta["name"]] = final_val

        try:
            cols, rows = self.db.query_with_columns(self.current_query_config["sql"], values)

            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = cols
            for c in cols:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=150)

            for r in rows:
                vals = [r[c] for c in cols]
                self.tree.insert("", tk.END, values=vals)

            self.btn_export.config(state=tk.NORMAL if rows else tk.DISABLED)
        except Exception as e:
            messagebox.showerror("SQL Помилка", str(e))

    def _export(self):
        items = self.tree.get_children()
        if not items: return

        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not fname: return

        try:
            with open(fname, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(self.tree["columns"])
                for i in items:
                    writer.writerow(self.tree.item(i)['values'])
            messagebox.showinfo("Успіх", "Файл збережено!")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))