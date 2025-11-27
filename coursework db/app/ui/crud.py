import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from typing import Dict, List, Any, Optional

class CRUDFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db

        # Змінна для зберігання поточного фільтру підрозділів (рота/взвод/відділення)
        self.current_subunit_type = tk.StringVar(value="company")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- ВЕРХНЯ ПАНЕЛЬ (Вибір таблиці) ---
        top_panel = ttk.Frame(self, padding=(10, 15))
        top_panel.grid(row=0, column=0, sticky="ew")

        ttk.Label(top_panel, text="Оберіть таблицю:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(top_panel, textvariable=self.entity_var, state="readonly", width=35,
                                         font=("Segoe UI", 10))
        self.entity_combo.pack(side=tk.LEFT)
        self.entity_combo.bind("<<ComboboxSelected>>", self._on_entity_select)

        # --- ОСНОВНА ОБЛАСТЬ ---
        self.content_frame = ttk.Frame(self, padding=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(2, weight=1)

        # ========================================================
        # КОНФІГУРАЦІЯ ТАБЛИЦЬ
        # ========================================================
        self.entities = {
            # ... (Інші таблиці без змін) ...
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
            # --- ОСНОВНА СТРУКТУРА ---
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
                "display_fields": ["id", "number", "name", "military_district_id"],
                "headers": ["ID", "Номер", "Назва", "ID Округу"]
            },
            "06. Корпуси": {
                "table": "corps",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "army_id", "type": "combo", "required": True, "label": "Армія",
                     "source": "armies", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "army_id"],
                "headers": ["ID", "Номер", "Назва", "ID Армії"]
            },
            "07. Дивізії": {
                "table": "divisions",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "corps_id", "type": "combo", "required": True, "label": "Корпус",
                     "source": "corps", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "corps_id"],
                "headers": ["ID", "Номер", "Назва", "ID Корпусу"]
            },
            "08. Бригади": {
                "table": "brigades",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер"},
                    {"name": "name", "type": "text", "required": False, "label": "Назва"},
                    {"name": "corps_id", "type": "combo", "required": True, "label": "Корпус",
                     "source": "corps", "source_display": "name"}
                ],
                "display_fields": ["id", "number", "name", "corps_id"],
                "headers": ["ID", "Номер", "Назва", "ID Корпусу"]
            },
            "09. Локації": {
                "table": "locations",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "address", "type": "text", "required": False, "label": "Адреса"},
                    {"name": "region", "type": "text", "required": False, "label": "Регіон"},
                    {"name": "coordinates", "type": "text", "required": False, "label": "Координати (50.45, 30.52)"}
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
                     # 1. КОМАНДИР ЧАСТИНИ: Рівень 3+ (Майор, Полковник, Генерал)
                     "custom_query": """
                        SELECT 
                            mp.id, 
                            mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val 
                        FROM military_personnel mp
                        JOIN ranks r ON mp.rank_id = r.id
                        WHERE r.command_level >= 3 
                        ORDER BY mp.last_name
                     """
                    }
                ],
                "display_fields": ["id", "number", "name", "division_id", "brigade_id", "location_id", "commander_id"],
                "headers": ["ID", "Номер в/ч", "Назва", "ID Дивізії", "ID Бригади", "ID Локації", "ID Командира"]
            },
            "11. Військовослужбовці": {
                "table": "military_personnel",
                "fields": [
                    {"name": "last_name", "type": "text", "required": True, "label": "Прізвище"},
                    {"name": "first_name", "type": "text", "required": True, "label": "Ім'я"},
                    {"name": "rank_id", "type": "combo", "required": True, "label": "Звання",
                     "source": "ranks", "source_display": "name"},

                    # Поля для редагування (залишаються як були)
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина (Головна)",
                     "source": "military_units", "source_display": "number"},
                    {"name": "company_id", "type": "combo", "required": False, "label": "Рота",
                     "source": "companies", "source_display": "name"},
                    {"name": "platoon_id", "type": "combo", "required": False, "label": "Взвод",
                     "source": "platoons", "source_display": "name"},
                    {"name": "squad_id", "type": "combo", "required": False, "label": "Відділення",
                     "source": "squads", "source_display": "name"},

                    {"name": "enlistment_date", "type": "date", "required": False, "label": "Дата прийняття"},
                    {"name": "birth_date", "type": "date", "required": False, "label": "Дата народження"}
                ],

                # 🔥 ТЕПЕР ТУТ ГАРНІ НАЗВИ ПОЛІВ (віртуальні)
                "display_fields": ["id", "last_name", "first_name", "rank_name", "full_location"],
                "headers": ["ID", "Прізвище", "Ім'я", "Звання", "Місце служби"],

                # 🔥 А ОСЬ МАГІЯ SQL 🔥
                "custom_sql": """
                    SELECT 
                        mp.id, 
                        mp.last_name, 
                        mp.first_name, 
                        r.name as rank_name,
                        -- Ця функція склеює частини, пропускаючи пусті (NULL)
                        CONCAT_WS(' / ', 
                            mu.number, 
                            c.name, 
                            p.name, 
                            s.name
                        ) as full_location
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
                "display_fields": ["id", "model", "serial_number", "year_manufactured", "equipment_type_id",
                                   "military_unit_id"],
                "headers": ["ID", "Модель", "Серійний №", "Рік", "ID Типу", "ID Частини"]
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
                "display_fields": ["id", "model", "serial_number", "caliber", "weapon_type_id", "military_unit_id"],
                "headers": ["ID", "Модель", "Номер", "Калібр", "ID Типу", "ID Частини"]
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
                "display_fields": ["id", "name", "type", "military_unit_id"],
                "headers": ["ID", "Назва", "Тип", "ID Частини"]
            },
            "15. ТТХ Зброї": {
                "table": "weapon_attributes",
                "pk": "weapon_id",
                "fields": [
                    {"name": "weapon_id", "type": "combo", "required": True, "label": "Озброєння",
                     "source": "weapons", "source_display": "model"},
                    {"name": "max_range_km", "type": "text", "required": True, "label": "Дальність (км)"}
                ],
                "display_fields": ["id", "weapon_id", "max_range_km"],
                "headers": ["ID", "Зброя", "Макс. дальність"]
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
                "display_fields": ["id", "equipment_id", "max_speed_kmh", "armor_thickness_mm"],
                "headers": ["ID", "Техніка", "Швидкість", "Броня"]
            },
            "17. Призначення спеціальностей": {
                "table": "personnel_specialties",
                "fields": [
                    {"name": "personnel_id", "type": "combo", "required": True, "label": "Військовий",
                     "source": "military_personnel", "source_display": "last_name"},
                    {"name": "specialty_id", "type": "combo", "required": True, "label": "Спеціальність",
                     "source": "specialties", "source_display": "name"}
                ],
                "display_fields": ["id", "personnel_id", "specialty_id"],
                "headers": ["ID", "ID Військового", "ID Спец."]
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
                "display_fields": ["personnel_id", "academy_graduation_date", "academy_name"],
                "headers": ["ID Генерала", "Дата випуску", "Академія"]
            },
            # --- 🔥 НОВІ ПУНКТИ ДЛЯ СТРУКТУРИ (РОТИ, ВЗВОДИ, ВІДДІЛЕННЯ) ---
            "19. Роти": {
                "table": "companies",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Військова частина",
                     "source": "military_units", "source_display": "number"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     # 2. КОМАНДИР РОТИ: Рівень 2+ (Лейтенант, Капітан і вище)
                     "custom_query": """
                        SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val 
                        FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id
                        WHERE r.command_level >= 2 ORDER BY mp.last_name
                     """
                    }
                ],
                "display_fields": ["id", "name", "military_unit_id", "commander_id"],
                "headers": ["ID", "Назва", "ID в/ч", "ID Командира"]
            },
            "20. Взводи": {
                "table": "platoons",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "company_id", "type": "combo", "required": True, "label": "Рота",
                     "source": "companies", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     # 3. КОМАНДИР ВЗВОДУ: Рівень 1+ (Сержант і вище)
                     "custom_query": """
                        SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val 
                        FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id
                        WHERE r.command_level >= 1 ORDER BY mp.last_name
                     """
                    }
                ],
                "display_fields": ["id", "name", "company_id", "commander_id"],
                "headers": ["ID", "Назва", "ID Роти", "ID Командира"]
            },
            "21. Відділення": {
                "table": "squads",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "platoon_id", "type": "combo", "required": True, "label": "Взвод",
                     "source": "platoons", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     # 4. КОМАНДИР ВІДДІЛЕННЯ: Рівень 1+ (Сержант і вище)
                     "custom_query": """
                        SELECT mp.id, mp.last_name || ' ' || mp.first_name || ' (' || r.name || ')' as d_val 
                        FROM military_personnel mp JOIN ranks r ON mp.rank_id = r.id
                        WHERE r.command_level >= 1 ORDER BY mp.last_name
                     """
                    }
                ],
                "display_fields": ["id", "name", "platoon_id", "commander_id"],
                "headers": ["ID", "Назва", "ID Взводу", "ID Командира"]
            },
            # --- 🔥 УНІФІКОВАНИЙ ПУНКТ РОЗКВАРТИРУВАННЯ ---
        }

        self.entity_combo['values'] = list(self.entities.keys())

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name: return

        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._create_crud_interface(self.entities[entity_name], entity_name)

    def _create_crud_interface(self, config: Dict[str, Any], entity_name: str):
        # 1. Панель управління
        control_panel = ttk.Frame(self.content_frame, padding=(0, 0, 0, 10))
        control_panel.grid(row=0, column=0, sticky="ew")

        # Кнопки
        btn_frame = ttk.Frame(control_panel)
        btn_frame.pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="➕ Додати", command=lambda: self._add_record(config)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✏️ Редагувати", command=lambda: self._edit_record(config)).pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(btn_frame, text="🗑️ Видалити", command=lambda: self._delete_record(config)).pack(side=tk.LEFT,
                                                                                                    padx=5)

        # --- 🔥 ДОДАТКОВИЙ ФІЛЬТР ДЛЯ РОЗКВАРТИРУВАННЯ ---
        if "Розквартирування" in entity_name:
            filter_frame = ttk.LabelFrame(control_panel, text=" Тип підрозділу ", padding=(5, 0))
            filter_frame.pack(side=tk.LEFT, padx=15)

            # Комбобокс для перемикання типу (рота/взвод/відділення)
            type_combo = ttk.Combobox(filter_frame, textvariable=self.current_subunit_type,
                                      values=["company", "platoon", "squad"], state="readonly", width=15)
            type_combo.pack()
            type_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_table(config))

        # Пошук
        search_frame = ttk.LabelFrame(control_panel, text=" Пошук ", padding=(10, 5))
        search_frame.pack(side=tk.RIGHT, padx=10)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self._search_records(config))

        ttk.Button(search_frame, text="🔄", width=3, command=lambda: self._refresh_table(config)).pack(side=tk.LEFT)

        # 2. Таблиця
        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Скролбари
        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.content_frame.rowconfigure(1, weight=1)
        self._refresh_table(config)

    def _refresh_table(self, config: Dict[str, Any]):
        table_name = config["table"]
        display_fields = config["display_fields"]
        headers = config.get("headers", display_fields)
        pk = config.get("pk", "id")

        # Очищаємо таблицю
        for item in self.tree.get_children(): self.tree.delete(item)

        # Налаштовуємо колонки
        self.tree["columns"] = display_fields
        for col, header in zip(display_fields, headers):
            self.tree.heading(col, text=header)
            # Робимо колонку "Місце служби" ширшою
            width = 300 if "location" in col else 120
            self.tree.column(col, width=width, anchor=tk.W)

        # 🔥 ГОЛОВНА ЗМІНА ТУТ 🔥
        # Якщо в конфігу є свій SQL - використовуємо його, інакше - стандартний
        if "custom_sql" in config:
            query = config["custom_sql"]
        else:
            # Стандартна логіка
            fields_str = ", ".join(display_fields)
            where_clause = ""
            if table_name == "facility_subunits":
                subtype = self.current_subunit_type.get()
                where_clause = f"WHERE subunit_type = '{subtype}'"
            query = f'SELECT {fields_str} FROM {table_name} {where_clause} ORDER BY {pk}'

        try:
            # Виконуємо запит
            # (query_with_columns не потрібен, бо ми знаємо порядок полів з display_fields)
            rows = self.db.query(query)

            for row in rows:
                # Збираємо дані в список у тому порядку, який вказано в display_fields
                # (Оскільки row - це словник, беремо значення по ключах)
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
        table_name = config["table"]
        display_fields = config["display_fields"]
        pk = config.get("pk", "id")
        conditions = [f'{field}::text ILIKE %s' for field in display_fields if field != pk]
        if not conditions: return

        # Враховуємо фільтр типу підрозділу при пошуку
        extra_where = ""
        if table_name == "facility_subunits":
            subtype = self.current_subunit_type.get()
            extra_where = f"AND subunit_type = '{subtype}'"

        where_clause = " OR ".join(conditions)
        query = f'SELECT {", ".join(display_fields)} FROM {table_name} WHERE ({where_clause}) {extra_where} ORDER BY {pk}'
        params = [f'%{search_term}%'] * len(conditions)
        try:
            cols, rows = self.db.query_with_columns(query, params)
            for item in self.tree.get_children(): self.tree.delete(item)
            for row in rows:
                values = [row.get(col) for col in display_fields]
                self.tree.insert("", tk.END, values=values)
        except Exception:
            pass

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
            messagebox.showerror("Помилка", f"Неможливо видалити: {e}")

    def _show_record_dialog(self, config: Dict[str, Any], title: str, record_data: Optional[Dict] = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("600x800")  # Збільшив висоту

        def close(event=None):
            dialog.destroy()
            return "break"

        dialog.bind('<Escape>', close)

        # Центрування
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

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

        # --- 🔥 ЛОГІКА РІВНІВ ПРИЗНАЧЕННЯ (Тільки для Військових) ---
        assignment_level_var = tk.StringVar(value="unit")  # unit, company, platoon, squad
        rows_map = {}  # Зберігатимемо посилання на рядки інтерфейсу, щоб ховати їх

        if config["table"] == "military_personnel":
            # Визначаємо початковий рівень, якщо редагуємо
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

            # Функція для приховування/показу полів
            def update_visibility():
                lvl = assignment_level_var.get()

                # Спочатку сховаємо все, крім Unit (він обов'язковий)
                if 'company_id' in rows_map: rows_map['company_id'].grid_remove()
                if 'platoon_id' in rows_map: rows_map['platoon_id'].grid_remove()
                if 'squad_id' in rows_map: rows_map['squad_id'].grid_remove()

                # Тепер показуємо залежно від рівня
                if lvl in ["company", "platoon", "squad"]:
                    if 'company_id' in rows_map: rows_map['company_id'].grid()

                if lvl in ["platoon", "squad"]:
                    if 'platoon_id' in rows_map: rows_map['platoon_id'].grid()

                if lvl == "squad":
                    if 'squad_id' in rows_map: rows_map['squad_id'].grid()

            ttk.Radiobutton(level_frame, text="Штаб Частини", variable=assignment_level_var, value="unit",
                            command=update_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Рота", variable=assignment_level_var, value="company",
                            command=update_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Взвод", variable=assignment_level_var, value="platoon",
                            command=update_visibility).pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(level_frame, text="Відділення", variable=assignment_level_var, value="squad",
                            command=update_visibility).pack(side=tk.LEFT, padx=5)

        # --- ГЕНЕРАЦІЯ ПОЛІВ ---
        # Логіка оновлення списків (каскад)
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
            if 'platoon_id' in widgets:
                widgets['platoon_id'].set("")
                widgets['platoon_id']['values'] = []
            if 'squad_id' in widgets:
                widgets['squad_id'].set("")
                widgets['squad_id']['values'] = []

        def on_company_change(event):
            val = widgets['company_id'].get()
            update_child_combo('platoon_id', 'platoons', 'company_id', val)
            if 'squad_id' in widgets:
                widgets['squad_id'].set("")
                widgets['squad_id']['values'] = []

        def on_platoon_change(event):
            val = widgets['platoon_id'].get()
            update_child_combo('squad_id', 'squads', 'platoon_id', val)

        for field in config["fields"]:
            f_name = field["name"]
            f_label = field["label"] + (" *" if field.get("required") else "")

            row = ttk.Frame(frame)
            row.grid(row=current_row_idx, column=0, sticky="ew", pady=5)
            rows_map[f_name] = row  # Зберігаємо посилання на рядок
            current_row_idx += 1

            ttk.Label(row, text=f_label, width=20).pack(side=tk.LEFT)

            w = None
            if field["type"] == "date":
                w = DateEntry(row, date_pattern="yyyy-mm-dd", width=25)
            elif field["type"] == "combo":
                load_now = True
                # Не вантажимо залежні списки одразу
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

            # --- ЗАПОВНЕННЯ ПРИ РЕДАГУВАННІ ---
            if record_data and f_name in record_data:
                val = record_data[f_name]
                if val is not None:
                    if field["type"] == "combo":
                        search_prefix = f"{val}:"
                        found = False
                        for item in w['values']:
                            if item.startswith(search_prefix):
                                w.set(item)
                                found = True
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

        # --- БІНДИНГ ПОДІЙ ---
        if config["table"] == "military_personnel":
            widgets['military_unit_id'].bind("<<ComboboxSelected>>", on_unit_change)
            widgets['company_id'].bind("<<ComboboxSelected>>", on_company_change)
            widgets['platoon_id'].bind("<<ComboboxSelected>>", on_platoon_change)

            # Відновлення каскаду при редагуванні
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

            # Оновлюємо видимість полів відповідно до обраного радіобаттона
            update_visibility()

        # --- ФУНКЦІЯ ЗБЕРЕЖЕННЯ ---
        def save():
            data = {}
            current_level = assignment_level_var.get()

            for f in config["fields"]:
                f_name = f["name"]
                w_widget = widgets[f_name]
                val = w_widget.get().strip()

                # Очищення даних залежно від рівня (Щоб не записати сміття)
                if config["table"] == "military_personnel":
                    if current_level == "unit":
                        if f_name in ["company_id", "platoon_id", "squad_id"]: val = ""
                    elif current_level == "company":
                        if f_name in ["platoon_id", "squad_id"]: val = ""
                    elif current_level == "platoon":
                        if f_name == "squad_id": val = ""

                if f.get("required") and not val:
                    # Перевіряємо, чи поле видиме (якщо сховане - ігноруємо required)
                    if f_name in rows_map:
                        if rows_map[f_name].winfo_viewable():
                            messagebox.showwarning("Увага", f"Заповніть поле '{f['label']}'")
                            return
                    else:
                        messagebox.showwarning("Увага", f"Заповніть поле '{f['label']}'")
                        return

                if f["type"] == "int":
                    data[f["name"]] = int(val) if val else None
                elif f["type"] == "combo":
                    data[f["name"]] = int(val.split(":")[0]) if val else None
                else:
                    data[f["name"]] = val if val else None

            try:
                if record_data:
                    set_cl = ", ".join([f"{k}=%s" for k in data])
                    params = list(data.values()) + [record_data[pk]]
                    self.db.execute(f'UPDATE {config["table"]} SET {set_cl} WHERE {pk}=%s', params)
                else:
                    cols = ", ".join(data.keys())
                    phs = ", ".join(["%s"] * len(data))
                    self.db.execute(f'INSERT INTO {config["table"]} ({cols}) VALUES ({phs})', list(data.values()))

                messagebox.showinfo("ОК", "Збережено")
                dialog.destroy()
                self._refresh_table(config)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(frame, text="💾 Зберегти", command=save).grid(row=current_row_idx, column=0, pady=20, sticky="ew")

        def save():
            data = {}
            for f in config["fields"]:
                w_widget = widgets[f["name"]]
                val = w_widget.get().strip()

                if f.get("required") and not val:
                    # Якщо поле приховане (через перемикач), ми не повинні вимагати його заповнення,
                    # але оскільки ми його очищуємо, валідація 'required' може спрацювати.
                    # В конфігу division_id і brigade_id мають required=False, тому тут все ок.
                    messagebox.showwarning("Увага", f"Заповніть поле '{f['label']}'")
                    return

                if f["type"] == "int":
                    data[f["name"]] = int(val) if val else None
                elif f["type"] == "combo" and ("source" in f or "custom_query" in f):
                    data[f["name"]] = int(val.split(":")[0]) if val else None
                else:
                    data[f["name"]] = val if val else None

            # --- ВАЛІДАЦІЯ: Військова частина не може бути одночасно і в Дивізії, і в Бригаді ---
            # Ця перевірка тепер менш критична, бо UI це контролює, але не завадить.
            if config["table"] == "military_units":
                div_id = data.get("division_id")
                brig_id = data.get("brigade_id")

                if div_id is not None and brig_id is not None:
                    messagebox.showerror(
                        "Помилка підпорядкування",
                        "Військова частина НЕ може підпорядковуватися одночасно і Дивізії, і Бригаді."
                    )
                    return
            # ------------------------------------------------------------------------------------

            try:
                if record_data:
                    set_cl = ", ".join([f"{k}=%s" for k in data])
                    params = list(data.values()) + [record_data[pk]]
                    self.db.execute(f'UPDATE {config["table"]} SET {set_cl} WHERE {pk}=%s', params)
                else:
                    cols = ", ".join(data.keys())
                    phs = ", ".join(["%s"] * len(data))
                    self.db.execute(f'INSERT INTO {config["table"]} ({cols}) VALUES ({phs})', list(data.values()))

                messagebox.showinfo("ОК", "Збережено")
                dialog.destroy()
                self._refresh_table(config)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(frame, text="💾 Зберегти", command=save).grid(row=current_row_idx, column=0, pady=20, sticky="ew")