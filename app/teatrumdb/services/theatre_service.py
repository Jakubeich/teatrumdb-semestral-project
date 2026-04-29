from __future__ import annotations

from decimal import Decimal
from typing import Any

from teatrumdb.catalog import QUERY_BY_KEY, STORED_QUERIES, StoredQuery
from teatrumdb.database import DatabaseClient


def format_currency(value: Any) -> str:
    if value is None:
        return "0 Kč"

    if isinstance(value, Decimal):
        value = float(value)

    amount = float(value)
    formatted = f"{amount:,.2f}".replace(",", " ")
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    return f"{formatted} Kč"


class TheatreService:
    def __init__(self, db: DatabaseClient) -> None:
        self.db = db

    def get_query_definitions(self) -> list[StoredQuery]:
        return STORED_QUERIES

    def get_dashboard_metrics(self) -> list[dict[str, str]]:
        metrics = [
            ("Navstevnici", "SELECT COUNT(*) FROM navstevnik", "registrovanych"),
            ("Budouci predstaveni", "SELECT COUNT(*) FROM predstaveni WHERE datum_cas >= SYSTIMESTAMP", "v planu a prodeji"),
            ("Aktivni rezervace", "SELECT COUNT(*) FROM rezervace WHERE stav <> 'ZRUSENA'", "nezrusenych"),
            ("Platby celkem", "SELECT COALESCE(SUM(castka), 0) FROM platba", "evidovany objem"),
        ]

        result: list[dict[str, str]] = []
        for label, sql, caption in metrics:
            value = self.db.fetch_scalar(sql, default=0)
            display = format_currency(value) if "Platby" in label else str(value or 0)
            result.append({"label": label, "value": display, "caption": caption})
        return result

    def get_upcoming_performances(self, limit: int = 8) -> tuple[list[str], list[tuple[Any, ...]]]:
        sql = """
SELECT *
  FROM (
        SELECT p.id_predstaveni,
               i.nazev,
               TO_CHAR(p.datum_cas, 'DD.MM.YYYY HH24:MI') AS termin,
               s.nazev AS sal,
               p.stav,
               COUNT(CASE WHEN r.stav <> 'ZRUSENA' THEN 1 END) AS rezervace
          FROM predstaveni p
          JOIN inscenace i ON i.id_inscenace = p.id_inscenace
          JOIN sal s ON s.id_sal = p.id_sal
          LEFT JOIN rezervace r ON r.id_predstaveni = p.id_predstaveni
         WHERE p.datum_cas >= SYSTIMESTAMP
         GROUP BY p.id_predstaveni, i.nazev, p.datum_cas, s.nazev, p.stav
         ORDER BY p.datum_cas
  )
 WHERE ROWNUM <= :limit
        """
        return self.db.fetch_all(sql, {"limit": limit})

    def get_top_spenders(self, limit: int = 6) -> tuple[list[str], list[tuple[Any, ...]]]:
        sql = """
SELECT *
  FROM (
        SELECT n.jmeno || ' ' || n.prijmeni AS navstevnik,
               NVL(TREAT(VALUE(n) AS navstevnik_t).celkem_utraceno(), 0) AS utraceno
          FROM navstevnik n
         ORDER BY 2 DESC NULLS LAST, 1
  )
 WHERE ROWNUM <= :limit
        """
        return self.db.fetch_all(sql, {"limit": limit})

    def list_visitors(self, search: str = "") -> tuple[list[str], list[tuple[Any, ...]]]:
        search = search.strip().lower()
        sql = """
SELECT n.rodne_cislo,
       n.jmeno,
       n.prijmeni,
       n.email,
       TO_CHAR(n.datum_narozeni, 'YYYY-MM-DD') AS datum_narozeni,
       n.vernostni_karta
  FROM navstevnik n
        """
        params: dict[str, Any] = {}
        if search:
            sql += """
 WHERE LOWER(n.jmeno || ' ' || n.prijmeni || ' ' || n.rodne_cislo || ' ' || n.email) LIKE :pattern
            """
            params["pattern"] = f"%{search}%"
        sql += " ORDER BY n.prijmeni, n.jmeno"
        return self.db.fetch_all(sql, params)

    def get_visitor_detail(self, visitor_id: str) -> dict[str, Any] | None:
        sql = """
SELECT n.rodne_cislo,
       n.jmeno,
       n.prijmeni,
       n.email,
       TO_CHAR(n.datum_narozeni, 'YYYY-MM-DD') AS datum_narozeni,
       n.vernostni_karta,
       n.adresa.ulice AS ulice,
       n.adresa.cislo_popisne AS cislo_popisne,
       n.adresa.mesto AS mesto,
       n.adresa.psc AS psc,
       n.adresa.stat AS stat,
       NVL((
           SELECT LISTAGG(t.COLUMN_VALUE, ', ') WITHIN GROUP (ORDER BY t.COLUMN_VALUE)
             FROM TABLE(n.telefony) t
       ), '') AS telefony
  FROM navstevnik n
 WHERE n.rodne_cislo = :visitor_id
        """
        columns, row = self.db.fetch_one(sql, {"visitor_id": visitor_id})
        if row is None:
            return None
        return self._as_record(columns, row)

    def create_visitor(self, payload: dict[str, Any]) -> None:
        phone_sql, phone_binds = self._phone_constructor(payload.get("telefony", ""))
        params = self._visitor_params(payload)
        params.update(phone_binds)
        sql = f"""
INSERT INTO navstevnik
VALUES (
    navstevnik_t(
        :rodne_cislo,
        :jmeno,
        :prijmeni,
        TO_DATE(:datum_narozeni, 'YYYY-MM-DD'),
        :email,
        adresa_t(:ulice, :cislo_popisne, :mesto, :psc, :stat),
        {phone_sql},
        SYSDATE,
        :vernostni_karta
    )
)
        """
        with self.db.transaction():
            with self.db.cursor() as cursor:
                cursor.execute(sql, params)

    def update_visitor(self, visitor_id: str, payload: dict[str, Any]) -> None:
        phone_sql, phone_binds = self._phone_constructor(payload.get("telefony", ""))
        params = self._visitor_params(payload)
        params.pop("rodne_cislo", None)
        params["visitor_id"] = visitor_id
        params.update(phone_binds)
        sql = f"""
UPDATE navstevnik
   SET jmeno = :jmeno,
       prijmeni = :prijmeni,
       email = :email,
       datum_narozeni = TO_DATE(:datum_narozeni, 'YYYY-MM-DD'),
       vernostni_karta = :vernostni_karta,
       adresa = adresa_t(:ulice, :cislo_popisne, :mesto, :psc, :stat),
       telefony = {phone_sql}
 WHERE rodne_cislo = :visitor_id
        """
        with self.db.transaction():
            with self.db.cursor() as cursor:
                cursor.execute(sql, params)

    def delete_visitor(self, visitor_id: str) -> None:
        with self.db.transaction():
            with self.db.cursor() as cursor:
                params = {"visitor_id": visitor_id}
                cursor.execute(
                    """
DELETE FROM platba
 WHERE id_rezervace IN (
       SELECT id_rezervace
         FROM rezervace
        WHERE id_navstevnik = :visitor_id
 )
                    """,
                    params,
                )
                cursor.execute(
                    """
DELETE FROM platba
 WHERE id_predplatne IN (
       SELECT id_predplatne
         FROM predplatne
        WHERE id_navstevnik = :visitor_id
 )
                    """,
                    params,
                )
                cursor.execute("DELETE FROM hodnoceni WHERE id_navstevnik = :visitor_id", params)
                cursor.execute("DELETE FROM rezervace WHERE id_navstevnik = :visitor_id", params)
                cursor.execute("DELETE FROM predplatne WHERE id_navstevnik = :visitor_id", params)
                cursor.execute("DELETE FROM navstevnik WHERE rodne_cislo = :visitor_id", params)

    def list_performances(self) -> tuple[list[str], list[tuple[Any, ...]]]:
        sql = """
SELECT p.id_predstaveni,
       i.nazev,
       TO_CHAR(p.datum_cas, 'DD.MM.YYYY HH24:MI') AS termin,
       s.nazev AS sal,
       p.zakladni_cena,
       p.stav,
       COUNT(CASE WHEN r.stav <> 'ZRUSENA' THEN 1 END) AS rezervace
  FROM predstaveni p
  JOIN inscenace i ON i.id_inscenace = p.id_inscenace
  JOIN sal s ON s.id_sal = p.id_sal
  LEFT JOIN rezervace r ON r.id_predstaveni = p.id_predstaveni
 GROUP BY p.id_predstaveni, i.nazev, p.datum_cas, s.nazev, p.zakladni_cena, p.stav
 ORDER BY p.datum_cas
        """
        return self.db.fetch_all(sql)

    def get_performance_detail(self, performance_id: int) -> dict[str, Any] | None:
        sql = """
SELECT p.id_predstaveni,
       i.nazev,
       i.zanr,
       TO_CHAR(i.premiera, 'YYYY-MM-DD') AS premiera,
       i.delka_min,
       NVL(r.jmeno || ' ' || r.prijmeni, 'Neuveden') AS reziser,
       TO_CHAR(p.datum_cas, 'DD.MM.YYYY HH24:MI') AS termin,
       s.nazev AS sal,
       s.kapacita,
       p.zakladni_cena,
       p.stav,
       NVL(fn_obsazenost_pct(p.id_predstaveni), 0) AS obsazenost,
       i.popis
  FROM predstaveni p
  JOIN inscenace i ON i.id_inscenace = p.id_inscenace
  JOIN sal s ON s.id_sal = p.id_sal
  LEFT JOIN reziser r ON r.rodne_cislo = i.id_reziser
 WHERE p.id_predstaveni = :performance_id
        """
        columns, row = self.db.fetch_one(sql, {"performance_id": performance_id})
        if row is None:
            return None
        return self._as_record(columns, row)

    def get_performance_occupancy(self, performance_id: int) -> float:
        with self.db.cursor() as cursor:
            value = cursor.callfunc("fn_obsazenost_pct", float, [performance_id])
        return float(value or 0)

    def list_reservations(self) -> tuple[list[str], list[tuple[Any, ...]]]:
        sql = """
SELECT r.id_rezervace,
       n.jmeno || ' ' || n.prijmeni AS navstevnik,
       i.nazev || ' / ' || TO_CHAR(p.datum_cas, 'DD.MM.YYYY HH24:MI') AS predstaveni,
       s.rada || '-' || s.cislo AS sedadlo,
       r.stav,
       TO_CHAR(r.datum_rezerv, 'YYYY-MM-DD HH24:MI') AS datum_rezerv
  FROM rezervace r
  JOIN navstevnik n ON n.rodne_cislo = r.id_navstevnik
  JOIN predstaveni p ON p.id_predstaveni = r.id_predstaveni
  JOIN inscenace i ON i.id_inscenace = p.id_inscenace
  JOIN sedadlo s ON s.id_sedadlo = r.id_sedadlo
 ORDER BY r.id_rezervace DESC
        """
        return self.db.fetch_all(sql)

    def create_reservation(self, visitor_id: str, performance_id: int, seat_id: int) -> int:
        with self.db.transaction():
            with self.db.cursor() as cursor:
                out_id = cursor.var(int)
                cursor.callproc(
                    "pr_vytvorit_rezervaci",
                    [visitor_id, int(performance_id), int(seat_id), out_id],
                )
                reservation_id = out_id.getvalue()
        return int(reservation_id)

    def cancel_reservation(self, reservation_id: int) -> float:
        with self.db.transaction():
            with self.db.cursor() as cursor:
                returned_value = cursor.var(float)
                cursor.callproc("pr_zrusit_rezervaci", [int(reservation_id), returned_value])
                refunded = returned_value.getvalue()
        return float(refunded or 0)

    def run_query(self, query_key: str) -> tuple[StoredQuery, list[str], list[tuple[Any, ...]]]:
        query = QUERY_BY_KEY[query_key]
        columns, rows = self.db.fetch_all(query.sql)
        return query, columns, rows

    def get_revenue(self, production_id: int) -> float:
        with self.db.cursor() as cursor:
            value = cursor.callfunc("fn_trzba_inscenace", float, [int(production_id)])
        return float(value or 0)

    def get_top_visitors(self, limit: int) -> tuple[list[str], list[tuple[Any, ...]]]:
        driver = self.db.driver
        with self.db.cursor() as cursor:
            ref_cursor = cursor.callfunc("fn_top_navstevnici", driver.CURSOR, [int(limit)])
            columns = [description[0] for description in ref_cursor.description or []]
            rows = ref_cursor.fetchall()
            ref_cursor.close()
        return columns, rows

    def generate_seats(self, hall_id: int, rows: int, seats_per_row: int) -> None:
        with self.db.transaction():
            with self.db.cursor() as cursor:
                cursor.callproc(
                    "pr_generuj_sedadla",
                    [int(hall_id), int(rows), int(seats_per_row)],
                )

    def _visitor_params(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "rodne_cislo": payload["rodne_cislo"].strip(),
            "jmeno": payload["jmeno"].strip(),
            "prijmeni": payload["prijmeni"].strip(),
            "email": payload["email"].strip(),
            "datum_narozeni": payload["datum_narozeni"].strip(),
            "vernostni_karta": payload.get("vernostni_karta", "N").strip() or "N",
            "ulice": payload.get("ulice", "").strip(),
            "cislo_popisne": payload.get("cislo_popisne", "").strip(),
            "mesto": payload.get("mesto", "").strip(),
            "psc": payload.get("psc", "").strip(),
            "stat": payload.get("stat", "").strip(),
        }

    def _phone_constructor(self, raw_phones: str) -> tuple[str, dict[str, str]]:
        phones = [phone.strip() for phone in raw_phones.split(",") if phone.strip()]
        if not phones:
            return "telefony_t()", {}

        bind_names = []
        params: dict[str, str] = {}
        for index, phone in enumerate(phones, start=1):
            key = f"telefon_{index}"
            bind_names.append(f":{key}")
            params[key] = phone
        return f"telefony_t({', '.join(bind_names)})", params

    def _as_record(self, columns: list[str], row: tuple[Any, ...]) -> dict[str, Any]:
        return {column.lower(): value for column, value in zip(columns, row)}
