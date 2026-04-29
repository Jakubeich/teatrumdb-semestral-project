from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "TeatrumDB_dokumentace.pdf"


def register_fonts() -> tuple[str, str]:
    regular_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    regular = next((path for path in regular_candidates if Path(path).exists()), None)
    bold = next((path for path in bold_candidates if Path(path).exists()), regular)

    if not regular:
        return "Helvetica", "Helvetica-Bold"

    pdfmetrics.registerFont(TTFont("DocFont", regular))
    pdfmetrics.registerFont(TTFont("DocFontBold", bold))
    return "DocFont", "DocFontBold"


BASE_FONT, BOLD_FONT = register_fonts()


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCz",
            parent=styles["Title"],
            fontName=BOLD_FONT,
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1f2933"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubTitleCz",
            parent=styles["Normal"],
            fontName=BASE_FONT,
            fontSize=12,
            leading=17,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#3f4f5f"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverMetaCz",
            parent=styles["SubTitleCz"],
            leading=14,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1Cz",
            parent=styles["Heading1"],
            fontName=BOLD_FONT,
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#17324d"),
            spaceBefore=12,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Cz",
            parent=styles["Heading2"],
            fontName=BOLD_FONT,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#25394d"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCz",
            parent=styles["BodyText"],
            fontName=BASE_FONT,
            fontSize=9.7,
            leading=13.5,
            textColor=colors.HexColor("#202a34"),
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCz",
            parent=styles["BodyText"],
            fontName=BASE_FONT,
            fontSize=8.0,
            leading=10.3,
            textColor=colors.HexColor("#25313d"),
            spaceAfter=0,
            alignment=TA_LEFT,
            splitLongWords=True,
            wordWrap="CJK",
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallBoldCz",
            parent=styles["SmallCz"],
            fontName=BOLD_FONT,
            textColor=colors.HexColor("#1f2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeCz",
            parent=styles["Code"],
            fontName=BASE_FONT,
            fontSize=7.2,
            leading=9.5,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=3,
            spaceAfter=5,
        )
    )
    return styles


STYLES = build_styles()
STORY = []


def p(text: str, style: str = "BodyCz") -> None:
    STORY.append(Paragraph(text, STYLES[style]))


def h(text: str) -> None:
    STORY.append(Paragraph(text, STYLES["H1Cz"]))


def h2(text: str) -> None:
    STORY.append(Paragraph(text, STYLES["H2Cz"]))


def bullet(items: list[str]) -> None:
    for item in items:
        p("• " + item)


def cell(value: object, header: bool = False) -> Paragraph:
    style = "SmallBoldCz" if header else "SmallCz"
    text = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(text, STYLES[style])


def make_table(data: list[list[object]], widths: list[float], header_rows: int = 1) -> None:
    wrapped = [
        [cell(value, row_index < header_rows) for value in row]
        for row_index, row in enumerate(data)
    ]
    tbl = Table(wrapped, colWidths=widths, hAlign="LEFT", repeatRows=header_rows)
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), BASE_FONT),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bac5d0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header_rows:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, header_rows - 1), colors.HexColor("#e9eef4")),
                ("TEXTCOLOR", (0, 0), (-1, header_rows - 1), colors.HexColor("#1f2933")),
            ]
        )
    tbl.setStyle(TableStyle(commands))
    STORY.append(tbl)
    STORY.append(Spacer(1, 7))


def code(text: str) -> None:
    STORY.append(Preformatted(text.strip(), STYLES["CodeCz"], maxLineLength=95))


def image(path: Path, width: float, height: float) -> None:
    if path.exists():
        STORY.append(Image(str(path), width=width, height=height, kind="proportional"))


def add_content() -> None:
    STORY.append(Spacer(1, 1.4 * cm))
    STORY.append(Paragraph("TeatrumDB - divadelní databázová aplikace", STYLES["TitleCz"]))
    STORY.append(Paragraph("Semestrální projekt z předmětu Databázové systémy 1", STYLES["SubTitleCz"]))
    STORY.append(Spacer(1, 0.55 * cm))
    STORY.append(Paragraph("Autor: Jakub Mitrega", STYLES["CoverMetaCz"]))
    STORY.append(Paragraph("Číslo studenta: R24080", STYLES["CoverMetaCz"]))
    STORY.append(PageBreak())

    make_table(
        [
            ["Aplikační doména", "správa divadelního provozu, rezervací a předplatného"],
            ["Databázová platforma", "Oracle Database 23c Free, objektově-relační model"],
            ["Aplikace", "desktopová aplikace v Pythonu / Tkinter"],
        ],
        [4.2 * cm, 11.2 * cm],
        header_rows=0,
    )
    STORY.append(Spacer(1, 0.45 * cm))

    h("1. Popis aplikační domény")
    p(
        "Zvolenou aplikační doménou je správa divadelního provozu. Systém TeatrumDB eviduje "
        "inscenace, jednotlivá představení, sály, sedadla, návštěvníky, rezervace, platby, "
        "předplatné, recenze a umělecký personál. Aplikace podporuje běžnou agendu divadla "
        "i analytické dotazy nad návštěvností, tržbami, obsazeností a hodnocením."
    )
    p(
        "Doména je vhodná pro objektově-relační návrh, protože přirozeně obsahuje osoby se "
        "společnými vlastnostmi, specializace osob přes ISA hierarchii, složené atributy adresy, "
        "vícehodnotové atributy jako telefony, jazyky, žánry a ocenění, a také vztahy s "
        "integritními pravidly."
    )

    h("2. Konceptuální model")
    p(
        "Konceptuální model obsahuje více než deset entit a pokrývá požadované konstrukce: "
        "složené atributy, vícehodnotové atributy, odvoditelné atributy, ISA hierarchii, "
        "non-transferable vztah a ARC vztah."
    )
    make_table(
        [
            ["Entita", "Účel v modelu"],
            ["Osoba", "společný nadtyp pro osoby v systému"],
            ["Návštěvník", "zákazník s rezervacemi, platbami a předplatným"],
            ["Zaměstnanec", "interní osoba s pracovním zařazením"],
            ["Herec", "umělec obsazovaný do rolí"],
            ["Režisér", "autor inscenačního nastudování"],
            ["Inscenace", "divadelní titul se žánrem, premiérou a režisérem"],
            ["Představení", "konkrétní termín inscenace v sále"],
            ["Sál", "prostor s kapacitou a sedadly"],
            ["Sedadlo", "konkrétní místo v sále"],
            ["Rezervace", "vazba návštěvníka, představení a sedadla"],
            ["Platba", "platba za rezervaci nebo předplatné"],
            ["Předplatné", "balíček návštěvníka"],
            ["Hodnocení", "hodnocení/recenze konkrétního představení návštěvníkem"],
            ["Role", "obsazení herce v inscenaci"],
        ],
        [4.2 * cm, 11.2 * cm],
    )
    bullet(
        [
            "Složený atribut: adresa je modelována typem adresa_t s ulicí, číslem, městem, PSČ a státem.",
            "Vícehodnotové atributy: telefony osoby, jazyky a ocenění umělce a žánry herce.",
            "Odvoditelné atributy: věk osoby, celková útrata návštěvníka, průměrné hodnocení inscenace, volná místa představení.",
            "ISA hierarchie: osoba_t je nadtyp pro navstevnik_t, zamestnanec_t, herec_t a reziser_t.",
            "Non-transferable vztah: role je po vytvoření pevně svázána s hercem a inscenací; nelze změnit herce ani inscenaci.",
            "ARC vztah: platba se vztahuje buď k rezervaci, nebo k předplatnému, nikdy k oběma současně.",
        ]
    )
    image(ROOT / "images" / "conceptual.png", 15.5 * cm, 8.5 * cm)
    STORY.append(PageBreak())

    h("3. Model datových typů")
    p(
        "Objektově-relační transformace používá Oracle ADT, dědičnost objektových typů, metody "
        "objektů, kolekce nested table a pole VARRAY."
    )
    make_table(
        [
            ["Typ", "Popis"],
            ["adresa_t", "složený atribut adresy"],
            ["telefony_t", "nested table telefonních čísel"],
            ["jazyky_t", "VARRAY jazyků umělce"],
            ["zanry_t", "VARRAY žánrů, ve kterých herec vystupuje"],
            ["oceneni_t", "VARRAY ocenění umělce"],
            ["osoba_t", "NOT FINAL objektový nadtyp, metoda vek()"],
            ["navstevnik_t", "podtyp osoby, metoda celkem_utraceno()"],
            ["zamestnanec_t", "podtyp osoby pro interní pracovníky"],
            ["herec_t", "podtyp osoby, kolekce jazyků"],
            ["reziser_t", "podtyp osoby, kolekce ocenění"],
            ["inscenace_util_t", "pomocný objektový typ s metodami prumerne_hodnoceni(), pocet_predstaveni() a volna_mista()"],
        ],
        [4.2 * cm, 11.2 * cm],
    )
    h2("Ukázky metod objektových typů")
    code(
        """
MEMBER FUNCTION vek RETURN NUMBER
MEMBER FUNCTION celkem_utraceno RETURN NUMBER
MEMBER FUNCTION prumerne_hodnoceni RETURN NUMBER
MEMBER FUNCTION volna_mista RETURN NUMBER
MEMBER FUNCTION pocet_predstaveni RETURN NUMBER
        """
    )
    image(ROOT / "images" / "object_model.png", 15.5 * cm, 8.5 * cm)
    STORY.append(PageBreak())

    h("4. Objektově-relační datový model")
    p(
        "Schéma je vytvořeno pro Oracle. Objektové tabulky používají konstrukci OF typ_t, běžné "
        "relační tabulky doplňují vazební entity a transakční agendu. Kolekce jsou ukládány přes "
        "NESTED TABLE a VARRAY přímo v objektových a relačních strukturách."
    )
    make_table(
        [
            ["Soubor", "Obsah"],
            ["sql/01_schema.sql", "typy, tabulky, sekvence, objektové metody, relace"],
            ["sql/02_triggers.sql", "triggery pro doménovou a referenční integritu"],
            ["sql/03_procedures.sql", "PL/SQL procedury a funkce"],
            ["sql/04_data.sql", "testovací data"],
            ["sql/05_queries.sql", "povinné dotazy"],
        ],
        [4.2 * cm, 11.2 * cm],
    )
    image(ROOT / "images" / "relational_model.png", 15.5 * cm, 8.5 * cm)

    h("5. Integritní pravidla a triggery")
    p(
        "Projekt obsahuje více než tři triggery. Níže jsou hlavní pravidla, která chrání "
        "doménovou a referenční integritu nad rámec běžných omezení."
    )
    make_table(
        [
            ["Trigger", "Kontrolované pravidlo"],
            ["trg_rez_integrita", "rezervace musí odpovídat existujícímu budoucímu představení a sedadlu ve správném sále"],
            ["trg_role_nontransferable", "u role nelze po vytvoření změnit herce ani inscenaci"],
            ["trg_hodn_validita", "hodnocení lze vložit jen pro proběhlé představení s platnou rezervací"],
            ["trg_platba_stav_rez", "po vložení platby za rezervaci se rezervace přepne na stav ZAPLACENA"],
            ["trg_pred_vyprodano", "při naplnění kapacity se představení přepne na stav VYPRODANO"],
        ],
        [4.2 * cm, 11.2 * cm],
    )
    STORY.append(PageBreak())

    h("6. Procedury a funkce PL/SQL")
    p(
        "PL/SQL rozhraní je součástí aplikační funkcionality. Aplikace volá procedury pro "
        "rezervace, rušení rezervací a generování sedadel, a funkce pro tržby, obsazenost a "
        "TOP návštěvníky."
    )
    make_table(
        [
            ["Název", "Typ", "Funkcionalita"],
            ["pr_vytvorit_rezervaci", "procedura", "vytvoří rezervaci po kontrole návštěvníka a volného sedadla"],
            ["pr_zrusit_rezervaci", "procedura", "zruší rezervaci a vrátí součet zaplacených částek"],
            ["pr_generuj_sedadla", "procedura", "hromadně vytvoří sedadla pro sál"],
            ["fn_trzba_inscenace", "funkce", "spočítá celkovou tržbu za inscenaci"],
            ["fn_obsazenost_pct", "funkce", "vrátí procentuální obsazenost představení"],
            ["fn_top_navstevnici", "funkce", "vrací REF CURSOR s návštěvníky podle útraty"],
        ],
        [4.6 * cm, 2.4 * cm, 8.6 * cm],
    )
    code(
        """
BEGIN
  pr_vytvorit_rezervaci(:navstevnik, :predstaveni, :sedadlo, :id_rezervace);
  pr_zrusit_rezervaci(:id_rezervace, :vraceno);
END;

SELECT fn_trzba_inscenace(1) FROM dual;
SELECT fn_obsazenost_pct(6) FROM dual;
        """
    )

    h("7. Dotazy")
    p(
        "Soubor sql/05_queries.sql obsahuje dvanáct dotazů. Dotazy pokrývají projekci, selekci, "
        "spojení, kvantifikaci, ALL, ANY, IN, seskupení, negaci existenčního kvantifikátoru a "
        "práci s ADT včetně kolekcí."
    )
    queries = [
        ["1", "Návštěvníci starší 30 let se strukturovanou adresou", "projekce, selekce, metoda ADT vek()", "5 řádků"],
        ["2", "Inscenace režisérů s oceněním Thálie 2021", "spojení, kolekce VARRAY přes TABLE()", "2 řádky"],
        ["3", "Přehled inscenací s počtem představení a průměrným hodnocením", "GROUP BY, metoda ADT", "5 řádků"],
        ["4", "Návštěvníci s maximálním hodnocením", "ALL", "3 řádky"],
        ["5", "Herci pro režiséra činohry", "ANY, spojení", "4 řádky"],
        ["6", "Budoucí představení bez aktivních rezervací", "NOT EXISTS", "5 řádků"],
        ["7", "Návštěvníci, kteří navštívili každý žánr", "dvojitá negace, kvantifikace", "2 řádky"],
        ["8", "Platby a ARC vazba na rezervaci nebo předplatné", "LEFT JOIN, ARC", "18 řádků"],
        ["9", "Herci, telefony a jazyky", "ADT a kolekce", "5 řádků"],
        ["10", "Herci bez muzikálu", "IN, NOT EXISTS nad VARRAY", "3 řádky"],
        ["11", "Sály podle rezervací", "GROUP BY, poddotaz, ORDER BY, ROWNUM", "3 řádky"],
        ["12", "Využití inscenací", "metody ADT, agregace", "5 řádků"],
    ]
    make_table(
        [["#", "Přirozený popis", "Konstrukce", "Odpověď"]] + queries,
        [0.8 * cm, 6.3 * cm, 5.2 * cm, 3.1 * cm],
    )
    h2("Ukázka dotazu nad kolekcí VARRAY")
    code(
        """
SELECT i.nazev, i.zanr, r.jmeno || ' ' || r.prijmeni AS reziser
  FROM inscenace i
  JOIN reziser r ON r.rodne_cislo = i.id_reziser
 WHERE EXISTS (
       SELECT 1 FROM TABLE(r.oceneni) o
        WHERE o.COLUMN_VALUE = 'Thálie 2021'
 );
        """
    )
    STORY.append(PageBreak())

    h("8. Aplikace")
    p(
        "Desktopová aplikace je vytvořena v Pythonu pomocí Tkinter. Připojuje se k Oracle přes "
        "python-oracledb a používá konfigurační hodnoty ze souboru .env."
    )
    make_table(
        [
            ["Oblast", "Funkcionalita"],
            ["Připojení", "nastavení uživatele, hesla a DSN, automatické připojení při startu"],
            ["Přehled", "rychlé metriky, budoucí představení, TOP návštěvníci"],
            [
                "Návštěvníci",
                "vkládání, úprava a mazání návštěvníků včetně adresy, telefonů a navázaných záznamů",
            ],
            ["Představení", "zobrazení detailu, obsazenosti, ceny a stavu prodeje"],
            ["Rezervace", "volání procedur pr_vytvorit_rezervaci a pr_zrusit_rezervaci"],
            ["Dotazy", "spouštění katalogu SQL dotazů"],
            ["Procedury a funkce", "výpočet tržby, TOP návštěvníci a generování sedadel"],
        ],
        [4.2 * cm, 11.2 * cm],
    )
    code(
        """
cd TeatrumDB
./scripts/db-up.sh
./run_app.sh
        """
    )

    h("9. Ověření funkčnosti")
    p(
        "Projekt byl ověřen čistým vytvořením Oracle schématu, načtením testovacích dat, "
        "kontrolou invalid objektů, spuštěním souboru sql/05_queries.sql a spuštěním aplikačního "
        "katalogu dotazů. Všechny dotazy i PL/SQL smoke test doběhly bez chyby."
    )
    make_table(
        [
            ["Kontrola", "Výsledek"],
            ["Oracle objekty", "0 invalid objektů"],
            ["Testovací data", "6 návštěvníků, 14 rezervací, 18 plateb"],
            ["SQL dotazy", "12/12 úspěšně spuštěno"],
            ["Aplikační katalog", "12/12 dotazů vrací výsledky"],
            ["PL/SQL", "procedury a funkce ověřeny smoke testem"],
        ],
        [4.2 * cm, 11.2 * cm],
    )

    h("10. Závěr")
    p(
        "TeatrumDB splňuje požadavky zadání: obsahuje vhodnou aplikační doménu, konceptuální "
        "model s požadovanými konstrukcemi, objektově-relační transformaci pro Oracle, ADT s "
        "metodami, kolekce, triggery, PL/SQL procedury a funkce, testovací data, povinné dotazy "
        "a funkční aplikaci pro správu dat."
    )


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(BASE_FONT, 8)
    canvas.setFillColor(colors.HexColor("#5b6875"))
    canvas.drawString(1.7 * cm, 1.15 * cm, "TeatrumDB — semestrální projekt Databázové systémy 1")
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.15 * cm, f"Strana {doc.page}")
    canvas.restoreState()


def main() -> None:
    add_content()
    pdf = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.8 * cm,
        title="TeatrumDB dokumentace",
        author="Jakub Mitrega",
        subject="KIP/XDBS1 — Databázové systémy 1",
    )
    pdf.build(STORY, onFirstPage=on_page, onLaterPages=on_page)
    print(OUTPUT)


if __name__ == "__main__":
    main()
