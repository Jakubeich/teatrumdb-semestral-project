from __future__ import annotations

from tkinter import ttk

from teatrumdb.services.theatre_service import format_currency
from teatrumdb.ui.screens.base import BaseScreen
from teatrumdb.ui.theme import PALETTE
from teatrumdb.ui.widgets import DataTable, MetricCard, PageHeader


class DashboardScreen(BaseScreen):
    screen_title = "Prehled"

    def __init__(self, parent, service, shell) -> None:
        super().__init__(parent, service, shell)

        header = PageHeader(self, "Prehled", "Rychly souhrn stavu divadelni databaze")
        header.pack(fill="x")
        ttk.Button(header.actions, text="Obnovit", style="Secondary.TButton", command=self.refresh).pack(
            side="right"
        )

        metrics_frame = ttk.Frame(self, style="TFrame")
        metrics_frame.pack(fill="x", padx=24)
        for column in range(4):
            metrics_frame.columnconfigure(column, weight=1)

        accents = [PALETTE["accent"], PALETTE["amber"], PALETTE["info"], PALETTE["danger"]]
        self.metric_cards = []
        for index, accent in enumerate(accents):
            card = MetricCard(metrics_frame, accent)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 12, 0))
            self.metric_cards.append(card)

        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=24)
        for column in range(2):
            content.columnconfigure(column, weight=1)
        content.rowconfigure(0, weight=1)

        upcoming_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        upcoming_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(upcoming_card, text="Nejblizsi predstaveni", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            upcoming_card,
            text="Aktualni terminova osa s poctem rezervaci.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 14))
        self.upcoming_table = DataTable(upcoming_card)
        self.upcoming_table.pack(fill="both", expand=True)

        spenders_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        spenders_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ttk.Label(spenders_card, text="Nejvyssi utrata", style="SectionTitle.TLabel").pack(anchor="w")
        ttk.Label(
            spenders_card,
            text="Navstevnici s nejvetsimi zaznamenanymi platbami.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(4, 14))
        self.spenders_table = DataTable(spenders_card)
        self.spenders_table.pack(fill="both", expand=True)

        self.reset()

    def reset(self) -> None:
        placeholders = [
            ("Navstevnici", "—", "cekam na pripojeni"),
            ("Budouci predstaveni", "—", "cekam na pripojeni"),
            ("Aktivni rezervace", "—", "cekam na pripojeni"),
            ("Platby celkem", "—", "cekam na pripojeni"),
        ]
        for card, values in zip(self.metric_cards, placeholders):
            card.update(*values)
        self.upcoming_table.clear()
        self.spenders_table.clear()

    def refresh(self) -> None:
        if not self.service.db.is_connected():
            self.reset()
            self.set_status("Prehled ceka na pripojeni k databazi.")
            return

        try:
            for card, metric in zip(self.metric_cards, self.service.get_dashboard_metrics()):
                card.update(metric["label"], metric["value"], metric["caption"])

            columns, rows = self.service.get_upcoming_performances()
            self.upcoming_table.load(columns, rows)

            spender_columns, spender_rows = self.service.get_top_spenders()
            formatted_rows = [(name, format_currency(amount)) for name, amount in spender_rows]
            self.spenders_table.load(spender_columns, formatted_rows)
            self.set_status("Prehled byl obnoven.")
        except Exception as error:
            self.show_error(error)

    def on_connection_changed(self) -> None:
        self.refresh()
