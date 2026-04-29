-- =============================================================================
-- TeatrumDB – Testovací data
-- Soubor: 04_data.sql
-- =============================================================================

SET DEFINE OFF;

-- ---------------------------------------------------------------------------
-- SÁLY
-- ---------------------------------------------------------------------------
INSERT INTO sal (id_sal, nazev, kapacita, pocet_rad)
VALUES (seq_sal.NEXTVAL, 'Velké jeviště', 60, 6);
INSERT INTO sal (id_sal, nazev, kapacita, pocet_rad)
VALUES (seq_sal.NEXTVAL, 'Komorní scéna', 24, 4);
INSERT INTO sal (id_sal, nazev, kapacita, pocet_rad)
VALUES (seq_sal.NEXTVAL, 'Studio M', 30, 5);

-- Sedadla – vygenerujeme procedurou
BEGIN
   pr_generuj_sedadla(1, 6, 10);   -- Velké jeviště 60
   pr_generuj_sedadla(2, 4, 6);    -- Komorní       24
   pr_generuj_sedadla(3, 5, 6);    -- Studio        30
END;
/

-- ---------------------------------------------------------------------------
-- NÁVŠTĚVNÍCI (objektové INSERT)
-- ---------------------------------------------------------------------------
INSERT INTO navstevnik VALUES (
   navstevnik_t('800101/1234','Jan','Novák',
                DATE '1980-01-01','jan.novak@seznam.cz',
                adresa_t('Masarykova','12','Ostrava','70200','CZ'),
                telefony_t('+420604111222','+420731999888'),
                DATE '2023-05-10','A'));

INSERT INTO navstevnik VALUES (
   navstevnik_t('905512/4567','Petra','Svobodová',
                DATE '1990-05-12','petra.svob@email.cz',
                adresa_t('Nádražní','45','Praha','11000','CZ'),
                telefony_t('+420602555111'),
                DATE '2022-09-01','A'));

INSERT INTO navstevnik VALUES (
   navstevnik_t('850810/8899','Tomáš','Dvořák',
                DATE '1985-08-10','dvorak.t@mail.cz',
                adresa_t('Lidická','3','Brno','60200','CZ'),
                telefony_t('+420777888000'),
                DATE '2024-01-15','N'));

INSERT INTO navstevnik VALUES (
   navstevnik_t('750303/2020','Eva','Veselá',
                DATE '1975-03-03','vesela@gmail.com',
                adresa_t('Havlíčkovo nám.','1','Havířov','73601','CZ'),
                telefony_t('+420606121212'),
                DATE '2021-02-20','A'));

INSERT INTO navstevnik VALUES (
   navstevnik_t('020914/8080','Karolína','Malá',
                DATE '2002-09-14','malakarolina@studenti.cz',
                adresa_t('Studentská','10','Olomouc','77900','CZ'),
                telefony_t('+420773000001','+420773000002'),
                DATE '2024-10-01','N'));

INSERT INTO navstevnik VALUES (
   navstevnik_t('681212/3355','Martin','Pokorný',
                DATE '1968-12-12','m.pokorny@firma.cz',
                adresa_t('Hlavní','200','Ostrava','70800','CZ'),
                telefony_t('+420604343434'),
                DATE '2020-10-10','A'));

-- ---------------------------------------------------------------------------
-- ZAMĚSTNANCI
-- ---------------------------------------------------------------------------
INSERT INTO zamestnanec VALUES (
   zamestnanec_t('770202/1111','Jana','Černá',
                 DATE '1977-02-02','cerna@teatrum.cz',
                 adresa_t('Divadelní','1','Ostrava','70200','CZ'),
                 telefony_t('+420777000111'),
                 'Z0001','Pokladní',DATE '2015-06-01',32000));

INSERT INTO zamestnanec VALUES (
   zamestnanec_t('820404/2222','David','Horák',
                 DATE '1982-04-04','horak@teatrum.cz',
                 adresa_t('Divadelní','1','Ostrava','70200','CZ'),
                 telefony_t('+420777000222'),
                 'Z0002','Dramaturg',DATE '2018-09-01',48000));

INSERT INTO zamestnanec VALUES (
   zamestnanec_t('660606/3333','Milena','Králová',
                 DATE '1966-06-06','kralova@teatrum.cz',
                 adresa_t('Divadelní','1','Ostrava','70200','CZ'),
                 telefony_t('+420777000333'),
                 'Z0003','Ředitelka',DATE '2010-01-01',95000));

-- ---------------------------------------------------------------------------
-- REŽISÉŘI
-- ---------------------------------------------------------------------------
INSERT INTO reziser VALUES (
   reziser_t('550515/0001','Pavel','Kohout',
             DATE '1955-05-15','kohout@reziser.cz',
             adresa_t('Umělecká','5','Praha','11000','CZ'),
             telefony_t('+420603111000'),
             'Pavel Kohout','Uznávaný režisér činoherních inscenací.',
             oceneni_t('Thálie 2010','Cena Alfréda Radoka 2015'),
             jazyky_t('čeština','angličtina','němčina'),
             'realistický', 28));

INSERT INTO reziser VALUES (
   reziser_t('720720/0002','Klára','Dufková',
             DATE '1972-07-20','dufkova@reziser.cz',
             adresa_t('Muzejní','20','Brno','60200','CZ'),
             telefony_t('+420605222000'),
             'Klára Dufková','Režie opery a muzikálu.',
             oceneni_t('Opera Award 2019','Thálie 2021','Český lev 2022'),
             jazyky_t('čeština','italština','angličtina','francouzština'),
             'expresivní', 15));

-- ---------------------------------------------------------------------------
-- HERCI
-- ---------------------------------------------------------------------------
INSERT INTO herec VALUES (
   herec_t('800808/8001','Marek','Vondráček',
           DATE '1980-08-08','vondracek@teatrum.cz',
           adresa_t('Divadelní','7','Ostrava','70200','CZ'),
           telefony_t('+420608111001'),
           'Marek Vondráček','Charakterní herec.',
           oceneni_t('Thálie 2018'),
           jazyky_t('čeština','angličtina'),
           'činohra', zanry_t('činohra','film','dabing'), 183));

INSERT INTO herec VALUES (
   herec_t('851010/8002','Lenka','Krásná',
           DATE '1985-10-10','krasna@teatrum.cz',
           adresa_t('Divadelní','7','Ostrava','70200','CZ'),
           telefony_t('+420608111002'),
           'Lenka Krásná','Muzikálová herečka.',
           oceneni_t('Thálie 2020','Cena diváků 2022'),
           jazyky_t('čeština','angličtina','francouzština'),
           'muzikál', zanry_t('muzikál','činohra'), 168));

INSERT INTO herec VALUES (
   herec_t('900101/8003','Roman','Černý',
           DATE '1990-01-01','cerny.h@teatrum.cz',
           adresa_t('Divadelní','7','Ostrava','70200','CZ'),
           telefony_t('+420608111003'),
           'Roman Černý','Mladý herec.',
           oceneni_t(),
           jazyky_t('čeština','angličtina','polština'),
           'činohra', zanry_t('činohra'), 178));

INSERT INTO herec VALUES (
   herec_t('950202/8004','Nikol','Bílá',
           DATE '1995-02-02','bila@teatrum.cz',
           adresa_t('Studentská','3','Ostrava','70200','CZ'),
           telefony_t('+420608111004'),
           'Nikol Bílá','Talentovaná mladá herečka.',
           oceneni_t('Objev roku 2022'),
           jazyky_t('čeština','angličtina','španělština'),
           'muzikál', zanry_t('muzikál','opera'), 165));

INSERT INTO herec VALUES (
   herec_t('700303/8005','Ivo','Starý',
           DATE '1970-03-03','stary@teatrum.cz',
           adresa_t('Husova','55','Ostrava','70200','CZ'),
           telefony_t('+420608111005'),
           'Ivo Starý','Zkušený charakterní herec.',
           oceneni_t('Thálie 2005','Thálie 2015','Cena diváků 2018','Za celoživotní dílo 2023'),
           jazyky_t('čeština','ruština','němčina'),
           'činohra', zanry_t('činohra','dabing'), 180));

-- ---------------------------------------------------------------------------
-- INSCENACE
-- ---------------------------------------------------------------------------
INSERT INTO inscenace (id_inscenace, nazev, zanr, premiera, delka_min, popis, id_reziser)
VALUES (seq_inscenace.NEXTVAL,'Hamlet','činohra',DATE '2024-09-10',180,
        'Klasická tragédie W. Shakespeara v moderním pojetí.','550515/0001');
INSERT INTO inscenace (id_inscenace, nazev, zanr, premiera, delka_min, popis, id_reziser)
VALUES (seq_inscenace.NEXTVAL,'Cats','muzikál',DATE '2024-11-20',135,
        'Slavný muzikál o kočkách – balada, tanec a hudba.','720720/0002');
INSERT INTO inscenace (id_inscenace, nazev, zanr, premiera, delka_min, popis, id_reziser)
VALUES (seq_inscenace.NEXTVAL,'Revizor','činohra',DATE '2025-02-14',150,
        'Gogolova satira na byrokracii a korupci.','550515/0001');
INSERT INTO inscenace (id_inscenace, nazev, zanr, premiera, delka_min, popis, id_reziser)
VALUES (seq_inscenace.NEXTVAL,'La Traviata','opera',DATE '2025-05-05',170,
        'Verdiho opera o lásce a oběti.','720720/0002');
INSERT INTO inscenace (id_inscenace, nazev, zanr, premiera, delka_min, popis, id_reziser)
VALUES (seq_inscenace.NEXTVAL,'Maryša','činohra',DATE '2025-10-01',140,
        'Klasické české drama bratří Mrštíků.','550515/0001');

-- ---------------------------------------------------------------------------
-- ROLE (herec v inscenaci)
-- ---------------------------------------------------------------------------
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (1,'800808/8001','Hamlet','A');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (1,'900101/8003','Horatio','N');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (1,'700303/8005','Claudius','N');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (1,'950202/8004','Ofélie','A');

INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (2,'851010/8002','Grizabella','A');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (2,'950202/8004','Jemima','N');

INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (3,'800808/8001','Chlestakov','A');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (3,'700303/8005','Horodnický','N');

INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (4,'851010/8002','Violetta','A');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (4,'900101/8003','Alfredo','A');

INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (5,'950202/8004','Maryša','A');
INSERT INTO role (id_inscenace, id_herec, nazev_postavy, hlavni_role)
VALUES (5,'800808/8001','Franc','N');

-- ---------------------------------------------------------------------------
-- PŘEDSTAVENÍ (některá v minulosti, některá v budoucnosti)
-- ---------------------------------------------------------------------------
-- V minulosti (pro možnost hodnocení)
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 1, 1, TIMESTAMP '2025-11-15 19:00:00', 450, 'PROBEHLO');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 2, 1, TIMESTAMP '2025-12-01 19:00:00', 550, 'PROBEHLO');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 3, 2, TIMESTAMP '2025-12-20 18:30:00', 390, 'PROBEHLO');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 1, 1, TIMESTAMP '2026-01-10 19:00:00', 450, 'PROBEHLO');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 4, 1, TIMESTAMP '2026-02-14 19:00:00', 620, 'PROBEHLO');

-- V budoucnosti (pro možnost rezervací)
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 2, 1, TIMESTAMP '2026-05-15 19:00:00', 550, 'PRODEJ');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 5, 3, TIMESTAMP '2026-06-01 19:00:00', 420, 'PRODEJ');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 1, 2, TIMESTAMP '2026-06-20 19:00:00', 480, 'PRODEJ');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 3, 3, TIMESTAMP '2026-07-05 19:00:00', 390, 'PRODEJ');
INSERT INTO predstaveni (id_predstaveni, id_inscenace, id_sal, datum_cas, zakladni_cena, stav)
VALUES (seq_predstaveni.NEXTVAL, 4, 1, TIMESTAMP '2026-09-15 19:00:00', 620, 'PRODEJ');

-- ---------------------------------------------------------------------------
-- REZERVACE + PLATBY (pro minulá představení)
-- Důležité: triggery pro "budoucí datum" a "stav=VYTVORENA" mají být splněny,
-- proto nejprve měníme stav těchto představení a po vložení vrátíme PROBEHLO.
-- ---------------------------------------------------------------------------
UPDATE predstaveni SET stav='PRODEJ' WHERE stav='PROBEHLO';
-- !!! kvůli triggeru trg_rez_integrita (kontroluje budoucnost)
-- dočasně tuto kontrolu u minulých představení obejdeme: INSERT s výjimkou
-- Pro jednoduchost demonstrace využijeme alternativní cestu: vložíme rezervace
-- PŘED povolením triggeru pomocí přímého INSERTu s tichým obejitím:
ALTER TRIGGER trg_rez_integrita DISABLE;

-- Představení 1 (Hamlet 2025-11-15)  – 3 rezervace
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('800101/1234', 1, 1, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('905512/4567', 1, 2, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('750303/2020', 1, 3, 'VYUZITA');

-- Představení 2 (Cats) – 4 rezervace
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('800101/1234', 2, 1, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('905512/4567', 2, 2, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('850810/8899', 2, 3, 'VYUZITA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('681212/3355', 2, 4, 'ZAPLACENA');

-- Představení 3 (Revizor) – 2 rezervace
-- Sedadla 61 a 62 jsou první dvě sedadla v sále 2.
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('800101/1234', 3, 61, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('750303/2020', 3, 62, 'ZAPLACENA');

-- Představení 4 (Hamlet 2026-01-10) – 2 rezervace
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('905512/4567', 4, 1, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('681212/3355', 4, 2, 'VYUZITA');

-- Představení 5 (La Traviata) – 3 rezervace
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('800101/1234', 5, 1, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('750303/2020', 5, 2, 'ZAPLACENA');
INSERT INTO rezervace (id_navstevnik, id_predstaveni, id_sedadlo, stav)
VALUES ('681212/3355', 5, 3, 'ZAPLACENA');

ALTER TRIGGER trg_rez_integrita ENABLE;

-- Vrácení stavu proběhlých představení
UPDATE predstaveni
   SET stav = 'PROBEHLO'
 WHERE datum_cas < SYSTIMESTAMP;

-- ---------------------------------------------------------------------------
-- PLATBY (za rezervace) – ARC – na straně rezervace
-- ---------------------------------------------------------------------------
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (1,450,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (2,450,'ONLINE');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (3,450,'HOTOVOST');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (4,550,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (5,550,'ONLINE');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (6,550,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (7,550,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (8,390,'PREVOD');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (9,390,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (10,450,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (11,450,'ONLINE');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (12,620,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (13,620,'KARTA');
INSERT INTO platba (id_rezervace, castka, metoda) VALUES (14,620,'ONLINE');

-- ---------------------------------------------------------------------------
-- PŘEDPLATNÉ + PLATBY (ARC – druhá strana)
-- ---------------------------------------------------------------------------
INSERT INTO predplatne (id_navstevnik, typ, platnost_od, platnost_do, cena)
VALUES ('800101/1234','ROCNI',DATE '2025-09-01',DATE '2026-08-31',4500);
INSERT INTO predplatne (id_navstevnik, typ, platnost_od, platnost_do, cena)
VALUES ('750303/2020','SEZONNI',DATE '2025-09-01',DATE '2026-02-28',2800);
INSERT INTO predplatne (id_navstevnik, typ, platnost_od, platnost_do, cena)
VALUES ('020914/8080','STUDENTSKE',DATE '2025-10-01',DATE '2026-06-30',1500);
INSERT INTO predplatne (id_navstevnik, typ, platnost_od, platnost_do, cena)
VALUES ('681212/3355','SENIOR',DATE '2025-09-01',DATE '2026-08-31',2400);

INSERT INTO platba (id_predplatne, castka, metoda) VALUES (1,4500,'PREVOD');
INSERT INTO platba (id_predplatne, castka, metoda) VALUES (2,2800,'KARTA');
INSERT INTO platba (id_predplatne, castka, metoda) VALUES (3,1500,'ONLINE');
INSERT INTO platba (id_predplatne, castka, metoda) VALUES (4,2400,'KARTA');

-- ---------------------------------------------------------------------------
-- HODNOCENÍ (jen na proběhlá představení, s povolenou rezervací)
-- ---------------------------------------------------------------------------
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('800101/1234', 1, 5, 'Skvělý Hamlet, moderní a přitom věrný textu.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('905512/4567', 1, 4, 'Velmi povedené, jen délka nás vyčerpala.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('750303/2020', 1, 5, 'Luxus. Rozhodně doporučuji.');

INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('800101/1234', 2, 4, 'Cats ve velkém stylu, hudba překrásná.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('905512/4567', 2, 5, 'Dokonalé!');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('850810/8899', 2, 3, 'Choreografie super, ale zpěv občas nevyrovnaný.');

INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('800101/1234', 3, 4, 'Revizor nezestárnul.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('750303/2020', 3, 3, 'Fajn, ale dramaturgicky slabší.');

INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('905512/4567', 4, 5, 'Druhé shlédnutí, ještě lepší.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('681212/3355', 4, 4, 'Solidní zážitek.');

INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('800101/1234', 5, 5, 'La Traviata – velkolepé.');
INSERT INTO hodnoceni (id_navstevnik, id_predstaveni, hodnoceni, komentar)
VALUES ('750303/2020', 5, 5, 'Přesně kvůli tomuhle chodíme do divadla.');

COMMIT;
PROMPT ==============================================================
PROMPT  Testovací data byla úspěšně vložena.
PROMPT ==============================================================
