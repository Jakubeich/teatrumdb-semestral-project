from __future__ import annotations

from teatrumdb.ui.shell import ApplicationShell


def create_app() -> ApplicationShell:
    return ApplicationShell()


def run() -> None:
    app = create_app()
    app.mainloop()
