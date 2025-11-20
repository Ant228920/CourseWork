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

        # Entity selection
        self.entity_var = tk.StringVar()
        self.entity_combo = ttk.Combobox(self, textvariable=self.entity_var, state="readonly")
        self.entity_combo.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        self.entity_combo.bind("<<ComboboxSelected>>", self._on_entity_select)

        # Main content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=6)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Define entities and their configurations
        self.entities = {
            "Military Districts": {
                "table": "military_districts",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "code", "type": "text", "required": False, "label": "Code"}
                ],
                "display_fields": ["id", "name", "code"]
            },
            "Armies": {
                "table": "armies",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Number"},
                    {"name": "name", "type": "text", "required": False, "label": "Name"},
                    {"name": "military_district_id", "type": "combo", "required": True, "label": "Military District",
                     "source": "military_districts"}
                ],
                "display_fields": ["id", "number", "name", "military_district_id"]
            },
            "Corps": {
                "table": "corps",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Number"},
                    {"name": "name", "type": "text", "required": False, "label": "Name"},
                    {"name": "army_id", "type": "combo", "required": True, "label": "Army", "source": "armies"}
                ],
                "display_fields": ["id", "number", "name", "army_id"]
            },
            "Divisions": {
                "table": "divisions",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Number"},
                    {"name": "name", "type": "text", "required": False, "label": "Name"},
                    {"name": "corps_id", "type": "combo", "required": True, "label": "Corps", "source": "corps"}
                ],
                "display_fields": ["id", "number", "name", "corps_id"]
            },
            "Military Units": {
                "table": "military_units",
                "fields": [
                    {"name": "number", "type": "text", "required": True, "label": "Number"},
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "division_id", "type": "combo", "required": True, "label": "Division",
                     "source": "divisions"},
                    {"name": "location_id", "type": "combo", "required": False, "label": "Location",
                     "source": "locations"}
                ],
                "display_fields": ["id", "number", "name", "division_id", "location_id"]
            },
            "Locations": {
                "table": "locations",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "address", "type": "text", "required": False, "label": "Address"},
                    {"name": "region", "type": "text", "required": False, "label": "Region"},
                    {"name": "coordinates", "type": "text", "required": False, "label": "Coordinates"}
                ],
                "display_fields": ["id", "name", "address", "region", "coordinates"]
            },
            "Ranks": {
                "table": "ranks",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "category_id", "type": "combo", "required": True, "label": "Category",
                     "source": "personnel_categories"}
                ],
                "display_fields": ["id", "name", "category_id"]
            },
            "Specialties": {
                "table": "specialties",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "code", "type": "text", "required": True, "label": "Code"}
                ],
                "display_fields": ["id", "name", "code"]
            },
            "Military Personnel": {
                "table": "military_personnel",
                "fields": [
                    {"name": "last_name", "type": "text", "required": True, "label": "Last Name"},
                    {"name": "first_name", "type": "text", "required": True, "label": "First Name"},
                    {"name": "middle_name", "type": "text", "required": False, "label": "Middle Name"},
                    {"name": "rank_id", "type": "combo", "required": True, "label": "Rank", "source": "ranks"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Military Unit",
                     "source": "military_units"},
                    {"name": "enlistment_date", "type": "date", "required": False, "label": "Enlistment Date"},
                    {"name": "birth_date", "type": "date", "required": False, "label": "Birth Date"}
                ],
                "display_fields": ["id", "last_name", "first_name", "middle_name", "rank_id", "military_unit_id"]
            },
            "Equipment Types": {
                "table": "equipment_types",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "category", "type": "text", "required": False, "label": "Category"}
                ],
                "display_fields": ["id", "name", "category"]
            },
            "Equipment": {
                "table": "equipment",
                "fields": [
                    {"name": "equipment_type_id", "type": "combo", "required": True, "label": "Equipment Type",
                     "source": "equipment_types"},
                    {"name": "model", "type": "text", "required": True, "label": "Model"},
                    {"name": "serial_number", "type": "text", "required": False, "label": "Serial Number"},
                    {"name": "year_manufactured", "type": "int", "required": False, "label": "Year Manufactured"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Military Unit",
                     "source": "military_units"},
                    {"name": "condition", "type": "text", "required": False, "label": "Condition"}
                ],
                "display_fields": ["id", "equipment_type_id", "model", "serial_number", "year_manufactured",
                                   "military_unit_id"]
            },
            "Weapon Types": {
                "table": "weapon_types",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "category", "type": "text", "required": False, "label": "Category"}
                ],
                "display_fields": ["id", "name", "category"]
            },
            "Weapons": {
                "table": "weapons",
                "fields": [
                    {"name": "weapon_type_id", "type": "combo", "required": True, "label": "Weapon Type",
                     "source": "weapon_types"},
                    {"name": "model", "type": "text", "required": True, "label": "Model"},
                    {"name": "serial_number", "type": "text", "required": False, "label": "Serial Number"},
                    {"name": "caliber", "type": "text", "required": False, "label": "Caliber"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Military Unit",
                     "source": "military_units"}
                ],
                "display_fields": ["id", "weapon_type_id", "model", "serial_number", "caliber", "military_unit_id"]
            },
            "Facilities": {
                "table": "facilities",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "label": "Name"},
                    {"name": "type", "type": "text", "required": True, "label": "Type"},
                    {"name": "address", "type": "text", "required": False, "label": "Address"},
                    {"name": "military_unit_id", "type": "combo", "required": True, "label": "Military Unit",
                     "source": "military_units"},
                    {"name": "location_id", "type": "combo", "required": False, "label": "Location",
                     "source": "locations"}
                ],
                "display_fields": ["id", "name", "type", "address", "military_unit_id", "location_id"]
            }
        }

        # Populate entity combo
        self.entity_combo['values'] = list(self.entities.keys())
        if self.entities:
            self.entity_combo.current(0)
            self._on_entity_select(None)

    def _on_entity_select(self, event):
        entity_name = self.entity_var.get()
        if not entity_name:
            return

        entity_config = self.entities[entity_name]

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create CRUD interface for selected entity
        self._create_crud_interface(entity_config)

    def _create_crud_interface(self, config: Dict[str, Any]):
        # Toolbar
        toolbar = ttk.Frame(self.content_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(toolbar, text="Add", command=lambda: self._add_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit", command=lambda: self._edit_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete", command=lambda: self._delete_record(config)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=lambda: self._refresh_table(config)).pack(side=tk.LEFT, padx=2)

        # Search frame
        search_frame = ttk.Frame(self.content_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', lambda e: self._search_records(config))

        # Table frame
        table_frame = ttk.Frame(self.content_frame)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Create treeview
        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Configure grid weights
        self.content_frame.rowconfigure(2, weight=1)

        # Load data
        self._refresh_table(config)

    def _refresh_table(self, config: Dict[str, Any]):
        """Refresh the table with current data"""
        table_name = config["table"]
        display_fields = config["display_fields"]

        # Build query
        fields_str = ", ".join(display_fields)
        query = f'SELECT {fields_str} FROM {table_name} ORDER BY id'

        try:
            cols, rows = self.db.query_with_columns(query)

            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Configure columns
            self.tree["columns"] = cols
            for col in cols:
                self.tree.heading(col, text=col.replace("_", " ").title())
                self.tree.column(col, width=120, anchor=tk.W)

            # Insert data
            for row in rows:
                values = [row.get(col) for col in cols]
                self.tree.insert("", tk.END, values=values)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def _search_records(self, config: Dict[str, Any]):
        """Search records based on search term"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self._refresh_table(config)
            return

        table_name = config["table"]
        display_fields = config["display_fields"]

        # Build search query
        search_conditions = []
        for field in display_fields:
            if field != "id":
                search_conditions.append(f'{field}::text ILIKE %s')

        if not search_conditions:
            return

        fields_str = ", ".join(display_fields)
        where_clause = " OR ".join(search_conditions)
        query = f'SELECT {fields_str} FROM {table_name} WHERE {where_clause} ORDER BY id'

        search_params = [f'%{search_term}%'] * len(search_conditions)

        try:
            cols, rows = self.db.query_with_columns(query, search_params)

            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Configure columns
            self.tree["columns"] = cols
            for col in cols:
                self.tree.heading(col, text=col.replace("_", " ").title())
                self.tree.column(col, width=120, anchor=tk.W)

            # Insert data
            for row in rows:
                values = [row.get(col) for col in cols]
                self.tree.insert("", tk.END, values=values)

        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")

    def _add_record(self, config: Dict[str, Any]):
        """Add new record"""
        self._show_record_dialog(config, "Add Record")

    def _edit_record(self, config: Dict[str, Any]):
        """Edit selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a record to edit")
            return

        item = self.tree.item(selection[0])
        record_id = item['values'][0]

        # Load record data
        table_name = config["table"]
        query = f'SELECT * FROM {table_name} WHERE id = %s'

        try:
            rows = self.db.query(query, [record_id])
            if not rows:
                messagebox.showerror("Error", "Record not found")
                return

            record_data = dict(rows[0])
            self._show_record_dialog(config, "Edit Record", record_data)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load record: {str(e)}")

    def _delete_record(self, config: Dict[str, Any]):
        """Delete selected record"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a record to delete")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return

        item = self.tree.item(selection[0])
        record_id = item['values'][0]

        table_name = config["table"]
        query = f'DELETE FROM {table_name} WHERE id = %s'

        try:
            affected_rows = self.db.execute(query, [record_id])
            if affected_rows > 0:
                messagebox.showinfo("Success", "Record deleted successfully")
                self._refresh_table(config)
            else:
                messagebox.showerror("Error", "Record was not deleted")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

    def _show_record_dialog(self, config: Dict[str, Any], title: str, record_data: Optional[Dict] = None):
        """Show dialog for adding/editing record"""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Create form
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        form_frame = ttk.Frame(canvas, padding=20)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas_frame = canvas.create_window((0, 0), window=form_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        form_frame.bind("<Configure>", on_frame_configure)

        # Store form widgets
        widgets = {}

        # Create form fields
        for i, field in enumerate(config["fields"]):
            field_name = field["name"]
            field_type = field["type"]
            required = field.get("required", False)
            label = field.get("label", field_name.replace("_", " ").title())

            # Label
            label_text = label
            if required:
                label_text += " *"
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="w", pady=5)

            # Input widget
            if field_type == "text":
                widget = ttk.Entry(form_frame, width=40)
            elif field_type == "int":
                widget = ttk.Entry(form_frame, width=40)
            elif field_type == "date":
                widget = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=37)
            elif field_type == "combo":
                if "source" in field:
                    source_table = field["source"]
                    try:
                        # Get name field from source table
                        name_field = "name" if source_table != "personnel_categories" else "name"
                        source_data = self.db.query(
                            f'SELECT id, {name_field} FROM {source_table} ORDER BY {name_field}')
                        values = [f"{row['id']}: {row[name_field]}" for row in source_data]
                    except Exception as e:
                        values = []
                        print(f"Error loading source data: {e}")
                    widget = ttk.Combobox(form_frame, values=values, state="readonly", width=37)
                elif "options" in field:
                    widget = ttk.Combobox(form_frame, values=field["options"], state="readonly", width=37)
                else:
                    widget = ttk.Entry(form_frame, width=40)
            else:
                widget = ttk.Entry(form_frame, width=40)

            widget.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
            widgets[field_name] = widget

            # Set initial value if editing
            if record_data and field_name in record_data:
                value = record_data[field_name]
                if value is not None:
                    if field_type == "combo" and "source" in field:
                        try:
                            source_table = field["source"]
                            name_field = "name"
                            source_data = self.db.query(f'SELECT id, {name_field} FROM {source_table} WHERE id = %s',
                                                        [value])
                            if source_data:
                                widget.set(f"{value}: {source_data[0][name_field]}")
                        except:
                            pass
                    else:
                        if field_type == "date":
                            widget.set_date(value)
                        else:
                            widget.insert(0, str(value))

        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10, side=tk.BOTTOM)

        def save_record():
            try:
                data = {}
                for field in config["fields"]:
                    field_name = field["name"]
                    field_type = field["type"]
                    widget = widgets[field_name]

                    value = widget.get().strip() if hasattr(widget, 'get') else None

                    if field.get("required", False) and not value:
                        messagebox.showerror("Error", f"Field '{field.get('label', field_name)}' is required")
                        return

                    if field_type == "int":
                        data[field_name] = int(value) if value else None
                    elif field_type == "combo" and "source" in field:
                        if value:
                            try:
                                data[field_name] = int(value.split(":")[0])
                            except (ValueError, IndexError):
                                messagebox.showerror("Error", f"Invalid format for field '{field_name}'")
                                return
                        else:
                            data[field_name] = None
                    else:
                        data[field_name] = value if value else None

                table_name = config["table"]
                if record_data:
                    set_clause = ", ".join([f'{k} = %s' for k in data.keys()])
                    query = f'UPDATE {table_name} SET {set_clause} WHERE id = %s'
                    params = list(data.values()) + [record_data["id"]]
                else:
                    fields = ", ".join(data.keys())
                    placeholders = ", ".join(["%s"] * len(data))
                    query = f'INSERT INTO {table_name} ({fields}) VALUES ({placeholders})'
                    params = list(data.values())

                affected_rows = self.db.execute(query, params)

                if affected_rows > 0:
                    messagebox.showinfo("Success", "Record saved successfully")
                    dialog.destroy()
                    self._refresh_table(config)
                else:
                    messagebox.showerror("Error", "Record was not saved")

            except Exception as e:
                messagebox.showerror("Error", f"Save error: {str(e)}")

        ttk.Button(button_frame, text="Save", command=save_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)