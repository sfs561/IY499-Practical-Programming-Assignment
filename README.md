# IY499-Practical-Programming-Assignment
IY499 Practical Programming Assignment


# Medical Appointment System
### IY499 – Introduction to Programming

---

Name: Batuhan Kantas
Student Number: 303061725
Course Code: IY499
GitHub Repository: https://github.com/sfs561/IY499-Practical-Programming-Assignment

---

## Declaration of Own Work

I confirm that this assignment is my own work.
Where I have referred to online sources, I have provided comments
detailing the reference and included a link to the source.

---

## Program Description

This is a graphical Medical Appointment Management System built with
Python and Tkinter. It allows clinic staff to manage patients and
appointments through a clean sidebar-navigation interface with four pages.

The Dashboard shows live statistics (patient count, total and upcoming
appointments, cancellations) and a chronologically sorted table of all
upcoming appointments.

The Patients page lets staff register new patients through a validated
modal form (name, date of birth, 10-digit NHS number, phone, email).
A live search box filters the list using a linear search algorithm (O(n)).

The Appointments page supports booking, cancelling, and rescheduling
appointments. Booking and rescheduling both use a conflict-checking
algorithm (O(n)) that prevents a doctor from being double-booked at
the same date and time. Appointments are displayed in chronological
order using Python's Timsort (O(n log n)). Rows are colour-coded by
status (green = Scheduled, red = Cancelled, orange = Rescheduled).

The Charts page embeds three live matplotlib visualisations: a bar
chart of appointments per doctor, a pie chart of status breakdown,
and a line chart of appointments by month.

All data is persisted to JSON files in a data/ directory that is
created automatically on first run.

---

## Libraries Used

- tkinter    — built-in GUI framework (no install needed)
- matplotlib — charts embedded via FigureCanvasTkAgg
- json, os, datetime, collections — built-in standard library

---

## Installation

1. Ensure Python 3.10 or later is installed.
2. Install the one external dependency:

    pip install -r requirements.txt

---

## How to Run

    python main.py

---

## File Structure

    medical_appointment_system/
    ├── main.py              # Entry point — launches the app
    ├── app.py               # Root window, sidebar, shared state
    ├── algorithms.py        # Search, sort, conflict-check algorithms
    ├── data_manager.py      # File I/O and data persistence
    ├── dialogs.py           # Modal forms (add patient, book appointment)
    ├── widgets.py           # Shared widget factories and style constants
    ├── pages/
    │   ├── __init__.py
    │   ├── base.py          # BasePage parent class
    │   ├── dashboard.py     # Dashboard page
    │   ├── patients.py      # Patients page
    │   ├── appointments.py  # Appointments page
    │   └── charts.py        # Charts & Reports page
    ├── requirements.txt
    ├── README.txt
    └── data/                # Auto-created on first run
        ├── patients.json
        ├── appointments.json
        └── doctors.json