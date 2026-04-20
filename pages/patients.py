"""
pages/patients.py
─────────────────
Patients page — register and browse patient records.

Features:
  - Register new patients via AddPatientDialog
  - Live search box that filters using linear_search_patients (O(n))
  - Sortable treeview (click any column header)
  - Row count status bar
"""

import tkinter as tk
from tkinter import messagebox
from datetime import date

from pages.base import BasePage
from dialogs import AddPatientDialog
from algorithms import generate_id, linear_search_patients
from widgets import (
    COLOURS, FONT_HEADER, FONT_BODY, FONT_SMALL,
    make_label, make_button, make_entry,
    make_treeview, populate_tree, add_scrollbar
)


class PatientsPage(BasePage):
    """Page for viewing and registering patients."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Patients", "Register and manage patient records")
        self._build_toolbar()
        self._build_table()
        self._build_status_bar()

    # ── Layout builders ──────────────────────────────────────────

    def _build_toolbar(self):
        """Top bar with 'New Patient' button and live search field."""
        toolbar = tk.Frame(self, bg=COLOURS["bg"], padx=24, pady=10)
        toolbar.pack(fill="x")

        make_button(toolbar, "＋ New Patient",
                    self._open_add_dialog).pack(side="left")

        make_label(toolbar, "Search:", bg=COLOURS["bg"]).pack(
            side="left", padx=(20, 4))

        self.search_var = tk.StringVar()
        # Trace fires _filter() on every keystroke
        self.search_var.trace_add("write", lambda *_: self._filter())
        make_entry(toolbar, textvariable=self.search_var,
                   width=24).pack(side="left")

    def _build_table(self):
        """Treeview displaying all patient records."""
        table_frame = tk.Frame(self, bg=COLOURS["bg"], padx=24)
        table_frame.pack(fill="both", expand=True, pady=(0, 4))

        cols = ["ID", "Name", "Date of Birth",
                "NHS Number", "Phone", "Email", "Registered"]
        self.tree = make_treeview(table_frame, cols, height=16)
        self.tree.column("ID",           width=70,  minwidth=60)
        self.tree.column("Name",         width=180, minwidth=140)
        self.tree.column("Date of Birth",width=110, minwidth=90)
        self.tree.column("NHS Number",   width=110, minwidth=90)
        self.tree.column("Phone",        width=120, minwidth=100)
        self.tree.column("Email",        width=180, minwidth=140)
        self.tree.column("Registered",   width=110, minwidth=90)

        add_scrollbar(table_frame, self.tree)

    def _build_status_bar(self):
        """Small label at the bottom showing the record count."""
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var,
                 font=FONT_SMALL, fg=COLOURS["muted"],
                 bg=COLOURS["bg"], anchor="w").pack(
            fill="x", padx=24, pady=(0, 6))

    # ── Data operations ──────────────────────────────────────────

    def refresh(self):
        """Reload the table whenever this page becomes active."""
        self._filter()

    def _filter(self):
        """
        Filter patients using the search box.
        Uses linear_search_patients from algorithms.py (O(n)).
        Falls back to the full list when the search box is empty.
        """
        query = self.search_var.get().strip()
        data  = (linear_search_patients(self.app.patients, query)
                 if query else self.app.patients)

        # Sort alphabetically by name for display (O(n log n))
        sorted_data = sorted(data, key=lambda p: p.get("name", "").lower())

        rows = [
            (p["id"], p["name"], p.get("dob", ""),
             p.get("nhs_number", ""), p.get("phone", ""),
             p.get("email", ""), p.get("registered", ""))
            for p in sorted_data
        ]
        populate_tree(self.tree, rows)
        self.status_var.set(
            f"Showing {len(rows)} of {len(self.app.patients)} patient(s)"
        )

    def _open_add_dialog(self):
        """Open the AddPatientDialog and save the result if submitted."""
        dlg = AddPatientDialog(self)
        if dlg.result:
            dlg.result["id"] = generate_id("P", self.app.patients)
            self.app.add_patient(dlg.result)
            self.refresh()
            messagebox.showinfo(
                "Patient Registered",
                f"'{dlg.result['name']}' has been registered successfully.",
                parent=self
            )