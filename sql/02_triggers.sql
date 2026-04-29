-- =============================================================================
-- TeatrumDB – Triggery pro doménovou a referenční integritu
-- Soubor: 02_triggers.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TRIGGER 1 – Automatické doplnění primárních klíčů ze sekvencí
--             (jednotné zachování integrity napříč tabulkami)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_sal_bi
BEFORE INSERT ON sal FOR EACH ROW
BEGIN
   IF :NEW.id_sal IS NULL THEN
      :NEW.id_sal := seq_sal.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_inscenace_bi
BEFORE INSERT ON inscenace FOR EACH ROW
BEGIN
   IF :NEW.id_inscenace IS NULL THEN
      :NEW.id_inscenace := seq_inscenace.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_pred_bi
BEFORE INSERT ON predstaveni FOR EACH ROW
BEGIN
   IF :NEW.id_predstaveni IS NULL THEN
      :NEW.id_predstaveni := seq_predstaveni.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_rez_bi
BEFORE INSERT ON rezervace FOR EACH ROW
BEGIN
   IF :NEW.id_rezervace IS NULL THEN
      :NEW.id_rezervace := seq_rezervace.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_pp_bi
BEFORE INSERT ON predplatne FOR EACH ROW
BEGIN
   IF :NEW.id_predplatne IS NULL THEN
      :NEW.id_predplatne := seq_predplatne.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_platba_bi
BEFORE INSERT ON platba FOR EACH ROW
BEGIN
   IF :NEW.id_platba IS NULL THEN
      :NEW.id_platba := seq_platba.NEXTVAL;
   END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_hodn_bi
BEFORE INSERT ON hodnoceni FOR EACH ROW
BEGIN
   IF :NEW.id_hodnoceni IS NULL THEN
      :NEW.id_hodnoceni := seq_hodnoceni.NEXTVAL;
   END IF;
END;
/

-- =============================================================================
-- POVINNÉ TRIGGERY – integrita (min. 3)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TRIGGER A – Hlídá KAPACITU a VALIDITU rezervace
--   * Nelze rezervovat sedadlo z jiného sálu, než ve kterém se hraje představení
--   * Nelze rezervovat zrušené/proběhlé představení
--   * Nelze překročit kapacitu sálu
--   * Zajišťuje DOMÉNOVOU i REFERENČNÍ integritu
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_rez_integrita
BEFORE INSERT OR UPDATE OF id_predstaveni, id_sedadlo ON rezervace
FOR EACH ROW
DECLARE
   v_sal_pred   NUMBER;
   v_sal_sed    NUMBER;
   v_stav_pred  VARCHAR2(12);
   v_datum      TIMESTAMP;
   v_kapacita   NUMBER;
   v_obsazeno   NUMBER;
BEGIN
   -- 1) Zjištění sálu z představení
   SELECT p.id_sal, p.stav, p.datum_cas, s.kapacita
     INTO v_sal_pred, v_stav_pred, v_datum, v_kapacita
     FROM predstaveni p
     JOIN sal s ON s.id_sal = p.id_sal
    WHERE p.id_predstaveni = :NEW.id_predstaveni;

   -- 2) Zjištění sálu ze sedadla
   SELECT id_sal INTO v_sal_sed
     FROM sedadlo
    WHERE id_sedadlo = :NEW.id_sedadlo;

   -- 3) Kontrola, že sedadlo patří do sálu, kde se představení koná
   IF v_sal_sed <> v_sal_pred THEN
      RAISE_APPLICATION_ERROR(-20010,
         'Sedadlo nepatří do sálu, kde se představení koná.');
   END IF;

   -- 4) Nelze rezervovat zrušené představení
   IF v_stav_pred = 'ZRUSENO' THEN
      RAISE_APPLICATION_ERROR(-20011,
         'Rezervaci nelze vytvořit – představení je ZRUŠENO.');
   END IF;

   -- 5) Nelze rezervovat představení, které již proběhlo
   IF v_stav_pred = 'PROBEHLO' OR v_datum < SYSTIMESTAMP THEN
      RAISE_APPLICATION_ERROR(-20012,
         'Rezervaci nelze vytvořit – představení již proběhlo.');
   END IF;

   -- 6) Kontrola kapacity (jen u INSERTu nebo u změny představení)
   IF INSERTING OR (UPDATING AND :OLD.id_predstaveni <> :NEW.id_predstaveni) THEN
      IF INSERTING THEN
         SELECT COUNT(*) INTO v_obsazeno
           FROM rezervace
          WHERE id_predstaveni = :NEW.id_predstaveni
            AND stav <> 'ZRUSENA';
      ELSE
         SELECT COUNT(*) INTO v_obsazeno
           FROM rezervace
          WHERE id_predstaveni = :NEW.id_predstaveni
            AND stav <> 'ZRUSENA'
            AND id_rezervace <> :OLD.id_rezervace;
      END IF;

      IF v_obsazeno >= v_kapacita THEN
         RAISE_APPLICATION_ERROR(-20013,
            'Kapacita sálu pro toto představení je vyčerpána.');
      END IF;
   END IF;
END;
/

-- -----------------------------------------------------------------------------
-- TRIGGER B – NON-TRANSFERABLE: přiřazení ROLE (herec v inscenaci)
--   Role je nepřenositelná – po vytvoření NELZE změnit herce ani inscenaci.
--   Lze pouze smazat a vytvořit novou.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_role_nontransferable
BEFORE UPDATE OF id_inscenace, id_herec ON role
FOR EACH ROW
BEGIN
   IF :OLD.id_inscenace <> :NEW.id_inscenace OR
      :OLD.id_herec     <> :NEW.id_herec     THEN
      RAISE_APPLICATION_ERROR(-20020,
         'Role je nepřenositelná – nelze měnit herce ani inscenaci. '||
         'Vytvořte novou roli a původní smažte.');
   END IF;
END;
/

-- -----------------------------------------------------------------------------
-- TRIGGER C – Validita HODNOCENÍ
--   * Hodnotit lze jen představení, které již proběhlo
--   * Hodnotit může jen návštěvník, který měl na dané představení rezervaci
--     ve stavu ZAPLACENA / VYUZITA
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_hodn_validita
BEFORE INSERT OR UPDATE ON hodnoceni
FOR EACH ROW
DECLARE
   v_datum    TIMESTAMP;
   v_cnt      NUMBER;
BEGIN
   SELECT datum_cas INTO v_datum
     FROM predstaveni
    WHERE id_predstaveni = :NEW.id_predstaveni;

   IF v_datum > SYSTIMESTAMP THEN
      RAISE_APPLICATION_ERROR(-20030,
         'Hodnotit lze jen představení, které již proběhlo.');
   END IF;

   SELECT COUNT(*) INTO v_cnt
     FROM rezervace
    WHERE id_navstevnik  = :NEW.id_navstevnik
      AND id_predstaveni = :NEW.id_predstaveni
      AND stav IN ('ZAPLACENA','VYUZITA');

   IF v_cnt = 0 THEN
      RAISE_APPLICATION_ERROR(-20031,
         'Hodnotit lze jen představení, na kterém měl návštěvník '||
         'zaplacenou/využitou rezervaci.');
   END IF;
END;
/

-- -----------------------------------------------------------------------------
-- TRIGGER D – Automatické přepnutí stavu REZERVACE při připsání platby
--   (demonstruje souhru platby a rezervace v rámci ARC vztahu)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_platba_stav_rez
AFTER INSERT ON platba
FOR EACH ROW
WHEN (NEW.id_rezervace IS NOT NULL)
BEGIN
   UPDATE rezervace
      SET stav = 'ZAPLACENA'
    WHERE id_rezervace = :NEW.id_rezervace
      AND stav = 'VYTVORENA';
END;
/

-- -----------------------------------------------------------------------------
-- TRIGGER E – Automatické přepnutí stavu PŘEDSTAVENÍ na VYPRODANO
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_pred_vyprodano
FOR INSERT OR UPDATE OF id_predstaveni, stav ON rezervace
COMPOUND TRIGGER
   TYPE t_predstaveni_ids IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
   g_predstaveni_ids t_predstaveni_ids;
   g_count           PLS_INTEGER := 0;

   PROCEDURE add_predstaveni_id(p_id NUMBER) IS
   BEGIN
      IF p_id IS NULL THEN
         RETURN;
      END IF;

      FOR i IN 1 .. g_count LOOP
         IF g_predstaveni_ids(i) = p_id THEN
            RETURN;
         END IF;
      END LOOP;

      g_count := g_count + 1;
      g_predstaveni_ids(g_count) := p_id;
   END add_predstaveni_id;

   AFTER EACH ROW IS
   BEGIN
      add_predstaveni_id(:NEW.id_predstaveni);

      IF UPDATING AND NVL(:OLD.id_predstaveni, -1) <> NVL(:NEW.id_predstaveni, -1) THEN
         add_predstaveni_id(:OLD.id_predstaveni);
      END IF;
   END AFTER EACH ROW;

   AFTER STATEMENT IS
      v_kapacita   NUMBER;
      v_obsazeno   NUMBER;
   BEGIN
      FOR i IN 1 .. g_count LOOP
         SELECT s.kapacita INTO v_kapacita
           FROM predstaveni p
           JOIN sal s ON s.id_sal = p.id_sal
          WHERE p.id_predstaveni = g_predstaveni_ids(i);

         SELECT COUNT(*) INTO v_obsazeno
           FROM rezervace
          WHERE id_predstaveni = g_predstaveni_ids(i)
            AND stav <> 'ZRUSENA';

         IF v_obsazeno >= v_kapacita THEN
            UPDATE predstaveni
               SET stav = 'VYPRODANO'
             WHERE id_predstaveni = g_predstaveni_ids(i)
               AND stav <> 'ZRUSENO';
         END IF;
      END LOOP;
   END AFTER STATEMENT;
END;
/

PROMPT ==============================================================
PROMPT  Triggery TeatrumDB byly úspěšně vytvořeny.
PROMPT ==============================================================
