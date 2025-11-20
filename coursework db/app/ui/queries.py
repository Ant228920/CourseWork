import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# ===============================
# PRESET QUERIES: OFFICER STAFF
# ===============================

# ===================================================================
# ПОВНИЙ СПИСОК ЗАПИТІВ (ВАРІАНТ 7)
# Скопіюйте цей список замість вашого старого PRESET_QUERIES
# ===================================================================

PRESET_QUERIES = [
    # --------------------------------------------------------
    # 1. ОФІЦЕРСЬКИЙ СКЛАД (Вже було у вас)
    # --------------------------------------------------------
    {
        "name": "1. Офіцери — загальний список",
        "sql": """
               SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
               FROM military_personnel mp
                        JOIN ranks r ON mp.rank_id = r.id
                        JOIN military_units mu ON mp.military_unit_id = mu.id
               WHERE r.category_id = 1;
               """
    },
    {
        "name": "1. Офіцери — за званням",
        "sql": """
               SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
               FROM military_personnel mp
                        JOIN ranks r ON mp.rank_id = r.id
                        JOIN military_units mu ON mp.military_unit_id = mu.id
               WHERE r.category_id = 1
                 AND r.name = %(rank_name)s;
               """,
        "params": ["RANK_NAME:str"]
    },

    # --------------------------------------------------------
    # 2. РЯДОВИЙ ТА СЕРЖАНТСЬКИЙ СКЛАД
    # --------------------------------------------------------
    {
        "name": "2. Рядові/Сержанти — загальний список",
        "sql": """
               SELECT mp.last_name, mp.first_name, r.name as rank, mu.name as unit
               FROM military_personnel mp
                        JOIN ranks r ON mp.rank_id = r.id
                        JOIN military_units mu ON mp.military_unit_id = mu.id
               WHERE r.category_id = 2;
               """
    },
    {
        "name": "2. Рядові/Сержанти — конкретної частини",
        "sql": """
               SELECT mp.last_name, mp.first_name, r.name as rank
               FROM military_personnel mp
                        JOIN ranks r ON mp.rank_id = r.id
               WHERE r.category_id = 2
                 AND mp.military_unit_id = %(unit_id)s;
               """,
        "params": ["UNIT_ID:int"]
    },

    # --------------------------------------------------------
    # 3. ВІЙСЬКОВА ТЕХНІКА (Vehicles)
    # --------------------------------------------------------
    {
        "name": "3. Техніка — наявність загалом",
        "sql": """
               SELECT v.name as vehicle, vc.name as category, mu.name as unit, v.serial_number
               FROM vehicles v
                        JOIN vehicle_categories vc ON v.category_id = vc.id
                        JOIN military_units mu ON v.military_unit_id = mu.id;
               """
    },
    {
        "name": "3. Техніка — певної категорії в Армії",
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
    },

    # --------------------------------------------------------
    # 4. ОЗБРОЄННЯ (Weapons)
    # --------------------------------------------------------
    {
        "name": "4. Озброєння — всього в окрузі",
        "sql": """
               SELECT w.name as weapon, wc.name as type, mu.name as unit, w.quantity
               FROM weapons w
                        JOIN weapon_categories wc ON w.category_id = wc.id
                        JOIN military_units mu ON w.military_unit_id = mu.id;
               """
    },
    {
        "name": "4. Озброєння — категорії у вказаній частині",
        "sql": """
               SELECT w.name, w.quantity, wc.name as category
               FROM weapons w
                        JOIN weapon_categories wc ON w.category_id = wc.id
               WHERE w.military_unit_id = %(unit_id)s
                 AND wc.name = %(cat_name)s;
               """,
        "params": ["UNIT_ID:int", "CAT_NAME:str"]
    },

    # --------------------------------------------------------
    # 5. СТАТИСТИКА (MAX/MIN частин)
    # --------------------------------------------------------
    {
        "name": "5. Армія з найбільшою к-стю частин",
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
        "name": "5. Дивізія з найменшою к-стю частин",
        "sql": """
               SELECT d.name as div_name, COUNT(mu.id) as units_count
               FROM divisions d
                        LEFT JOIN military_units mu ON mu.division_id = d.id
               GROUP BY d.id, d.name
               ORDER BY units_count ASC LIMIT 1;
               """
    },

    # --------------------------------------------------------
    # 6. ПЕРЕЛІК ЧАСТИН ТА ЇХ КЕРІВНИКІВ
    # --------------------------------------------------------
    {
        "name": "6. Частини та командири (вказаної дивізії)",
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
    },

    # --------------------------------------------------------
    # 7. МІСЦЯ ДИСЛОКАЦІЇ
    # --------------------------------------------------------
    {
        "name": "7. Дислокація — всі частини округу",
        "sql": """
               SELECT mu.name as unit, loc.address, loc.city
               FROM military_units mu
                        JOIN locations loc ON mu.location_id = loc.id;
               """
    },

    # --------------------------------------------------------
    # 8. СКЛАДНІ ЗАПИТИ (КІЛЬКІСТЬ ТЕХНІКИ/ЗБРОЇ)
    # --------------------------------------------------------
    {
        "name": "8. Частини з вказаною кількістю техніки (вид)",
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
        "name": "8. Частини БЕЗ вказаного виду озброєння",
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

    # --------------------------------------------------------
    # 9. СПЕЦІАЛЬНОСТІ
    # --------------------------------------------------------
    {
        "name": "9. Військові певної спеціальності (в частині)",
        "sql": """
               SELECT mp.last_name, mp.first_name, s.name as specialty
               FROM military_personnel mp
                        JOIN personnel_specialties ps ON mp.id = ps.personnel_id
                        JOIN specialties s ON ps.specialty_id = s.id
               WHERE s.name = %(spec_name)s
                 AND mp.military_unit_id = %(unit_id)s;
               """,
        "params": ["SPEC_NAME:str", "UNIT_ID:int"]
    },

    # --------------------------------------------------------
    # 10. СПОРУДИ
    # --------------------------------------------------------
    {
        "name": "10. Споруди — більше 1 підрозділу",
        "sql": """
               SELECT b.name as building, b.address, COUNT(u.id) as units_inside
               FROM buildings b
                        JOIN military_units u ON u.building_id = b.id
               GROUP BY b.id, b.name
               HAVING COUNT(u.id) > 1;
               """
    }
]

# ========================================
# QUERIES FRAME — FULL WORKING CLASS
# ========================================

class QueriesFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Query chooser
        self.cmb = ttk.Combobox(
            self, state="readonly",
            values=[q["name"] for q in PRESET_QUERIES]
        )
        self.cmb.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        self.cmb.bind("<<ComboboxSelected>>", self._on_select)

        # Params block
        self.params_frame = ttk.Frame(self)
        self.params_frame.grid(row=1, column=0, sticky="ew", padx=8)

        # Results tree
        self.tree = ttk.Treeview(self, show="headings")
        sb_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=(8,0), pady=8)
        sb_y.grid(row=2, column=0, sticky="nse", padx=(0,8), pady=8)

        # Run button
        btn_run = ttk.Button(self, text="Виконати", command=self._run)
        btn_run.grid(row=3, column=0, sticky="e", padx=8, pady=(0,8))

        self._param_widgets = []

        # Initialize first query
        if PRESET_QUERIES:
            self.cmb.current(0)
            self._build_params(0)

    # When user selects a query
    def _on_select(self, _):
        self._build_params(self.cmb.current())

    # Build parameter inputs
    def _build_params(self, idx):
        for w in self._param_widgets:
            w.destroy()
        self._param_widgets.clear()

        cfg = PRESET_QUERIES[idx]
        params = cfg.get("params", [])

        for i, spec in enumerate(params):
            name, typ = spec.split(":", 1)
            lbl = ttk.Label(self.params_frame, text=name)
            lbl.grid(row=0, column=i * 2, sticky="w", padx=(0, 4), pady=6)

            if typ == "date":
                ent = DateEntry(self.params_frame, date_pattern="yyyy-mm-dd")
            else:
                ent = ttk.Entry(self.params_frame)

            ent.grid(row=0, column=i * 2 + 1, sticky="ew", padx=(0, 12), pady=6)
            self.params_frame.columnconfigure(i * 2 + 1, weight=1)

            self._param_widgets.append(lbl)
            self._param_widgets.append(ent)

    # Collect param values
    def _collect_params(self, idx):
        cfg = PRESET_QUERIES[idx]
        params = cfg.get("params", [])
        values = {}  # Змінено на словник

        entries = [w for i, w in enumerate(self._param_widgets) if i % 2 == 1]

        for spec, widget in zip(params, entries):
            name, typ = spec.split(":", 1)
            val = widget.get()

            if typ == "int":
                try:
                    val = int(val)
                except ValueError:
                    messagebox.showerror("Помилка", f"Параметр {name} має бути числом")
                    return None

            # Використовуємо ім'я параметра як ключ (lowercase)
            values[name.lower()] = val

        return values

    # Execute SQL
    def _run(self):
        idx = self.cmb.current()
        cfg = PRESET_QUERIES[idx]
        params = self._collect_params(idx)

        if params is None:
            return

        try:
            # Main DB call
            cols, rows = self.db.query_with_columns(cfg["sql"], params)

            # Clear old rows
            self.tree.delete(*self.tree.get_children())

            # Setup columns
            self.tree["columns"] = cols
            for c in cols:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=160, anchor=tk.W)

            # Insert rows
            for r in rows:
                self.tree.insert("", tk.END, values=[r.get(c) for c in cols])

        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
