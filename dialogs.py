"""
dialogs.py
──────────
Modal dialog windows for the Medical Appointment System.

Classes:
  - AddPatientDialog      : Form for registering a new patient
  - BookAppointmentDialog : Form for booking or rescheduling an appointment
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from algorithms import check_conflict
from widgets import (
    COLOURS, FONT_HEADER, FONT_BODY, FONT_BOLD,
    make_label, make_button, make_entry
)


class AddPatientDialog(tk.Toplevel):
    """
    Modal pop-up form for registering a new patient.

    On successful submission, self.result is set to a dict containing
    the validated patient fields. If the user cancels, self.result
    remains None.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register New Patient")
        self.resizable(False, False)
        self.configure(bg=COLOURS["bg"])
        self.grab_set()   # Block interaction with parent window
        self.result = None
        self._build()
        self.wait_window()  # Pause caller until dialog is closed

    def _build(self):
        """Lay out all form fields and action buttons."""
        pad = {"padx": 10, "pady": 6}
        frame = tk.Frame(self, bg=COLOURS["bg"], padx=28, pady=22)
        frame.pack(fill="both", expand=True)

        make_label(frame, "Register New Patient",
                   font=FONT_HEADER, bg=COLOURS["bg"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # Field definitions: (display label, internal key, placeholder hint)
        fields = [
            ("Full Name *",          "name",  ""),
            ("Date of Birth *",      "dob",   "YYYY-MM-DD"),
            ("NHS Number *",         "nhs",   "10 digits"),
            ("Phone Number *",       "phone", ""),
            ("Email (optional)",     "email", ""),
        ]

        self.vars = {}
        self._hint_entries = {}

        for row_idx, (label, key, hint) in enumerate(fields, start=1):
            make_label(frame, label, bg=COLOURS["bg"]).grid(
                row=row_idx, column=0, sticky="w", **pad)

            var = tk.StringVar()
            self.vars[key] = var
            entry = make_entry(frame, textvariable=var)

            # Show placeholder hint in muted colour
            if hint:
                entry.insert(0, hint)
                entry.config(fg=COLOURS["muted"])
                entry.bind("<FocusIn>",
                           lambda e, en=entry, h=hint: self._clear_hint(en, h))
                entry.bind("<FocusOut>",
                           lambda e, en=entry, h=hint, v=var: self._restore_hint(en, h, v))
                self._hint_entries[key] = hint

            entry.grid(row=row_idx, column=1, sticky="ew", **pad)

        # Action buttons
        btn_frame = tk.Frame(frame, bg=COLOURS["bg"])
        btn_frame.grid(row=len(fields) + 1, column=0,
                       columnspan=2, pady=(16, 0))
        make_button(btn_frame, "Register", self._submit,
                    width=12).pack(side="left", padx=5)
        make_button(btn_frame, "Cancel", self.destroy,
                    colour=COLOURS["muted"], width=12).pack(side="left", padx=5)

    def _clear_hint(self, entry: tk.Entry, hint: str):
        """Remove placeholder text when the user focuses the field."""
        if entry.get() == hint:
            entry.delete(0, "end")
            entry.config(fg=COLOURS["text"])

    def _restore_hint(self, entry: tk.Entry, hint: str, var: tk.StringVar):
        """Re-show placeholder text if the field is left empty."""
        if not entry.get():
            entry.insert(0, hint)
            entry.config(fg=COLOURS["muted"])
            var.set("")

    def _submit(self):
        """Validate all fields; populate self.result and close on success."""
        name  = self.vars["name"].get().strip()
        dob   = self.vars["dob"].get().strip()
        nhs   = (self.vars["nhs"].get().strip()
                 .replace(" ", "").replace("-", ""))
        phone = self.vars["phone"].get().strip()
        email = self.vars["email"].get().strip()

        # ── Validation ───────────────────────────────────────────
        if not name:
            messagebox.showerror("Validation", "Full name is required.", parent=self)
            return
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation",
                                 "Date of Birth must be in YYYY-MM-DD format.\n"
                                 "Example: 1990-06-15", parent=self)
            return
        if not (nhs.isdigit() and len(nhs) == 10):
            messagebox.showerror("Validation",
                                 "NHS Number must be exactly 10 digits.",
                                 parent=self)
            return
        if not phone:
            messagebox.showerror("Validation",
                                 "Phone number is required.", parent=self)
            return

        self.result = {
            "name":       name,
            "dob":        dob,
            "nhs_number": nhs,
            "phone":      phone,
            "email":      email,
            "registered": date.today().isoformat(),
        }
        self.destroy()


class BookAppointmentDialog(tk.Toplevel):
    """
    Modal pop-up form for booking a new appointment or rescheduling
    an existing one.

    Parameters
    ----------
    parent      : parent Tk widget
    patients    : current patients list (for the dropdown)
    doctors     : current doctors list (for the dropdown)
    appointments: current appointments list (for conflict checking)
    prefill     : dict of existing appointment fields (for reschedule)
    exclude_id  : appointment ID to exclude from conflict check (reschedule)

    On successful submission, self.result is set to a dict of validated
    fields. If the user cancels, self.result remains None.
    """

    def __init__(self, parent, patients: list, doctors: list,
                 appointments: list, prefill: dict = None,
                 exclude_id: str = None):
        super().__init__(parent)
        is_reschedule = exclude_id is not None
        self.title("Reschedule Appointment" if is_reschedule
                   else "Book Appointment")
        self.resizable(False, False)
        self.configure(bg=COLOURS["bg"])
        self.grab_set()

        self.patients     = patients
        self.doctors      = doctors
        self.appointments = appointments
        self.prefill      = prefill or {}
        self.exclude_id   = exclude_id
        self.result       = None

        self._build(is_reschedule)
        self.wait_window()

    def _build(self, is_reschedule: bool):
        """Lay out dropdown selectors, date/time fields, and buttons."""
        pad = {"padx": 10, "pady": 6}
        frame = tk.Frame(self, bg=COLOURS["bg"], padx=28, pady=22)
        frame.pack(fill="both", expand=True)

        title = "Reschedule Appointment" if is_reschedule else "Book New Appointment"
        make_label(frame, title, font=FONT_HEADER,
                   bg=COLOURS["bg"]).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # ── Patient dropdown ─────────────────────────────────────
        make_label(frame, "Patient *", bg=COLOURS["bg"]).grid(
            row=1, column=0, sticky="w", **pad)
        self.patient_var = tk.StringVar()
        patient_options  = [f"{p['id']} – {p['name']}" for p in self.patients]
        if not patient_options:
            patient_options = ["No patients registered"]

        pat_combo = ttk.Combobox(frame, textvariable=self.patient_var,
                                 values=patient_options,
                                 state="readonly", width=32)
        # Pre-select if rescheduling
        if self.prefill.get("patient_id"):
            for opt in patient_options:
                if opt.startswith(self.prefill["patient_id"]):
                    self.patient_var.set(opt)
                    break
        pat_combo.grid(row=1, column=1, sticky="ew", **pad)

        # ── Doctor dropdown ──────────────────────────────────────
        make_label(frame, "Doctor *", bg=COLOURS["bg"]).grid(
            row=2, column=0, sticky="w", **pad)
        self.doctor_var = tk.StringVar()
        doctor_options  = [f"{d['id']} – {d['name']} ({d['speciality']})"
                           for d in self.doctors]
        doc_combo = ttk.Combobox(frame, textvariable=self.doctor_var,
                                 values=doctor_options,
                                 state="readonly", width=32)
        if self.prefill.get("doctor_id"):
            for opt in doctor_options:
                if opt.startswith(self.prefill["doctor_id"]):
                    self.doctor_var.set(opt)
                    break
        doc_combo.grid(row=2, column=1, sticky="ew", **pad)

        # ── Date ─────────────────────────────────────────────────
        make_label(frame, "Date * (YYYY-MM-DD)",
                   bg=COLOURS["bg"]).grid(row=3, column=0, sticky="w", **pad)
        self.date_var = tk.StringVar(value=self.prefill.get("date", ""))
        make_entry(frame, textvariable=self.date_var).grid(
            row=3, column=1, sticky="ew", **pad)

        # ── Time ─────────────────────────────────────────────────
        make_label(frame, "Time * (HH:MM)",
                   bg=COLOURS["bg"]).grid(row=4, column=0, sticky="w", **pad)
        self.time_var = tk.StringVar(value=self.prefill.get("time", ""))
        make_entry(frame, textvariable=self.time_var).grid(
            row=4, column=1, sticky="ew", **pad)

        # ── Reason ───────────────────────────────────────────────
        make_label(frame, "Reason *",
                   bg=COLOURS["bg"]).grid(row=5, column=0, sticky="w", **pad)
        self.reason_var = tk.StringVar(value=self.prefill.get("reason", ""))
        make_entry(frame, textvariable=self.reason_var).grid(
            row=5, column=1, sticky="ew", **pad)

        # ── Buttons ──────────────────────────────────────────────
        btn_lbl = "Reschedule" if is_reschedule else "Book"
        btn_frame = tk.Frame(frame, bg=COLOURS["bg"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(16, 0))
        make_button(btn_frame, btn_lbl, self._submit,
                    width=12).pack(side="left", padx=5)
        make_button(btn_frame, "Cancel", self.destroy,
                    colour=COLOURS["muted"], width=12).pack(side="left", padx=5)

    def _submit(self):
        """Validate inputs, run conflict check, populate self.result."""
        pat_sel    = self.patient_var.get()
        doc_sel    = self.doctor_var.get()
        appt_date  = self.date_var.get().strip()
        appt_time  = self.time_var.get().strip()
        reason     = self.reason_var.get().strip()

        # ── Field validation ─────────────────────────────────────
        if not pat_sel or "No patients" in pat_sel:
            messagebox.showerror("Validation",
                                 "Please select a patient.", parent=self)
            return
        if not doc_sel:
            messagebox.showerror("Validation",
                                 "Please select a doctor.", parent=self)
            return
        try:
            datetime.strptime(appt_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation",
                                 "Date must be YYYY-MM-DD (e.g. 2025-06-15).",
                                 parent=self)
            return
        from datetime import date as date_cls
        if appt_date < date_cls.today().isoformat():
            messagebox.showerror("Validation",
                                 "Cannot book an appointment in the past.",
                                 parent=self)
            return
        try:
            datetime.strptime(appt_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation",
                                 "Time must be HH:MM (e.g. 09:30).",
                                 parent=self)
            return
        if not reason:
            messagebox.showerror("Validation",
                                 "Reason is required.", parent=self)
            return

        # ── Resolve IDs from dropdown strings ────────────────────
        patient_id = pat_sel.split(" – ")[0]
        doctor_id  = doc_sel.split(" – ")[0]
        patient    = next((p for p in self.patients
                           if p["id"] == patient_id), None)
        doctor     = next((d for d in self.doctors
                           if d["id"] == doctor_id), None)

        # ── Conflict check (algorithm from algorithms.py) ────────
        if check_conflict(self.appointments, doctor_id, appt_date,
                          appt_time, exclude_id=self.exclude_id):
            messagebox.showerror(
                "Booking Conflict",
                f"{doctor['name']} is already booked on "
                f"{appt_date} at {appt_time}.\n"
                "Please choose a different date or time.",
                parent=self
            )
            return

        self.result = {
            "patient_id":   patient_id,
            "patient_name": patient["name"],
            "doctor_id":    doctor_id,
            "doctor_name":  doctor["name"],
            "date":         appt_date,
            "time":         appt_time,
            "reason":       reason,
        }
        self.destroy()