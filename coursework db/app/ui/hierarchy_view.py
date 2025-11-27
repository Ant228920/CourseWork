# ui/hierarchy_view.py
import tkinter as tk
from tkinter import ttk

from db import Database


# ----------------------------
# ФУНКЦІЇ-ПОМІЧНИКИ (повертають список кортежів: (id, label, next_level))
# ----------------------------
def get_districts_rows(db: Database):
    rows = db.query("SELECT id, name FROM military_districts ORDER BY name")
    return [(r["id"], r["name"], "army") for r in rows]


def get_armies_rows(db: Database, district_id: int):
    rows = db.query("""
        SELECT id, number, name
        FROM armies
        WHERE military_district_id = %s
        ORDER BY number
    """, (district_id,))
    return [(r["id"], f"Армія {r['number']} — {r['name'] or ''}".strip(" — "), "corps") for r in rows]


def get_corps_rows(db: Database, army_id: int):
    rows = db.query("""
        SELECT id, number, name
        FROM corps
        WHERE army_id = %s
        ORDER BY number
    """, (army_id,))
    return [(r["id"], f"Корпус {r['number']} — {r['name'] or ''}".strip(" — "), "corps_children") for r in rows]


def get_corps_children_rows(db: Database, corps_id: int):
    """Повертаємо і divisions, і brigades як діти corps — з різними next_level."""
    result = []

    divs = db.query("""
        SELECT id, number, name
        FROM divisions
        WHERE corps_id = %s
        ORDER BY number
    """, (corps_id,))
    for r in divs:
        label = f"Дивізія {r['number']} — {r['name'] or ''}".strip(" — ")
        result.append((r["id"], label, "division"))

    brs = db.query("""
        SELECT id, number, name
        FROM brigades
        WHERE corps_id = %s
        ORDER BY number
    """, (corps_id,))
    for r in brs:
        label = f"Бригада {r['number']} — {r['name'] or ''}".strip(" — ")
        result.append((r["id"], label, "brigade"))

    return result


def get_units_rows_by_division(db: Database, division_id: int):
    rows = db.query("""
        SELECT id, number, name
        FROM military_units
        WHERE division_id = %s
        ORDER BY number
    """, (division_id,))
    return [(r["id"], f"Частина {r['number']} — {r['name'] or ''}".strip(" — "), "unit") for r in rows]


def get_units_rows_by_brigade(db: Database, brigade_id: int):
    rows = db.query("""
        SELECT id, number, name
        FROM military_units
        WHERE brigade_id = %s
        ORDER BY number
    """, (brigade_id,))
    return [(r["id"], f"Частина {r['number']} — {r['name'] or ''}".strip(" — "), "unit") for r in rows]


def get_companies_rows(db: Database, unit_id: int):
    rows = db.query("""
        SELECT id, name
        FROM companies
        WHERE military_unit_id = %s
        ORDER BY name
    """, (unit_id,))
    return [(r["id"], f"Рота: {r['name']}", "company") for r in rows]


def get_platoons_rows(db: Database, company_id: int):
    rows = db.query("""
        SELECT id, name
        FROM platoons
        WHERE company_id = %s
        ORDER BY name
    """, (company_id,))
    return [(r["id"], f"Взвод: {r['name']}", "platoon") for r in rows]


def get_squads_rows(db: Database, platoon_id: int):
    rows = db.query("""
        SELECT id, name
        FROM squads
        WHERE platoon_id = %s
        ORDER BY name
    """, (platoon_id,))
    return [(r["id"], f"Відділення: {r['name']}", None) for r in rows]  # None -> листок


LEVEL_FETCHERS = {
    "district": get_armies_rows,
    "army": get_corps_rows,
    "corps": get_corps_children_rows,
    "division": get_units_rows_by_division,
    "brigade": get_units_rows_by_brigade,
    "unit": get_companies_rows,
    "company": get_platoons_rows,
    "platoon": get_squads_rows,
}


# ----------------------------
# HierarchyTree
# ----------------------------
class HierarchyTree(tk.Frame):
    def __init__(self, master, db: Database):
        super().__init__(master)
        self.db = db

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<<TreeviewOpen>>", self.on_open)

        self.load_root_nodes()

    def load_root_nodes(self):
        try:
            rows = get_districts_rows(self.db)
        except Exception as e:
            self.tree.insert("", "end", text=f"(Помилка при завантаженні округів: {e})")
            return

        for id_, label, next_lvl in rows:
            node = self.tree.insert("", "end", text=f"Округ: {label}", values=(id_, "district"), open=False)
            if next_lvl in LEVEL_FETCHERS:
                self.tree.insert(node, "end", text="loading")

    def on_open(self, event):
        node = self.tree.focus()
        vals = self.tree.item(node, "values") or ()
        if len(vals) < 2:
            return
        item_id_str, level = vals[0], vals[1]
        try:
            item_id = int(item_id_str)
        except Exception:
            return

        children = self.tree.get_children(node)
        if children and self.tree.item(children[0], "text") != "loading":
            return

        for ch in children:
            self.tree.delete(ch)

        fetcher = LEVEL_FETCHERS.get(level)
        if not fetcher:
            return

        try:
            items = fetcher(self.db, item_id)
        except Exception as e:
            self.tree.insert(node, "end", text=f"(Error: {e})")
            return

        for child_id, child_label, child_next in items:
            self.tree.insert(node, "end", text=child_label, values=(child_id, child_next or ""), open=False)
            if child_next and child_next in LEVEL_FETCHERS:
                new_children = self.tree.get_children(node)
                if new_children:
                    last = new_children[-1]
                    self.tree.insert(last, "end", text="loading")

