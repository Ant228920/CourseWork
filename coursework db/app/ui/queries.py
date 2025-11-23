import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from tkcalendar import DateEntry

# ===================================================================
# ГРУПОВАНА СТРУКТУРА ЗАПИТІВ
# ===================================================================

QUERY_GROUPS = {
    "Офіцерський склад": [
        {
            "name": "Загальний список",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id = 1;
                   """
        },
        {
            "name": "Пошук за званням",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id = 1
                     AND r.name = %(rank_name)s;
                   """,
            "params": ["RANK_NAME:str"]
        }
    ],
    "Рядовий та сержантський склад": [
        {
            "name": "Загальний список",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                            JOIN military_units mu ON mp.military_unit_id = mu.id
                   WHERE r.category_id = 2;
                   """
        },
        {
            "name": "Список конкретної частини",
            "sql": """
                   SELECT mp.last_name, mp.first_name, r.name as rank
                   FROM military_personnel mp
                            JOIN ranks r ON mp.rank_id = r.id
                   WHERE r.category_id = 2
                     AND mp.military_unit_id = %(unit_id)s;
                   """,
            "params": ["UNIT_ID:int"]
        }
    ],
    "Військова техніка": [
        {
            "name": "Наявність загалом",
            "sql": """
                   SELECT v.name as vehicle, vc.name as category, mu.name as unit, v.serial_number
                   FROM vehicles v
                            JOIN vehicle_categories vc ON v.category_id = vc.id
                            JOIN military_units mu ON v.military_unit_id = mu.id;
                   """
        },
        {
            "name": "Певної категорії в Армії",
            "sql": """
                   SELECT v.name, v.serial_number, mu.name as unit_name
                   FROM vehicles v
                            JOIN vehicle_categories vc ON v.category_id = vc.id
                            JOIN military_units mu ON v.military_unit_id = mu.id
                            JOIN divisions d ON mu.division_id = d.id
                            JOIN corps c ON d.corps_id = c.id
                   WHERE vc.name = %(category_name)s
                     AND c.army_id = %(army_id)s;
                   """,
            "params": ["CATEGORY_NAME:str", "ARMY_ID:int"]
        }
    ],
    "Озброєння": [
        {
            "name": "Всього в окрузі",
            "sql": """
                   SELECT w.name as weapon, wc.name as type, mu.name as unit, w.quantity
                   FROM weapons w
                            JOIN weapon_categories wc ON w.category_id = wc.id
                            JOIN military_units mu ON w.military_unit_id = mu.id;
                   """
        },
        {
            "name": "Категорії у вказаній частині",
            "sql": """
                   SELECT w.name, w.quantity, wc.name as category
                   FROM weapons w
                            JOIN weapon_categories wc ON w.category_id = wc.id
                   WHERE w.military_unit_id = %(unit_id)s
                     AND wc.name = %(cat_name)s;
                   """,
            "params": ["UNIT_ID:int", "CAT_NAME:str"]
        }
    ],
    "Статистика частин": [
        {
            "name": "Армія з найбільшою к-стю частин",
            "sql": """
                   SELECT a.name as army_name, COUNT(mu.id) as units_count
                   FROM armies a
                            JOIN corps c ON c.army_id = a.id
                            JOIN divisions d ON d.corps_id = c.id
                            JOIN military_units mu ON mu.division_id = d.id
                   GROUP BY a.id, a.name
                   ORDER BY units_count DESC LIMIT 1;
                   """
        },
        {
            "name": "Дивізія з найменшою к-стю частин",
            "sql": """
                   SELECT d.name as div_name, COUNT(mu.id) as units_count
                   FROM divisions d
                            LEFT JOIN military_units mu ON mu.division_id = d.id
                   GROUP BY d.id, d.name
                   ORDER BY units_count ASC LIMIT 1;
                   """
        }
    ],
    "Керівний склад": [
        {
            "name": "Частини та командири (вказаної дивізії)",
            "sql": """
                   SELECT mu.name      as unit,
                          mp.last_name as commander_surname,
                          r.name       as commander_rank
                   FROM military_units mu
                            JOIN military_personnel mp ON mu.commander_id = mp.id
                            JOIN ranks r ON mp.rank_id = r.id
                   WHERE mu.division_id = %(div_id)s;
                   """,
            "params": ["DIV_ID:int"]
        }
    ],
    "Інфраструктура та Дислокація": [
        {
            "name": "Дислокація всіх частин",
            "sql": """
                   SELECT mu.name as unit, loc.address, loc.city
                   FROM military_units mu
                            JOIN locations loc ON mu.location_id = loc.id;
                   """
        },
        {
            "name": "Споруди з >1 підрозділом",
            "sql": """
                   SELECT b.name as building, b.address, COUNT(u.id) as units_inside
                   FROM buildings b
                            JOIN military_units u ON u.building_id = b.id
                   GROUP BY b.id, b.name
                   HAVING COUNT(u.id) > 1;
                   """
        }
    ],
    "Спеціальні запити": [
        {
            "name": "Частини за кількістю техніки",
            "sql": """
                   SELECT mu.name as unit, COUNT(v.id) as amount
                   FROM military_units mu
                            JOIN vehicles v ON v.military_unit_id = mu.id
                            JOIN vehicle_categories vc ON v.category_id = vc.id
                   WHERE vc.name = %(veh_type)s
                   GROUP BY mu.id, mu.name
                   HAVING COUNT(v.id) = %(amount)s;
                   """,
            "params": ["VEH_TYPE:str", "AMOUNT:int"]
        },
        {
            "name": "Частини БЕЗ вказаного озброєння",
            "sql": """
                   SELECT mu.name
                   FROM military_units mu
                   WHERE mu.id NOT IN (SELECT w.military_unit_id
                                       FROM weapons w
                                                JOIN weapon_categories wc ON w.category_id = wc.id
                                       WHERE wc.name = %(weapon_type)s);
                   """,
            "params": ["WEAPON_TYPE:str"]
        },
        {
            "name": "Військові певної спеціальності",
            "sql": """
                   SELECT mp.last_name, mp.first_name, s.name as specialty
                   FROM military_personnel mp
                            JOIN personnel_specialties ps ON mp.id = ps.personnel_id
                            JOIN specialties s ON ps.specialty_id = s.id
                   WHERE s.name = %(spec_name)s
                     AND mp.military_unit_id = %(unit_id)s;
                   """,
            "params": ["SPEC_NAME:str", "UNIT_ID:int"]
        }
    ]
}


# ========================================
# QUERIES FRAME
# ========================================

class QueriesFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.current_query_config = None  # Тут зберігаємо поточний вибраний конфіг

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)  # Таблиця розтягується

        # --- БЛОК ВИБОРУ ---
        selection_frame = ttk.LabelFrame(self, text="Вибір запиту", padding=10)
        selection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        selection_frame.columnconfigure(1, weight=1)

        # 1. Категорія
        ttk.Label(selection_frame, text="Категорія:").grid(row=0, column=0, sticky="w", padx=5)
        self.cat_combo = ttk.Combobox(selection_frame, state="readonly", values=list(QUERY_GROUPS.keys()))
        self.cat_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.cat_combo.bind("<<ComboboxSelected>>", self._on_category_select)

        # 2. Конкретний запит
        ttk.Label(selection_frame, text="Запит:").grid(row=1, column=0, sticky="w", padx=5)
        self.query_combo = ttk.Combobox(selection_frame, state="readonly")
        self.query_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.query_combo.bind("<<ComboboxSelected>>", self._on_query_select)

        # --- БЛОК ПАРАМЕТРІВ ---
        self.params_wrapper = ttk.LabelFrame(self, text="Параметри пошуку", padding=10)
        self.params_wrapper.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.params_frame = ttk.Frame(self.params_wrapper)
        self.params_frame.pack(fill=tk.X)
        self._param_widgets = []

        # --- КНОПКИ ---
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.btn_run = ttk.Button(btn_frame, text="▶ Виконати", command=self._run, state=tk.DISABLED)
        self.btn_run.pack(side=tk.LEFT)

        self.btn_export = ttk.Button(btn_frame, text="💾 Експорт (CSV)", command=self._export, state=tk.DISABLED)
        self.btn_export.pack(side=tk.RIGHT)

        # --- ТАБЛИЦЯ РЕЗУЛЬТАТІВ ---
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
        """Коли обрали категорію, оновлюємо список запитів"""
        category = self.cat_combo.get()
        queries = QUERY_GROUPS.get(category, [])

        # Оновлюємо другий комбобокс
        self.query_combo['values'] = [q['name'] for q in queries]
        if queries:
            self.query_combo.current(0)
            self._on_query_select(None)  # Автоматично вибираємо перший
        else:
            self.query_combo.set('')
            self._clear_params()

    def _on_query_select(self, event):
        """Коли обрали конкретний запит, будуємо поля для параметрів"""
        category = self.cat_combo.get()
        query_name = self.query_combo.get()

        # Шукаємо конфіг у словнику
        queries = QUERY_GROUPS.get(category, [])
        self.current_query_config = next((q for q in queries if q['name'] == query_name), None)

        if self.current_query_config:
            self.btn_run.config(state=tk.NORMAL)
            self._build_params(self.current_query_config)
        else:
            self.btn_run.config(state=tk.DISABLED)

    def _clear_params(self):
        for w in self._param_widgets: w.destroy()
        self._param_widgets.clear()

    def _build_params(self, cfg):
        self._clear_params()
        params = cfg.get("params", [])

        if not params:
            lbl = ttk.Label(self.params_frame, text="Цей запит не потребує параметрів", foreground="grey")
            lbl.pack(anchor="w")
            self._param_widgets.append(lbl)
            return

        # Будуємо сітку параметрів
        for i, spec in enumerate(params):
            name, typ = spec.split(":", 1)

            row_f = ttk.Frame(self.params_frame)
            row_f.pack(fill=tk.X, pady=2)

            lbl = ttk.Label(row_f, text=f"{name}:", width=20)
            lbl.pack(side=tk.LEFT)

            if typ == "date":
                ent = DateEntry(row_f, date_pattern="yyyy-mm-dd", width=20)
            else:
                ent = ttk.Entry(row_f, width=25)

            ent.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Зберігаємо посилання на віджети
            self._param_widgets.append((name, typ, ent))

    def _collect_params(self):
        if not self.current_query_config: return None

        params_def = self.current_query_config.get("params", [])
        if not params_def: return {}  # Порожній словник, якщо параметрів немає

        values = {}
        # self._param_widgets тепер містить кортежі (name, type, widget)
        # Або лейбл, якщо параметрів немає (тоді список пустий для циклу нижче)

        real_widgets = [w for w in self._param_widgets if isinstance(w, tuple)]

        for name, typ, widget in real_widgets:
            val = widget.get()
            if not val:  # Проста перевірка на пустоту
                messagebox.showwarning("Увага", f"Заповніть поле '{name}'")
                return None

            if typ == "int":
                try:
                    val = int(val)
                except ValueError:
                    messagebox.showerror("Помилка", f"Параметр '{name}' має бути числом")
                    return None

            values[name.lower()] = val

        return values

    def _run(self):
        if not self.current_query_config: return

        params = self._collect_params()
        if params is None: return

        try:
            # Main DB call
            cols, rows = self.db.query_with_columns(self.current_query_config["sql"], params)

            # Clear old rows
            self.tree.delete(*self.tree.get_children())

            # Setup columns
            self.tree["columns"] = cols
            for c in cols:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=150, anchor=tk.W)

            # Insert rows
            for r in rows:
                # r - це словник, тому беремо значення по ключах колонок
                values = [r.get(c) for c in cols]
                self.tree.insert("", tk.END, values=values)

            self.btn_export.config(state=tk.NORMAL if rows else tk.DISABLED)

        except Exception as e:
            messagebox.showerror("SQL Error", str(e))

    def _export(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Увага", "Немає даних для експорту")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filename: return

        try:
            cols = self.tree["columns"]
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for item in items:
                    writer.writerow(self.tree.item(item)['values'])
            messagebox.showinfo("Успіх", "Звіт збережено!")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))