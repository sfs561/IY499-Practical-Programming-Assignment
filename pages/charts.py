"""
pages/charts.py
───────────────
Charts page — visualise appointment data using matplotlib embedded in Tkinter.

Three chart types available:
  1. Bar chart    — appointments per doctor
  2. Pie chart    — appointment status breakdown
  3. Line chart   — appointments booked per calendar month

Charts render live inside the application window using FigureCanvasTkAgg.
"""

import tkinter as tk
from collections import Counter

from pages.base import BasePage
from widgets import COLOURS, make_label, make_button, FONT_BOLD

# Optional matplotlib import — graceful fallback if not installed
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartsPage(BasePage):
    """Page for visualising appointment statistics."""

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.page_header("Charts & Reports",
                         "Visual summary of appointment data")
        self._build_toolbar()

        # Container for the matplotlib canvas
        self.chart_area = tk.Frame(self, bg=COLOURS["bg"])
        self.chart_area.pack(fill="both", expand=True, padx=24, pady=8)

    def _build_toolbar(self):
        """Three buttons to switch between chart types."""
        tb = tk.Frame(self, bg=COLOURS["bg"], padx=24, pady=8)
        tb.pack(fill="x")

        make_button(tb, "Appointments / Doctor",
                    lambda: self._draw("doctor")).pack(side="left", padx=(0, 8))
        make_button(tb, "Status Breakdown",
                    lambda: self._draw("status"),
                    colour="#7B1FA2").pack(side="left", padx=(0, 8))
        make_button(tb, "By Month",
                    lambda: self._draw("monthly"),
                    colour=COLOURS["warning"]).pack(side="left")

    # ── Refresh ──────────────────────────────────────────────────

    def refresh(self):
        """Show the default chart (appointments per doctor) on page load."""
        self._draw("doctor")

    # ── Chart rendering ──────────────────────────────────────────

    def _clear_chart_area(self):
        """Remove any previously rendered chart widget."""
        for widget in self.chart_area.winfo_children():
            widget.destroy()

    def _show_message(self, message: str, colour: str = None):
        """Display a plain-text message in the chart area."""
        self._clear_chart_area()
        make_label(self.chart_area, message,
                   font=FONT_BOLD,
                   fg=colour or COLOURS["muted"],
                   bg=COLOURS["bg"]).pack(pady=60)

    def _draw(self, chart_type: str):
        """
        Render the selected chart type into the chart area.

        chart_type options:
          'doctor'  — bar chart of appointments per doctor
          'status'  — pie chart of appointment status breakdown
          'monthly' — line chart of appointments by calendar month
        """
        if not MATPLOTLIB_AVAILABLE:
            self._show_message(
                "matplotlib is not installed.\nRun: pip install matplotlib",
                colour=COLOURS["danger"]
            )
            return

        if not self.app.appointments:
            self._show_message("No appointment data to chart yet.")
            return

        self._clear_chart_area()

        fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=COLOURS["bg"])
        ax.set_facecolor(COLOURS["card"])

        if chart_type == "doctor":
            self._chart_by_doctor(ax)
        elif chart_type == "status":
            self._chart_by_status(ax)
        elif chart_type == "monthly":
            self._chart_by_month(ax)

        plt.tight_layout()

        # Embed the figure into the Tkinter frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _chart_by_doctor(self, ax):
        """Bar chart — total appointments per doctor (sorted descending)."""
        counts = Counter(a.get("doctor_name", "Unknown")
                         for a in self.app.appointments)
        # Sort by count descending (O(n log n))
        items  = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        names, values = zip(*items)

        bars = ax.bar(names, values,
                      color=COLOURS["primary"],
                      edgecolor="white", linewidth=0.7)
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.set_title("Appointments per Doctor",
                     fontsize=13, fontweight="bold", color=COLOURS["text"])
        ax.set_ylabel("Number of Appointments", color=COLOURS["muted"])
        ax.set_ylim(0, max(values) + 2)
        plt.xticks(rotation=10, ha="right", fontsize=9)

    def _chart_by_status(self, ax):
        """Pie chart — proportion of each appointment status."""
        counts  = Counter(a.get("status", "Unknown")
                          for a in self.app.appointments)
        labels  = list(counts.keys())
        sizes   = list(counts.values())
        colours = ["#2979FF", "#E53935", "#F57C00", "#2E7D32", "#9B59B6"]

        wedges, texts, autos = ax.pie(
            sizes, labels=labels,
            colors=colours[:len(labels)],
            autopct="%1.1f%%", startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5}
        )
        for t in autos:
            t.set_fontsize(9)
        ax.set_title("Appointment Status Breakdown",
                     fontsize=13, fontweight="bold", color=COLOURS["text"])

    def _chart_by_month(self, ax):
        """Line chart — number of appointments booked per calendar month."""
        month_counts = Counter()
        for a in self.app.appointments:
            appt_date = a.get("date", "")
            if len(appt_date) >= 7:
                month_counts[appt_date[:7]] += 1  # 'YYYY-MM'

        if not month_counts:
            return

        months = sorted(month_counts.keys())
        values = [month_counts[m] for m in months]

        ax.plot(months, values, marker="o", linewidth=2,
                color=COLOURS["primary"],
                markerfacecolor=COLOURS["primary_dark"])
        ax.fill_between(months, values, alpha=0.1, color=COLOURS["primary"])
        ax.set_title("Appointments by Month",
                     fontsize=13, fontweight="bold", color=COLOURS["text"])
        ax.set_ylabel("Number of Appointments", color=COLOURS["muted"])
        plt.xticks(rotation=20, ha="right", fontsize=9)