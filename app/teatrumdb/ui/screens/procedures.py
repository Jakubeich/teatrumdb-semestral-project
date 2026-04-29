from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb.services.theatre_service import format_currency
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.widgets import DataTable, PageHeader


class ProceduresScreen(BaseScreen):
    screen_title = "Procedury a funkce"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.production_id_var = tk.StringVar()
        self.top_n_var = tk.StringVar(value="5")
        self.hall_id_var = tk.StringVar()
        self.rows_var = tk.StringVar()
        self.seats_per_row_var = tk.StringVar()
        self.revenue_result_var = tk.StringVar(value="—")
        self.generation_result_var = tk.StringVar(value="—")

        header = PageHeader(self, "Procedury a funkce", "PL/SQL operace vystavene v aplikacnim rozhrani")
        header.pack(fill="x")

        cards = ttk.Frame(self, style="TFrame")
        cards.pack(fill="x", padx=24)
        for column in range(3):
            cards.columnconfigure(column, weight=1)

        revenue_card = ttk.Frame(cards, style="Card.TFrame", padding=18)
        revenue_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._build_revenue_card(revenue_card)

        top_card = ttk.Frame(cards, style="Card.TFrame", padding=18)
        top_card.grid(row=0, column=1, sticky="nsew", padx=(12, 12))
        self._build_top_card(top_card)

        seats_card = ttk.Frame(cards, style="Card.TFrame", padding=18)
        seats_card.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        self._build_seats_card(seats_card)

        result_card = ttk.Frame(self, style="Card.TFrame", padding=18)
        result_card.pack(fill="both", expand=True, padx=24, pady=24)
        ttk.Label(result_card, text="Vystup procedur a funkci", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            result_card,
            text="Tabulkove vysledky a pomocne vystupy z PL/SQL rozhrani.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 14))
        self.table = DataTable(result_card)
        self.table.pack(fill="both", expand=True)

    def _build_revenue_card(self, parent) -> None:
        ttk.Label(parent, text="fn_trzba_inscenace", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(parent, text="Celkovy objem plateb za inscenaci.", style="CardMuted.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 14)
        )
        self._add_field(parent, 2, "ID inscenace", self.production_id_var)
        ttk.Label(parent, text="Trzba", style="DetailLabel.TLabel").grid(row=3, column=0, sticky="e", padx=(0, 12), pady=8)
        ttk.Label(parent, textvariable=self.revenue_result_var, style="DetailValue.TLabel").grid(
            row=3, column=1, sticky="w", pady=8
        )
        ttk.Button(parent, text="Spocitat", style="Accent.TButton", command=self.run_revenue).grid(
            row=4, column=1, sticky="e", pady=(18, 0)
        )
        parent.columnconfigure(1, weight=1)

    def _build_top_card(self, parent) -> None:
        ttk.Label(parent, text="fn_top_navstevnici", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(parent, text="REF CURSOR s TOP N navstevniky.", style="CardMuted.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 14)
        )
        self._add_field(parent, 2, "Pocet navstevniku", self.top_n_var)
        ttk.Button(parent, text="Nacist TOP", style="Secondary.TButton", command=self.run_top_visitors).grid(
            row=3, column=1, sticky="e", pady=(18, 0)
        )
        parent.columnconfigure(1, weight=1)

    def _build_seats_card(self, parent) -> None:
        ttk.Label(parent, text="pr_generuj_sedadla", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(parent, text="Hromadne doplneni sedadel v salu.", style="CardMuted.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 14)
        )
        self._add_field(parent, 2, "ID salu", self.hall_id_var)
        self._add_field(parent, 3, "Pocet rad", self.rows_var)
        self._add_field(parent, 4, "Sedadel v rade", self.seats_per_row_var)
        ttk.Label(parent, text="Stav", style="DetailLabel.TLabel").grid(row=5, column=0, sticky="e", padx=(0, 12), pady=8)
        ttk.Label(parent, textvariable=self.generation_result_var, style="DetailValue.TLabel").grid(
            row=5, column=1, sticky="w", pady=8
        )
        ttk.Button(parent, text="Generovat", style="Accent.TButton", command=self.run_generate_seats).grid(
            row=6, column=1, sticky="e", pady=(18, 0)
        )
        parent.columnconfigure(1, weight=1)

    def _add_field(self, parent, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="CardMuted.TLabel").grid(row=row, column=0, sticky="e", padx=(0, 12), pady=8)
        ttk.Entry(parent, textvariable=variable, width=18).grid(row=row, column=1, sticky="ew", pady=8)

    def run_revenue(self) -> None:
        if not self.require_connection():
            return

        try:
            revenue = self.service.get_revenue(int(self.production_id_var.get().strip()))
            self.revenue_result_var.set(format_currency(revenue))
            self.set_status("Byla spocitana trzba inscenace.")
        except ValueError:
            messagebox.showwarning("Neplatny vstup", "ID inscenace musi byt cislo.", parent=self)
        except Exception as error:
            self.show_error(error)

    def run_top_visitors(self) -> None:
        if not self.require_connection():
            return

        try:
            columns, rows = self.service.get_top_visitors(int(self.top_n_var.get().strip()))
            formatted_rows = [(name, format_currency(amount)) for name, amount in rows]
            self.table.load(columns, formatted_rows)
            self.set_status("Top navstevnici byli nacteni.")
        except ValueError:
            messagebox.showwarning("Neplatny vstup", "Pocet navstevniku musi byt cislo.", parent=self)
        except Exception as error:
            self.show_error(error)

    def run_generate_seats(self) -> None:
        if not self.require_connection():
            return

        try:
            self.service.generate_seats(
                int(self.hall_id_var.get().strip()),
                int(self.rows_var.get().strip()),
                int(self.seats_per_row_var.get().strip()),
            )
            self.generation_result_var.set("Dokonceno")
            self.set_status("Sedadla byla vygenerovana.")
            messagebox.showinfo("Hotovo", "Sedadla byla vygenerovana.", parent=self)
        except ValueError:
            messagebox.showwarning("Neplatny vstup", "Vsechny hodnoty musi byt cisla.", parent=self)
        except Exception as error:
            self.show_error(error)

    def on_connection_changed(self) -> None:
        if not self.service.db.is_connected():
            self.table.clear()
            self.revenue_result_var.set("—")
            self.generation_result_var.set("—")
