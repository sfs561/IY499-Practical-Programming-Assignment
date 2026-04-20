"""
widgets.py
──────────
Shared Tkinter widget factory functions and style constants.

All pages and dialogs import from here to keep the visual
language consistent across the entire application.
"""

import tkinter as tk
from tkinter import ttk

# ── Colour palette ───────────────────────────────────────────────
COLOURS = {
    "bg":            "#F0F4F8",
    "sidebar":       "#1B2A4A",
    "sidebar_hover": "#2E4270",
    "sidebar_sel":   "#2979FF",
    "card":          "#FFFFFF",
    "primary":       "#2979FF",
    "primary_dark":  "#1565C0",
    "danger":        "#E53935",
    "success":       "#2E7D32",
    "warning":       "#F57C00",
    "text":          "#1A202C",
    "muted":         "#718096",
    "border":        "#E2E8F0",
    "header_bg":     "#EBF0FB",
    "row_alt":       "#F7FAFC",
}

# ── Font definitions ─────────────────────────────────────────────
FONT_TITLE  = ("Georgia", 22, "bold")
FONT_HEADER = ("Georgia", 14, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_SMALL  = ("Helvetica", 9)
FONT_BOLD   = ("Helvetica", 11, "bold")


# ── Factory functions ────────────────────────────────────────────

def make_label(parent, text: str, font=None, fg: str = None,
               bg: str = None, **kw) -> tk.Label:
    """Create a Label using the application colour scheme."""
    font = font or FONT_BODY
    fg   = fg   or COLOURS["text"]
    bg   = bg   or parent.cget("bg")
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)


def make_button(parent, text: str, command, colour: str = None,
                width: int = 14, **kw) -> tk.Button:
    """Create a flat, styled Button."""
    colour = colour or COLOURS["primary"]
    return tk.Button(
        parent, text=text, command=command,
        bg=colour, fg="white", font=FONT_BOLD,
        relief="flat", bd=0, padx=12, pady=6,
        cursor="hand2",
        activebackground=COLOURS["primary_dark"],
        activeforeground="white",
        width=width, **kw
    )


def make_entry(parent, textvariable=None, width: int = 28,
               **kw) -> tk.Entry:
    """Create a styled Entry widget with a subtle border."""
    return tk.Entry(
        parent, textvariable=textvariable, width=width,
        font=FONT_BODY, relief="solid", bd=1,
        highlightthickness=1,
        highlightcolor=COLOURS["primary"],
        highlightbackground=COLOURS["border"],
        **kw
    )


def make_treeview(parent, columns: list,
                  height: int = 14) -> ttk.Treeview:
    """
    Create a styled ttk.Treeview with:
      - Clickable column headers that sort the column
      - Alternating row background colours
      - Application colour scheme applied via ttk.Style
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "App.Treeview",
        background=COLOURS["card"],
        fieldbackground=COLOURS["card"],
        foreground=COLOURS["text"],
        rowheight=26,
        font=FONT_BODY
    )
    style.configure(
        "App.Treeview.Heading",
        background=COLOURS["header_bg"],
        foreground=COLOURS["text"],
        font=FONT_BOLD,
        relief="flat"
    )
    style.map(
        "App.Treeview",
        background=[("selected", COLOURS["primary"])],
        foreground=[("selected", "white")]
    )

    tree = ttk.Treeview(
        parent, columns=columns, show="headings",
        height=height, style="App.Treeview"
    )

    # Bind each header to sort on click
    for col in columns:
        tree.heading(col, text=col,
                     command=lambda c=col, t=tree: _sort_tree_by_col(t, c))
        tree.column(col, anchor="w", width=120)

    # Tag for alternating row colours
    tree.tag_configure("alt", background=COLOURS["row_alt"])
    return tree


def populate_tree(tree: ttk.Treeview, rows: list):
    """
    Clear the treeview and insert new rows with alternating colours.
    Each row in `rows` should be a tuple matching the tree's columns.
    """
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "alt" if i % 2 else ""
        tree.insert("", "end", values=row, tags=(tag,))


def add_scrollbar(parent, tree: ttk.Treeview):
    """Attach a vertical scrollbar to a treeview and pack both."""
    sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")


# ── Internal helper ──────────────────────────────────────────────

def _sort_tree_by_col(tree: ttk.Treeview, col: str):
    """Sort all rows in a treeview alphabetically by the given column."""
    data = [(tree.set(child, col), child) for child in tree.get_children("")]
    data.sort()
    for i, (_, child) in enumerate(data):
        tree.move(child, "", i)
        tree.item(child, tags=("alt",) if i % 2 else ())