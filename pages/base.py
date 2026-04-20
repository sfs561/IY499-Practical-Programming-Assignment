"""
pages/base.py
─────────────
BasePage — the parent class that every page in the application inherits.

Provides:
  - A standard page_header() builder
  - An empty refresh() hook that subclasses override
"""

import tkinter as tk
from tkinter import ttk

from widgets import COLOURS, FONT_TITLE, FONT_BODY, make_label


class BasePage(tk.Frame):
    """
    Base class for all full-screen pages displayed in the content area.

    Each page receives a reference to the MedicalApp root so it can
    read/write shared data (patients, appointments, doctors).
    """

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOURS["bg"])
        self.app = app  # Reference to MedicalApp for shared state

    def refresh(self):
        """
        Called every time the page becomes visible.
        Subclasses override this to reload and redisplay their data.
        """
        pass

    def page_header(self, title: str, subtitle: str = ""):
        """
        Render a consistent page title and optional subtitle,
        followed by a horizontal separator.
        """
        header_frame = tk.Frame(self, bg=COLOURS["bg"], pady=18, padx=24)
        header_frame.pack(fill="x")

        make_label(header_frame, title,
                   font=FONT_TITLE, bg=COLOURS["bg"]).pack(anchor="w")

        if subtitle:
            make_label(header_frame, subtitle,
                       font=FONT_BODY, fg=COLOURS["muted"],
                       bg=COLOURS["bg"]).pack(anchor="w")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24)