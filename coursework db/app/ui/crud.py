import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from typing import Dict, List, Any, Optional


class CRUDFrame(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- ВЕРХНЯ ПАНЕЛЬ (Вибір таблиці) ---
        top_panel = ttk.Frame(self, padding=(10, 15))
        top_panel.grid(row=0, column=0, sticky="ew")

        ttk.Label(top_panel, text="Оберіть таблицю для редагування:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT,
                                                                                                          padx=(0, 10))

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
            # --- ДОВІДНИКИ ---
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
                     "source": "armies", "source_display": "number"}
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
                     "source": "corps", "source_display": "number"}
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
                    {"name": "region", "type": "text", "required": False, "label": "Регіон"}
                ],
                "display_fields": ["id", "name", "address", "region"],
                "headers": ["ID", "Назва", "Адреса", "Регіон"]
            },
            "10. Військові Частини": {
                "table": "military_units",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Номер в/ч"},
                    {"name": "name", "type": "text", "required": True, "label": "Назва"},
                    {"name": "division_id", "type": "combo", "required": False, "label": "Дивізія",
                     "source": "divisions", "source_display": "number"},
                    {"name": "brigade_id", "type": "combo", "required": False, "label": "Бригада",
                     "source": "brigades", "source_display": "number"},
                    {"name": "location_id", "type": "combo", "required": False, "label": "Дислокація",
                     "source": "locations", "source_display": "name"},
                    {"name": "commander_id", "type": "combo", "required": False, "label": "Командир",
                     "source": "military_personnel", "source_display": "last_name"}
                ],
                "display_fields": ["id", "number", "name", "division_id", "brigade_id", "location_id", "commander_id"],
                "headers": ["ID", "Номер в/ч", "Назва", "ID Дивізії", "ID Бригади", "ID Локації", "ID Командира"]
            },
            "11. Військовослужбовці": {
                "table": "military_personnel",
                "fields": [
                    {"name": "last_name", "type": "text", "required": True, "label": "Прізвище"},
                    {"name": "first_name", "type": "text", "required": True, "label": "Ім'я"},
                    {"name": "middle_name", "type": "text", "required": False, "label": "По батькові"},
                    {"name": "rank_id", "type": "combo", "required": True, "label": "Звання",
                     "source": "ranks", "source_display": "name"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Частина",
                     "source": "military_units", "source_display": "number"},
                    {"name": "enlistment_date", "type": "date", "required": False, "label": "Дата прийняття"},
                    {"name": "birth_date", "type": "date", "required": False, "label": "Дата народження"}
                ],
                "display_fields": ["id", "last_name", "first_name", "rank_id", "military_unit_id"],
                "headers": ["ID", "Прізвище", "Ім'я", "ID Звання", "ID Частини"]
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
            }
        }

        self.entity_combo['values'] = list(self.entities.keys())

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name: return

        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._create_crud_interface(self.entities[entity_name])

    def _create_crud_interface(self, config: Dict[str, Any]):
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
        fields_str = ", ".join(display_fields)
        query = f'SELECT {fields_str} FROM {table_name} ORDER BY id'

        try:
            cols, rows = self.db.query_with_columns(query)
            for item in self.tree.get_children(): self.tree.delete(item)

            self.tree["columns"] = display_fields
            for col, header in zip(display_fields, headers):
                self.tree.heading(col, text=header)
                self.tree.column(col, width=120, anchor=tk.W)

            for row in rows:
                values = [row.get(col) for col in display_fields]
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

        conditions = [f'{field}::text ILIKE %s' for field in display_fields if field != "id"]
        if not conditions: return

        where_clause = " OR ".join(conditions)
        query = f'SELECT {", ".join(display_fields)} FROM {table_name} WHERE {where_clause} ORDER BY id'
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
        try:
            rows = self.db.query(f'SELECT * FROM {config["table"]} WHERE id=%s', [rid])
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
        try:
            self.db.execute(f'DELETE FROM {config["table"]} WHERE id=%s', [rid])
            self._refresh_table(config)
            messagebox.showinfo("Успіх", "Видалено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Неможливо видалити: {e}")

    def _show_record_dialog(self, config: Dict[str, Any], title: str, record_data: Optional[Dict] = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("550x650")

        # 🔥 ЛОГІКА ESC ДЛЯ ЗАКРИТТЯ
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

        widgets = {}

        ttk.Label(frame, text=title, font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        for field in config["fields"]:
            f_name = field["name"]
            f_label = field["label"] + (" *" if field.get("required") else "")

            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=5)

            ttk.Label(row, text=f_label, width=20).pack(side=tk.LEFT)

            if field["type"] == "date":
                w = DateEntry(row, date_pattern="yyyy-mm-dd", width=25)
            elif field["type"] == "combo":
                if "source" in field:
                    disp = field.get("source_display", "name")
                    try:
                        # Використовуємо аліас d_val
                        data = self.db.query(f'SELECT id, {disp} as d_val FROM {field["source"]} ORDER BY {disp}')
                        vals = [f"{r['id']}: {r['d_val']}" for r in data]
                        if not field.get("required"): vals.insert(0, "")
                    except:
                        vals = []
                    w = ttk.Combobox(row, values=vals, state="readonly", width=28)
                else:
                    w = ttk.Combobox(row, values=field["options"], state="readonly", width=28)
            else:
                w = ttk.Entry(row, width=30)

            w.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            widgets[f_name] = w

            # Заповнення
            if record_data and f_name in record_data:
                val = record_data[f_name]
                if val is not None:
                    if field["type"] == "combo" and "source" in field:
                        try:
                            disp = field.get("source_display", "name")
                            res = self.db.query(f'SELECT {disp} as d_val FROM {field["source"]} WHERE id=%s', [val])
                            if res: w.set(f"{val}: {res[0]['d_val']}")
                        except:
                            pass
                    elif field["type"] == "date":
                        w.set_date(val)
                    else:
                        w.insert(0, str(val))

        def save():
            data = {}
            for f in config["fields"]:
                val = widgets[f["name"]].get().strip()
                if f.get("required") and not val:
                    messagebox.showwarning("Увага", f"Заповніть поле '{f['label']}'")
                    return

                if f["type"] == "int":
                    data[f["name"]] = int(val) if val else None
                elif f["type"] == "combo" and "source" in f:
                    data[f["name"]] = int(val.split(":")[0]) if val else None
                else:
                    data[f["name"]] = val if val else None

            try:
                if record_data:
                    set_cl = ", ".join([f"{k}=%s" for k in data])
                    self.db.execute(f'UPDATE {config["table"]} SET {set_cl} WHERE id=%s',
                                    list(data.values()) + [record_data["id"]])
                else:
                    cols = ", ".join(data.keys())
                    phs = ", ".join(["%s"] * len(data))
                    self.db.execute(f'INSERT INTO {config["table"]} ({cols}) VALUES ({phs})', list(data.values()))

                messagebox.showinfo("ОК", "Збережено")
                dialog.destroy()
                self._refresh_table(config)
            except Exception as e:
                messagebox.showerror("Помилка", str(e))

        ttk.Button(frame, text="💾 Зберегти", command=save).pack(pady=20, fill=tk.X)