from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from teatrumdb import config
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.widgets import PageHeader


class ConnectionScreen(BaseScreen):
    screen_title = "Pripojeni"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        self.user_var = tk.StringVar(value=config.DEFAULT_ORACLE_USER)
        self.password_var = tk.StringVar(value=config.DEFAULT_ORACLE_PASSWORD)
        self.dsn_var = tk.StringVar(value=config.DEFAULT_ORACLE_DSN)
        self.current_status_var = tk.StringVar(value="Nepripojeno")
        self.current_info_var = tk.StringVar(value="—")

        header = PageHeader(self, "Pripojeni", "Oracle spojeni pro praci s projektem TeatrumDB")
        header.pack(fill="x")

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        for column in range(2):
            content.columnconfigure(column, weight=1)

        form_card = ttk.Frame(content, style="Card.TFrame", padding=20)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(form_card, text="Prihlasovaci udaje", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            form_card,
            text="Vychozi hodnoty se nacitaji z ORA_USER, ORA_PASS a ORA_DSN. Pokud je ORA_PASS nastavene, app se zkusi pripojit uz pri startu.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 18))

        self._add_field(form_card, 2, "Uzivatel", self.user_var)
        self._add_field(form_card, 3, "Heslo", self.password_var, show="*")
        self._add_field(form_card, 4, "DSN", self.dsn_var)

        actions = ttk.Frame(form_card, style="Card.TFrame")
        actions.grid(row=5, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(actions, text="Odpojit", command=self._disconnect).pack(side="right")
        ttk.Button(actions, text="Pripojit", style="Accent.TButton", command=self._connect).pack(
            side="right", padx=(0, 10)
        )

        form_card.columnconfigure(1, weight=1)

        info_card = ttk.Frame(content, style="Card.TFrame", padding=20)
        info_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(info_card, text="Stav spojeni", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            info_card,
            text="Aktualni stav a pouzite parametry relace.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 18))

        details = ttk.Frame(info_card, style="Card.TFrame")
        details.pack(fill="x")
        self._add_detail(details, 0, "Stav", self.current_status_var)
        self._add_detail(details, 1, "Pripojeni", self.current_info_var)
        self._add_detail(details, 2, "Vychozi uzivatel", tk.StringVar(value=config.DEFAULT_ORACLE_USER))
        self._add_detail(details, 3, "Vychozi DSN", tk.StringVar(value=config.DEFAULT_ORACLE_DSN))

        self.on_connection_changed()

    def _add_field(self, parent, row: int, label: str, variable: tk.StringVar, show: str | None = None) -> None:
        ttk.Label(parent, text=label, style="CardMuted.TLabel").grid(row=row, column=0, sticky="e", padx=(0, 12), pady=8)
        entry = ttk.Entry(parent, textvariable=variable, show=show or "", width=34)
        entry.grid(row=row, column=1, sticky="ew", pady=8)

    def _add_detail(self, parent, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="DetailLabel.TLabel").grid(row=row, column=0, sticky="w", pady=8)
        ttk.Label(parent, textvariable=variable, style="DetailValue.TLabel").grid(
            row=row, column=1, sticky="e", padx=(18, 0), pady=8
        )
        parent.columnconfigure(1, weight=1)

    def _connect(self) -> None:
        connected = self.shell.connect_database(
            self.user_var.get().strip(),
            self.password_var.get(),
            self.dsn_var.get().strip(),
        )
        if connected:
            self.shell.notify("Pripojeni", f"Pripojeni k databazi bylo uspesne: {self.service.db.info}")
            self.shell.show_screen("dashboard")

    def _disconnect(self) -> None:
        self.shell.disconnect_database()

    def on_connection_changed(self) -> None:
        if self.service.db.is_connected():
            self.current_status_var.set("Pripojeno")
            self.current_info_var.set(self.service.db.info)
        else:
            self.current_status_var.set("Nepripojeno")
            self.current_info_var.set("—")
