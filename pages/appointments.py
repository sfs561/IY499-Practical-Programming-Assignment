"""
pages/appointments.py
─────────────────────
Appointments page — book, view, cancel, and reschedule appointments.

Features:
  - Book appointments via BookAppointmentDialog (conflict checked)
  - Cancel or reschedule selected appointments
  - Filter by status (All / Scheduled / Rescheduled / Cancelled / Upcoming)
  - Live search across patient name, doctor name, date, and status
  - Colour-coded rows (green = Scheduled, red = Cancelled, orange = Rescheduled)
  - Chronological sort using sort_appointments from algorithms.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

from pages.base import BasePage
from dialogs import BookAppointmentDialog
from algorithms import generate_id, sort_appointments
from widgets import (
    COLOURS, FONT_SMALL,
    make_label, make_button, make_entry,
    make_treeview, add_scrollbar
)


class AppointmentsPage(BasePage):
    """Page for managing all appointment operations."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Appointments",
                         "Book, manage, and view all appointments")
        self._build_toolbar()
        self._build_table()
        self._build_status_bar()

    # ── Layout builders ──────────────────────────────────────────

    def _build_toolbar(self):
        """Action buttons, status filter dropdown, and live search."""
        toolbar = tk.Frame(self, bg=COLOURS["bg"], padx=24, pady=10)
        toolbar.pack(fill="x")

        make_button(toolbar, "＋ Book",
                    self._book).pack(side="left", padx=(0, 6))
        make_button(toolbar, "✏  Reschedule", self._reschedule,
                    colour="#7B1FA2").pack(side="left", padx=(0, 6))
        make_button(toolbar, "✕ Cancel", self._cancel,
                    colour=COLOURS["danger"]).pack(side="left", padx=(0, 20))

        make_label(toolbar, "Filter:", bg=COLOURS["bg"]).pack(
            side="left", padx=(0, 4))
        self.filter_var = tk.StringVar(value="All")
        ttk.Combobox(
            toolbar, textvariable=self.filter_var, width=14,
            values=["All", "Scheduled", "Rescheduled",
                    "Cancelled", "Upcoming Only"],
            state="readonly"
        ).pack(side="left", padx=(0, 12))
        self.filter_var.trace_add("write", lambda *_: self.refresh())

        make_label(toolbar, "Search:", bg=COLOURS["bg"]).pack(
            side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        make_entry(toolbar, textvariable=self.search_var,
                   width=20).pack(side="left")

    def _build_table(self):
        """Treeview with colour-coded rows by appointment status."""
        table_frame = tk.Frame(self, bg=COLOURS["bg"], padx=24)
        table_frame.pack(fill="both", expand=True, pady=(0, 4))

        cols = ["ID", "Patient", "Doctor", "Date", "Time", "Status", "Reason"]
        self.tree = make_treeview(table_frame, cols, height=16)
        self.tree.column("ID",      width=70,  minwidth=60)
        self.tree.column("Patient", width=160, minwidth=120)
        self.tree.column("Doctor",  width=180, minwidth=140)
        self.tree.column("Date",    width=100, minwidth=90)
        self.tree.column("Time",    width=70,  minwidth=60)
        self.tree.column("Status",  width=110, minwidth=90)
        self.tree.column("Reason",  width=220, minwidth=150)

        # Status-based row colours
        self.tree.tag_configure("Scheduled",
                                foreground=COLOURS["success"])
        self.tree.tag_configure("Cancelled",
                                foreground=COLOURS["danger"])
        self.tree.tag_configure("Rescheduled",
                                foreground=COLOURS["warning"])

        add_scrollbar(table_frame, self.tree)

    def _build_status_bar(self):
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var,
                 font=FONT_SMALL, fg=COLOURS["muted"],
                 bg=COLOURS["bg"], anchor="w").pack(
            fill="x", padx=24, pady=(0, 6))

    # ── Data operations ──────────────────────────────────────────

    def refresh(self):
        """Apply current filter and search, then redraw the table."""
        today  = date.today().isoformat()
        filt   = self.filter_var.get()
        query  = self.search_var.get().strip().lower()
        data   = self.app.appointments

        # ── Status filter ────────────────────────────────────────
        if filt == "Upcoming Only":
            data = [a for a in data
                    if a.get("date", "") >= today
                    and a.get("status") != "Cancelled"]
        elif filt != "All":
            data = [a for a in data if a.get("status") == filt]

        # ── Linear search across multiple fields ─────────────────
        if query:
            data = [a for a in data
                    if query in a.get("patient_name", "").lower()
                    or query in a.get("doctor_name",  "").lower()
                    or query in a.get("date",         "")
                    or query in a.get("status",       "").lower()]

        # ── Chronological sort from algorithms.py (O(n log n)) ───
        sorted_data = sort_appointments(data)

        # ── Populate treeview with status colour tags ─────────────
        self.tree.delete(*self.tree.get_children())
        for i, appt in enumerate(sorted_data):
            status = appt.get("status", "")
            tags   = [status] if status in ("Scheduled", "Cancelled",
                                            "Rescheduled") else []
            if i % 2:
                tags.append("alt")
            self.tree.insert(
                "", "end",
                values=(appt["id"], appt["patient_name"],
                        appt["doctor_name"], appt["date"],
                        appt["time"], status, appt.get("reason", "")),
                tags=tuple(tags)
            )

        self.status_var.set(
            f"Showing {len(sorted_data)} of "
            f"{len(self.app.appointments)} appointment(s)"
        )

    def _get_selected_id(self) -> str | None:
        """Return the ID of the currently selected row, or None."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection",
                                   "Please select an appointment first.",
                                   parent=self)
            return None
        return str(self.tree.item(selection[0])["values"][0])

    def _book(self):
        """Open booking dialog and save the new appointment."""
        if not self.app.patients:
            messagebox.showwarning(
                "No Patients",
                "Please register a patient before booking an appointment.",
                parent=self
            )
            return

        dlg = BookAppointmentDialog(
            self, self.app.patients, self.app.doctors,
            self.app.appointments
        )
        if dlg.result:
            dlg.result["id"]      = generate_id("A", self.app.appointments)
            dlg.result["status"]  = "Scheduled"
            dlg.result["created"] = datetime.now().isoformat(timespec="seconds")
            self.app.book_appointment(dlg.result)
            self.refresh()
            messagebox.showinfo(
                "Appointment Booked",
                f"Appointment booked for {dlg.result['patient_name']} "
                f"with {dlg.result['doctor_name']}\n"
                f"on {dlg.result['date']} at {dlg.result['time']}.",
                parent=self
            )

    def _cancel(self):
        """Mark the selected appointment as Cancelled."""
        appt_id = self._get_selected_id()
        if not appt_id:
            return

        appt = next((a for a in self.app.appointments
                     if a["id"] == appt_id), None)
        if appt and appt.get("status") == "Cancelled":
            messagebox.showinfo("Already Cancelled",
                                "This appointment is already cancelled.",
                                parent=self)
            return

        if messagebox.askyesno("Confirm Cancellation",
                               f"Cancel appointment {appt_id}?",
                               parent=self):
            self.app.cancel_appointment(appt_id)
            self.refresh()

    def _reschedule(self):
        """Open booking dialog pre-filled with the selected appointment."""
        appt_id = self._get_selected_id()
        if not appt_id:
            return

        appt = next((a for a in self.app.appointments
                     if a["id"] == appt_id), None)
        if not appt:
            return
        if appt.get("status") == "Cancelled":
            messagebox.showerror("Cannot Reschedule",
                                 "A cancelled appointment cannot be rescheduled.",
                                 parent=self)
            return

        dlg = BookAppointmentDialog(
            self, self.app.patients, self.app.doctors,
            self.app.appointments,
            prefill=appt, exclude_id=appt_id
        )
        if dlg.result:
            self.app.reschedule_appointment(appt_id, dlg.result)
            self.refresh()
            messagebox.showinfo(
                "Appointment Rescheduled",
                f"Appointment {appt_id} moved to "
                f"{dlg.result['date']} at {dlg.result['time']}.",
                parent=self
            )