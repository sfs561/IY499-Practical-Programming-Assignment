"""
data_manager.py
───────────────
Handles all file input/output for the Medical Appointment System.

Responsibilities:
  - Load and save JSON data files
  - Ensure the data/ directory exists
  - Seed default doctors on first run
  - Expose a single load_all() convenience function
"""

import json
import os
from datetime import date

# ── File paths ──────────────────────────────────────────────────
DATA_DIR          = "data"
PATIENTS_FILE     = os.path.join(DATA_DIR, "patients.json")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.json")
DOCTORS_FILE      = os.path.join(DATA_DIR, "doctors.json")


def ensure_data_dir():
    """Create the data/ directory if it does not already exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_data(filepath: str) -> list:
    """
    Load a JSON file and return its contents as a Python list.

    Error recovery:
      - Missing file  → returns empty list (first run behaviour)
      - Corrupt JSON  → returns empty list and prints a warning
    This prevents the application from crashing due to bad data files.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []  # Normal on first run
    except json.JSONDecodeError:
        print(f"[Warning] '{filepath}' is corrupt. Starting with empty data.")
        return []


def save_data(filepath: str, data: list) -> bool:
    """
    Serialise a list of records to a JSON file with pretty formatting.

    Returns True on success, False if an OS error occurs (e.g. disk full).
    Always calls ensure_data_dir() first so the directory is guaranteed
    to exist before writing.
    """
    ensure_data_dir()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"[Error] Could not save '{filepath}': {e}")
        return False


def load_all() -> tuple:
    """
    Convenience function — load all three data files at once.
    Returns a tuple: (patients, appointments, doctors).
    """
    patients     = load_data(PATIENTS_FILE)
    appointments = load_data(APPOINTMENTS_FILE)
    doctors      = load_data(DOCTORS_FILE)
    return patients, appointments, doctors


def seed_doctors(doctors: list) -> list:
    """
    Populate a default set of four doctors on the very first run.
    If doctors already exist the list is returned unchanged.
    """
    if doctors:
        return doctors

    default_doctors = [
        {"id": "D001", "name": "Dr. Sarah Ahmed",  "speciality": "General Practitioner"},
        {"id": "D002", "name": "Dr. James Walker", "speciality": "Cardiologist"},
        {"id": "D003", "name": "Dr. Priya Sharma", "speciality": "Dermatologist"},
        {"id": "D004", "name": "Dr. Tom Collins",  "speciality": "Orthopaedic Surgeon"},
    ]
    save_data(DOCTORS_FILE, default_doctors)
    return default_doctors


def save_patient(patients: list, patient_data: dict) -> list:
    """
    Append a new patient record to the list and persist it to disk.
    Returns the updated patients list.
    """
    patients.append(patient_data)
    save_data(PATIENTS_FILE, patients)
    return patients


def save_appointment(appointments: list, appt_data: dict) -> list:
    """
    Append a new appointment record to the list and persist it to disk.
    Returns the updated appointments list.
    """
    appointments.append(appt_data)
    save_data(APPOINTMENTS_FILE, appointments)
    return appointments


def update_appointment(appointments: list, appt_id: str,
                       updates: dict) -> list:
    """
    Apply a dict of field updates to the appointment matching appt_id.
    Saves the updated list to disk.
    Returns the updated appointments list.
    """
    for appt in appointments:
        if appt.get("id") == appt_id:
            appt.update(updates)
            break
    save_data(APPOINTMENTS_FILE, appointments)
    return appointments