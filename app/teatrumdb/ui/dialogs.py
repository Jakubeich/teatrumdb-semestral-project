from __future__ import annotations

from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk

from teatrumdb.ui.theme import PALETTE


class VisitorDialog(tk.Toplevel):
    FIELD_LABELS = [
        ("rodne_cislo", "Rodne cislo"),
        ("jmeno", "Jmeno"),
        ("prijmeni", "Prijmeni"),
        ("email", "E-mail"),
        ("datum_narozeni", "Datum narozeni (YYYY-MM-DD)"),
        ("vernostni_karta", "Vernostni karta"),
        ("ulice", "Ulice"),
        ("cislo_popisne", "Cislo popisne"),
        ("mesto", "Mesto"),
        ("psc", "PSC"),
        ("stat", "Stat"),
        ("telefony", "Telefony (oddelene carkou)"),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        initial: dict[str, str] | None = None,
        allow_id_edit: bool = True,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.configure(background=PALETTE["bg"])
        self.resizable(False, False)
        self.transient(parent)
        self.result: dict[str, str] | None = None

        self.variables = {
            key: tk.StringVar(
                value=(initial or {}).get(key, "N" if key == "vernostni_karta" else "")
            )
            for key, _ in self.FIELD_LABELS
        }

        container = ttk.Frame(self, style="Card.TFrame", padding=22)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        ttk.Label(container, text=title, style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            container,
            text="Osobni a kontaktni udaje navstevnika.",
            style="CardMuted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

        for index, (key, label) in enumerate(self.FIELD_LABELS, start=2):
            ttk.Label(container, text=label, style="CardMuted.TLabel").grid(
                row=index, column=0, sticky="e", padx=(0, 12), pady=6
            )

            if key == "vernostni_karta":
                widget = ttk.Combobox(
                    container,
                    textvariable=self.variables[key],
                    values=("A", "N"),
                    state="readonly",
                    width=28,
                )
            else:
                widget = ttk.Entry(container, textvariable=self.variables[key], width=32)
                if key == "rodne_cislo" and not allow_id_edit:
                    widget.configure(state="disabled")

            widget.grid(row=index, column=1, sticky="ew", pady=6)

        actions = ttk.Frame(container, style="Card.TFrame")
        actions.grid(row=len(self.FIELD_LABELS) + 2, column=0, columnspan=2, sticky="e", pady=(18, 0))
        ttk.Button(actions, text="Zrusit", command=self._cancel).pack(side="right")
        ttk.Button(actions, text="Ulozit", style="Accent.TButton", command=self._submit).pack(
            side="right", padx=(0, 10)
        )

        container.columnconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Return>", lambda _event: self._submit())
        self.bind("<Escape>", lambda _event: self._cancel())
        self._center(parent)

    @classmethod
    def show(
        cls,
        parent: tk.Widget,
        title: str,
        initial: dict[str, str] | None = None,
        allow_id_edit: bool = True,
    ) -> dict[str, str] | None:
        dialog = cls(parent, title, initial=initial, allow_id_edit=allow_id_edit)
        dialog.grab_set()
        parent.wait_window(dialog)
        return dialog.result

    def _submit(self) -> None:
        payload = {key: variable.get().strip() for key, variable in self.variables.items()}
        required_fields = ["rodne_cislo", "jmeno", "prijmeni", "email", "datum_narozeni"]
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            messagebox.showwarning("Chybi data", "Vyplnte povinna pole navstevnika.", parent=self)
            return

        try:
            date.fromisoformat(payload["datum_narozeni"])
        except ValueError:
            messagebox.showwarning(
                "Neplatne datum",
                "Datum narozeni musi byt ve formatu YYYY-MM-DD.",
                parent=self,
            )
            return

        if payload["vernostni_karta"] not in {"A", "N"}:
            payload["vernostni_karta"] = "N"

        self.result = payload
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        self.update_idletasks()
        parent.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_rootx() + max(20, (parent.winfo_width() - width) // 2)
        y = parent.winfo_rooty() + max(20, (parent.winfo_height() - height) // 2)
        self.geometry(f"+{x}+{y}")
