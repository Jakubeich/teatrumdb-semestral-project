# TeatrumDB

TeatrumDB je semestrální databázový projekt pro evidenci divadelního provozu. Modeluje návštěvníky, zaměstnance, herce, režiséry, inscenace, představení, sály, sedadla, rezervace, platby, předplatné a hodnocení.

Projekt obsahuje objektově-relační schéma pro Oracle Database, ukázková data, PL/SQL triggery, procedury a funkce, demonstrační SQL dotazy a jednoduchou desktopovou aplikaci v Pythonu.

## Hlavní funkce

- objektově-relační návrh nad Oracle Database,
- ISA hierarchie osob: návštěvník, zaměstnanec, herec a režisér,
- složený atribut adresy a vícehodnotové atributy přes kolekce,
- rezervace sedadel na konkrétní představení,
- evidence plateb za rezervace nebo předplatné,
- databázové triggery pro kontrolu integrity,
- PL/SQL procedury pro vytvoření a zrušení rezervace,
- PL/SQL funkce pro tržby, obsazenost a TOP návštěvníky,
- sada demonstračních SQL dotazů,
- desktopová aplikace pro práci s daty a spouštění dotazů.

## Použité technologie

- Oracle Database Free v Dockeru,
- SQL a PL/SQL,
- Python,
- Tkinter,
- knihovna `oracledb`,
- Docker Compose.

## Struktura projektu

```text
TeatrumDB/
├── app/                    # Python desktopová aplikace
├── docker/init/            # Inicializace databázového uživatele a schématu
├── images/                 # Diagramy modelů
├── presentation/           # Prezentace a poznámky
├── scripts/                # Pomocné skripty pro DB a aplikaci
├── sql/                    # SQL a PL/SQL část projektu
├── docker-compose.yml      # Oracle kontejner
├── run_app.sh              # Spuštění aplikace
└── README.md
```

## Databázová část

SQL skripty jsou rozdělené podle účelu:

- `sql/01_schema.sql` vytváří objektové typy, kolekce, tabulky, sekvence a metody.
- `sql/02_triggers.sql` obsahuje triggery pro automatické ID a integritní pravidla.
- `sql/03_procedures.sql` obsahuje procedury a funkce v PL/SQL.
- `sql/04_data.sql` vkládá demonstrační data.
- `sql/05_queries.sql` obsahuje demonstrační dotazy.

Schéma používá například:

- objektový typ `osoba_t` a jeho podtypy,
- typ `adresa_t` pro složený atribut adresy,
- kolekce `telefony_t`, `oceneni_t`, `jazyky_t` a `zanry_t`,
- ARC vztah u platby, která patří buď k rezervaci, nebo k předplatnému,
- non-transferable vztah u role herce v inscenaci,
- metody jako `vek()`, `cela_adresa()`, `celkem_utraceno()` nebo `volna_mista()`.

## Aplikační část

Aplikace je jednoduché desktopové rozhraní v Pythonu. Po připojení k databázi umožňuje:

- zobrazit základní přehled a metriky,
- spravovat návštěvníky,
- prohlížet představení a obsazenost,
- vytvářet a rušit rezervace,
- spouštět připravené SQL dotazy,
- volat vybrané PL/SQL procedury a funkce.

Vstupní soubor aplikace je `app/app.py`. Nejjednodušší spuštění zajišťuje skript `run_app.sh`.

## Požadavky

Před spuštěním je potřeba mít nainstalované:

- Docker a Docker Compose,
- Python 3,
- Tkinter pro Python,
- internetové připojení při prvním stažení Docker image a Python závislostí.

## Nastavení prostředí

Projekt používá soubor `.env` v kořenové složce. Minimální konfigurace může vypadat takto:

```env
ORACLE_PASSWORD=oracle_admin_password
APP_USER=teatrum
APP_USER_PASSWORD=teatrum_password

ORA_USER=teatrum
ORA_PASS=teatrum_password
ORA_DSN=localhost:1521/FREEPDB1
TEATRUMDB_AUTO_CONNECT=1
```

Proměnné `APP_USER` a `APP_USER_PASSWORD` se používají při inicializaci Oracle kontejneru. Proměnné `ORA_USER`, `ORA_PASS` a `ORA_DSN` používá Python aplikace pro připojení k databázi.

## Spuštění projektu

Nejjednodušší postup:

```bash
./run_app.sh
```

Skript provede tyto kroky:

1. načte `.env`,
2. vytvoří lokální virtuální prostředí `.venv`, pokud ještě neexistuje,
3. nainstaluje závislosti z `app/requirements.txt`,
4. spustí Oracle databázi v Dockeru,
5. otevře desktopovou aplikaci TeatrumDB.

Pokud má databáze už běžet samostatně a aplikace ji nemá startovat:

```bash
TEATRUMDB_START_DB=0 ./run_app.sh
```

## Práce s databází

Spuštění nebo ověření Oracle kontejneru:

```bash
./scripts/db-up.sh
```

Zastavení databáze a smazání perzistentních dat:

```bash
./scripts/db-reset.sh
```

Po resetu se při dalším startu databáze znovu načte schéma, triggery, procedury a demonstrační data ze složky `sql/`.

## Diagramy a dokumentace

Ve složce `images/` jsou uložené diagramy:

- `images/conceptual.png` - konceptuální model,
- `images/object_model.png` - objektový model,
- `images/relational_model.png` - relační model.

Součástí repozitáře je také:

- `TeatrumDB_dokumentace.pdf` - vygenerovaná dokumentace,
- `presentation/TeatrumDB_prezentace.pptx` - prezentace projektu,
- `presentation/poznamky_k_prezentaci.md` - poznámky k prezentaci.

## Ukázkové dotazy

Soubor `sql/05_queries.sql` obsahuje dotazy demonstrující:

- projekci a selekci,
- spojení tabulek,
- agregace a seskupení,
- práci s objektovými metodami,
- práci s kolekcemi přes `TABLE()`,
- `ALL`, `ANY`, `IN`,
- existenční a univerzální kvantifikaci přes `NOT EXISTS`,
- práci s ARC vztahem u plateb.

Stejné dotazy je možné spustit i z desktopové aplikace v části `Dotazy`.

## Poznámky

Databáze běží na adrese `localhost:1521/FREEPDB1`. Při prvním spuštění může start Oracle kontejneru trvat několik minut, protože se stahuje image a inicializuje databázové schéma.
