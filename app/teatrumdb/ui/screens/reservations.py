from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb.services.theatre_service import format_currency
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.widgets import DataTable, PageHeader


class ReservationsScreen(BaseScreen):
    screen_title = "Rezervace"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.visitor_var = tk.StringVar()
        self.performance_var = tk.StringVar()
        self.seat_var = tk.StringVar()
        self.reservation_id_var = tk.StringVar()
        self.refund_var = tk.StringVar(value="—")

        header = PageHeader(self, "Rezervace", "Prace nad procedurami pro vytvoreni a zruseni rezervace")
        header.pack(fill="x")
        ttk.Button(header.actions, text="Obnovit", style="Secondary.TButton", command=self.refresh).pack(side="right")

        form_row = ttk.Frame(self, style="TFrame")
        form_row.pack(fill="x", padx=24)
        for column in range(2):
            form_row.columnconfigure(column, weight=1)

        create_card = ttk.Frame(form_row, style="Card.TFrame", padding=18)
        create_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(create_card, text="Nova rezervace", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            create_card,
            text="Volani procedury pr_vytvorit_rezervaci.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))
        self._add_field(create_card, 2, "Rodne cislo", self.visitor_var)
        self._add_field(create_card, 3, "ID predstaveni", self.performance_var)
        self._add_field(create_card, 4, "ID sedadla", self.seat_var)
        ttk.Button(create_card, text="Vytvorit rezervaci", style="Accent.TButton", command=self.create_reservation).grid(
            row=5, column=1, sticky="e", pady=(18, 0)
        )
        create_card.columnconfigure(1, weight=1)

        cancel_card = ttk.Frame(form_row, style="Card.TFrame", padding=18)
        cancel_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(cancel_card, text="Zruseni rezervace", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            cancel_card,
            text="Volani procedury pr_zrusit_rezervaci a vracena castka.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))
        self._add_field(cancel_card, 2, "ID rezervace", self.reservation_id_var)
        ttk.Label(cancel_card, text="Vraceno", style="DetailLabel.TLabel").grid(
            row=3, column=0, sticky="e", padx=(0, 12), pady=8
        )
        ttk.Label(cancel_card, textvariable=self.refund_var, style="DetailValue.TLabel").grid(
            row=3, column=1, sticky="w", pady=8
        )
        ttk.Button(cancel_card, text="Zrusit rezervaci", style="Danger.TButton", command=self.cancel_reservation).grid(
            row=4, column=1, sticky="e", pady=(18, 0)
        )
        cancel_card.columnconfigure(1, weight=1)

        table_card = ttk.Frame(self, style="Card.TFrame", padding=18)
        table_card.pack(fill="both", expand=True, padx=24, pady=24)
        ttk.Label(table_card, text="Evidence rezervaci", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            table_card,
            text="Vyber rezervace rovnou predvyplni ID pro zruseni.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 14))
        self.table = DataTable(table_card)
        self.table.pack(fill="both", expand=True)
        self.table.bind_select(self._on_selection_changed)

    def _add_field(self, parent, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="CardMuted.TLabel").grid(row=row, column=0, sticky="e", padx=(0, 12), pady=8)
        ttk.Entry(parent, textvariable=variable, width=28).grid(row=row, column=1, sticky="ew", pady=8)

    def refresh(self) -> None:
        if not self.service.db.is_connected():
            self.table.clear()
            self.refund_var.set("—")
            self.set_status("Agenda rezervaci ceka na pripojeni.")
            return

        try:
            columns, rows = self.service.list_reservations()
            self.table.load(columns, rows)
            self.set_status("Rezervace byly nacteny.")
        except Exception as error:
            self.show_error(error)

    def create_reservation(self) -> None:
        if not self.require_connection():
            return

        try:
            reservation_id = self.service.create_reservation(
                self.visitor_var.get().strip(),
                int(self.performance_var.get().strip()),
                int(self.seat_var.get().strip()),
            )
            self.refresh()
            self.set_status(f"Rezervace {reservation_id} byla vytvorena.")
            messagebox.showinfo(
                "Hotovo",
                f"Rezervace byla vytvorena pod ID {reservation_id}.",
                parent=self,
            )
        except ValueError:
            messagebox.showwarning("Neplatny vstup", "ID predstaveni i sedadla musi byt cisla.", parent=self)
        except Exception as error:
            self.show_error(error)

    def cancel_reservation(self) -> None:
        if not self.require_connection():
            return

        try:
            refunded = self.service.cancel_reservation(int(self.reservation_id_var.get().strip()))
            self.refund_var.set(format_currency(refunded))
            self.refresh()
            self.set_status("Rezervace byla zrusena.")
            messagebox.showinfo(
                "Hotovo",
                f"Rezervace byla zrusena. Vraceno: {format_currency(refunded)}.",
                parent=self,
            )
        except ValueError:
            messagebox.showwarning("Neplatny vstup", "ID rezervace musi byt cislo.", parent=self)
        except Exception as error:
            self.show_error(error)

    def _on_selection_changed(self, _event=None) -> None:
        selected = self.table.selected_values()
        if not selected:
            return
        self.reservation_id_var.set(str(selected[0]))

    def on_connection_changed(self) -> None:
        self.refresh()
