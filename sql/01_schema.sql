-- =============================================================================
-- TeatrumDB – Divadelní rezervační a předplatitelský systém
-- Soubor: 01_schema.sql
-- Obsah : Objektově-relační schéma (typy, kolekce, metody, tabulky, constraints)
-- =============================================================================

-- Pořadí úklidu: tabulky -> sekvence -> typy (opačně než závislosti).
-- Používáme USER_OBJECTS místo USER_TABLES, protože po neúplném rebuild
-- mohou v Oracle zůstat invalidní objektové tabulky, které USER_TABLES
-- nevrátí, ale jejich název stále blokuje nové CREATE TABLE.
DECLARE
   PROCEDURE drop_if_exists(p_sql VARCHAR2) IS
   BEGIN
      EXECUTE IMMEDIATE p_sql;
   EXCEPTION
      WHEN OTHERS THEN NULL;
   END drop_if_exists;
BEGIN
   FOR tr IN (SELECT trigger_name FROM user_triggers
              WHERE trigger_name IN (
                'TRG_SAL_BI','TRG_INSCENACE_BI','TRG_PRED_BI',
                'TRG_REZ_BI','TRG_PP_BI','TRG_PLATBA_BI','TRG_HODN_BI',
                'TRG_REZ_INTEGRITA','TRG_ROLE_NONTRANSFERABLE',
                'TRG_HODN_VALIDITA','TRG_PLATBA_STAV_REZ','TRG_PRED_VYPRODANO'))
   LOOP
      drop_if_exists('DROP TRIGGER '||tr.trigger_name);
   END LOOP;

   FOR p IN (SELECT object_name, object_type FROM user_objects
             WHERE object_type IN ('PROCEDURE','FUNCTION')
               AND object_name IN (
                'PR_VYTVORIT_REZERVACI','PR_ZRUSIT_REZERVACI',
                'PR_GENERUJ_SEDADLA','FN_TRZBA_INSCENACE',
                'FN_OBSAZENOST_PCT','FN_TOP_NAVSTEVNICI'))
   LOOP
      drop_if_exists('DROP '||p.object_type||' '||p.object_name);
   END LOOP;

   FOR t IN (SELECT object_name AS table_name FROM user_objects
             WHERE object_type = 'TABLE'
               AND object_name IN (
                'HODNOCENI','PLATBA','REZERVACE','PREDPLATNE',
                'ROLE','PREDSTAVENI','INSCENACE','SEDADLO','SAL',
                'HEREC','REZISER','UMELEC','ZAMESTNANEC','NAVSTEVNIK')
             ORDER BY CASE object_name
                WHEN 'HODNOCENI'   THEN 1
                WHEN 'PLATBA'      THEN 2
                WHEN 'REZERVACE'   THEN 3
                WHEN 'PREDPLATNE'  THEN 4
                WHEN 'ROLE'        THEN 5
                WHEN 'PREDSTAVENI' THEN 6
                WHEN 'INSCENACE'   THEN 7
                WHEN 'SEDADLO'     THEN 8
                WHEN 'SAL'         THEN 9
                WHEN 'HEREC'       THEN 10
                WHEN 'REZISER'     THEN 11
                WHEN 'ZAMESTNANEC' THEN 12
                WHEN 'NAVSTEVNIK'  THEN 13
                ELSE 99 END)
   LOOP
      drop_if_exists('DROP TABLE '||t.table_name||' CASCADE CONSTRAINTS PURGE');
   END LOOP;

   FOR s IN (SELECT sequence_name FROM user_sequences
             WHERE sequence_name IN (
                'SEQ_SAL','SEQ_INSCENACE','SEQ_PREDSTAVENI',
                'SEQ_PREDPLATNE','SEQ_REZERVACE','SEQ_PLATBA',
                'SEQ_HODNOCENI'))
   LOOP
      drop_if_exists('DROP SEQUENCE '||s.sequence_name);
   END LOOP;

   FOR o IN (SELECT type_name FROM user_types
             ORDER BY CASE type_name
                WHEN 'HEREC_T'        THEN 1
                WHEN 'REZISER_T'      THEN 2
                WHEN 'UMELEC_T'       THEN 3
                WHEN 'ZAMESTNANEC_T'  THEN 4
                WHEN 'NAVSTEVNIK_T'   THEN 5
                WHEN 'OSOBA_T'        THEN 6
                WHEN 'INSCENACE_UTIL_T' THEN 7
                WHEN 'ADRESA_T'       THEN 8
                WHEN 'TELEFONY_T'     THEN 9
                WHEN 'OCENENI_T'      THEN 10
                WHEN 'JAZYKY_T'       THEN 11
                WHEN 'ZANRY_T'        THEN 12
                ELSE 99 END)
   LOOP
      drop_if_exists('DROP TYPE '||o.type_name||' FORCE');
   END LOOP;
END;
/

-- =============================================================================
-- 1) KOLEKCE (pro vícehodnotové atributy)
-- =============================================================================

-- Telefonní čísla – NESTED TABLE (proměnná délka)
CREATE OR REPLACE TYPE telefony_t    AS TABLE OF VARCHAR2(20);
/
-- Ocenění umělce – VARRAY s maximem 10 položek
CREATE OR REPLACE TYPE oceneni_t     AS VARRAY(10) OF VARCHAR2(120);
/
-- Jazyky, kterými umělec mluví – VARRAY
CREATE OR REPLACE TYPE jazyky_t      AS VARRAY(6)  OF VARCHAR2(30);
/
-- Žánry, ve kterých herec vystupuje – VARRAY
CREATE OR REPLACE TYPE zanry_t       AS VARRAY(8)  OF VARCHAR2(40);
/

-- =============================================================================
-- 2) SLOŽENÝ ATRIBUT: Adresa
-- =============================================================================
CREATE OR REPLACE TYPE adresa_t AS OBJECT (
   ulice           VARCHAR2(80),
   cislo_popisne   VARCHAR2(12),
   mesto           VARCHAR2(60),
   psc             VARCHAR2(10),
   stat            VARCHAR2(40),

   MEMBER FUNCTION cela_adresa RETURN VARCHAR2
);
/
CREATE OR REPLACE TYPE BODY adresa_t AS
   MEMBER FUNCTION cela_adresa RETURN VARCHAR2 IS
   BEGIN
      RETURN ulice || ' ' || cislo_popisne || ', ' || psc || ' ' || mesto ||
             ', ' || stat;
   END cela_adresa;
END;
/

-- =============================================================================
-- 3) ISA HIERARCHIE – nadtyp OSOBA a jeho podtypy
--    (NOT FINAL + NOT INSTANTIABLE u Osoba_t ~ abstraktní supertyp)
-- =============================================================================

CREATE OR REPLACE TYPE osoba_t AS OBJECT (
   rodne_cislo     VARCHAR2(11),
   jmeno           VARCHAR2(40),
   prijmeni        VARCHAR2(60),
   datum_narozeni  DATE,
   email           VARCHAR2(120),
   adresa          adresa_t,
   telefony        telefony_t,

   -- ODVOZENÝ ATRIBUT implementovaný metodou: věk
   MEMBER FUNCTION vek RETURN NUMBER,
   MEMBER FUNCTION cele_jmeno RETURN VARCHAR2
) NOT FINAL NOT INSTANTIABLE;
/
CREATE OR REPLACE TYPE BODY osoba_t AS
   MEMBER FUNCTION vek RETURN NUMBER IS
   BEGIN
      IF datum_narozeni IS NULL THEN RETURN NULL; END IF;
      RETURN TRUNC( MONTHS_BETWEEN(SYSDATE, datum_narozeni) / 12 );
   END vek;

   MEMBER FUNCTION cele_jmeno RETURN VARCHAR2 IS
   BEGIN
      RETURN jmeno || ' ' || prijmeni;
   END cele_jmeno;
END;
/

-- ---- NAVSTEVNIK (ISA Osoba) --------------------------------------------------
CREATE OR REPLACE TYPE navstevnik_t UNDER osoba_t (
   prihlasen_od     DATE,
   vernostni_karta  CHAR(1),         -- 'A' / 'N'

   -- ODVOZENÝ ATRIBUT: počet provedených rezervací
   MEMBER FUNCTION pocet_rezervaci RETURN NUMBER,
   -- ODVOZENÝ ATRIBUT: součet plateb
   MEMBER FUNCTION celkem_utraceno RETURN NUMBER
) NOT FINAL;
/

-- ---- ZAMESTNANEC (ISA Osoba) -------------------------------------------------
CREATE OR REPLACE TYPE zamestnanec_t UNDER osoba_t (
   osobni_cislo     VARCHAR2(10),
   pozice           VARCHAR2(40),
   datum_nastupu    DATE,
   plat             NUMBER(9,2),

   MEMBER FUNCTION odpracovano_let RETURN NUMBER
) NOT FINAL;
/

-- ---- UMELEC (ISA Osoba) ------------------------------------------------------
CREATE OR REPLACE TYPE umelec_t UNDER osoba_t (
   umelecke_jmeno   VARCHAR2(80),
   bio              VARCHAR2(1000),
   oceneni          oceneni_t,
   jazyky           jazyky_t
) NOT FINAL;
/

-- ---- HEREC (ISA Umelec) ------------------------------------------------------
CREATE OR REPLACE TYPE herec_t UNDER umelec_t (
   hlavni_obor      VARCHAR2(40),   -- činohra / muzikál / opera …
   zanry            zanry_t,
   vyska_cm         NUMBER(3)
) FINAL;
/

-- ---- REZISER (ISA Umelec) ----------------------------------------------------
CREATE OR REPLACE TYPE reziser_t UNDER umelec_t (
   rezijni_styl     VARCHAR2(80),
   pocet_realizaci  NUMBER          -- přibližný počet režií
) FINAL;
/

-- =============================================================================
-- 4) TABULKY – objektové a relační
-- =============================================================================

-- Tabulky podtypů (nezávislé) – každý podtyp má vlastní tabulku
CREATE TABLE navstevnik   OF navstevnik_t (
   rodne_cislo     PRIMARY KEY,
   jmeno           NOT NULL,
   prijmeni        NOT NULL,
   email           NOT NULL CONSTRAINT uq_navstevnik_email UNIQUE,
   vernostni_karta DEFAULT 'N'
      CONSTRAINT chk_nav_vernostni CHECK (vernostni_karta IN ('A','N'))
) NESTED TABLE telefony STORE AS navstevnik_telefony;

CREATE TABLE zamestnanec  OF zamestnanec_t (
   rodne_cislo     PRIMARY KEY,
   jmeno           NOT NULL,
   prijmeni        NOT NULL,
   osobni_cislo    NOT NULL CONSTRAINT uq_zam_osobni UNIQUE,
   plat            CONSTRAINT chk_zam_plat CHECK (plat >= 0)
) NESTED TABLE telefony STORE AS zamestnanec_telefony;

CREATE TABLE herec        OF herec_t (
   rodne_cislo     PRIMARY KEY,
   jmeno           NOT NULL,
   prijmeni        NOT NULL,
   hlavni_obor     NOT NULL
) NESTED TABLE telefony STORE AS herec_telefony;

CREATE TABLE reziser      OF reziser_t (
   rodne_cislo     PRIMARY KEY,
   jmeno           NOT NULL,
   prijmeni        NOT NULL
) NESTED TABLE telefony STORE AS reziser_telefony;

-- ---- Sál ---------------------------------------------------------------------
CREATE SEQUENCE seq_sal START WITH 1;
CREATE TABLE sal (
   id_sal        NUMBER       CONSTRAINT pk_sal PRIMARY KEY,
   nazev         VARCHAR2(60) NOT NULL CONSTRAINT uq_sal_nazev UNIQUE,
   kapacita      NUMBER       NOT NULL
                 CONSTRAINT chk_sal_kapacita CHECK (kapacita BETWEEN 10 AND 2000),
   pocet_rad     NUMBER       NOT NULL
);

-- ---- Sedadlo (závislé na sále – slabá entita) --------------------------------
CREATE TABLE sedadlo (
   id_sedadlo    NUMBER        GENERATED ALWAYS AS IDENTITY
                 CONSTRAINT pk_sedadlo PRIMARY KEY,
   id_sal        NUMBER        NOT NULL
                 CONSTRAINT fk_sed_sal REFERENCES sal(id_sal),
   rada          NUMBER        NOT NULL,
   cislo         NUMBER        NOT NULL,
   typ           VARCHAR2(10)  DEFAULT 'STANDARD'
                 CONSTRAINT chk_sed_typ CHECK (typ IN ('STANDARD','VIP','BALKON')),
   CONSTRAINT uq_sedadlo UNIQUE (id_sal, rada, cislo)
);

-- ---- Inscenace ---------------------------------------------------------------
CREATE SEQUENCE seq_inscenace START WITH 1;
CREATE TABLE inscenace (
   id_inscenace  NUMBER        CONSTRAINT pk_inscenace PRIMARY KEY,
   nazev         VARCHAR2(120) NOT NULL,
   zanr          VARCHAR2(40)  NOT NULL,
   premiera      DATE          NOT NULL,
   delka_min     NUMBER        CONSTRAINT chk_ins_delka CHECK (delka_min BETWEEN 30 AND 600),
   popis         VARCHAR2(2000),
   id_reziser    VARCHAR2(11)
                 CONSTRAINT fk_ins_reziser REFERENCES reziser(rodne_cislo)
);

-- ---- Role (herec v inscenaci; NON-TRANSFERABLE viz trigger) -----------------
CREATE TABLE role (
   id_role       NUMBER        GENERATED ALWAYS AS IDENTITY
                 CONSTRAINT pk_role PRIMARY KEY,
   id_inscenace  NUMBER        NOT NULL
                 CONSTRAINT fk_role_ins REFERENCES inscenace(id_inscenace),
   id_herec      VARCHAR2(11)  NOT NULL
                 CONSTRAINT fk_role_herec REFERENCES herec(rodne_cislo),
   nazev_postavy VARCHAR2(80)  NOT NULL,
   hlavni_role   CHAR(1)       DEFAULT 'N'
                 CONSTRAINT chk_role_hlavni CHECK (hlavni_role IN ('A','N')),
   CONSTRAINT uq_role UNIQUE (id_inscenace, id_herec, nazev_postavy)
);

-- ---- Představení -------------------------------------------------------------
CREATE SEQUENCE seq_predstaveni START WITH 1;
CREATE TABLE predstaveni (
   id_predstaveni NUMBER       CONSTRAINT pk_pred PRIMARY KEY,
   id_inscenace   NUMBER       NOT NULL
                  CONSTRAINT fk_pred_ins REFERENCES inscenace(id_inscenace),
   id_sal         NUMBER       NOT NULL
                  CONSTRAINT fk_pred_sal REFERENCES sal(id_sal),
   datum_cas      TIMESTAMP    NOT NULL,
   zakladni_cena  NUMBER(8,2)  NOT NULL
                  CONSTRAINT chk_pred_cena CHECK (zakladni_cena > 0),
   stav           VARCHAR2(12) DEFAULT 'PLANOVANO'
                  CONSTRAINT chk_pred_stav CHECK (stav IN ('PLANOVANO','PRODEJ','VYPRODANO','ZRUSENO','PROBEHLO')),
   CONSTRAINT uq_pred UNIQUE (id_sal, datum_cas)
);

-- ---- Předplatné --------------------------------------------------------------
CREATE SEQUENCE seq_predplatne START WITH 1;
CREATE TABLE predplatne (
   id_predplatne  NUMBER        CONSTRAINT pk_predplatne PRIMARY KEY,
   id_navstevnik  VARCHAR2(11)  NOT NULL
                  CONSTRAINT fk_pp_nav REFERENCES navstevnik(rodne_cislo),
   typ            VARCHAR2(20)  NOT NULL
                  CONSTRAINT chk_pp_typ CHECK (typ IN ('SEZONNI','ROCNI','STUDENTSKE','SENIOR')),
   platnost_od    DATE          NOT NULL,
   platnost_do    DATE          NOT NULL,
   cena           NUMBER(8,2)   NOT NULL
                  CONSTRAINT chk_pp_cena CHECK (cena > 0),
   CONSTRAINT chk_pp_interval CHECK (platnost_do > platnost_od)
);

-- ---- Rezervace ---------------------------------------------------------------
CREATE SEQUENCE seq_rezervace START WITH 1;
CREATE TABLE rezervace (
   id_rezervace   NUMBER        CONSTRAINT pk_rezervace PRIMARY KEY,
   id_navstevnik  VARCHAR2(11)  NOT NULL
                  CONSTRAINT fk_rez_nav REFERENCES navstevnik(rodne_cislo),
   id_predstaveni NUMBER        NOT NULL
                  CONSTRAINT fk_rez_pred REFERENCES predstaveni(id_predstaveni),
   datum_rezerv   TIMESTAMP     DEFAULT SYSTIMESTAMP,
   stav           VARCHAR2(12)  DEFAULT 'VYTVORENA'
                  CONSTRAINT chk_rez_stav CHECK (stav IN ('VYTVORENA','ZAPLACENA','ZRUSENA','VYUZITA')),
   id_sedadlo     NUMBER        NOT NULL
                  CONSTRAINT fk_rez_sed REFERENCES sedadlo(id_sedadlo),
   CONSTRAINT uq_rez_sedadlo_pred UNIQUE (id_predstaveni, id_sedadlo) -- jedno sedadlo na představení pouze jednou
);

-- ---- Platba (ARC vztah: rezervace NEBO předplatné – přesně jedno z obou) ----
CREATE SEQUENCE seq_platba START WITH 1;
CREATE TABLE platba (
   id_platba      NUMBER        CONSTRAINT pk_platba PRIMARY KEY,
   datum_platby   TIMESTAMP     DEFAULT SYSTIMESTAMP,
   castka         NUMBER(9,2)   NOT NULL
                  CONSTRAINT chk_platba_castka CHECK (castka > 0),
   metoda         VARCHAR2(16)  NOT NULL
                  CONSTRAINT chk_platba_metoda CHECK (metoda IN ('HOTOVOST','KARTA','PREVOD','ONLINE')),
   -- ARC: právě jeden z následujících odkazů je vyplněn
   id_rezervace   NUMBER
                  CONSTRAINT fk_pl_rez REFERENCES rezervace(id_rezervace),
   id_predplatne  NUMBER
                  CONSTRAINT fk_pl_pp  REFERENCES predplatne(id_predplatne),
   CONSTRAINT chk_platba_arc CHECK (
       (id_rezervace  IS NOT NULL AND id_predplatne IS NULL)
    OR (id_rezervace  IS NULL     AND id_predplatne IS NOT NULL)
   )
);

-- ---- Hodnocení --------------------------------------------------------------
CREATE SEQUENCE seq_hodnoceni START WITH 1;
CREATE TABLE hodnoceni (
   id_hodnoceni   NUMBER        CONSTRAINT pk_hodn PRIMARY KEY,
   id_navstevnik  VARCHAR2(11)  NOT NULL
                  CONSTRAINT fk_hod_nav REFERENCES navstevnik(rodne_cislo),
   id_predstaveni NUMBER        NOT NULL
                  CONSTRAINT fk_hod_pred REFERENCES predstaveni(id_predstaveni),
   hodnoceni      NUMBER(1)     NOT NULL
                  CONSTRAINT chk_hod_hod CHECK (hodnoceni BETWEEN 1 AND 5),
   komentar       VARCHAR2(1000),
   datum          DATE          DEFAULT SYSDATE,
   CONSTRAINT uq_hod UNIQUE (id_navstevnik, id_predstaveni)
);

-- =============================================================================
-- 5) TĚLA METOD PRO NAVSTEVNIK_T A ZAMESTNANEC_T
--    (řešíme až po vytvoření tabulek, které metody používají)
-- =============================================================================
CREATE OR REPLACE TYPE BODY navstevnik_t AS
   MEMBER FUNCTION pocet_rezervaci RETURN NUMBER IS
      v NUMBER;
   BEGIN
      SELECT COUNT(*) INTO v
        FROM rezervace r WHERE r.id_navstevnik = SELF.rodne_cislo;
      RETURN v;
   END pocet_rezervaci;

   MEMBER FUNCTION celkem_utraceno RETURN NUMBER IS
      v NUMBER := 0;
   BEGIN
      SELECT COALESCE(SUM(p.castka),0) INTO v
        FROM platba p
        LEFT JOIN rezervace   r  ON r.id_rezervace   = p.id_rezervace
        LEFT JOIN predplatne  pp ON pp.id_predplatne = p.id_predplatne
       WHERE r.id_navstevnik  = SELF.rodne_cislo
          OR pp.id_navstevnik = SELF.rodne_cislo;
      RETURN v;
   END celkem_utraceno;
END;
/

CREATE OR REPLACE TYPE BODY zamestnanec_t AS
   MEMBER FUNCTION odpracovano_let RETURN NUMBER IS
   BEGIN
      IF datum_nastupu IS NULL THEN RETURN 0; END IF;
      RETURN TRUNC(MONTHS_BETWEEN(SYSDATE, datum_nastupu)/12);
   END odpracovano_let;
END;
/

-- =============================================================================
-- 6) SAMOSTATNÝ OBJEKT. TYP PRO "ODVOZENÉ" METODY NAD INSCENACÍ A PŘEDSTAVENÍM
--    Použit jako utilita (další tři metody nad daty)
-- =============================================================================
CREATE OR REPLACE TYPE inscenace_util_t AS OBJECT (
   id_inscenace NUMBER,
   MEMBER FUNCTION prumerne_hodnoceni RETURN NUMBER,
   MEMBER FUNCTION pocet_predstaveni  RETURN NUMBER,
   STATIC  FUNCTION volna_mista (p_id_pred NUMBER) RETURN NUMBER
);
/
CREATE OR REPLACE TYPE BODY inscenace_util_t AS
   MEMBER FUNCTION prumerne_hodnoceni RETURN NUMBER IS
      v NUMBER;
   BEGIN
      SELECT AVG(h.hodnoceni) INTO v
        FROM hodnoceni h
        JOIN predstaveni p ON p.id_predstaveni = h.id_predstaveni
       WHERE p.id_inscenace = SELF.id_inscenace;
      RETURN ROUND(NVL(v,0),2);
   END prumerne_hodnoceni;

   MEMBER FUNCTION pocet_predstaveni RETURN NUMBER IS
      v NUMBER;
   BEGIN
      SELECT COUNT(*) INTO v
        FROM predstaveni p
       WHERE p.id_inscenace = SELF.id_inscenace;
      RETURN v;
   END pocet_predstaveni;

   STATIC FUNCTION volna_mista (p_id_pred NUMBER) RETURN NUMBER IS
      v_kap   NUMBER;
      v_obs   NUMBER;
   BEGIN
      SELECT s.kapacita INTO v_kap
        FROM predstaveni p JOIN sal s ON s.id_sal = p.id_sal
       WHERE p.id_predstaveni = p_id_pred;

      SELECT COUNT(*) INTO v_obs
        FROM rezervace r
       WHERE r.id_predstaveni = p_id_pred
         AND r.stav <> 'ZRUSENA';

      RETURN v_kap - v_obs;
   END volna_mista;
END;
/

PROMPT ==============================================================
PROMPT  Schema TeatrumDB bylo úspěšně vytvořeno.
PROMPT ==============================================================
