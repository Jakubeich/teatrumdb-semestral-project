from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from teatrumdb.ui.theme import PALETTE, style_text_widget


class PageHeader(ttk.Frame):
    def __init__(self, parent: tk.Widget, title: str, subtitle: str) -> None:
        super().__init__(parent, style="Header.TFrame", padding=(24, 24, 24, 18))

        text_block = ttk.Frame(self, style="Header.TFrame")
        text_block.pack(side="left", fill="x", expand=True)

        ttk.Label(text_block, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(text_block, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(6, 0))

        self.actions = ttk.Frame(self, style="Header.TFrame")
        self.actions.pack(side="right", anchor="n")


class MetricCard(ttk.Frame):
    def __init__(self, parent: tk.Widget, accent: str) -> None:
        super().__init__(parent, style="Card.TFrame", padding=0)

        accent_bar = tk.Frame(self, background=accent, height=5)
        accent_bar.pack(fill="x")

        body = ttk.Frame(self, style="Card.TFrame", padding=18)
        body.pack(fill="both", expand=True)

        self.title_var = tk.StringVar(value="—")
        self.value_var = tk.StringVar(value="—")
        self.caption_var = tk.StringVar(value="—")

        ttk.Label(body, textvariable=self.title_var, style="MetricTitle.TLabel").pack(anchor="w")
        ttk.Label(body, textvariable=self.value_var, style="MetricValue.TLabel").pack(anchor="w", pady=(10, 2))
        ttk.Label(body, textvariable=self.caption_var, style="MetricCaption.TLabel").pack(anchor="w")

    def update(self, title: str, value: str, caption: str) -> None:
        self.title_var.set(title)
        self.value_var.set(value)
        self.caption_var.set(caption)


class DataTable(ttk.Frame):
    def __init__(self, parent: tk.Widget, height: int | None = None) -> None:
        super().__init__(parent, style="Card.TFrame")

        self.tree = ttk.Treeview(self, style="Data.Treeview", show="headings", height=height)
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        xscroll.grid(row=1, column=0, sticky="ew")

        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def load(self, columns: list[str] | tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
        self.clear()
        self.tree["columns"] = list(columns)

        total_columns = max(1, len(columns))
        base_width = max(100, int(980 / total_columns))

        for column in columns:
            title = str(column).replace("_", " ").title()
            self.tree.heading(column, text=title)
            self.tree.column(column, width=base_width, stretch=True, anchor="w")

        for index, row in enumerate(rows):
            values = ["" if value is None else str(value) for value in row]
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=values, tags=(tag,))

        self.tree.tag_configure("evenrow", background=PALETTE["surface"])
        self.tree.tag_configure("oddrow", background=PALETTE["surface_alt"])

    def clear(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()

    def bind_select(self, callback) -> None:
        self.tree.bind("<<TreeviewSelect>>", callback)

    def bind_double_click(self, callback) -> None:
        self.tree.bind("<Double-1>", callback)

    def selected_values(self) -> list[object] | None:
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0]).get("values")


class ReadOnlyText(ttk.Frame):
    def __init__(self, parent: tk.Widget, height: int = 8) -> None:
        super().__init__(parent, style="Card.TFrame")

        self.text = tk.Text(self, height=height, wrap="word")
        style_text_widget(self.text)
        self.text.pack(fill="both", expand=True)
        self.set_text("")

    def set_text(self, value: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.configure(state="disabled")
