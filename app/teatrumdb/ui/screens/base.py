from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class BaseScreen(ttk.Frame):
    screen_title = ""

    def __init__(self, parent: tk.Widget, service, shell) -> None:
        super().__init__(parent, style="TFrame")
        self.service = service
        self.shell = shell

    def require_connection(self) -> bool:
        if self.service.db.is_connected():
            return True

        messagebox.showwarning("Pripojeni", "Nejdriv se pripojte k databazi Oracle.", parent=self)
        return False

    def show_error(self, error: Exception) -> None:
        self.shell.show_error(error)

    def set_status(self, message: str) -> None:
        self.shell.set_status(message)

    def on_connection_changed(self) -> None:
        """Hook for screens that react to DB reconnect/disconnect."""
