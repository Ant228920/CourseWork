import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from typing import Dict, Any, Optional
from datetime import datetime, date


class CRUDFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db

        self.current_subunit_type = tk.StringVar(value="company")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- ВЕРХНЯ ПАНЕЛЬ ---
        top_panel = ttk.Frame(self, padding=(10, 15))
        top_panel.grid(row=0, column=0, sticky="ew")

        ttk.Label(top_panel, text="Оберіть таблицю:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(top_panel, textvariable=self.entity_var, state="readonly", width=35,
                                         font=("Segoe UI", 10))
        self.entity_combo.pack(side=tk.LEFT)
        self.entity_combo.bind("<<ComboboxSelected>>", self._on_entity_select)

        self.content_frame = ttk.Frame(self, padding=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(2, weight=1)

        # ========================================================
        # КОНФІГУРАЦІЯ ТАБЛИЦЬ (З JOINS)
        # ========================================================
        self.entities = {
            "01. Типи Техніки": {
                "table": "equipment_types",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "category", "type": "combo", "required": True, "label": "Категорія",
                     "options": ["Combat Vehicle", "Transport Vehicle", "Artillery", "Special"]}
                ],
                "display_fields": ["id", "name", "category"],
                "headers": ["ID", "Назва", "Категорія"]
            },
            "02. Типи Озброєння": {
                "table": "weapon_types",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "category", "type": "combo", "required": True, "label": "Категорія",
                     "options": ["Small Arms", "Artillery", "Rocket Systems", "Anti-Tank"]}
                ],
                "display_fields": ["id", "name", "category"],
                "headers": ["ID", "Назва", "Категорія"]
            },
            "03. Спеціальності": {
                "table": "specialties",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "code", "type": "text", "required": True, "label": "Код"}
                ],
                "display_fields": ["id", "name", "code"],
                "headers": ["ID", "Назва", "Код"]
            },
            "04. Військові Округи": {
                "table": "military_districts",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва округу"},
                    {"name": "code", "type": "text", "required": False, "label": "Код"}
                ],
                "display_fields": ["id", "name", "code"],
                "headers": ["ID", "Назва", "Код"]
            },
            "05. Армії": {
                "table": "armies",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "military_district_id", "type": "combo", "required": True, "label": "Округ",
                     "source": "military_districts", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "district_name"],
                "headers": ["ID", "Номер", "Назва", "Округ"],
                "custom_sql": """
                              SELECT a.id, a.number, a.name, md.name as district_name
                              FROM armies a
                                       LEFT JOIN military_districts md ON a.military_district_id = md.id
                              ORDER BY a.number
                              """
            },
            "06. Корпуси": {
                "table": "corps",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "army_id", "type": "combo", "required": True, "label": "Армія",
                     "source": "armies", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "army_name"],
                "headers": ["ID", "Номер", "Назва", "Армія"],
                "custom_sql": """
                              SELECT c.id, c.number, c.name, a.name as army_name
                              FROM corps c
                                       LEFT JOIN armies a ON c.army_id = a.id
                              ORDER BY c.number
                              """
            },
            "07. Дивізії": {
                "table": "divisions",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "corps_id", "type": "combo", "required": True, "label": "Корпус",
                     "source": "corps", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "corps_name"],
                "headers": ["ID", "Номер", "Назва", "Корпус"],
                "custom_sql": """
                              SELECT d.id, d.number, d.name, c.name as corps_name
                              FROM divisions d
                                       LEFT JOIN corps c ON d.corps_id = c.id
                              ORDER BY d.number
                              """
            },
            "08. Бригади": {
                "table": "brigades",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "corps_id", "type": "combo", "required": True, "label": "Корпус",
                     "source": "corps", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "corps_name"],
                "headers": ["ID", "Номер", "Назва", "Корпус"],
                "custom_sql": """
                              SELECT b.id, b.number, b.name, c.name as corps_name
                              FROM brigades b
                                       LEFT JOIN corps c ON b.corps_id = c.id
                              ORDER BY b.number
                              """
            },
            "09. Локації": {
                "table": "locations",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "address", "type": "text", "required": False, "label": "Адреса"},
                    {"name": "region", "type": "text", "required": False, "label": "Регіон"},
                    {"name": "coordinates", "type": "text", "required": False, "label": "Координати"}
                ],
                "display_fields": ["id", "name", "address", "region", "coordinates"],
                "headers": ["ID", "Назва", "Адреса", "Регіон", "Координати"]
            },
            "10. Військові Частини": {
                "table": "military_units",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер в/ч"},
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "division_id", "type": "combo", "required": False, "label": "Дивізія",
                     "source": "divisions", "source_display": "number"},
                    {"name": "brigade_id", "type": "combo", "required": False, "label": "Бригада",
                     "source": "brigades", "source_display": "name"},
                    {"name": "location_id", "type": "combo", "required": False, "label": "Дислокація",
                     "source": "locations", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     "custom_query": "SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id WHERE r.command_level >= 3 ORDER BY mp.last_name"}
                ],
                "display_fields": ["id", "number", "name", "parent_unit", "location_name", "commander_name"],
                "headers": ["ID", "Номер в/ч", "Назва", "Підпорядкування", "Дислокація", "Командир"],
                "custom_sql": """
                              SELECT mu.id,
                                     mu.number,
                                     mu.name,
                                     COALESCE('Див. ' || d.number, 'Бриг. ' || b.number) as parent_unit,
                                     l.name                                              as location_name,
                                     mp.last_name || ' ' || LEFT (mp.first_name, 1) || '.' as commander_name
                              FROM military_units mu
                                  LEFT JOIN divisions d
                              ON mu.division_id = d.id
                                  LEFT JOIN brigades b ON mu.brigade_id = b.id
                                  LEFT JOIN locations l ON mu.location_id = l.id
                                  LEFT JOIN military_personnel mp ON mu.commander_id = mp.id
                              ORDER BY mu.number
                              """
            },
            "11. Військовослужбовці": {
                "table": "military_personnel",
                "fields": [
                    {"name": "last_name", "type": "text", "required": True, "label": "Прізвище"},
                    {"name": "first_name", "type": "text", "required": True, "label": "Ім'я"},
                    {"name": "middle_name", "type": "text", "required": False, "label": "По батькові"},  # 🔥 ДОДАНО
                    {"name": "rank_id", "type": "combo", "required": True, "label": "Звання",
                     "source": "ranks", "source_display": "name"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина",
                     "source": "military_units", "source_display": "number"},
                    {"name": "company_id", "type": "combo", "required": False, "label": "Рота", "source": "companies",
                     "source_display": "name"},
                    {"name": "platoon_id", "type": "combo", "required": False, "label": "Взвод", "source": "platoons",
                     "source_display": "name"},
                    {"name": "squad_id", "type": "combo", "required": False, "label": "Відділення", "source": "squads",
                     "source_display": "name"},
                    {"name": "enlistment_date", "type": "date", "required": False, "label": "Дата прийняття"},
                    {"name": "birth_date", "type": "date", "required": False, "label": "Дата народження"}
                ],
                # 🔥 Додано middle_name у display_fields
                "display_fields": ["id", "last_name", "first_name", "middle_name", "rank_name", "full_location"],
                "headers": ["ID", "Прізвище", "Ім'я", "По батькові", "Звання", "Місце служби"],
                "custom_sql": """
                              SELECT mp.id,
                                     mp.last_name,
                                     mp.first_name,
                                     mp.middle_name, -- 🔥 ДОДАНО
                                     r.name                                              as rank_name,
                                     CONCAT_WS(' / ', mu.number, c.name, p.name, s.name) as full_location
                              FROM military_personnel mp
                                       JOIN ranks r ON mp.rank_id = r.id
                                       JOIN military_units mu ON mp.military_unit_id = mu.id
                                       LEFT JOIN companies c ON mp.company_id = c.id
                                       LEFT JOIN platoons p ON mp.platoon_id = p.id
                                       LEFT JOIN squads s ON mp.squad_id = s.id
                              ORDER BY mp.id
                              """
            },
            "12. Техніка": {
                "table": "equipment",
                "fields": [
                    {"name": "model", "type": "text", "required": True, "label": "Модель"},
                    {"name": "serial_number", "type": "text", "required": False, "label": "Серійний номер"},
                    {"name": "year_manufactured", "type": "int", "required": False, "label": "Рік випуску"},
                    {"name": "equipment_type_id", "type": "combo", "required": True, "label": "Тип",
                     "source": "equipment_types", "source_display": "name"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина",
                     "source": "military_units", "source_display": "number"}
                ],
                "display_fields": ["id", "model", "serial_number", "type_name", "unit_num"],
                "headers": ["ID", "Модель", "Серійний №", "Тип", "В/Ч"],
                "custom_sql": """
                              SELECT e.id, e.model, e.serial_number, et.name as type_name, mu.number as unit_num
                              FROM equipment e
                                       JOIN equipment_types et ON e.equipment_type_id = et.id
                                       JOIN military_units mu ON e.military_unit_id = mu.id
                              ORDER BY e.model
                              """
            },
            "13. Озброєння": {
                "table": "weapons",
                "fields": [
                    {"name": "model", "type": "text", "required": True, "label": "Модель"},
                    {"name": "serial_number", "type": "text", "required": False, "label": "Номер"},
                    {"name": "caliber", "type": "text", "required": False, "label": "Калібр"},
                    {"name": "weapon_type_id", "type": "combo", "required": True, "label": "Тип",
                     "source": "weapon_types", "source_display": "name"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина",
                     "source": "military_units", "source_display": "number"}
                ],
                "display_fields": ["id", "model", "serial_number", "caliber", "type_name", "unit_num"],
                "headers": ["ID", "Модель", "Номер", "Калібр", "Тип", "В/Ч"],
                "custom_sql": """
                              SELECT w.id,
                                     w.model,
                                     w.serial_number,
                                     w.caliber,
                                     wt.name   as type_name,
                                     mu.number as unit_num
                              FROM weapons w
                                       JOIN weapon_types wt ON w.weapon_type_id = wt.id
                                       JOIN military_units mu ON w.military_unit_id = mu.id
                              ORDER BY w.model
                              """
            },
            "14. Споруди": {
                "table": "facilities",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "type", "type": "text", "required": True, "label": "Тип"},
                    {"name": "address", "type": "text", "required": False, "label": "Адреса"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина",
                     "source": "military_units", "source_display": "number"},
                    {"name": "location_id", "type": "combo", "required": False, "label": "Локація",
                     "source": "locations", "source_display": "name"}
                ],
                "display_fields": ["id", "name", "type", "unit_num", "loc_name"],
                "headers": ["ID", "Назва", "Тип", "Частина", "Локація"],
                "custom_sql": """
                              SELECT f.id, f.name, f.type, mu.number as unit_num, l.name as loc_name
                              FROM facilities f
                                       JOIN military_units mu ON f.military_unit_id = mu.id
                                       LEFT JOIN locations l ON f.location_id = l.id
                              ORDER BY f.name
                              """
            },
            "15. ТТХ Зброї": {
                "table": "weapon_attributes",
                "pk": "weapon_id",
                "fields": [
                    {"name": "weapon_id", "type": "combo", "required": True, "label": "Озброєння",
                     "source": "weapons", "source_display": "model"},
                    {"name": "max_range_km", "type": "text", "required": True, "label": "Дальність (км)"}
                ],
                "display_fields": ["id", "weapon_model", "max_range_km"],
                "headers": ["ID", "Модель зброї", "Макс. дальність"],
                "custom_sql": """
                              SELECT wa.id, w.model as weapon_model, wa.max_range_km
                              FROM weapon_attributes wa
                                       JOIN weapons w ON wa.weapon_id = w.id
                              """
            },
            "16. ТТХ Техніки": {
                "table": "vehicle_attributes",
                "pk": "equipment_id",
                "fields": [
                    {"name": "equipment_id", "type": "combo", "required": True, "label": "Техніка",
                     "source": "equipment", "source_display": "model"},
                    {"name": "max_speed_kmh", "type": "int", "required": False, "label": "Швидкість (км/г)"},
                    {"name": "armor_thickness_mm", "type": "int", "required": False, "label": "Броня (мм)"}
                ],
                "display_fields": ["id", "eq_model", "max_speed_kmh", "armor_thickness_mm"],
                "headers": ["ID", "Модель техніки", "Швидкість", "Броня"],
                "custom_sql": """
                              SELECT va.id, e.model as eq_model, va.max_speed_kmh, va.armor_thickness_mm
                              FROM vehicle_attributes va
                                       JOIN equipment e ON va.equipment_id = e.id
                              """
            },
            "17. Призначення спеціальностей": {
                "table": "personnel_specialties",
                "fields": [
                    {"name": "personnel_id", "type": "combo", "required": True, "label": "Військовий",
                     "source": "military_personnel", "source_display": "last_name"},
                    {"name": "specialty_id", "type": "combo", "required": True, "label": "Спеціальність",
                     "source": "specialties", "source_display": "name"}
                ],
                "display_fields": ["id", "person_name", "spec_name"],
                "headers": ["ID", "Військовий", "Спеціальність"],
                "custom_sql": """
                              SELECT ps.id, (mp.last_name || ' ' || mp.first_name) as person_name, s.name as spec_name
                              FROM personnel_specialties ps
                                       JOIN military_personnel mp ON ps.personnel_id = mp.id
                                       JOIN specialties s ON ps.specialty_id = s.id
                              """
            },
            "18. Інфо про Генералів": {
                "table": "generals_info",
                "pk": "personnel_id",
                "fields": [
                    {"name": "personnel_id", "type": "combo", "required": True, "label": "Генерал",
                     "source": "military_personnel", "source_display": "last_name"},
                    {"name": "academy_graduation_date", "type": "date", "required": False, "label": "Дата випуску"},
                    {"name": "academy_name", "type": "text", "required": True, "label": "Академія"}
                ],
                "display_fields": ["personnel_id", "gen_name", "academy_graduation_date", "academy_name"],
                "headers": ["ID", "Генерал", "Дата випуску", "Академія"],
                "custom_sql": """
                              SELECT gi.personnel_id,
                                     (mp.last_name || ' ' || mp.first_name) as gen_name,
                                     gi.academy_graduation_date,
                                     gi.academy_name
                              FROM generals_info gi
                                       JOIN military_personnel mp ON gi.personnel_id = mp.id
                              """
            },
            "19. Роти": {
                "table": "companies",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Військова частина",
                     "source": "military_units", "source_display": "number"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     "custom_query": "SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id WHERE r.command_level >= 2 ORDER BY mp.last_name"}
                ],
                "display_fields": ["id", "name", "unit_num", "cmdr_name"],
                "headers": ["ID", "Назва", "В/Ч", "Командир"],
                "custom_sql": """
                              SELECT c.id,
                                     c.name,
                                     mu.number                                               as unit_num,
                                     (mp.last_name || ' ' || LEFT (mp.first_name, 1) || '.') as cmdr_name
                              FROM companies c
                                       JOIN military_units mu ON c.military_unit_id = mu.id
                                       LEFT JOIN military_personnel mp ON c.commander_id = mp.id
                              """
            },
            "20. Взводи": {
                "table": "platoons",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "company_id", "type": "combo", "required": True, "label": "Рота",
                     "source": "companies", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     "custom_query": "SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id WHERE r.command_level >= 1 ORDER BY mp.last_name"}
                ],
                "display_fields": ["id", "name", "comp_name", "cmdr_name"],
                "headers": ["ID", "Назва", "Рота", "Командир"],
                "custom_sql": """
                              SELECT p.id,
                                     p.name,
                                     c.name                                                  as comp_name,
                                     (mp.last_name || ' ' || LEFT (mp.first_name, 1) || '.') as cmdr_name
                              FROM platoons p
                                       JOIN companies c ON p.company_id = c.id
                                       LEFT JOIN military_personnel mp ON p.commander_id = mp.id
                              """
            },
            "21. Відділення": {
                "table": "squads",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "platoon_id", "type": "combo", "required": True, "label": "Взвод",
                     "source": "platoons", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     "custom_query": "SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id WHERE r.command_level >= 1 ORDER BY mp.last_name"}
                ],
                "display_fields": ["id", "name", "plat_name", "cmdr_name"],
                "headers": ["ID", "Назва", "Взвод", "Командир"],
                "custom_sql": """
                              SELECT s.id,
                                     s.name,
                                     p.name                                                  as plat_name,
                                     (mp.last_name || ' ' || LEFT (mp.first_name, 1) || '.') as cmdr_name
                              FROM squads s
                                       JOIN platoons p ON s.platoon_id = p.id
                                       LEFT JOIN military_personnel mp ON s.commander_id = mp.id
                              """
            },
        }

        self.entity_combo['values'] = list(self.entities.keys())

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name: return

        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._create_crud_interface(self.entities[entity_name], entity_name)

    def _create_crud_interface(self, config: Dict[str, Any], entity_name: str):
        control_panel = ttk.Frame(self.content_frame, padding=(0, 0, 0, 10))
        control_panel.grid(row=0, column=0, sticky="ew")

        btn_frame = ttk.Frame(control_panel)
        btn_frame.pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="➕ Додати", command=lambda: self._add_record(config)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✏️ Редагувати", command=lambda: self._edit_record(config)).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(btn_frame, text="🗑️ Видалити", command=lambda: self._delete_record(config)).pack(side=tk.LEFT,
                                                                                                    padx=5)

        search_frame = ttk.LabelFrame(control_panel, text=" Пошук ", padding=(10, 5))
        search_frame.pack(side=tk.RIGHT, padx=10)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._search_records(config))

        ttk.Button(search_frame, text="🔄", width=3, command=lambda: self._refresh_table(config)).pack(side=tk.LEFT)

        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.content_frame.rowconfigure(1, weight=1)
        self._refresh_table(config)

    def _refresh_table(self, config: Dict[str, Any]):
        display_fields = config["display_fields"]
        headers = config.get("headers", display_fields)

        for item in self.tree.get_children(): self.tree.delete(item)

        self.tree["columns"] = display_fields
        for col, header in zip(display_fields, headers):
            self.tree.heading(col, text=header)
            width = 300 if "location" in col else 120
            self.tree.column(col, width=width, anchor=tk.W)

        if "custom_sql" in config:
            query = config["custom_sql"]
        else:
            table_name = config["table"]
            pk = config.get("pk", "id")
            fields_str = ", ".join(display_fields)
            query = f'SELECT {fields_str} FROM {table_name} ORDER BY {pk}'

        try:
            rows = self.db.query(query)
            for row in rows:
                values = []
                for col in display_fields:
                    val = row.get(col)
                    values.append(val if val is not None else "")
                self.tree.insert("", tk.END, values=values)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка завантаження: {e}")

    def _search_records(self, config: Dict[str, Any]):
        search_term = self.search_var.get().strip()
        if not search_term:
            self._refresh_table(config)
            return

        display_fields = config["display_fields"]
        pk = config.get("pk", "id")

        conditions = [f'{field}::text ILIKE %s' for field in display_fields if field != pk]
        if not conditions: return
        where_clause = " OR ".join(conditions)
        params = [f'%{search_term}%'] * len(conditions)

        if "custom_sql" in config:
            base_sql = config["custom_sql"]
            query = f"SELECT * FROM ({base_sql}) AS search_sub WHERE {where_clause}"
        else:
            table_name = config["table"]
            query = f'SELECT {", ".join(display_fields)} FROM {table_name} WHERE {where_clause} ORDER BY {pk}'

        try:
            cols, rows = self.db.query_with_columns(query, params)
            for item in self.tree.get_children(): self.tree.delete(item)
            for row in rows:
                values = [row.get(col) for col in display_fields]
                self.tree.insert("", tk.END, values=values)
        except Exception as e:
            print(f"Search error: {e}")

    def _add_record(self, config):
        self._show_record_dialog(config, "Додати запис")

    def _edit_record(self, config):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Виберіть запис!")
            return
        rid = self.tree.item(selection[0])['values'][0]
        pk = config.get("pk", "id")
        try:
            rows = self.db.query(f'SELECT * FROM {config["table"]} WHERE {pk}=%s', [rid])
            if rows: self._show_record_dialog(config, "Редагувати", dict(rows[0]))
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def _delete_record(self, config):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Виберіть запис!")
            return
        if not messagebox.askyesno("Підтвердження", "Видалити запис?"): return
        rid = self.tree.item(selection[0])['values'][0]
        pk = config.get("pk", "id")
        try:
            self.db.execute(f'DELETE FROM {config["table"]} WHERE {pk}=%s', [rid])
            self._refresh_table(config)
            messagebox.showinfo("Успіх", "Видалено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Неможливо видалити (можливо, є пов'язані записи): {e}")

    def _show_record_dialog(self, config: Dict[str, Any], title: str, record_data: Optional[Dict] = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("600x800")

        def close(event=None):
            dialog.destroy()
            return "break"

        dialog.bind('<Escape>', close)

        dialog.update_idletasks()
        try:
            x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
            y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
        except:
            pass

        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, padding=20)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        frame.columnconfigure(0, weight=1)

        widgets = {}
        pk = config.get("pk", "id")

        ttk.Label(frame, text=title, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, pady=(0, 20))
        current_row_idx = 1

        assignment_level_var = tk.StringVar(value="unit")
        unit_parent_var = tk.StringVar(value="division")
        rows_map = {}

        if config["table"] == "military_personnel":
            if record_data:
                if record_data.get('squad_id'):
                    assignment_level_var.set("squad")
                elif record_data.get('platoon_id'):
                    assignment_level_var.set("platoon")
                elif record_data.get('company_id'):
                    assignment_level_var.set("company")
                else:
                    assignment_level_var.set("unit")

            level_frame = ttk.LabelFrame(frame, text="Рівень призначення", padding=10)
            level_frame.grid(row=current_row_idx, column=0, sticky="ew", pady=(0, 15))
            current_row_idx += 1

            def update_personnel_visibility():
                lvl = assignment_level_var.get()
                if 'company_id' in rows_map: rows_map['company_id'].grid_remove()
                if 'platoon_id' in rows_map: rows_map['platoon_id'].grid_remove()
                if 'squad_id' in rows_map: rows_map['squad_id'].grid_remove()

                if lvl in ["company", "platoon", "squad"] and 'company_id' in rows_map:
                    rows_map['company_id'].grid()
                if lvl in ["platoon", "squad"] and 'platoon_id' in rows_map:
                    rows_map['platoon_id'].grid()
                if lvl == "squad" and 'squad_id' in rows_map:
                    rows_map['squad_id'].grid()

            ttk.Radiobutton(level_frame, text="Штаб Частини", variable=assignment_level_var, value="unit",
                            command=update_personnel_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Рота", variable=assignment_level_var, value="company",
                            command=update_personnel_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Взвод", variable=assignment_level_var, value="platoon",
                            command=update_personnel_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Відділення", variable=assignment_level_var, value="squad",
                            command=update_personnel_visibility).pack(side=tk.LEFT, padx=5)

        if config["table"] == "military_units":
            if record_data:
                if record_data.get('brigade_id'):
                    unit_parent_var.set("brigade")
                else:
                    unit_parent_var.set("division")

            parent_frame = ttk.LabelFrame(frame, text="Підпорядкування", padding=10)
            parent_frame.grid(row=current_row_idx, column=0, sticky="ew", pady=(0, 15))
            current_row_idx += 1

            def update_unit_visibility():
                ptype = unit_parent_var.get()
                if 'division_id' in rows_map:
                    if ptype == "division":
                        rows_map['division_id'].grid()
                    else:
                        rows_map['division_id'].grid_remove()

                if 'brigade_id' in rows_map:
                    if ptype == "brigade":
                        rows_map['brigade_id'].grid()
                    else:
                        rows_map['brigade_id'].grid_remove()

            ttk.Radiobutton(parent_frame, text="Дивізія", variable=unit_parent_var, value="division",
                            command=update_unit_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(parent_frame, text="Бригада", variable=unit_parent_var, value="brigade",
                            command=update_unit_visibility).pack(side=tk.LEFT, padx=5)

        def update_child_combo(child_name, table, fk_col, parent_id_str):
            child_widget = widgets.get(child_name)
            if not child_widget: return
            child_widget.set("")
            if not parent_id_str:
                child_widget['values'] = []
                return
            try:
                parent_id = int(parent_id_str.split(":")[0])
                sql = f"SELECT id, name as d_val FROM {table} WHERE {fk_col} = {parent_id} ORDER BY name"
                data = self.db.query(sql)
                vals = [f"{r['id']}: {r['d_val']}" for r in data]
                vals.insert(0, "")
                child_widget['values'] = vals
            except Exception as e:
                print(f"Combo error: {e}")

        def on_unit_change(event):
            val = widgets['military_unit_id'].get()
            update_child_combo('company_id', 'companies', 'military_unit_id', val)
            if 'platoon_id' in widgets: widgets['platoon_id'].set(""); widgets['platoon_id']['values'] = []
            if 'squad_id' in widgets: widgets['squad_id'].set(""); widgets['squad_id']['values'] = []

        def on_company_change(event):
            val = widgets['company_id'].get()
            update_child_combo('platoon_id', 'platoons', 'company_id', val)
            if 'squad_id' in widgets: widgets['squad_id'].set(""); widgets['squad_id']['values'] = []

        def on_platoon_change(event):
            val = widgets['platoon_id'].get()
            update_child_combo('squad_id', 'squads', 'platoon_id', val)

        for field in config["fields"]:
            f_name = field["name"]
            f_label = field["label"] + (" *" if field.get("required") else "")

            row = ttk.Frame(frame)
            row.grid(row=current_row_idx, column=0, sticky="ew", pady=5)
            rows_map[f_name] = row
            current_row_idx += 1

            ttk.Label(row, text=f_label, width=20).pack(side=tk.LEFT)

            w = None
            if field["type"] == "date":
                w = DateEntry(row, date_pattern="yyyy-mm-dd", width=25)
            elif field["type"] == "combo":
                load_now = True
                if config["table"] == "military_personnel" and f_name in ['company_id', 'platoon_id',
                                                                          'squad_id'] and not record_data:
                    load_now = False

                vals = []
                if load_now:
                    if "custom_query" in field:
                        try:
                            data = self.db.query(field["custom_query"])
                            vals = [f"{r['id']}: {r['d_val']}" for r in data]
                        except:
                            pass
                    elif "source" in field:
                        disp = field.get("source_display", "name")
                        try:
                            data = self.db.query(f'SELECT id, {disp} as d_val FROM {field["source"]} ORDER BY {disp}')
                            vals = [f"{r['id']}: {r['d_val']}" for r in data]
                        except:
                            pass
                    if not field.get("required"): vals.insert(0, "")

                w = ttk.Combobox(row, values=vals, state="readonly", width=28)
            else:
                w = ttk.Entry(row, width=30)

            w.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            widgets[f_name] = w

            if record_data and f_name in record_data:
                val = record_data[f_name]
                if val is not None:
                    if field["type"] == "combo":
                        search_prefix = f"{val}:"
                        found = False
                        for item in w['values']:
                            if item.startswith(search_prefix):
                                w.set(item);
                                found = True;
                                break
                        if not found and "source" in field:
                            try:
                                t_src = field["source"]
                                t_disp = field.get("source_display", "name")
                                res = self.db.query(f"SELECT {t_disp} FROM {t_src} WHERE id={val}")
                                if res: w.set(f"{val}: {res[0][t_disp]}")
                            except:
                                w.set(val)
                    elif field["type"] == "date":
                        try:
                            w.set_date(val)
                        except:
                            pass
                    elif hasattr(w, 'insert'):
                        w.delete(0, tk.END)
                        w.insert(0, str(val))


        if config["table"] == "military_personnel":
            widgets['military_unit_id'].bind("<<ComboboxSelected>>", on_unit_change)
            widgets['company_id'].bind("<<ComboboxSelected>>", on_company_change)
            widgets['platoon_id'].bind("<<ComboboxSelected>>", on_platoon_change)

            # Відновлення каскаду
            if record_data:
                u_val = widgets['military_unit_id'].get()
                update_child_combo('company_id', 'companies', 'military_unit_id', u_val)
                if record_data.get('company_id'):
                    c_id = record_data['company_id']
                    for v in widgets['company_id']['values']:
                        if v.startswith(f"{c_id}:"): widgets['company_id'].set(v); break

                c_val = widgets['company_id'].get()
                update_child_combo('platoon_id', 'platoons', 'company_id', c_val)
                if record_data.get('platoon_id'):
                    p_id = record_data['platoon_id']
                    for v in widgets['platoon_id']['values']:
                        if v.startswith(f"{p_id}:"): widgets['platoon_id'].set(v); break

                p_val = widgets['platoon_id'].get()
                update_child_combo('squad_id', 'squads', 'platoon_id', p_val)
                if record_data.get('squad_id'):
                    s_id = record_data['squad_id']
                    for v in widgets['squad_id']['values']:
                        if v.startswith(f"{s_id}:"): widgets['squad_id'].set(v); break

            update_personnel_visibility()

        if config["table"] == "military_units":
            update_unit_visibility()

        def save():
            data = {}

            personnel_level = assignment_level_var.get()
            unit_level = unit_parent_var.get()

            for f in config["fields"]:
                f_name = f["name"]
                w_widget = widgets[f_name]
                val = w_widget.get().strip()

                if config["table"] == "military_personnel":
                    if personnel_level == "unit":
                        if f_name in ["company_id", "platoon_id", "squad_id"]: val = ""
                    elif personnel_level == "company":
                        if f_name in ["platoon_id", "squad_id"]: val = ""
                    elif personnel_level == "platoon":
                        if f_name == "squad_id": val = ""

                if config["table"] == "military_units":
                    if unit_level == "division":
                        if f_name == "brigade_id": val = ""
                    else:  # brigade
                        if f_name == "division_id": val = ""

                if f.get("required") and not val:
                    if f_name in rows_map and not rows_map[f_name].winfo_viewable():
                        pass
                    else:
                        messagebox.showwarning("Не всі поля заповнені", f"Будь ласка, заповніть поле: '{f['label']}'")
                        return

                if f["type"] == "int":
                    data[f["name"]] = int(val) if val else None
                elif f["type"] == "combo":
                    data[f["name"]] = int(val.split(":")[0]) if val else None
                else:
                    data[f["name"]] = val if val else None

            if config["table"] == "military_units":
                if unit_level == "division" and not data.get("division_id"):
                    messagebox.showwarning("Увага", "Ви обрали тип 'Дивізія', але не вказали саму Дивізію.")
                    return
                if unit_level == "brigade" and not data.get("brigade_id"):
                    messagebox.showwarning("Увага", "Ви обрали тип 'Бригада', але не вказали саму Бригаду.")
                    return

            if config["table"] == "military_personnel":
                b_date = data.get("birth_date")
                e_date = data.get("enlistment_date")

                if b_date:
                    try:
                        if isinstance(b_date, str):
                            b_date_obj = datetime.strptime(b_date, "%Y-%m-%d").date()
                        else:
                            b_date_obj = b_date

                        today = date.today()
                        age = today.year - b_date_obj.year - (
                                    (today.month, today.day) < (b_date_obj.month, b_date_obj.day))

                        if age < 18:
                            messagebox.showwarning("Помилка віку", "Військовослужбовцю повинно бути мінімум 18 років!")
                            return
                    except Exception as e:
                        print(f"Date check error: {e}")

                if e_date:
                    try:
                        if isinstance(e_date, str):
                            e_date_obj = datetime.strptime(e_date, "%Y-%m-%d").date()
                        else:
                            e_date_obj = e_date

                        if e_date_obj > date.today():
                            messagebox.showwarning("Помилка дати",
                                                   "Дата прийняття на службу не може бути в майбутньому!")
                            return
                    except:
                        pass

            try:
                if record_data:
                    set_cl = ", ".join([f"{k}=%s" for k in data])
                    params = list(data.values()) + [record_data[pk]]
                    self.db.execute(f'UPDATE {config["table"]} SET {set_cl} WHERE {pk}=%s', params)
                else:
                    cols = ", ".join(data.keys())
                    phs = ", ".join(["%s"] * len(data))
                    self.db.execute(f'INSERT INTO {config["table"]} ({cols}) VALUES ({phs})', list(data.values()))

                messagebox.showinfo("Успіх", "Запис успішно збережено!")
                dialog.destroy()
                self._refresh_table(config)

            except Exception as e:
                if "duplicate key" in str(e):
                    messagebox.showerror("Помилка бази даних", "Такий запис вже існує (дублювання унікального поля).")
                else:
                    messagebox.showerror("Системна помилка", f"Деталі: {str(e)}")

        ttk.Button(frame, text="💾 Зберегти", command=save).grid(row=current_row_idx, column=0, pady=20, sticky="ew")