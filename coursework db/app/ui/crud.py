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

        # Верхня панель: Вибір таблиці
        top_panel = ttk.Frame(self, padding=5)
        top_panel.grid(row=0, column=0, sticky="ew")

        ttk.Label(top_panel, text="Оберіть таблицю для редагування:").pack(side=tk.LEFT, padx=5)

        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(top_panel, textvariable=self.entity_var, state="readonly", width=40)
        self.entity_combo.pack(side=tk.LEFT, padx=5)
        self.entity_combo.bind("<<ComboboxSelected>>", self._on_entity_select)

        # Основна область контенту
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(2, weight=1)  # Таблиця розтягується

        # ========================================================
        # КОНФІГУРАЦІЯ ТАБЛИЦЬ (Повний список)
        # ========================================================
        self.entities = {
            # --- ДОВІДНИКИ (ТЕХНІКА ТА ЗБРОЯ) ---
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
                     "source": "corps", "source_display": "number"}
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
            "12. Техніка (Одиниці)": {
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
            "13. Озброєння (Одиниці)": {
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
            }
        }

        self.entity_combo['values'] = list(self.entities.keys())

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name: return
        entity_config = self.entities[entity_name]

        for widget in self.content_frame.winfo_children(): widget.destroy()
        self._create_crud_interface(entity_config)

    def _create_crud_interface(self, config: Dict[str, Any]):
        # Toolbar
        toolbar = ttk.Frame(self.content_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(toolbar, text="➕ Додати", command=lambda: self._add_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Редагувати", command=lambda: self._edit_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Видалити", command=lambda: self._delete_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Оновити", command=lambda: self._refresh_table(config)).pack(side=tk.LEFT, padx=2)

        # Search
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(search_frame, text="Пошук:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self._search_records(config))

        # Table
        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)

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
            messagebox.showerror("Помилка", f"Не вдалося завантажити дані: {str(e)}")

    def _search_records(self, config: Dict[str, Any]):
        search_term = self.search_var.get().strip()
        if not search_term:
            self._refresh_table(config)
            return

        table_name = config["table"]
        display_fields = config["display_fields"]

        search_conditions = [f'{field}::text ILIKE %s' for field in display_fields if field != "id"]
        if not search_conditions: return

        fields_str = ", ".join(display_fields)
        where_clause = " OR ".join(search_conditions)
        query = f'SELECT {fields_str} FROM {table_name} WHERE {where_clause} ORDER BY id'
        search_params = [f'%{search_term}%'] * len(search_conditions)

        try:
            cols, rows = self.db.query_with_columns(query, search_params)
            for item in self.tree.get_children(): self.tree.delete(item)

            for row in rows:
                values = [row.get(col) for col in display_fields]
                self.tree.insert("", tk.END, values=values)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка пошуку: {str(e)}")

    def _add_record(self, config):
        self._show_record_dialog(config, "Додати запис")

    def _edit_record(self, config):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Оберіть запис для редагування")
            return

        record_id = self.tree.item(selection[0])['values'][0]
        table_name = config["table"]

        try:
            rows = self.db.query(f'SELECT * FROM {table_name} WHERE id = %s', [record_id])
            if rows: self._show_record_dialog(config, "Редагувати запис", dict(rows[0]))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити запис: {str(e)}")

    def _delete_record(self, config):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "Оберіть запис для видалення")
            return

        if not messagebox.askyesno("Підтвердження", "Ви впевнені?"): return

        record_id = self.tree.item(selection[0])['values'][0]
        try:
            self.db.execute(f'DELETE FROM {config["table"]} WHERE id = %s', [record_id])
            self._refresh_table(config)
            messagebox.showinfo("Успіх", "Запис видалено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося видалити (можливо, є пов'язані дані): {str(e)}")

    def _show_record_dialog(self, config: Dict[str, Any], title: str, record_data: Optional[Dict] = None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("550x650")

        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=form_frame, anchor="nw")

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        widgets = {}

        for i, field in enumerate(config["fields"]):
            field_name = field["name"]
            field_type = field["type"]
            required = field.get("required", False)
            label = field.get("label", field_name)
            if required: label += " *"

            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)

            if field_type == "text" or field_type == "int":
                widget = ttk.Entry(form_frame, width=40)
            elif field_type == "date":
                widget = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=37)
            elif field_type == "combo":
                if "source" in field:
                    # ВАЖЛИВО: Визначаємо, яку колонку показувати (source_display)
                    display_col = field.get("source_display", "name")
                    try:
                        query = f'SELECT id, {display_col} FROM {field["source"]} ORDER BY {display_col}'
                        source_data = self.db.query(query)
                        # Формат списку: "ID: Значення"
                        values = [f"{row['id']}: {row[display_col]}" for row in source_data]

                        if not required: values.insert(0, "")

                    except:
                        values = []
                    widget = ttk.Combobox(form_frame, values=values, state="readonly", width=37)
                elif "options" in field:
                    widget = ttk.Combobox(form_frame, values=field["options"], state="readonly", width=37)
                else:
                    widget = ttk.Entry(form_frame, width=40)
            else:
                widget = ttk.Entry(form_frame, width=40)

            widget.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
            widgets[field_name] = widget

            # Заповнення при редагуванні
            if record_data and field_name in record_data:
                val = record_data[field_name]
                if val is not None:
                    if field_type == "combo" and "source" in field:
                        try:
                            display_col = field.get("source_display", "name")
                            res = self.db.query(f'SELECT {display_col} FROM {field["source"]} WHERE id = %s', [val])
                            if res: widget.set(f"{val}: {res[0][display_col]}")
                        except:
                            pass
                    elif field_type == "date":
                        widget.set_date(val)
                    else:
                        widget.insert(0, str(val))

        def save():
            try:
                data = {}
                for field in config["fields"]:
                    fname = field["name"]
                    ftype = field["type"]
                    w = widgets[fname]
                    val = w.get().strip() if hasattr(w, 'get') else None

                    if field.get("required") and not val:
                        messagebox.showerror("Помилка", f"Поле '{field['label']}' обов'язкове")
                        return

                    if ftype == "int":
                        data[fname] = int(val) if val else None
                    elif ftype == "combo" and "source" in field:
                        if val:
                            data[fname] = int(val.split(":")[0])
                        else:
                            data[fname] = None
                    else:
                        data[fname] = val if val else None

                if record_data:
                    set_cl = ", ".join([f'{k}=%s' for k in data])
                    self.db.execute(f'UPDATE {config["table"]} SET {set_cl} WHERE id=%s',
                                    list(data.values()) + [record_data["id"]])
                else:
                    cols = ", ".join(data.keys())
                    phs = ", ".join(["%s"] * len(data))
                    self.db.execute(f'INSERT INTO {config["table"]} ({cols}) VALUES ({phs})', list(data.values()))

                messagebox.showinfo("Успіх", "Збережено")
                dialog.destroy()
                self._refresh_table(config)
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка при збереженні:\n{str(e)}")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        ttk.Button(btn_frame, text="💾 Зберегти", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Скасувати", command=dialog.destroy).pack(side=tk.LEFT, padx=5)