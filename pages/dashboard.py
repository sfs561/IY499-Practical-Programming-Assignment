"""
pages/dashboard.py
──────────────────
Dashboard page — the home screen of the Medical Appointment System.

Displays:
  - Four summary stat cards (patients, total appts, upcoming, cancelled)
  - A sortable table of all upcoming scheduled appointments
"""

import tkinter as tk
from tkinter import ttk
from datetime import date

from pages.base import BasePage
from algorithms import sort_appointments
from widgets import (
    COLOURS, FONT_HEADER, FONT_BOLD, FONT_BODY, FONT_SMALL,
    make_label, make_treeview, populate_tree, add_scrollbar
)


class DashboardPage(BasePage):
    """Home page showing a high-level clinic overview."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Dashboard", "Overview of your clinic at a glance")

        # Placeholder frames — populated by refresh()
        self.stats_frame    = tk.Frame(self, bg=COLOURS["bg"])
        self.stats_frame.pack(fill="x", padx=24, pady=16)

        self.upcoming_frame = tk.Frame(self, bg=COLOURS["bg"])
        self.upcoming_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    # ── Refresh ──────────────────────────────────────────────────

    def refresh(self):
        """Rebuild stat cards and upcoming appointments table from live data."""
        self._rebuild_stats()
        self._rebuild_upcoming_table()

    def _rebuild_stats(self):
        """Recalculate and redraw the four KPI stat cards."""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        today      = date.today().isoformat()
        appointments = self.app.appointments

        total_patients = len(self.app.patients)
        total_appts    = len(appointments)
        upcoming_count = sum(
            1 for a in appointments
            if a.get("date", "") >= today and a.get("status") == "Scheduled"
        )
        cancelled_count = sum(
            1 for a in appointments if a.get("status") == "Cancelled"
        )

        stats = [
            ("👤", "Patients",    str(total_patients),  COLOURS["primary"]),
            ("📅", "Total Appts", str(total_appts),     "#7B1FA2"),
            ("✅", "Upcoming",    str(upcoming_count),  COLOURS["success"]),
            ("❌", "Cancelled",   str(cancelled_count), COLOURS["danger"]),
        ]

        for col_idx, (icon, label, value, colour) in enumerate(stats):
            card = tk.Frame(self.stats_frame, bg=COLOURS["card"],
                            padx=20, pady=14, relief="flat")
            card.grid(row=0, column=col_idx, padx=8, pady=4, sticky="nsew")
            self.stats_frame.columnconfigure(col_idx, weight=1)

            tk.Label(card, text=icon,  font=("Helvetica", 22),
                     bg=COLOURS["card"], fg=colour).pack(anchor="w")
            tk.Label(card, text=value, font=("Georgia", 26, "bold"),
                     bg=COLOURS["card"], fg=colour).pack(anchor="w")
            tk.Label(card, text=label, font=FONT_BODY,
                     bg=COLOURS["card"], fg=COLOURS["muted"]).pack(anchor="w")

    def _rebuild_upcoming_table(self):
        """Redraw the upcoming appointments treeview."""
        for widget in self.upcoming_frame.winfo_children():
            widget.destroy()

        make_label(self.upcoming_frame, "Upcoming Appointments",
                   font=FONT_HEADER, bg=COLOURS["bg"]).pack(
            anchor="w", pady=(8, 6))

        today    = date.today().isoformat()
        upcoming = [
            a for a in self.app.appointments
            if a.get("date", "") >= today and a.get("status") == "Scheduled"
        ]

        cols = ["ID", "Patient", "Doctor", "Date", "Time", "Reason"]
        tree = make_treeview(self.upcoming_frame, cols, height=10)
        tree.column("ID",      width=70,  minwidth=60)
        tree.column("Patient", width=160, minwidth=120)
        tree.column("Doctor",  width=180, minwidth=140)
        tree.column("Date",    width=100, minwidth=90)
        tree.column("Time",    width=70,  minwidth=60)
        tree.column("Reason",  width=200, minwidth=140)

        sorted_upcoming = sort_appointments(upcoming)
        rows = [
            (a["id"], a["patient_name"], a["doctor_name"],
             a["date"], a["time"], a.get("reason", ""))
            for a in sorted_upcoming
        ]
        populate_tree(tree, rows)
        add_scrollbar(self.upcoming_frame, tree)