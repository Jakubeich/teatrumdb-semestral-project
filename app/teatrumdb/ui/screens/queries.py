from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.theme import PALETTE
from teatrumdb.ui.widgets import DataTable, PageHeader, ReadOnlyText


class QueriesScreen(BaseScreen):
    screen_title = "Dotazy"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.queries = self.service.get_query_definitions()
        self.description_var = tk.StringVar(value="")

        header = PageHeader(self, "Dotazy", "Predpripravena sada SQL dotazu pro obhajobu projektu")
        header.pack(fill="x")
        ttk.Button(header.actions, text="Spustit dotaz", style="Accent.TButton", command=self.run_selected).pack(
            side="right"
        )

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=1)

        list_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(list_card, text="Katalog dotazu", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(list_card, text="Vyberte dotaz a spustte ho nad databazi.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(4, 14)
        )

        self.listbox = tk.Listbox(
            list_card,
            activestyle="none",
            background=PALETTE["surface_alt"],
            foreground=PALETTE["text"],
            highlightthickness=0,
            borderwidth=0,
            selectbackground=PALETTE["accent"],
            selectforeground="#08130f",
            font=("Helvetica", 11),
        )
        self.listbox.pack(fill="both", expand=True)
        for query in self.queries:
            self.listbox.insert("end", query.title)
        self.listbox.bind("<<ListboxSelect>>", self._on_query_selected)

        right = ttk.Frame(content, style="TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        sql_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        sql_card.grid(row=0, column=0, sticky="nsew")
        ttk.Label(sql_card, text="SQL nahled", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(sql_card, textvariable=self.description_var, style="CardMuted.TLabel", wraplength=820).pack(
            anchor="w", pady=(4, 14)
        )
        self.sql_preview = ReadOnlyText(sql_card, height=10)
        self.sql_preview.pack(fill="both", expand=True)

        result_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        result_card.grid(row=1, column=0, sticky="nsew", pady=(18, 0))
        result_card.rowconfigure(1, weight=1)
        result_card.columnconfigure(0, weight=1)
        ttk.Label(result_card, text="Vysledky dotazu", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.table = DataTable(result_card)
        self.table.grid(row=1, column=0, sticky="nsew", pady=(14, 0))

        if self.queries:
            self.listbox.selection_set(0)
            self._update_preview(self.queries[0])

    def _on_query_selected(self, _event=None) -> None:
        query = self._selected_query()
        if query:
            self._update_preview(query)

    def _selected_query(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        return self.queries[selection[0]]

    def _update_preview(self, query) -> None:
        self.description_var.set(query.description)
        self.sql_preview.set_text(query.sql)

    def run_selected(self) -> None:
        if not self.require_connection():
            return

        query = self._selected_query()
        if query is None:
            return

        try:
            _, columns, rows = self.service.run_query(query.key)
            self.table.load(columns, rows)
            self.set_status(f"Dotaz '{query.title}' byl spusten.")
        except Exception as error:
            self.show_error(error)

    def on_connection_changed(self) -> None:
        if not self.service.db.is_connected():
            self.table.clear()
            self.set_status("Dotazy cekaji na pripojeni.")
