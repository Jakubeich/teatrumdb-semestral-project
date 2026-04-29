from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb.ui.dialogs import VisitorDialog
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.widgets import DataTable, PageHeader


class VisitorsScreen(BaseScreen):
    screen_title = "Navstevnici"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.search_var = tk.StringVar()
        self.detail_vars = {
            "cele_jmeno": tk.StringVar(value="—"),
            "rodne_cislo": tk.StringVar(value="—"),
            "email": tk.StringVar(value="—"),
            "datum_narozeni": tk.StringVar(value="—"),
            "vernostni_karta": tk.StringVar(value="—"),
            "adresa": tk.StringVar(value="—"),
            "telefony": tk.StringVar(value="—"),
        }

        header = PageHeader(self, "Navstevnici", "CRUD agenda nad objektovou tabulkou navstevnik")
        header.pack(fill="x")
        ttk.Button(header.actions, text="Obnovit", style="Secondary.TButton", command=self.refresh).pack(side="right")

        action_card = ttk.Frame(self, style="Card.TFrame", padding=18)
        action_card.pack(fill="x", padx=24)
        ttk.Label(action_card, text="Filtr a akce", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            action_card,
            text="Vyhledavani podle jmena, prijmeni, rodneho cisla nebo e-mailu.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        controls = ttk.Frame(action_card, style="Card.TFrame")
        controls.pack(fill="x")
        ttk.Entry(controls, textvariable=self.search_var, width=36).pack(side="left", fill="x", expand=True)
        ttk.Button(controls, text="Hledat", command=self.refresh).pack(side="left", padx=(10, 0))
        ttk.Button(controls, text="Pridat", style="Accent.TButton", command=self.add_visitor).pack(side="left", padx=(10, 0))
        ttk.Button(controls, text="Upravit", command=self.edit_visitor).pack(side="left", padx=(10, 0))
        ttk.Button(controls, text="Smazat", style="Danger.TButton", command=self.delete_visitor).pack(side="left", padx=(10, 0))

        self.search_var.trace_add("write", self._on_search_change)

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=24)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        table_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(table_card, text="Seznam navstevniku", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(table_card, text="Prehled zakladnich osobnich udaju.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(4, 14)
        )
        self.table = DataTable(table_card)
        self.table.pack(fill="both", expand=True)
        self.table.bind_select(self._load_selected_detail)
        self.table.bind_double_click(lambda _event: self.edit_visitor())

        detail_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        detail_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(detail_card, text="Detail vybraneho navstevnika", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(detail_card, text="Rozsirene atributy vcetne adresy a telefonu.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(4, 16)
        )

        fields = [
            ("Jmeno", "cele_jmeno"),
            ("Rodne cislo", "rodne_cislo"),
            ("E-mail", "email"),
            ("Datum narozeni", "datum_narozeni"),
            ("Vernostni karta", "vernostni_karta"),
            ("Adresa", "adresa"),
            ("Telefony", "telefony"),
        ]

        for label, key in fields:
            section = ttk.Frame(detail_card, style="Card.TFrame")
            section.pack(fill="x", pady=6)
            ttk.Label(section, text=label, style="DetailLabel.TLabel").pack(anchor="w")
            ttk.Label(section, textvariable=self.detail_vars[key], style="DetailValue.TLabel", wraplength=340).pack(
                anchor="w", pady=(4, 0)
            )

    def _on_search_change(self, *_args) -> None:
        if not self.search_var.get():
            self.refresh()

    def refresh(self) -> None:
        if not self.service.db.is_connected():
            self.table.clear()
            self._clear_detail()
            self.set_status("Agenda navstevniku ceka na pripojeni.")
            return

        try:
            columns, rows = self.service.list_visitors(self.search_var.get())
            self.table.load(columns, rows)
            self._select_first_row()
            self.set_status("Seznam navstevniku byl nacten.")
        except Exception as error:
            self.show_error(error)

    def add_visitor(self) -> None:
        if not self.require_connection():
            return

        payload = VisitorDialog.show(self, "Pridat navstevnika")
        if not payload:
            return

        try:
            self.service.create_visitor(payload)
            self.refresh()
            self.set_status(f"Navstevnik {payload['jmeno']} {payload['prijmeni']} byl pridan.")
        except Exception as error:
            self.show_error(error)

    def edit_visitor(self) -> None:
        if not self.require_connection():
            return

        visitor_id = self._selected_visitor_id()
        if not visitor_id:
            messagebox.showwarning("Vyber zaznam", "Vyberte navstevnika k uprave.", parent=self)
            return

        try:
            detail = self.service.get_visitor_detail(str(visitor_id))
            if detail is None:
                messagebox.showwarning("Nenalezeno", "Vybrany navstevnik nebyl nalezen.", parent=self)
                return

            payload = VisitorDialog.show(
                self,
                "Upravit navstevnika",
                initial=detail,
                allow_id_edit=False,
            )
            if not payload:
                return

            self.service.update_visitor(str(visitor_id), payload)
            self.refresh()
            self.set_status(f"Navstevnik {visitor_id} byl upraven.")
        except Exception as error:
            self.show_error(error)

    def delete_visitor(self) -> None:
        if not self.require_connection():
            return

        visitor_id = self._selected_visitor_id()
        if not visitor_id:
            messagebox.showwarning("Vyber zaznam", "Vyberte navstevnika ke smazani.", parent=self)
            return

        if not messagebox.askyesno(
            "Potvrzeni",
            f"Opravdu chcete smazat navstevnika {visitor_id}?\n\n"
            "Smazou se i jeho rezervace, platby, predplatne a hodnoceni.",
            parent=self,
        ):
            return

        try:
            self.service.delete_visitor(str(visitor_id))
            self.refresh()
            self.set_status(f"Navstevnik {visitor_id} byl smazan.")
        except Exception as error:
            self.show_error(error)

    def _selected_visitor_id(self) -> str | None:
        selected = self.table.selected_values()
        if not selected:
            return None
        return str(selected[0])

    def _select_first_row(self) -> None:
        children = self.table.tree.get_children()
        if not children:
            self._clear_detail()
            return
        self.table.tree.selection_set(children[0])
        self.table.tree.focus(children[0])
        self._load_selected_detail()

    def _load_selected_detail(self, _event=None) -> None:
        visitor_id = self._selected_visitor_id()
        if not visitor_id:
            self._clear_detail()
            return

        try:
            detail = self.service.get_visitor_detail(str(visitor_id))
            if not detail:
                self._clear_detail()
                return

            self.detail_vars["cele_jmeno"].set(f"{detail['jmeno']} {detail['prijmeni']}")
            self.detail_vars["rodne_cislo"].set(detail["rodne_cislo"])
            self.detail_vars["email"].set(detail["email"])
            self.detail_vars["datum_narozeni"].set(detail["datum_narozeni"])
            self.detail_vars["vernostni_karta"].set("Ano" if detail["vernostni_karta"] == "A" else "Ne")
            adresa = ", ".join(
                value
                for value in [
                    f"{detail['ulice']} {detail['cislo_popisne']}".strip(),
                    f"{detail['psc']} {detail['mesto']}".strip(),
                    detail["stat"],
                ]
                if value.strip()
            )
            self.detail_vars["adresa"].set(adresa or "—")
            self.detail_vars["telefony"].set(detail["telefony"] or "—")
        except Exception as error:
            self.show_error(error)

    def _clear_detail(self) -> None:
        for variable in self.detail_vars.values():
            variable.set("—")

    def on_connection_changed(self) -> None:
        self.refresh()
