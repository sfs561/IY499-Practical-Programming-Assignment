"""
algorithms.py
─────────────
Core algorithms used by the Medical Appointment System.

Contains:
  - linear_search_patients : O(n) patient search
  - sort_appointments      : O(n log n) chronological sort via Timsort
  - check_conflict         : O(n) double-booking detection
  - generate_id            : O(n) sequential ID generation
"""


def generate_id(prefix: str, records: list) -> str:
    """
    Generate the next sequential ID for a given prefix (e.g. 'P', 'A').
    Scans all existing records to find the highest number and increments it.

    Example: existing ['P001', 'P003'] → returns 'P004'
    Time complexity: O(n) where n = number of existing records.
    """
    max_num = 0
    for record in records:
        record_id = record.get("id", "")
        if record_id.startswith(prefix):
            try:
                num = int(record_id[len(prefix):])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass  # Skip malformed IDs
    return f"{prefix}{max_num + 1:03d}"


def linear_search_patients(patients: list, query: str) -> list:
    """
    Search patients by name or NHS number using a linear search.
    Case-insensitive. Returns all records that contain the query string.

    Time complexity: O(n) — every record must be inspected.
    """
    query_lower = query.lower()
    results = []
    for patient in patients:
        name = patient.get("name", "").lower()
        nhs  = patient.get("nhs_number", "").lower()
        if query_lower in name or query_lower in nhs:
            results.append(patient)
    return results


def sort_appointments(appointments: list) -> list:
    """
    Sort a list of appointment dicts chronologically by date then time.
    Uses Python's built-in Timsort on a composite (date, time) key.

    Does NOT mutate the original list — returns a new sorted list.
    Time complexity: O(n log n).
    """
    return sorted(
        appointments,
        key=lambda a: (a.get("date", "9999-12-31"), a.get("time", "00:00"))
    )


def check_conflict(appointments: list, doctor_id: str, appt_date: str,
                   appt_time: str, exclude_id: str = None) -> bool:
    """
    Detect whether a doctor is already booked at the given date and time slot.

    Cancelled appointments are ignored (they free the slot).
    The exclude_id parameter lets you skip the appointment being edited
    so a reschedule does not conflict with itself.

    Returns True if a conflict exists, False if the slot is free.
    Time complexity: O(n) where n = number of existing appointments.
    """
    for appt in appointments:
        if appt.get("id") == exclude_id:
            continue  # Ignore the appointment being rescheduled

        same_doctor = appt.get("doctor_id") == doctor_id
        same_date   = appt.get("date")      == appt_date
        same_time   = appt.get("time")      == appt_time
        not_cancelled = appt.get("status")  != "Cancelled"

        if same_doctor and same_date and same_time and not_cancelled:
            return True  # Conflict found

    return False  # Slot is free