"""
main.py
───────
Entry point for the Medical Appointment System.

Run with:
    python main.py

This file does nothing except import MedicalApp and start the
Tkinter event loop. All application logic lives in the other modules.
"""

from app import MedicalApp

if __name__ == "__main__":
    app = MedicalApp()
    app.mainloop()