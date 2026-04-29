-- =============================================================================
-- TeatrumDB – Procedury a funkce v jazyce PL/SQL
-- Soubor: 03_procedures.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- PROCEDURA 1 – Vytvoření nové rezervace s ověřením vstupních dat
--    Návstěvník, představení, sedadlo → vytvoří záznam a vrátí jeho ID.
--    Vyjímky z triggerů jsou pouze propuštěny dále do aplikace.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE pr_vytvorit_rezervaci (
   p_navstevnik   IN  VARCHAR2,
   p_predstaveni  IN  NUMBER,
   p_sedadlo      IN  NUMBER,
   p_id_rezervace OUT NUMBER
) IS
   v_existuje  NUMBER;
BEGIN
   -- Návštěvník musí existovat
   SELECT COUNT(*) INTO v_existuje
     FROM navstevnik WHERE rodne_cislo = p_navstevnik;
   IF v_existuje = 0 THEN
      RAISE_APPLICATION_ERROR(-20100,
         'Návštěvník s rodným číslem '||p_navstevnik||' neexistuje.');
   END IF;

   -- Sedadlo nesmí být na daném představení už obsazeno (kromě zrušených)
   SELECT COUNT(*) INTO v_existuje
     FROM rezervace
    WHERE id_predstaveni = p_predstaveni
      AND id_sedadlo     = p_sedadlo
      AND stav <> 'ZRUSENA';
   IF v_existuje > 0 THEN
      RAISE_APPLICATION_ERROR(-20101,
         'Vybrané sedadlo je na tomto představení již rezervováno.');
   END IF;

   INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo)
   VALUES (p_navstevnik, p_predstaveni, p_sedadlo)
   RETURNING id_rezervace INTO p_id_rezervace;
END pr_vytvorit_rezervaci;
/

-- -----------------------------------------------------------------------------
-- PROCEDURA 2 – Zrušení rezervace a případné vrácení peněz
--    Změní stav rezervace na ZRUSENA a vrátí součet již zaplacených částek.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE pr_zrusit_rezervaci (
   p_id_rezervace  IN  NUMBER,
   p_vraceno       OUT NUMBER
) IS
   v_stav  VARCHAR2(12);
BEGIN
   SELECT stav INTO v_stav FROM rezervace WHERE id_rezervace = p_id_rezervace
      FOR UPDATE;

   IF v_stav = 'ZRUSENA' THEN
      RAISE_APPLICATION_ERROR(-20110,'Rezervace je již zrušena.');
   ELSIF v_stav = 'VYUZITA' THEN
      RAISE_APPLICATION_ERROR(-20111,'Využitou rezervaci nelze zrušit.');
   END IF;

   SELECT COALESCE(SUM(castka),0) INTO p_vraceno
     FROM platba WHERE id_rezervace = p_id_rezervace;

   UPDATE rezervace
      SET stav = 'ZRUSENA'
    WHERE id_rezervace = p_id_rezervace;

   -- Jakmile se uvolní místo, představení už nemůže být vyprodáno
   UPDATE predstaveni p
      SET stav = 'PRODEJ'
    WHERE p.id_predstaveni = (
           SELECT id_predstaveni FROM rezervace
            WHERE id_rezervace = p_id_rezervace)
      AND p.stav = 'VYPRODANO';
END pr_zrusit_rezervaci;
/

-- -----------------------------------------------------------------------------
-- PROCEDURA 3 – Hromadné vytvoření sedadel pro celý sál
--   Generuje sedadla podle zadaného počtu řad a sedadel na řadu.
--   První dvě řady mají typ VIP, poslední řadu označíme jako BALKON.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE pr_generuj_sedadla (
   p_id_sal        IN NUMBER,
   p_pocet_rad     IN NUMBER,
   p_sedadel_rada  IN NUMBER
) IS
   v_typ VARCHAR2(10);
BEGIN
   FOR r IN 1 .. p_pocet_rad LOOP
      FOR c IN 1 .. p_sedadel_rada LOOP
         IF r <= 2 THEN
            v_typ := 'VIP';
         ELSIF r = p_pocet_rad THEN
            v_typ := 'BALKON';
         ELSE
            v_typ := 'STANDARD';
         END IF;
         BEGIN
            INSERT INTO sedadlo (id_sal, rada, cislo, typ)
            VALUES (p_id_sal, r, c, v_typ);
         EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL;
         END;
      END LOOP;
   END LOOP;
END pr_generuj_sedadla;
/

-- -----------------------------------------------------------------------------
-- FUNKCE 1 – Celková tržba za inscenaci
--   Agreguje platby za všechny rezervace všech jejích představení.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_trzba_inscenace (
   p_id_inscenace NUMBER
) RETURN NUMBER IS
   v_trzba NUMBER;
BEGIN
   SELECT COALESCE(SUM(pl.castka),0)
     INTO v_trzba
     FROM platba      pl
     JOIN rezervace   r  ON r.id_rezervace   = pl.id_rezervace
     JOIN predstaveni p  ON p.id_predstaveni = r.id_predstaveni
    WHERE p.id_inscenace = p_id_inscenace;

   RETURN v_trzba;
END fn_trzba_inscenace;
/

-- -----------------------------------------------------------------------------
-- FUNKCE 2 – Obsazenost představení v procentech
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_obsazenost_pct (
   p_id_predstaveni NUMBER
) RETURN NUMBER IS
   v_kap NUMBER; v_obs NUMBER;
BEGIN
   SELECT s.kapacita INTO v_kap
     FROM predstaveni p JOIN sal s ON s.id_sal = p.id_sal
    WHERE p.id_predstaveni = p_id_predstaveni;

   SELECT COUNT(*) INTO v_obs
     FROM rezervace
    WHERE id_predstaveni = p_id_predstaveni
      AND stav <> 'ZRUSENA';

   IF v_kap = 0 THEN RETURN 0; END IF;
   RETURN ROUND( v_obs / v_kap * 100, 2);
END fn_obsazenost_pct;
/

-- -----------------------------------------------------------------------------
-- FUNKCE 3 – Vrací REF CURSOR s TOP N návštěvníky podle útraty
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_top_navstevnici (
   p_top_n NUMBER DEFAULT 5
) RETURN SYS_REFCURSOR IS
   v_cur SYS_REFCURSOR;
BEGIN
   OPEN v_cur FOR
      SELECT * FROM (
         SELECT n.jmeno || ' ' || n.prijmeni AS navstevnik,
                TREAT(VALUE(n) AS navstevnik_t).celkem_utraceno() AS utraceno
           FROM navstevnik n
          ORDER BY 2 DESC NULLS LAST
      ) WHERE ROWNUM <= p_top_n;
   RETURN v_cur;
END fn_top_navstevnici;
/

PROMPT ==============================================================
PROMPT  Procedury a funkce TeatrumDB byly úspěšně vytvořeny.
PROMPT ==============================================================
