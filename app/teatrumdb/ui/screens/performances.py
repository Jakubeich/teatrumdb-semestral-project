from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb.services.theatre_service import format_currency
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.widgets import DataTable, PageHeader, ReadOnlyText


class PerformancesScreen(BaseScreen):
    screen_title = "Predstaveni"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.detail_vars = {
            "nazev": tk.StringVar(value="—"),
            "zanr": tk.StringVar(value="—"),
            "reziser": tk.StringVar(value="—"),
            "termin": tk.StringVar(value="—"),
            "premiera": tk.StringVar(value="—"),
            "delka_min": tk.StringVar(value="—"),
            "sal": tk.StringVar(value="—"),
            "kapacita": tk.StringVar(value="—"),
            "stav": tk.StringVar(value="—"),
            "obsazenost": tk.StringVar(value="—"),
            "zakladni_cena": tk.StringVar(value="—"),
        }

        header = PageHeader(self, "Predstaveni", "Harmonogram predstaveni a rychly nahled na obsazenost")
        header.pack(fill="x")
        ttk.Button(header.actions, text="Obsazenost", command=self.show_occupancy).pack(side="right")
        ttk.Button(header.actions, text="Obnovit", style="Secondary.TButton", command=self.refresh).pack(
            side="right", padx=(0, 10)
        )

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        table_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(table_card, text="Kalendar predstaveni", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(table_card, text="Jednotliva predstaveni, saly a stav prodeje.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(4, 14)
        )
        self.table = DataTable(table_card)
        self.table.pack(fill="both", expand=True)
        self.table.bind_select(self._load_selected_detail)

        detail_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        detail_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(detail_card, text="Detail predstaveni", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(detail_card, text="Inscenace, rezie, termin, kapacita a popis.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(4, 16)
        )

        for label, key in [
            ("Nazev", "nazev"),
            ("Zanr", "zanr"),
            ("Reziser", "reziser"),
            ("Termin", "termin"),
            ("Premiera", "premiera"),
            ("Delka", "delka_min"),
            ("Sal", "sal"),
            ("Kapacita", "kapacita"),
            ("Stav", "stav"),
            ("Obsazenost", "obsazenost"),
            ("Cena", "zakladni_cena"),
        ]:
            row = ttk.Frame(detail_card, style="Card.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, style="DetailLabel.TLabel").pack(anchor="w")
            ttk.Label(row, textvariable=self.detail_vars[key], style="DetailValue.TLabel", wraplength=340).pack(
                anchor="w", pady=(4, 0)
            )

        ttk.Label(detail_card, text="Popis inscenace", style="DetailLabel.TLabel").pack(anchor="w", pady=(14, 6))
        self.description = ReadOnlyText(detail_card, height=10)
        self.description.pack(fill="both", expand=True)

    def refresh(self) -> None:
        if not self.service.db.is_connected():
            self.table.clear()
            self._clear_detail()
            self.set_status("Prehled predstaveni ceka na pripojeni.")
            return

        try:
            columns, rows = self.service.list_performances()
            self.table.load(columns, rows)
            children = self.table.tree.get_children()
            if children:
                self.table.tree.selection_set(children[0])
                self.table.tree.focus(children[0])
                self._load_selected_detail()
            else:
                self._clear_detail()
            self.set_status("Seznam predstaveni byl obnoven.")
        except Exception as error:
            self.show_error(error)

    def show_occupancy(self) -> None:
        if not self.require_connection():
            return

        performance_id = self._selected_performance_id()
        if performance_id is None:
            messagebox.showwarning("Vyber zaznam", "Vyberte predstaveni.", parent=self)
            return

        try:
            occupancy = self.service.get_performance_occupancy(performance_id)
            self.detail_vars["obsazenost"].set(f"{occupancy:.2f} %")
            messagebox.showinfo(
                "Obsazenost",
                f"Obsazenost predstaveni {performance_id}: {occupancy:.2f} %",
                parent=self,
            )
        except Exception as error:
            self.show_error(error)

    def _selected_performance_id(self) -> int | None:
        selected = self.table.selected_values()
        if not selected:
            return None
        return int(selected[0])

    def _load_selected_detail(self, _event=None) -> None:
        performance_id = self._selected_performance_id()
        if performance_id is None:
            self._clear_detail()
            return

        try:
            detail = self.service.get_performance_detail(performance_id)
            if not detail:
                self._clear_detail()
                return

            self.detail_vars["nazev"].set(detail["nazev"])
            self.detail_vars["zanr"].set(detail["zanr"])
            self.detail_vars["reziser"].set(detail["reziser"])
            self.detail_vars["termin"].set(detail["termin"])
            self.detail_vars["premiera"].set(detail["premiera"])
            self.detail_vars["delka_min"].set(f"{detail['delka_min']} min")
            self.detail_vars["sal"].set(detail["sal"])
            self.detail_vars["kapacita"].set(str(detail["kapacita"]))
            self.detail_vars["stav"].set(detail["stav"])
            self.detail_vars["obsazenost"].set(f"{float(detail['obsazenost']):.2f} %")
            self.detail_vars["zakladni_cena"].set(format_currency(detail["zakladni_cena"]))
            self.description.set_text(detail["popis"] or "")
        except Exception as error:
            self.show_error(error)

    def _clear_detail(self) -> None:
        for variable in self.detail_vars.values():
            variable.set("—")
        self.description.set_text("")

    def on_connection_changed(self) -> None:
        self.refresh()
