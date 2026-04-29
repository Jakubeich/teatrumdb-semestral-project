from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoredQuery:
    key: str
    title: str
    description: str
    sql: str


STORED_QUERIES = [
    StoredQuery(
        key="visitors_over_30",
        title="Navstevnici nad 30 let",
        description="ADT metody nad objektovym typem navstevnik_t a adresa_t.",
        sql="""
SELECT n.jmeno,
       n.prijmeni,
       TREAT(VALUE(n) AS navstevnik_t).vek() AS vek,
       n.adresa.cela_adresa() AS adresa
  FROM navstevnik n
 WHERE TREAT(VALUE(n) AS navstevnik_t).vek() > 30
        """.strip(),
    ),
    StoredQuery(
        key="productions_by_awarded_director",
        title="Inscenace rezisera s oceneni 'Thalie 2021'",
        description="Vyuziti kolekce oceneni pres TABLE() nad VARRAY.",
        sql="""
SELECT i.nazev,
       i.zanr,
       r.jmeno || ' ' || r.prijmeni AS reziser
  FROM inscenace i
  JOIN reziser r ON r.rodne_cislo = i.id_reziser
 WHERE EXISTS (
       SELECT 1
         FROM TABLE(r.oceneni) o
        WHERE o.COLUMN_VALUE = 'Thálie 2021'
 )
        """.strip(),
    ),
    StoredQuery(
        key="production_overview",
        title="Prehled inscenaci a hodnoceni",
        description="Seskupeni, pocet predstaveni a prumerne hodnoceni.",
        sql="""
SELECT i.nazev,
       COUNT(DISTINCT p.id_predstaveni) AS pocet_predstaveni,
       ROUND(AVG(h.hodnoceni), 2) AS prumer
  FROM inscenace i
  LEFT JOIN predstaveni p ON p.id_inscenace = i.id_inscenace
  LEFT JOIN hodnoceni h ON h.id_predstaveni = p.id_predstaveni
 GROUP BY i.id_inscenace, i.nazev
 ORDER BY prumer DESC NULLS LAST
        """.strip(),
    ),
    StoredQuery(
        key="max_rating_visitors",
        title="Navstevnici s maximalnim hodnocenim",
        description="Konstrukce ALL nad vsemi hodnotami v tabulce hodnoceni.",
        sql="""
SELECT DISTINCT n.jmeno,
       n.prijmeni,
       h.hodnoceni
  FROM navstevnik n
  JOIN hodnoceni h ON h.id_navstevnik = n.rodne_cislo
 WHERE h.hodnoceni >= ALL (SELECT hodnoceni FROM hodnoceni)
        """.strip(),
    ),
    StoredQuery(
        key="actors_for_director",
        title="Herci v inscenacich rezisera 550515/0001",
        description="Pouziti ANY na mnozine id inscenaci daneho rezisera.",
        sql="""
SELECT DISTINCT h.jmeno,
       h.prijmeni,
       h.hlavni_obor
  FROM herec h
  JOIN role r ON r.id_herec = h.rodne_cislo
 WHERE r.id_inscenace = ANY (
       SELECT id_inscenace
         FROM inscenace
        WHERE id_reziser = '550515/0001'
 )
        """.strip(),
    ),
    StoredQuery(
        key="future_without_reservations",
        title="Budouci predstaveni bez rezervaci",
        description="Negace existencniho kvantifikatoru pomoci NOT EXISTS.",
        sql="""
SELECT p.id_predstaveni,
       i.nazev,
       p.datum_cas,
       s.nazev AS sal
  FROM predstaveni p
  JOIN inscenace i ON i.id_inscenace = p.id_inscenace
  JOIN sal s ON s.id_sal = p.id_sal
 WHERE NOT EXISTS (
       SELECT 1
         FROM rezervace r
        WHERE r.id_predstaveni = p.id_predstaveni
          AND r.stav <> 'ZRUSENA'
 )
   AND p.datum_cas > SYSTIMESTAMP
        """.strip(),
    ),
    StoredQuery(
        key="visitor_every_genre",
        title="Navstevnik s rezervaci v kazdem zanru",
        description="Univerzalni kvantifikace zapsana dvojitym NOT EXISTS.",
        sql="""
SELECT n.jmeno,
       n.prijmeni
  FROM navstevnik n
 WHERE NOT EXISTS (
       SELECT DISTINCT i.zanr
         FROM inscenace i
        WHERE NOT EXISTS (
              SELECT 1
                FROM rezervace r
                JOIN predstaveni p ON p.id_predstaveni = r.id_predstaveni
                JOIN inscenace ii ON ii.id_inscenace = p.id_inscenace
               WHERE r.id_navstevnik = n.rodne_cislo
                 AND ii.zanr = i.zanr
        )
 )
        """.strip(),
    ),
    StoredQuery(
        key="payments_arc",
        title="Platby a ARC vztah",
        description="Platba smeruje bud do rezervace, nebo do predplatneho.",
        sql="""
SELECT pl.id_platba,
       pl.datum_platby,
       pl.castka,
       pl.metoda,
       CASE
           WHEN pl.id_rezervace IS NOT NULL THEN 'REZERVACE'
           WHEN pl.id_predplatne IS NOT NULL THEN 'PREDPLATNE'
       END AS druh,
       COALESCE(n1.jmeno, n2.jmeno) || ' ' || COALESCE(n1.prijmeni, n2.prijmeni) AS navstevnik
  FROM platba pl
  LEFT JOIN rezervace r ON r.id_rezervace = pl.id_rezervace
  LEFT JOIN navstevnik n1 ON n1.rodne_cislo = r.id_navstevnik
  LEFT JOIN predplatne pp ON pp.id_predplatne = pl.id_predplatne
  LEFT JOIN navstevnik n2 ON n2.rodne_cislo = pp.id_navstevnik
 ORDER BY pl.datum_platby
        """.strip(),
    ),
    StoredQuery(
        key="actors_phones_languages",
        title="Telefony hercu a seznam jazyku",
        description="Prace s kolekcemi pres TABLE() a LISTAGG.",
        sql="""
SELECT h.jmeno,
       h.prijmeni,
       t.COLUMN_VALUE AS telefon,
       (
           SELECT LISTAGG(j.COLUMN_VALUE, ', ') WITHIN GROUP (ORDER BY j.COLUMN_VALUE)
             FROM TABLE(h.jazyky) j
       ) AS jazyky
  FROM herec h,
       TABLE(h.telefony) t
        """.strip(),
    ),
    StoredQuery(
        key="actors_without_musical",
        title="Herci bez zanru muzikal v inscenacich 1, 3, 5",
        description="Kombinace IN a NOT EXISTS nad kolekci zanru pres TABLE().",
        sql="""
SELECT DISTINCT h.jmeno,
       h.prijmeni,
       h.hlavni_obor
  FROM herec h
  JOIN role r ON r.id_herec = h.rodne_cislo
 WHERE r.id_inscenace IN (1, 3, 5)
   AND NOT EXISTS (
       SELECT 1
         FROM TABLE(h.zanry) z
        WHERE z.COLUMN_VALUE = 'muzikál'
 )
        """.strip(),
    ),
    StoredQuery(
        key="top_halls",
        title="Top 3 nejvyuzitejsi saly",
        description="Seskupeni nad saly a vyber tri nejvytizenejsich.",
        sql="""
SELECT *
  FROM (
        SELECT s.nazev,
               s.kapacita,
               COUNT(r.id_rezervace) AS rez_cnt
          FROM sal s
          JOIN predstaveni p ON p.id_sal = s.id_sal
          LEFT JOIN rezervace r ON r.id_predstaveni = p.id_predstaveni
                               AND r.stav <> 'ZRUSENA'
         GROUP BY s.id_sal, s.nazev, s.kapacita
         ORDER BY rez_cnt DESC
  )
 WHERE ROWNUM <= 3
        """.strip(),
    ),
    StoredQuery(
        key="inscenace_util",
        title="ADT utility nad inscenaci",
        description="Volani clenskych metod nad pomocnym objektovym typem.",
        sql="""
SELECT i.nazev,
       inscenace_util_t(i.id_inscenace).prumerne_hodnoceni() AS prumer,
       inscenace_util_t(i.id_inscenace).pocet_predstaveni() AS pocet_pred,
       (
           SELECT inscenace_util_t.volna_mista(MIN(p.id_predstaveni))
             FROM predstaveni p
            WHERE p.id_inscenace = i.id_inscenace
              AND p.datum_cas > SYSTIMESTAMP
       ) AS volna_mista_pristi
  FROM inscenace i
        """.strip(),
    ),
]


QUERY_BY_KEY = {query.key: query for query in STORED_QUERIES}
