import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

PRESET_QUERIES = [
	{"name": "Частини з належністю", "sql": "SELECT mu.id, mu.number, mu.name, d.number AS division, c.number AS corps, a.number AS army, md.name AS district FROM military_units mu JOIN divisions d ON d.id=mu.division_id JOIN corps c ON c.id=d.corps_id JOIN armies a ON a.id=c.army_id JOIN military_districts md ON md.id=a.military_district_id"},
	{"name": "Техніка по типах у частині ($PART_ID)", "sql": "SELECT et.name AS type, COUNT(*) AS count FROM equipment e JOIN equipment_types et ON et.id=e.equipment_type_id WHERE e.military_unit_id = %s GROUP BY et.name ORDER BY 2 DESC", "params": ["PART_ID:int"]},
	{"name": "Озброєння по підрозділах ($PART_ID)", "sql": "SELECT s.name AS subunit, COUNT(w.id) AS units FROM weapons w LEFT JOIN subunits s ON s.id=w.subunit_id WHERE w.military_unit_id = %s GROUP BY s.name", "params": ["PART_ID:int"]},
	{"name": "Персонал за званнями ($DIV_ID)", "sql": "SELECT rank, COUNT(*) AS count FROM military_personnel mp JOIN military_units mu ON mu.id=mp.military_unit_id WHERE mu.division_id=%s GROUP BY rank ORDER BY 2 DESC", "params": ["DIV_ID:int"]},
	{"name": "Список споруд частини ($PART_ID)", "sql": "SELECT f.name, f.type, f.address FROM facilities f WHERE f.military_unit_id=%s", "params": ["PART_ID:int"]},
	{"name": "Пошук військовослужбовців (%Q%)", "sql": "SELECT * FROM military_personnel WHERE LOWER(last_name||' '||first_name||' '||COALESCE(middle_name,'')) LIKE LOWER('%' || %s || '%')", "params": ["Q:str"]},
	{"name": "Середній рік випуску техніки", "sql": "SELECT et.name AS type, AVG(e.year_manufactured)::INT AS avg_year FROM equipment e JOIN equipment_types et ON et.id=e.equipment_type_id GROUP BY et.name"},
	{"name": "ТОП-10 частин за кількістю техніки", "sql": "SELECT mu.number, mu.name, COUNT(e.id) AS equipment FROM military_units mu LEFT JOIN equipment e ON e.military_unit_id=mu.id GROUP BY mu.id ORDER BY 3 DESC LIMIT 10"},
	{"name": "Ієрархія округ-армія-корпус-дивізія", "sql": "SELECT md.name AS district, a.number AS army, c.number AS corps, d.number AS division FROM military_districts md LEFT JOIN armies a ON a.military_district_id=md.id LEFT JOIN corps c ON c.army_id=a.id LEFT JOIN divisions d ON d.corps_id=c.id"},
	{"name": "Прийняття на службу по місяцях (>= дата)", "sql": "SELECT DATE_TRUNC('month', enlistment_date) AS month, COUNT(*) AS enlisted FROM military_personnel WHERE enlistment_date IS NOT NULL AND enlistment_date>=%s GROUP BY 1 ORDER BY 1", "params": ["DATE:date"]},
]

class QueriesFrame(tk.Frame):
	def __init__(self, master, db):
		super().__init__(master)
		self.db = db

		self.columnconfigure(0, weight=1)
		self.rowconfigure(2, weight=1)

		self.cmb = ttk.Combobox(self, state="readonly", values=[q["name"] for q in PRESET_QUERIES])
		self.cmb.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
		self.cmb.bind("<<ComboboxSelected>>", self._on_select)

		self.params_frame = ttk.Frame(self)
		self.params_frame.grid(row=1, column=0, sticky="ew", padx=8)

		self.tree = ttk.Treeview(self, show="headings")
		sb_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscrollcommand=sb_y.set)
		self.tree.grid(row=2, column=0, sticky="nsew", padx=(8,0), pady=8)
		sb_y.grid(row=2, column=0, sticky="nse", padx=(0,8), pady=8)

		btn_run = ttk.Button(self, text="Виконати", command=self._run)
		btn_run.grid(row=3, column=0, sticky="e", padx=8, pady=(0,8))

		self._param_widgets = []
		if PRESET_QUERIES:
			self.cmb.current(0)
			self._build_params(0)

	def _on_select(self, _):
		self._build_params(self.cmb.current())

	def _build_params(self, idx: int):
		for w in self._param_widgets:
			w.destroy()
		self._param_widgets.clear()
		cfg = PRESET_QUERIES[idx]
		params = cfg.get("params", [])
		for i, spec in enumerate(params):
			name, typ = spec.split(":", 1)
			lbl = ttk.Label(self.params_frame, text=name)
			lbl.grid(row=0, column=i*2, sticky="w", padx=(0,4), pady=6)
			if typ == "date":
				ent = DateEntry(self.params_frame, date_pattern="yyyy-mm-dd")
			else:
				ent = ttk.Entry(self.params_frame)
			ent.grid(row=0, column=i*2+1, sticky="ew", padx=(0,12), pady=6)
			self.params_frame.columnconfigure(i*2+1, weight=1)
			self._param_widgets.append(ent)

	def _collect_params(self, idx: int):
		cfg = PRESET_QUERIES[idx]
		params = cfg.get("params", [])
		values = []
		for spec, widget in zip(params, self._param_widgets):
			name, typ = spec.split(":", 1)
			val = widget.get()
			if typ == "int":
				try:
					val = int(val)
				except Exception:
					messagebox.showerror("Помилка", f"Параметр {name} має бути цілим числом")
					return None
			values.append(val)
		return values

	def _run(self):
		idx = self.cmb.current()
		cfg = PRESET_QUERIES[idx]
		params = self._collect_params(idx)
		if params is None:
			return
		cols, rows = self.db.query_with_columns(cfg["sql"], params)
		for c in self.tree.get_children():
			self.tree.delete(c)
		self.tree["columns"] = cols
		for c in cols:
			self.tree.heading(c, text=c)
			self.tree.column(c, width=160, anchor=tk.W)
		for r in rows:
			self.tree.insert("", tk.END, values=[r.get(c) for c in cols])
