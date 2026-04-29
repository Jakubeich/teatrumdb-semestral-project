from __future__ import annotations

import sys
from pathlib import Path
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from teatrumdb import config  # noqa: E402
from teatrumdb.database import DatabaseClient  # noqa: E402
from teatrumdb.ui.screens import visitors as visitors_module  # noqa: E402
from teatrumdb.ui.shell import ApplicationShell  # noqa: E402


LOG = ROOT / "logs" / "ui-clickthrough-report.txt"
VISITOR_ID = "990101/7777"
DEPENDENT_VISITOR_ID = "800101/1234"


class UiClickthrough:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.errors: list[str] = []
        self.infos: list[str] = []
        self.warnings: list[str] = []
        self.created_reservation_id: int | None = None
        self.app: ApplicationShell | None = None

    def log(self, message: str) -> None:
        print(message)
        self.lines.append(message)

    def fail(self, message: str) -> None:
        raise AssertionError(message)

    def row_count(self, table) -> int:
        return len(table.tree.get_children())

    def tree_values(self, table) -> list[list[str]]:
        return [
            list(map(str, table.tree.item(item).get("values", [])))
            for item in table.tree.get_children()
        ]

    def find_button(self, root, text: str):
        stack = [root]
        while stack:
            widget = stack.pop(0)
            try:
                if isinstance(widget, ttk.Button) and widget.cget("text") == text:
                    return widget
            except Exception:
                pass
            stack.extend(widget.winfo_children())
        self.fail(f"Tlacitko nenalezeno: {text}")

    def click_button(self, root, text: str) -> None:
        assert self.app is not None
        button = self.find_button(root, text)
        self.log(f"CLICK: {text}")
        button.invoke()
        self.app.update_idletasks()
        self.app.update()
        if self.errors:
            self.fail(f"Po kliknuti {text} vznikla chyba: {self.errors[-1]}")

    def assert_rows(self, label: str, table, minimum: int = 1) -> None:
        count = self.row_count(table)
        self.log(f"{label}: {count} radku")
        if count < minimum:
            self.fail(f"{label}: ocekavano alespon {minimum}, realne {count}")

    def select_row_by_first_value(self, table, value: str) -> None:
        for item in table.tree.get_children():
            values = table.tree.item(item).get("values", [])
            if values and str(values[0]) == value:
                table.tree.selection_set(item)
                table.tree.focus(item)
                table.tree.event_generate("<<TreeviewSelect>>")
                return
        self.fail(f"Radek s prvni hodnotou {value!r} nebyl nalezen")

    def patch_dialogs(self) -> None:
        messagebox.showinfo = lambda title, message, **kwargs: self.infos.append(
            f"{title}: {message}"
        ) or "ok"
        messagebox.showwarning = lambda title, message, **kwargs: self.warnings.append(
            f"{title}: {message}"
        ) or "ok"
        messagebox.showerror = lambda title, message, **kwargs: self.errors.append(
            f"{title}: {message}"
        ) or "ok"
        messagebox.askyesno = lambda title, message, **kwargs: True

        add_payload = {
            "rodne_cislo": VISITOR_ID,
            "jmeno": "Test",
            "prijmeni": "Klikac",
            "email": "test.klikac@example.cz",
            "datum_narozeni": "1999-01-01",
            "vernostni_karta": "N",
            "ulice": "Testovaci",
            "cislo_popisne": "1",
            "mesto": "Ostrava",
            "psc": "70000",
            "stat": "CZ",
            "telefony": "+420700111222",
        }
        edit_payload = dict(add_payload)
        edit_payload.update(
            {
                "jmeno": "Test",
                "prijmeni": "Upraveny",
                "email": "test.upraveny@example.cz",
                "vernostni_karta": "A",
            }
        )
        payloads = [add_payload, edit_payload]

        def fake_visitor_dialog_show(parent, title, initial=None, allow_id_edit=True):
            if not payloads:
                self.fail(f"Neocekavany dialog navstevnika: {title}")
            payload = payloads.pop(0)
            self.log(f"DIALOG: {title} -> {payload['rodne_cislo']}")
            return dict(payload)

        visitors_module.VisitorDialog.show = fake_visitor_dialog_show

    def cleanup_test_rows(self) -> None:
        client = DatabaseClient()
        client.connect(
            config.DEFAULT_ORACLE_USER,
            config.DEFAULT_ORACLE_PASSWORD,
            config.DEFAULT_ORACLE_DSN,
        )
        with client.transaction():
            with client.cursor() as cursor:
                if self.created_reservation_id is not None:
                    cursor.execute(
                        "DELETE FROM rezervace WHERE id_rezervace = :id",
                        {"id": self.created_reservation_id},
                    )
                cursor.execute(
                    "DELETE FROM navstevnik WHERE rodne_cislo = :id",
                    {"id": VISITOR_ID},
                )
        client.disconnect()

    def run(self) -> None:
        self.patch_dialogs()
        self.cleanup_test_rows()

        try:
            self.app = ApplicationShell()
            self.app.update_idletasks()
            self.app.update()
            self.log(f"APP: started, connected={self.app.db.is_connected()}, info={self.app.db.info}")
            if not self.app.db.is_connected():
                self.fail("Aplikace se po startu nepripojila k Oracle")

            self.test_connection()
            self.test_dashboard()
            self.test_visitors()
            self.test_performances()
            self.test_reservations()
            self.test_queries()
            self.test_procedures()
            self.test_dependent_visitor_delete()

            if self.warnings:
                self.log("WARNINGS: " + " | ".join(self.warnings))
            if self.infos:
                self.log(f"INFO dialogs: {len(self.infos)}")
            self.log("UI_CLICKTHROUGH_RESULT=OK")
        finally:
            if self.app is not None:
                try:
                    self.app.db.disconnect()
                    self.app.destroy()
                except Exception:
                    pass
            self.cleanup_test_rows()
            LOG.parent.mkdir(exist_ok=True)
            LOG.write_text("\n".join(self.lines) + "\n", encoding="utf-8")

    def test_connection(self) -> None:
        assert self.app is not None
        self.app.show_screen("connection")
        self.app.update()
        screen = self.app.screens["connection"]
        self.click_button(screen, "Odpojit")
        if self.app.db.is_connected():
            self.fail("Odpojit neprerusilo spojeni")
        self.click_button(screen, "Pripojit")
        if not self.app.db.is_connected():
            self.fail("Pripojit nenavazalo spojeni")
        self.log("Pripojeni: odpojit/pripojit OK")

    def test_dashboard(self) -> None:
        assert self.app is not None
        self.app.show_screen("dashboard")
        screen = self.app.screens["dashboard"]
        self.click_button(screen, "Obnovit")
        metric_values = [card.value_var.get() for card in screen.metric_cards]
        self.log(f"Prehled metriky: {metric_values}")
        if any(value == "—" for value in metric_values):
            self.fail("Dashboard metriky zustaly prazdne")
        self.assert_rows("Prehled - nejblizsi predstaveni", screen.upcoming_table, 1)
        self.assert_rows("Prehled - nejvyssi utrata", screen.spenders_table, 1)

    def test_visitors(self) -> None:
        assert self.app is not None
        self.app.show_screen("visitors")
        screen = self.app.screens["visitors"]
        self.click_button(screen, "Obnovit")
        initial = self.row_count(screen.table)
        self.click_button(screen, "Pridat")
        if not any(row and row[0] == VISITOR_ID for row in self.tree_values(screen.table)):
            self.fail("Pridany navstevnik neni v tabulce")
        self.select_row_by_first_value(screen.table, VISITOR_ID)
        self.click_button(screen, "Upravit")
        self.select_row_by_first_value(screen.table, VISITOR_ID)
        detail = screen.service.get_visitor_detail(VISITOR_ID)
        if not detail or detail["prijmeni"] != "Upraveny" or detail["vernostni_karta"] != "A":
            self.fail(f"Uprava navstevnika se neprojevila: {detail}")
        self.click_button(screen, "Smazat")
        if any(row and row[0] == VISITOR_ID for row in self.tree_values(screen.table)):
            self.fail("Smazany navstevnik zustal v tabulce")
        self.log(f"Navstevnici CRUD OK: {initial} -> add/edit/delete")

    def test_performances(self) -> None:
        assert self.app is not None
        self.app.show_screen("performances")
        screen = self.app.screens["performances"]
        self.click_button(screen, "Obnovit")
        self.assert_rows("Predstaveni", screen.table, 1)
        first = screen.table.tree.get_children()[0]
        screen.table.tree.selection_set(first)
        screen.table.tree.focus(first)
        screen.table.tree.event_generate("<<TreeviewSelect>>")
        self.app.update()
        if screen.detail_vars["nazev"].get() == "—":
            self.fail("Detail predstaveni se nenacetl")
        self.click_button(screen, "Obsazenost")
        self.log(f"Predstaveni detail OK: {screen.detail_vars['nazev'].get()}")

    def test_reservations(self) -> None:
        assert self.app is not None
        self.app.show_screen("reservations")
        screen = self.app.screens["reservations"]
        self.click_button(screen, "Obnovit")
        before = self.row_count(screen.table)
        screen.visitor_var.set("020914/8080")
        screen.performance_var.set("6")
        screen.seat_var.set("5")
        self.click_button(screen, "Vytvorit rezervaci")
        if self.row_count(screen.table) <= before:
            self.fail("Nova rezervace se neobjevila v tabulce")
        self.created_reservation_id = max(
            int(row[0]) for row in self.tree_values(screen.table) if row and str(row[0]).isdigit()
        )
        screen.reservation_id_var.set(str(self.created_reservation_id))
        self.click_button(screen, "Zrusit rezervaci")
        if screen.refund_var.get() == "—":
            self.fail("Zruseni rezervace nevyplnilo vracenou castku")
        self.log(f"Rezervace OK: vytvorena a zrusena ID {self.created_reservation_id}")

    def test_queries(self) -> None:
        assert self.app is not None
        self.app.show_screen("queries")
        screen = self.app.screens["queries"]
        run_button = self.find_button(screen, "Spustit dotaz")
        for index, query in enumerate(screen.queries):
            screen.listbox.selection_clear(0, "end")
            screen.listbox.selection_set(index)
            screen.listbox.activate(index)
            screen.listbox.event_generate("<<ListboxSelect>>")
            self.app.update()
            self.log(f"CLICK: Spustit dotaz -> {query.key}")
            run_button.invoke()
            self.app.update_idletasks()
            self.app.update()
            if self.errors:
                self.fail(f"Dotaz {query.key} skoncil chybou: {self.errors[-1]}")
            self.assert_rows(f"Dotaz {index + 1} {query.key}", screen.table, 0)
        self.log("Dotazy: vsech 12 dotazu spusteno pres UI")

    def test_procedures(self) -> None:
        assert self.app is not None
        self.app.show_screen("procedures")
        screen = self.app.screens["procedures"]
        screen.production_id_var.set("1")
        self.click_button(screen, "Spocitat")
        if screen.revenue_result_var.get() in {"—", "0 Kč"}:
            self.fail(f"Trzba se nespocitala: {screen.revenue_result_var.get()}")
        screen.top_n_var.set("5")
        self.click_button(screen, "Nacist TOP")
        self.assert_rows("Procedury - TOP navstevnici", screen.table, 1)
        screen.hall_id_var.set("3")
        screen.rows_var.set("5")
        screen.seats_per_row_var.set("6")
        self.click_button(screen, "Generovat")
        if screen.generation_result_var.get() != "Dokonceno":
            self.fail("Generovani sedadel nepotvrdilo dokonceni")
        self.log(
            f"Procedury OK: trzba={screen.revenue_result_var.get()}, "
            f"generovani={screen.generation_result_var.get()}"
        )

    def test_dependent_visitor_delete(self) -> None:
        assert self.app is not None
        self.app.show_screen("visitors")
        screen = self.app.screens["visitors"]
        self.click_button(screen, "Obnovit")
        self.select_row_by_first_value(screen.table, DEPENDENT_VISITOR_ID)
        self.click_button(screen, "Smazat")
        if any(row and row[0] == DEPENDENT_VISITOR_ID for row in self.tree_values(screen.table)):
            self.fail("Navstevnik s navazanymi zaznamy zustal po smazani v tabulce")
        self.log(f"Navstevnici cascade delete OK: {DEPENDENT_VISITOR_ID}")


if __name__ == "__main__":
    UiClickthrough().run()
