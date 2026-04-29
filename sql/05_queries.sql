-- =============================================================================
-- TeatrumDB – Dotazy (min. 10)
-- Soubor: 05_queries.sql
--
-- Každý dotaz má:
--   • popis v přirozeném jazyce,
--   • seznam demonstrovaných konstrukcí SQL,
--   • vlastní příkaz SELECT.
-- =============================================================================

-- --------------------------------------------------------------------------
-- DOTAZ 1
-- Popis:   Vypiš jméno, věk (odvozený atribut přes metodu) a celý text
--          první adresy (složený atribut – metoda cela_adresa())
--          všech návštěvníků starších 30 let.
-- Konstrukce: PROJEKCE, SELEKCE, DOTAZ NA ADT (volání metody na objektu
--             a na jeho složeném atributu).
-- --------------------------------------------------------------------------
SELECT n.jmeno,
       n.prijmeni,
       TREAT(VALUE(n) AS navstevnik_t).vek()                AS vek,
       n.adresa.cela_adresa()                               AS adresa
  FROM navstevnik n
 WHERE TREAT(VALUE(n) AS navstevnik_t).vek() > 30;

-- --------------------------------------------------------------------------
-- DOTAZ 2
-- Popis:   Vypiš názvy inscenací režiséra, který má v kolekci ocenění
--          položku "Thálie 2021".
-- Konstrukce: SPOJENÍ (JOIN), DOTAZ NA KOLEKCI (TABLE nad VARRAY).
-- --------------------------------------------------------------------------
SELECT i.nazev,
       i.zanr,
       r.jmeno || ' ' || r.prijmeni AS reziser
  FROM inscenace i
  JOIN reziser   r  ON r.rodne_cislo = i.id_reziser
 WHERE EXISTS (
       SELECT 1
         FROM TABLE(r.oceneni) o
        WHERE o.COLUMN_VALUE = 'Thálie 2021');

-- --------------------------------------------------------------------------
-- DOTAZ 3
-- Popis:   Pro každou inscenaci vypiš počet představení a průměrné hodnocení.
-- Konstrukce: SPOJENÍ, SESKUPENÍ (GROUP BY), AGREGACE,
--             LEFT JOIN (inscenace bez hodnocení), PROJEKCE.
-- --------------------------------------------------------------------------
SELECT i.nazev,
       COUNT(DISTINCT p.id_predstaveni)  AS pocet_predstaveni,
       ROUND(AVG(h.hodnoceni),2)         AS prumer_hodnoceni
  FROM inscenace   i
  LEFT JOIN predstaveni p ON p.id_inscenace  = i.id_inscenace
  LEFT JOIN hodnoceni   h ON h.id_predstaveni = p.id_predstaveni
 GROUP BY i.id_inscenace, i.nazev
 ORDER BY prumer_hodnoceni DESC NULLS LAST;

-- --------------------------------------------------------------------------
-- DOTAZ 4
-- Popis:   Návštěvníci, kteří mají alespoň jedno maximální hodnocení
--          v porovnání se všemi hodnotami v tabulce hodnocení.
-- Konstrukce: ALL, PODDOTAZ, PROJEKCE, SELEKCE.
-- --------------------------------------------------------------------------
SELECT DISTINCT n.jmeno, n.prijmeni, h.hodnoceni
  FROM navstevnik n
  JOIN hodnoceni  h ON h.id_navstevnik = n.rodne_cislo
 WHERE h.hodnoceni >= ALL (SELECT hodnoceni FROM hodnoceni);

-- --------------------------------------------------------------------------
-- DOTAZ 5
-- Popis:   Herci, kteří hráli alespoň v jedné inscenaci, již režíroval
--          režisér s rodným číslem '550515/0001'.
-- Konstrukce: ANY, SPOJENÍ, PODDOTAZ.
-- --------------------------------------------------------------------------
SELECT DISTINCT h.jmeno, h.prijmeni, h.hlavni_obor
  FROM herec h
  JOIN role  r ON r.id_herec = h.rodne_cislo
 WHERE r.id_inscenace = ANY (
         SELECT id_inscenace
           FROM inscenace
          WHERE id_reziser = '550515/0001');

-- --------------------------------------------------------------------------
-- DOTAZ 6
-- Popis:   Představení, na která zatím NEEXISTUJE žádná rezervace
--          (budoucí představení bez rezervací).
-- Konstrukce: NEGACE EXISTENČNÍHO KVANTIFIKÁTORU (NOT EXISTS), SPOJENÍ.
-- --------------------------------------------------------------------------
SELECT p.id_predstaveni,
       i.nazev,
       p.datum_cas,
       s.nazev AS sal
  FROM predstaveni p
  JOIN inscenace   i ON i.id_inscenace = p.id_inscenace
  JOIN sal         s ON s.id_sal       = p.id_sal
 WHERE NOT EXISTS (
         SELECT 1 FROM rezervace r
          WHERE r.id_predstaveni = p.id_predstaveni
            AND r.stav <> 'ZRUSENA')
   AND p.datum_cas > SYSTIMESTAMP;

-- --------------------------------------------------------------------------
-- DOTAZ 7
-- Popis:   Návštěvníci, kteří mají rezervaci v každém žánru, ve kterém
--          divadlo hraje (univerzální kvantifikace – dvojitá negace
--          existence).
-- Konstrukce: UNIVERZÁLNÍ KVANTIFIKACE (NOT EXISTS NOT EXISTS), SPOJENÍ.
-- --------------------------------------------------------------------------
SELECT n.jmeno, n.prijmeni
  FROM navstevnik n
 WHERE NOT EXISTS (                         -- neexistuje žánr,
        SELECT DISTINCT i.zanr
          FROM inscenace i
         WHERE NOT EXISTS (                 -- který by návštěvník nerezervoval
                SELECT 1
                  FROM rezervace   r
                  JOIN predstaveni p  ON p.id_predstaveni = r.id_predstaveni
                  JOIN inscenace   ii ON ii.id_inscenace   = p.id_inscenace
                 WHERE r.id_navstevnik = n.rodne_cislo
                   AND ii.zanr        = i.zanr));

-- --------------------------------------------------------------------------
-- DOTAZ 8
-- Popis:   Detail platby s jejím „vlastníkem“ – návštěvníkem.
--          Ukazuje práci s ARC: JOIN se oběma větvemi (rezervace /
--          předplatné) a výběr pomocí COALESCE.
-- Konstrukce: SPOJENÍ (LEFT JOIN 2x), ARC vztah, projekce, funkce.
-- --------------------------------------------------------------------------
SELECT pl.id_platba,
       pl.datum_platby,
       pl.castka,
       pl.metoda,
       CASE
          WHEN pl.id_rezervace  IS NOT NULL THEN 'REZERVACE'
          WHEN pl.id_predplatne IS NOT NULL THEN 'PREDPLATNE'
       END AS druh_platby,
       COALESCE(n1.jmeno, n2.jmeno) || ' ' ||
       COALESCE(n1.prijmeni, n2.prijmeni) AS navstevnik
  FROM platba pl
  LEFT JOIN rezervace   r   ON r.id_rezervace   = pl.id_rezervace
  LEFT JOIN navstevnik  n1  ON n1.rodne_cislo   = r.id_navstevnik
  LEFT JOIN predplatne  pp  ON pp.id_predplatne = pl.id_predplatne
  LEFT JOIN navstevnik  n2  ON n2.rodne_cislo   = pp.id_navstevnik
 ORDER BY pl.datum_platby;

-- --------------------------------------------------------------------------
-- DOTAZ 9
-- Popis:   Seznam všech telefonních čísel herců (rozpletení nested table)
--          s informací, ve kterých jazycích herec mluví.
-- Konstrukce: TABLE() – rozpletení vícehodnotového atributu,
--             LISTAGG nad kolekcí jazyků.
-- --------------------------------------------------------------------------
SELECT h.jmeno,
       h.prijmeni,
       t.COLUMN_VALUE AS telefon,
       (SELECT LISTAGG(j.COLUMN_VALUE, ', ') WITHIN GROUP (ORDER BY j.COLUMN_VALUE)
          FROM TABLE(h.jazyky) j) AS jazyky
  FROM herec h,
       TABLE(h.telefony) t;

-- --------------------------------------------------------------------------
-- DOTAZ 10
-- Popis:   Herci, kteří ve svých žánrech (zanry – VARRAY) NEMAJÍ
--          "muzikál" a zároveň PATŘÍ do souboru hrajícího inscenaci
--          s ID v množině (1,3,5).
-- Konstrukce: IN, DOTAZ NA VARRAY přes TABLE(), PODDOTAZ, SPOJENÍ.
-- --------------------------------------------------------------------------
SELECT DISTINCT h.jmeno, h.prijmeni, h.hlavni_obor
  FROM herec h
  JOIN role  r ON r.id_herec = h.rodne_cislo
 WHERE r.id_inscenace IN (1,3,5)
   AND NOT EXISTS (
       SELECT 1
         FROM TABLE(h.zanry) z
        WHERE z.COLUMN_VALUE = 'muzikál');

-- --------------------------------------------------------------------------
-- DOTAZ 11 (bonus)
-- Popis:   TOP-3 nejvyužitější sály podle počtu aktivních rezervací.
--          Ukazuje poddotaz v FROM, seskupení a řazení.
-- Konstrukce: PROJEKCE, SESKUPENÍ, PODDOTAZ, ORDER, ROWNUM.
-- --------------------------------------------------------------------------
SELECT *
  FROM (SELECT s.nazev,
               s.kapacita,
               COUNT(r.id_rezervace) AS pocet_rez
          FROM sal s
          JOIN predstaveni p ON p.id_sal = s.id_sal
          LEFT JOIN rezervace r ON r.id_predstaveni = p.id_predstaveni
                              AND r.stav <> 'ZRUSENA'
         GROUP BY s.id_sal, s.nazev, s.kapacita
         ORDER BY pocet_rez DESC)
 WHERE ROWNUM <= 3;

-- --------------------------------------------------------------------------
-- DOTAZ 12 (bonus – ADT metody v SELECT listu)
-- Popis:   Pro každou inscenaci vypiš statické i členské metody objektu
--          inscenace_util_t: průměrné hodnocení, počet představení
--          a u prvního představení volná místa.
-- Konstrukce: VOLÁNÍ MEMBER/STATIC METOD, SPOJENÍ, PODDOTAZ.
-- --------------------------------------------------------------------------
SELECT i.nazev,
       inscenace_util_t(i.id_inscenace).prumerne_hodnoceni() AS prumer,
       inscenace_util_t(i.id_inscenace).pocet_predstaveni()  AS pocet_pred,
       (SELECT inscenace_util_t.volna_mista(MIN(p.id_predstaveni))
          FROM predstaveni p
         WHERE p.id_inscenace = i.id_inscenace
           AND p.datum_cas > SYSTIMESTAMP) AS volna_mista_pristi
  FROM inscenace i;
