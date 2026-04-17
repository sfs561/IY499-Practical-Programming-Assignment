import sqlite3


def create_connection():
    """Create and return a connection to the clinic database."""
    return sqlite3.connect("clinic.db")


def create_tables():
    """Create the patients, doctors, and appointments tables if they do not exist."""

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        phone TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        reason TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )
    """)

    conn.commit()
    conn.close()


def add_patient(name, age, phone):
    """Add a new patient to the database."""

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients (name, age, phone)
    VALUES (?, ?, ?)
    """, (name, age, phone))

    conn.commit()
    conn.close()


def add_doctor(name, specialty):
    """Add a new doctor to the database."""

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO doctors (name, specialty)
    VALUES (?, ?)
    """, (name, specialty))

    conn.commit()
    conn.close()