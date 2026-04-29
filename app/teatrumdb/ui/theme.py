from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


PALETTE = {
    "bg": "#17181c",
    "sidebar": "#141519",
    "surface": "#22252d",
    "surface_alt": "#2b2f38",
    "surface_hover": "#353b46",
    "border": "#3d4452",
    "text": "#f3efe7",
    "muted": "#a3aab5",
    "accent": "#19a779",
    "accent_hover": "#14835f",
    "accent_soft": "#143b31",
    "amber": "#c98b33",
    "amber_soft": "#4f3312",
    "danger": "#d56565",
    "danger_hover": "#b84f4f",
    "info": "#3e8ef7",
}

MONO_FONT = ("Menlo", 11)


def configure_theme(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(background=PALETTE["bg"])

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=11)

    heading_font = tkfont.Font(family=default_font.actual("family"), size=13, weight="bold")
    title_font = tkfont.Font(family=default_font.actual("family"), size=22, weight="bold")
    metric_font = tkfont.Font(family=default_font.actual("family"), size=24, weight="bold")
    badge_font = tkfont.Font(family=default_font.actual("family"), size=10, weight="bold")

    style.configure(".", background=PALETTE["bg"], foreground=PALETTE["text"], font=default_font)
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("Sidebar.TFrame", background=PALETTE["sidebar"])
    style.configure("Header.TFrame", background=PALETTE["bg"])
    style.configure("Card.TFrame", background=PALETTE["surface"])
    style.configure("SurfaceAlt.TFrame", background=PALETTE["surface_alt"])

    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", background=PALETTE["bg"], foreground=PALETTE["muted"])
    style.configure("SidebarMuted.TLabel", background=PALETTE["sidebar"], foreground=PALETTE["muted"])
    style.configure("Card.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("CardMuted.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("Title.TLabel", background=PALETTE["bg"], foreground=PALETTE["text"], font=title_font)
    style.configure("Subtitle.TLabel", background=PALETTE["bg"], foreground=PALETTE["muted"])
    style.configure("SectionTitle.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=heading_font)
    style.configure("MetricTitle.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("MetricValue.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=metric_font)
    style.configure("MetricCaption.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("DetailLabel.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"])
    style.configure("DetailValue.TLabel", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("BadgeConnected.TLabel", background=PALETTE["accent_soft"], foreground=PALETTE["text"], font=badge_font, padding=(12, 6))
    style.configure("BadgeDisconnected.TLabel", background="#4a2325", foreground=PALETTE["text"], font=badge_font, padding=(12, 6))
    style.configure("Status.TLabel", background=PALETTE["surface_alt"], foreground=PALETTE["muted"], padding=(16, 8))

    style.configure(
        "TButton",
        background=PALETTE["surface_alt"],
        foreground=PALETTE["text"],
        borderwidth=0,
        focusthickness=0,
        padding=(14, 10),
    )
    style.map("TButton", background=[("active", PALETTE["surface_hover"])])

    style.configure("Accent.TButton", background=PALETTE["accent"], foreground="#08130f")
    style.map("Accent.TButton", background=[("active", PALETTE["accent_hover"])])

    style.configure("Secondary.TButton", background=PALETTE["amber"], foreground="#1c1305")
    style.map("Secondary.TButton", background=[("active", "#b17829")])

    style.configure("Danger.TButton", background=PALETTE["danger"], foreground="#210909")
    style.map("Danger.TButton", background=[("active", PALETTE["danger_hover"])])

    style.configure(
        "Nav.TButton",
        background=PALETTE["sidebar"],
        foreground=PALETTE["muted"],
        padding=(14, 12),
        anchor="w",
        borderwidth=0,
    )
    style.map("Nav.TButton", background=[("active", PALETTE["surface"])], foreground=[("active", PALETTE["text"])])
    style.configure("Selected.Nav.TButton", background=PALETTE["surface"], foreground=PALETTE["text"])

    style.configure(
        "TEntry",
        fieldbackground=PALETTE["surface_alt"],
        foreground=PALETTE["text"],
        insertcolor=PALETTE["text"],
        bordercolor=PALETTE["border"],
        lightcolor=PALETTE["border"],
        darkcolor=PALETTE["border"],
        padding=(10, 8),
    )
    style.configure(
        "TCombobox",
        fieldbackground=PALETTE["surface_alt"],
        foreground=PALETTE["text"],
        arrowsize=14,
        padding=(10, 8),
    )

    style.configure(
        "Data.Treeview",
        background=PALETTE["surface"],
        fieldbackground=PALETTE["surface"],
        foreground=PALETTE["text"],
        bordercolor=PALETTE["border"],
        rowheight=30,
    )
    style.map("Data.Treeview", background=[("selected", PALETTE["accent"])], foreground=[("selected", "#08130f")])
    style.configure(
        "Data.Treeview.Heading",
        background=PALETTE["surface_alt"],
        foreground=PALETTE["text"],
        relief="flat",
        padding=(10, 10),
        font=badge_font,
    )
    style.map("Data.Treeview.Heading", background=[("active", PALETTE["surface_hover"])])

    style.configure("TLabelframe", background=PALETTE["surface"], foreground=PALETTE["text"])
    style.configure("TLabelframe.Label", background=PALETTE["surface"], foreground=PALETTE["text"], font=heading_font)

    root.option_add("*TCombobox*Listbox.background", PALETTE["surface_alt"])
    root.option_add("*TCombobox*Listbox.foreground", PALETTE["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", PALETTE["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#08130f")
    return style


def style_text_widget(widget: tk.Text) -> None:
    widget.configure(
        background=PALETTE["surface_alt"],
        foreground=PALETTE["text"],
        insertbackground=PALETTE["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=PALETTE["border"],
        highlightcolor=PALETTE["accent"],
        padx=12,
        pady=12,
        font=MONO_FONT,
    )
