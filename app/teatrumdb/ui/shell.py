from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb import config
from teatrumdb.database import DatabaseClient
from teatrumdb.services.theatre_service import TheatreService
from teatrumdb.ui.screens.connection import ConnectionScreen
from teatrumdb.ui.screens.dashboard import DashboardScreen
from teatrumdb.ui.screens.performances import PerformancesScreen
from teatrumdb.ui.screens.procedures import ProceduresScreen
from teatrumdb.ui.screens.queries import QueriesScreen
from teatrumdb.ui.screens.reservations import ReservationsScreen
from teatrumdb.ui.screens.visitors import VisitorsScreen
from teatrumdb.ui.theme import configure_theme


class ApplicationShell(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        self.minsize(*config.MIN_WINDOW_SIZE)
        configure_theme(self)

        self.db = DatabaseClient()
        self.service = TheatreService(self.db)
        self.status_var = tk.StringVar(value="Pripraveno.")
        self.connection_var = tk.StringVar(value="Nepripojeno")

        self.nav_buttons: dict[str, ttk.Button] = {}
        self.screens = {}
        self.current_screen = ""

        self._build_layout()
        self._register_screens()
        self._update_connection_badge()
        self.show_screen("dashboard")
        self._try_auto_connect()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame", padding=(24, 20))
        header.pack(fill="x")

        brand = ttk.Frame(header, style="Header.TFrame")
        brand.pack(side="left", fill="x", expand=True)
        ttk.Label(brand, text=config.APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(brand, text=config.APP_SUBTITLE, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        self.connection_badge = ttk.Label(header, textvariable=self.connection_var, style="BadgeDisconnected.TLabel")
        self.connection_badge.pack(side="right")

        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(body, style="Sidebar.TFrame", padding=(18, 24))
        self.sidebar.pack(side="left", fill="y")
        ttk.Label(self.sidebar, text="Navigace", style="SidebarMuted.TLabel").pack(anchor="w", pady=(0, 16))

        self.content = ttk.Frame(body, style="TFrame")
        self.content.pack(side="left", fill="both", expand=True)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        status_bar = ttk.Frame(self, style="SurfaceAlt.TFrame")
        status_bar.pack(fill="x")
        ttk.Label(status_bar, textvariable=self.status_var, style="Status.TLabel").pack(fill="x")

    def _register_screens(self) -> None:
        screens = [
            ("dashboard", "Prehled", DashboardScreen),
            ("connection", "Pripojeni", ConnectionScreen),
            ("visitors", "Navstevnici", VisitorsScreen),
            ("performances", "Predstaveni", PerformancesScreen),
            ("reservations", "Rezervace", ReservationsScreen),
            ("queries", "Dotazy", QueriesScreen),
            ("procedures", "Procedury", ProceduresScreen),
        ]

        for key, label, screen_cls in screens:
            button = ttk.Button(
                self.sidebar,
                text=label,
                style="Nav.TButton",
                command=lambda target=key: self.show_screen(target),
            )
            button.pack(fill="x", pady=4)
            self.nav_buttons[key] = button

            screen = screen_cls(self.content, self.service, self)
            screen.grid(row=0, column=0, sticky="nsew")
            self.screens[key] = screen

    def show_screen(self, screen_key: str) -> None:
        if screen_key not in self.screens:
            return

        self.current_screen = screen_key
        self.screens[screen_key].tkraise()
        for key, button in self.nav_buttons.items():
            button.configure(style="Selected.Nav.TButton" if key == screen_key else "Nav.TButton")

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def notify(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message, parent=self)

    def show_error(self, error: Exception) -> None:
        self.set_status("Operace skoncila chybou.")
        messagebox.showerror("Chyba aplikace", str(error), parent=self)

    def connect_database(self, user: str, password: str, dsn: str) -> bool:
        try:
            self.db.connect(user, password, dsn)
        except Exception as error:
            self.show_error(error)
            return False

        self._update_connection_badge()
        self._broadcast_connection_change()
        self.set_status(f"Pripojeno k Oracle databazi jako {self.db.info}.")
        return True

    def _try_auto_connect(self) -> None:
        if not config.AUTO_CONNECT_ON_START:
            return

        if not config.DEFAULT_ORACLE_PASSWORD:
            self.set_status("Aplikace je pripravena. Nastav ORA_PASS nebo se pripoj rucne v zalozce Pripojeni.")
            return

        try:
            self.db.connect(
                config.DEFAULT_ORACLE_USER,
                config.DEFAULT_ORACLE_PASSWORD,
                config.DEFAULT_ORACLE_DSN,
            )
        except Exception as error:
            self._update_connection_badge()
            self._broadcast_connection_change()
            self.set_status(
                "Automaticke pripojeni selhalo. Zkontroluj, ze bezi Oracle a sedi ORA_USER/ORA_PASS/ORA_DSN. "
                f"Detail: {error}"
            )
            return

        self._update_connection_badge()
        self._broadcast_connection_change()
        self.set_status(f"Automaticky pripojeno k Oracle databazi jako {self.db.info}.")
        self.show_screen("dashboard")

    def disconnect_database(self) -> None:
        self.db.disconnect()
        self._update_connection_badge()
        self._broadcast_connection_change()
        self.set_status("Spojeni s databazi bylo ukonceno.")

    def _broadcast_connection_change(self) -> None:
        for screen in self.screens.values():
            screen.on_connection_changed()

    def _update_connection_badge(self) -> None:
        if self.db.is_connected():
            self.connection_var.set(self.db.info)
            self.connection_badge.configure(style="BadgeConnected.TLabel")
        else:
            self.connection_var.set("Nepripojeno")
            self.connection_badge.configure(style="BadgeDisconnected.TLabel")

    def _on_close(self) -> None:
        self.db.disconnect()
        self.destroy()
