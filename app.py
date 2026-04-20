"""
app.py
──────
MedicalApp — the root Tkinter window for the Medical Appointment System.

Responsibilities:
  - Build the sidebar navigation and content area
  - Own the shared in-memory state: patients, appointments, doctors
  - Provide mutator methods that pages call to modify and persist data
  - Route navigation between the four pages
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from data_manager import (
    load_all, seed_doctors,
    save_patient, save_appointment, update_appointment,
    PATIENTS_FILE, APPOINTMENTS_FILE
)
from widgets import COLOURS, FONT_BOLD, FONT_SMALL

# Page imports
from pages.dashboard    import DashboardPage
from pages.patients     import PatientsPage
from pages.appointments import AppointmentsPage
from pages.charts       import ChartsPage


class MedicalApp(tk.Tk):
    """
    Root application window.

    Owns all shared data and provides the mutator methods used by pages
    to add, cancel, and reschedule records. Pages never write to disk
    directly — they call these methods so all persistence is centralised.
    """

    def __init__(self):
        super().__init__()
        self.title("Medical Appointment System")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(bg=COLOURS["bg"])

        # ── Load all data from disk ──────────────────────────────
        self.patients, self.appointments, doctors = load_all()
        self.doctors = seed_doctors(doctors)

        # ── Build UI ─────────────────────────────────────────────
        self._build_sidebar()
        self._build_content_area()
        self._show_page("dashboard")

    # ── UI construction ──────────────────────────────────────────

    def _build_sidebar(self):
        """Left-hand navigation panel with logo and nav buttons."""
        self.sidebar = tk.Frame(self, bg=COLOURS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo block
        logo = tk.Frame(self.sidebar, bg=COLOURS["sidebar"], pady=20)
        logo.pack(fill="x")
        tk.Label(logo, text="🏥", font=("Helvetica", 28),
                 bg=COLOURS["sidebar"], fg="white").pack()
        tk.Label(logo, text="MedAppoint",
                 font=("Georgia", 13, "bold"),
                 bg=COLOURS["sidebar"], fg="white").pack()
        tk.Label(logo, text="Appointment System",
                 font=FONT_SMALL, bg=COLOURS["sidebar"],
                 fg=COLOURS["muted"]).pack()

        ttk.Separator(self.sidebar,
                      orient="horizontal").pack(fill="x", padx=16, pady=4)

        # Navigation buttons
        nav_items = [
            ("dashboard",    "📊  Dashboard"),
            ("patients",     "👤  Patients"),
            ("appointments", "📅  Appointments"),
            ("charts",       "📈  Charts"),
        ]
        self.nav_buttons = {}
        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar, text=label, anchor="w",
                font=("Helvetica", 11),
                bg=COLOURS["sidebar"], fg="white",
                relief="flat", bd=0, padx=20, pady=10,
                cursor="hand2",
                activebackground=COLOURS["sidebar_hover"],
                activeforeground="white",
                command=lambda k=key: self._show_page(k)
            )
            btn.pack(fill="x")
            # Hover highlight (skip if already selected)
            btn.bind("<Enter>",
                     lambda e, b=btn: b.config(bg=COLOURS["sidebar_hover"])
                     if b.cget("bg") != COLOURS["sidebar_sel"] else None)
            btn.bind("<Leave>",
                     lambda e, b=btn: b.config(
                         bg=COLOURS["sidebar_sel"]
                         if b.cget("bg") == COLOURS["sidebar_sel"]
                         else COLOURS["sidebar"]))
            self.nav_buttons[key] = btn

    def _build_content_area(self):
        """Right-hand content pane containing all page frames."""
        self.content = tk.Frame(self, bg=COLOURS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {
            "dashboard":    DashboardPage(self.content, self),
            "patients":     PatientsPage(self.content, self),
            "appointments": AppointmentsPage(self.content, self),
            "charts":       ChartsPage(self.content, self),
        }

    def _show_page(self, name: str):
        """
        Hide all pages, show the selected one, and highlight its nav button.
        Calls refresh() on the visible page so data is always up to date.
        """
        for key, page in self.pages.items():
            page.pack_forget()
        for key, btn in self.nav_buttons.items():
            btn.config(bg=COLOURS["sidebar_sel"]
                       if key == name else COLOURS["sidebar"])
        self.pages[name].pack(fill="both", expand=True)
        self.pages[name].refresh()

    # ── Data mutators (called by pages) ──────────────────────────

    def add_patient(self, patient_data: dict):
        """Append a new patient and persist to disk."""
        self.patients = save_patient(self.patients, patient_data)

    def book_appointment(self, appt_data: dict):
        """Append a new appointment and persist to disk."""
        self.appointments = save_appointment(self.appointments, appt_data)

    def cancel_appointment(self, appt_id: str):
        """Mark an appointment as Cancelled and persist."""
        self.appointments = update_appointment(
            self.appointments, appt_id, {"status": "Cancelled"}
        )

    def reschedule_appointment(self, appt_id: str, new_data: dict):
        """Update date/time of an appointment and persist."""
        self.appointments = update_appointment(
            self.appointments, appt_id, {
                "date":   new_data["date"],
                "time":   new_data["time"],
                "status": "Rescheduled",
            }
        )