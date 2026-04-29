import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);

function loadPptxgen() {
  try {
    return require("pptxgenjs");
  } catch {
    return require(
      "/Users/jakubmitrega/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pptxgenjs",
    );
  }
}

const pptxgen = loadPptxgen();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "presentation");
const previewDir = path.join(outDir, "previews");
const pptxPath = path.join(outDir, "TeatrumDB_prezentace.pptx");
const notesPath = path.join(outDir, "poznamky_k_prezentaci.md");

const nodeModules =
  process.env.NODE_MODULES ||
  "/Users/jakubmitrega/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";

const artifactModulePath = path.join(nodeModules, "@oai/artifact-tool/dist/artifact_tool.mjs");
const skiaModulePath = path.join(nodeModules, "@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs");

const COLORS = {
  bg: "F8F6F0",
  ink: "172330",
  muted: "546170",
  line: "C9D1D8",
  soft: "ECEFF1",
  red: "B63A3A",
  redDark: "7C1F25",
  gold: "D8A62A",
  teal: "2F8F83",
  green: "2E7D57",
  blue: "2A5D84",
  white: "FFFFFF",
};

const SLIDE_NOTES = [
  {
    title: "TeatrumDB",
    body: `Dobrý den, představím projekt TeatrumDB.

Je to databázová aplikace pro divadelní provoz. Vybral jsem si divadlo proto, že se tam přirozeně potkávají lidé, představení, sedadla, rezervace i platby.

Snažil jsem se, aby to nebyla jen izolovaná evidence, ale aby jednotlivé části dávaly dohromady jeden použitelný celek.`,
  },
  {
    title: "Aplikační doména: provoz divadla",
    body: `Začal jsem aplikační doménou, tedy provozem divadla.

V modelu jsou návštěvníci, umělecký personál, inscenace, představení, sály, sedadla, rezervace, platby i recenze.

Základní tok je jednoduchý: divadlo má inscenaci, ta se hraje v konkrétním termínu, návštěvník si vybere sedadlo, vytvoří rezervaci a ta se následně zaplatí.

Na téhle doméně mi přišlo dobré, že má provozní část i obchodní část a zároveň z ní jdou dělat smysluplné přehledy.`,
  },
  {
    title: "Konceptuální model",
    body: `Konceptuální model vychází z toho divadelního toku.

Model má víc než deset entit. Základ tvoří osoby, tedy návštěvník, zaměstnanec, herec a režisér. Vedle toho jsou provozní entity jako inscenace, představení, sál, sedadlo, rezervace, platba, předplatné, recenze a role.

Model využívá několik výraznějších databázových konstrukcí. ISA hierarchie je řešená přes obecnou osobu a její specializace. ARC vztah je u platby, která patří buď k rezervaci, nebo k předplatnému. Non-transferable vztah je u rezervace, protože rezervaci nelze převést na jiného návštěvníka.

Model obsahuje i složené atributy, například adresu, a vícehodnotové atributy, například telefony, jazyky, žánry a ocenění.`,
  },
  {
    title: "Objektové typy, metody a kolekce",
    body: `Po konceptuálním modelu jsem část návrhu převedl do objektových typů v Oracle.

V Oracle jsou vytvořené objektové typy. Například osoba_t je nadtyp, ze kterého vychází navstevnik_t, zamestnanec_t, herec_t a reziser_t.

Složený atribut adresa je samostatný typ adresa_t. Vícehodnotové atributy jsou implementované kolekcemi: telefony a jazyky jako nested table, žánry a ocenění jako VARRAY.

Odvoditelné atributy nejsou uložené jako běžné sloupce, ale jako metody objektových typů. Příklady jsou vek(), celkem_utraceno(), prumerne_hodnoceni() a volna_mista(). Díky tomu zůstává výpočet hodnot přímo u dat, kterých se týká.`,
  },
  {
    title: "Objektově-relační schéma v Oracle",
    body: `Tento slide ukazuje fyzický objektově-relační model v Oracle.

Schéma je rozdělené do několika SQL souborů. První soubor vytváří typy, tabulky, sekvence a objektové metody. Druhý soubor obsahuje triggery. Třetí soubor obsahuje procedury a funkce. Čtvrtý soubor vkládá testovací data a pátý obsahuje demonstrační dotazy.

Projekt kombinuje objektové tabulky a klasické relační vazby. Objektové prvky používám hlavně u osob, adres a metod. Provozní vazby jako rezervace, role nebo platby jsou modelované relačně.

Celé schéma se dá vytvořit v Oracle kontejneru přes Docker.`,
  },
  {
    title: "Integrita a PL/SQL funkcionalita",
    body: `Databáze tady nehlídá jen běžné cizí klíče.

Triggery hlídají doménovou a referenční integritu nad rámec běžných cizích klíčů. Například rezervace musí být na existující budoucí představení a na sedadlo ve správném sále. Další trigger hlídá, že rezervaci nelze převést na jiného návštěvníka. U plateb se kontroluje ARC pravidlo, tedy že platba patří buď k rezervaci, nebo k předplatnému, ne k oběma najednou.

PL/SQL část obsahuje procedury pro vytvoření rezervace, zrušení rezervace a generování sedadel. Funkce potom počítají tržbu inscenace, obsazenost představení a TOP návštěvníky podle útraty.

Tyto procedury a funkce nejsou jen ve schématu, ale aplikace je skutečně volá.`,
  },
  {
    title: "Demonstrační SQL dotazy",
    body: `Dotazy jsem bral jako způsob, jak ukázat, co se z těch dat dá získat.

Je jich dvanáct a týkají se návštěvníků, obsazenosti, hodnocení, rolí, plateb i práce s objektovými atributy.

Vedle běžných spojení a agregací jsou tam i dotazy s ALL, ANY, IN a NOT EXISTS. Příklad práce s objektovým typem je volání metody vek() nebo adresa.cela_adresa(). Příklad práce s kolekcí je TABLE(r.oceneni) nebo TABLE(h.zanry).`,
  },
  {
    title: "Desktopová aplikace",
    body: `Aplikační část je jednoduché desktopové rozhraní v Pythonu.

Aplikace je vytvořená v Pythonu pomocí Tkinteru a připojuje se k Oracle databázi. Má několik částí: připojení, přehled, návštěvníky, rezervace, dotazy a procedury.

U návštěvníků je možné vkládat, upravovat a mazat data. Aplikace pracuje i se složenou adresou a telefony. U rezervací aplikace neprovádí logiku sama ručně, ale volá PL/SQL procedury v databázi.

Samostatná část aplikace umožňuje spouštět připravené SQL dotazy a zobrazovat výsledky. Další část volá funkce pro tržby, obsazenost a TOP návštěvníky.`,
  },
  {
    title: "Závěr",
    body: `Na závěr bych to shrnul jednoduše.

Projekt vychází z jedné konkrétní domény a kolem ní jsou postavené všechny části: model, databázová logika, dotazy i aplikace.

Nechtěl jsem dělat jen sadu nesouvisejících tabulek. Cílem bylo, aby šlo projít celý proces od představení přes rezervaci až po platbu a následné přehledy.

Tím bych prezentaci uzavřel a dál můžu ukázat konkrétní část projektu.`,
  },
];

const SLIDE_W = 13.333;
const SLIDE_H = 7.5;
const M = 0.58;

const images = {
  conceptual: { path: path.join(root, "images/conceptual.png"), w: 2604, h: 823 },
  object: { path: path.join(root, "images/object_model.png"), w: 2222, h: 1231 },
  relational: { path: path.join(root, "images/relational_model.png"), w: 2770, h: 1668 },
};

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Jakub Mitrega";
pptx.company = "KIP/XDBS1";
pptx.subject = "Semestrální projekt Databázové systémy 1";
pptx.title = "TeatrumDB - prezentace projektu";
pptx.lang = "cs-CZ";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "cs-CZ",
};
pptx.defineLayout({ name: "CUSTOM_WIDE", width: SLIDE_W, height: SLIDE_H });
pptx.layout = "CUSTOM_WIDE";

function addBg(slide, inverse = false) {
  slide.background = { color: inverse ? COLORS.ink : COLORS.bg };
}

function addFooter(slide, n, inverse = false) {
  slide.addShape(pptx.ShapeType.line, {
    x: M,
    y: 7.05,
    w: 12.15,
    h: 0,
    line: { color: inverse ? "52606E" : "D8DED9", width: 0.7 },
  });
  slide.addText("TeatrumDB | Databázové systémy 1", {
    x: M,
    y: 7.13,
    w: 4.8,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 7.8,
    color: inverse ? "CAD3DA" : COLORS.muted,
    margin: 0,
  });
  slide.addText(String(n).padStart(2, "0"), {
    x: 12.22,
    y: 7.13,
    w: 0.55,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 7.8,
    color: inverse ? "CAD3DA" : COLORS.muted,
    align: "right",
    margin: 0,
  });
}

function addSpeakerNotes(slide, n) {
  const note = SLIDE_NOTES[n - 1];
  if (!note) return;
  slide.addNotes(note.body.trim());
}

function renderNotesMarkdown() {
  return [
    "# Poznámky k prezentaci TeatrumDB",
    "",
    "Tyto poznámky slouží jako mluvený tahák ke slidům prezentace.",
    "",
    ...SLIDE_NOTES.map((note, index) => `## Slide ${index + 1}: ${note.title}\n\n${note.body.trim()}`),
    "",
  ].join("\n");
}

function title(slide, n, heading, sub = "", opts = {}) {
  const inverse = opts.inverse || false;
  const color = inverse ? COLORS.white : COLORS.ink;
  const muted = inverse ? "CAD3DA" : COLORS.muted;
  slide.addText(String(n).padStart(2, "0"), {
    x: M,
    y: 0.37,
    w: 0.65,
    h: 0.28,
    fontSize: 10,
    bold: true,
    color: opts.accent || COLORS.red,
    margin: 0,
  });
  slide.addText(heading, {
    x: M,
    y: 0.65,
    w: 8.9,
    h: 0.62,
    fontFace: "Aptos Display",
    fontSize: 23,
    bold: true,
    color,
    margin: 0,
    fit: "shrink",
  });
  if (sub) {
    slide.addText(sub, {
      x: M,
      y: 1.24,
      w: 10.8,
      h: 0.42,
      fontSize: 9.8,
      color: muted,
      margin: 0,
      breakLine: false,
      fit: "shrink",
    });
  }
}

function sectionLabel(slide, text, x, y, w, color = COLORS.red) {
  slide.addText(text.toUpperCase(), {
    x,
    y,
    w,
    h: 0.22,
    fontSize: 7.5,
    bold: true,
    color,
    charSpace: 1.1,
    margin: 0,
  });
}

function addPill(slide, label, x, y, w, color, inverse = false) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.34,
    rectRadius: 0.08,
    fill: { color: inverse ? "263544" : "FFFFFF", transparency: inverse ? 0 : 10 },
    line: { color, width: 1.2 },
  });
  slide.addText(label, {
    x: x + 0.12,
    y: y + 0.075,
    w: w - 0.24,
    h: 0.14,
    fontSize: 8,
    bold: true,
    color: inverse ? COLORS.white : color,
    align: "center",
    margin: 0,
  });
}

function addOpenMetric(slide, value, label, x, y, color = COLORS.red, w = 1.7) {
  slide.addText(value, {
    x,
    y,
    w,
    h: 0.52,
    fontSize: 25,
    bold: true,
    color,
    margin: 0,
  });
  slide.addText(label, {
    x,
    y: y + 0.54,
    w: w + 0.55,
    h: 0.3,
    fontSize: 8,
    color: COLORS.muted,
    margin: 0,
    fit: "shrink",
  });
}

function addCallout(slide, text, x, y, w, h, color = COLORS.red, fill = "FFFFFF") {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: fill, transparency: 0 },
    line: { color: "D7DEE4", width: 0.8 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w: 0.08,
    h,
    fill: { color },
    line: { color },
  });
  slide.addText(text, {
    x: x + 0.2,
    y: y + 0.16,
    w: w - 0.35,
    h: h - 0.24,
    fontSize: 9.4,
    color: COLORS.ink,
    margin: 0,
    fit: "shrink",
    breakLine: false,
  });
}

function addTable(slide, rows, x, y, colWs, rowH, opts = {}) {
  const header = opts.header ?? true;
  const fontSize = opts.fontSize ?? 8.6;
  let cy = y;
  rows.forEach((row, rIdx) => {
    let cx = x;
    const isHeader = header && rIdx === 0;
    const fill = isHeader ? opts.headerFill || "E9EEF0" : rIdx % 2 ? "FFFFFF" : "F3F5F6";
    row.forEach((cell, cIdx) => {
      slide.addShape(pptx.ShapeType.rect, {
        x: cx,
        y: cy,
        w: colWs[cIdx],
        h: rowH,
        fill: { color: fill },
        line: { color: "CAD2D8", width: 0.55 },
      });
      slide.addText(cell, {
        x: cx + 0.08,
        y: cy + 0.065,
        w: colWs[cIdx] - 0.16,
        h: rowH - 0.1,
        fontSize,
        bold: isHeader,
        color: isHeader ? COLORS.ink : COLORS.ink,
        margin: 0,
        fit: "shrink",
        breakLine: false,
      });
      cx += colWs[cIdx];
    });
    cy += rowH;
  });
}

function addContainImage(slide, img, x, y, w, h, opts = {}) {
  const ratio = img.w / img.h;
  const boxRatio = w / h;
  let iw;
  let ih;
  if (ratio > boxRatio) {
    iw = w;
    ih = w / ratio;
  } else {
    ih = h;
    iw = h * ratio;
  }
  if (opts.frame !== false) {
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w,
      h,
      rectRadius: 0.06,
      fill: { color: COLORS.white },
      line: { color: "D1D7DD", width: 0.7 },
      shadow: { type: "outer", color: "B8C0C8", opacity: 0.18, blur: 2, angle: 45, distance: 1 },
    });
  }
  slide.addImage({
    path: img.path,
    x: x + (w - iw) / 2,
    y: y + (h - ih) / 2,
    w: iw,
    h: ih,
  });
}

function addFlow(slide, steps, x, y, totalW, color = COLORS.red) {
  const gap = 0.18;
  const w = (totalW - gap * (steps.length - 1)) / steps.length;
  steps.forEach((step, i) => {
    const sx = x + i * (w + gap);
    slide.addShape(pptx.ShapeType.roundRect, {
      x: sx,
      y,
      w,
      h: 0.78,
      rectRadius: 0.08,
      fill: { color: i % 2 ? "FFFFFF" : "F1F3F4" },
      line: { color: "C8D0D7", width: 0.8 },
    });
    slide.addText(step, {
      x: sx + 0.12,
      y: y + 0.21,
      w: w - 0.24,
      h: 0.25,
      fontSize: 9,
      bold: true,
      color: COLORS.ink,
      align: "center",
      margin: 0,
      fit: "shrink",
    });
    if (i < steps.length - 1) {
      slide.addShape(pptx.ShapeType.line, {
        x: sx + w + 0.02,
        y: y + 0.39,
        w: gap - 0.04,
        h: 0,
        line: { color, width: 1.4, beginArrowType: "none", endArrowType: "triangle" },
      });
    }
  });
}

function addCheckList(slide, items, x, y, w, gap = 0.42, color = COLORS.green) {
  items.forEach((item, idx) => {
    const cy = y + idx * gap;
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: cy + 0.01,
      w: 0.19,
      h: 0.19,
      fill: { color },
      line: { color },
    });
    slide.addText(item, {
      x: x + 0.32,
      y: cy,
      w,
      h: 0.28,
      fontSize: 9.3,
      color: COLORS.ink,
      margin: 0,
      fit: "shrink",
      breakLine: false,
    });
  });
}

function cover() {
  const slide = pptx.addSlide();
  addBg(slide, true);
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 1.35, h: SLIDE_H, fill: { color: COLORS.redDark }, line: { color: COLORS.redDark } });
  slide.addShape(pptx.ShapeType.rect, { x: 1.35, y: 0, w: 0.13, h: SLIDE_H, fill: { color: COLORS.gold }, line: { color: COLORS.gold } });
  slide.addText("TeatrumDB", {
    x: 1.95,
    y: 1.38,
    w: 8.8,
    h: 0.75,
    fontFace: "Aptos Display",
    fontSize: 43,
    bold: true,
    color: COLORS.white,
    margin: 0,
  });
  slide.addText("divadelní databázová aplikace", {
    x: 1.98,
    y: 2.12,
    w: 8.2,
    h: 0.42,
    fontSize: 18,
    color: "D8E0E6",
    margin: 0,
  });
  slide.addText("Semestrální projekt | Databázové systémy 1", {
    x: 1.98,
    y: 3.1,
    w: 5.7,
    h: 0.28,
    fontSize: 10,
    color: "AEBAC4",
    charSpace: 1,
    margin: 0,
  });
  slide.addText("Jakub Mitrega | R24080", {
    x: 1.98,
    y: 3.46,
    w: 3.8,
    h: 0.26,
    fontSize: 11.5,
    bold: true,
    color: COLORS.gold,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, { x: 1.98, y: 4.15, w: 3.4, h: 0, line: { color: COLORS.red, width: 2 } });
  slide.addText("Oracle objektově-relační schéma, PL/SQL logika a desktopová aplikace pro správu provozu divadla.", {
    x: 1.98,
    y: 4.42,
    w: 7.6,
    h: 0.6,
    fontSize: 13,
    color: "EEF3F4",
    breakLine: false,
    fit: "shrink",
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.arc, {
    x: 10.1,
    y: 0.7,
    w: 2.5,
    h: 5.2,
    line: { color: "485866", transparency: 35, width: 1.5 },
    adjustPoint: 0.3,
  });
  slide.addText("prezentace semestrálního projektu", { x: 9.62, y: 6.64, w: 2.7, h: 0.2, fontSize: 8.5, color: "AEBAC4", align: "right", margin: 0 });
  addSpeakerNotes(slide, 1);
}

function slideDomain() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 2, "Aplikační doména: provoz divadla", "Evidence od inscenace až po platbu a vyhodnocení návštěvnosti.");
  addFlow(slide, ["Inscenace", "Představení", "Sedadlo", "Rezervace", "Platba"], 0.72, 2.05, 7.85, COLORS.red);
  sectionLabel(slide, "co systém pokrývá", 0.72, 3.15, 3);
  addCheckList(slide, [
    "návštěvníky, adresy, telefony a věrnostní karty",
    "sály, sedadla, termíny představení a obsazenost",
    "rezervace, předplatné, platby a ARC pravidlo",
    "herce, režiséry, role, recenze a hodnocení",
  ], 0.78, 3.55, 6.9, 0.44, COLORS.teal);
  addCallout(slide, "Doména je vhodná pro objektově-relační model: obsahuje osoby s dědičností, složené atributy, kolekce, odvozené hodnoty i integritní pravidla.", 8.95, 1.9, 3.55, 1.45, COLORS.red);
  sectionLabel(slide, "technologická část", 9.0, 3.78, 3);
  addPill(slide, "Oracle 23c Free", 9.0, 4.18, 1.85, COLORS.blue);
  addPill(slide, "PL/SQL", 10.98, 4.18, 1.15, COLORS.red);
  addPill(slide, "Python / Tkinter", 9.0, 4.7, 2.15, COLORS.teal);
  addPill(slide, "Docker", 11.28, 4.7, 0.95, COLORS.gold);
  addFooter(slide, 2);
  addSpeakerNotes(slide, 2);
}

function slideConceptual() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 3, "Konceptuální model", "Jádro modelu propojuje provozní agendu, osoby a obchodní transakce.");
  addContainImage(slide, images.conceptual, 0.72, 1.65, 11.9, 3.92);
  addCallout(slide, "Klíčové konstrukce: ISA hierarchie osob, ARC vztah plateb, non-transferable vztah rezervace, složené a vícehodnotové atributy.", 0.8, 5.85, 5.7, 0.85, COLORS.red);
  addCallout(slide, "Model má dost datových vazeb pro demonstraci spojení, kvantifikace, agregací i dotazů nad kolekcemi.", 6.75, 5.85, 5.45, 0.85, COLORS.teal);
  addFooter(slide, 3);
  addSpeakerNotes(slide, 3);
}

function slideObjectTypes() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 4, "Objektové typy, metody a kolekce", "Odvoditelné atributy jsou implementované jako metody objektových typů.");
  addContainImage(slide, images.object, 5.95, 1.5, 6.45, 4.75);
  sectionLabel(slide, "použité adt", 0.72, 1.72, 2);
  addCheckList(slide, [
    "osoba_t jako NOT FINAL nadtyp",
    "navstevnik_t, zamestnanec_t, herec_t, reziser_t",
    "adresa_t jako složený atribut",
    "telefony_t a jazyky_t jako nested table",
    "zanry_t a oceneni_t jako VARRAY",
  ], 0.78, 2.1, 4.7, 0.39, COLORS.blue);
  sectionLabel(slide, "metody", 0.72, 4.38, 2);
  addPill(slide, "vek()", 0.78, 4.75, 1.0, COLORS.red);
  addPill(slide, "celkem_utraceno()", 1.94, 4.75, 2.0, COLORS.teal);
  addPill(slide, "prumerne_hodnoceni()", 0.78, 5.24, 2.55, COLORS.gold);
  addPill(slide, "volna_mista()", 3.48, 5.24, 1.65, COLORS.blue);
  addFooter(slide, 4);
  addSpeakerNotes(slide, 4);
}

function slideOracleModel() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 5, "Objektově-relační schéma v Oracle", "Schéma kombinuje objektové tabulky, relační vazby, kolekce a PL/SQL balík funkcionality.");
  addContainImage(slide, images.relational, 0.72, 1.45, 8.2, 4.95);
  sectionLabel(slide, "skripty", 9.28, 1.63, 2);
  const rows = [
    ["Soubor", "Obsah"],
    ["01_schema.sql", "typy, tabulky, sekvence, metody"],
    ["02_triggers.sql", "integrita a doménová pravidla"],
    ["03_procedures.sql", "procedury a funkce PL/SQL"],
    ["04_data.sql", "testovací data"],
    ["05_queries.sql", "12 demonstračních dotazů"],
  ];
  addTable(slide, rows, 9.27, 2.0, [1.65, 2.25], 0.44, { fontSize: 7.1, headerFill: "E8EDF0" });
  addCallout(slide, "Instalace je spustitelná v Dockeru a vytváří uživatele teatrum v PDB FREEPDB1.", 9.25, 4.95, 3.25, 0.92, COLORS.blue);
  addFooter(slide, 5);
  addSpeakerNotes(slide, 5);
}

function slideIntegrityPlsql() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 6, "Integrita a PL/SQL funkcionalita", "Triggery hlídají pravidla domény, procedury a funkce tvoří aplikační rozhraní.");
  sectionLabel(slide, "triggery", 0.72, 1.72, 2);
  addTable(slide, [
    ["Trigger", "Pravidlo"],
    ["trg_rez_integrita", "rezervace jen pro existující budoucí představení a sedadlo ve správném sále"],
    ["trg_role_nontransferable", "u role nelze změnit herce ani inscenaci"],
    ["trg_hodn_validita", "hodnocení jen po proběhlém představení s rezervací"],
    ["trg_platba_stav_rez", "platba přepne rezervaci na stav ZAPLACENA"],
    ["trg_pred_vyprodano", "naplněná kapacita přepne představení na VYPRODANO"],
  ], 0.72, 2.05, [2.25, 4.65], 0.48, { fontSize: 7.3, headerFill: "E8EDF0" });
  sectionLabel(slide, "procedury a funkce", 7.85, 1.72, 3);
  addTable(slide, [
    ["Název", "Účel"],
    ["pr_vytvorit_rezervaci", "vytvoření rezervace"],
    ["pr_zrusit_rezervaci", "zrušení a vrácená částka"],
    ["pr_generuj_sedadla", "hromadné vytvoření sedadel"],
    ["fn_trzba_inscenace", "tržba za inscenaci"],
    ["fn_obsazenost_pct", "obsazenost představení"],
    ["fn_top_navstevnici", "REF CURSOR TOP návštěvníků"],
  ], 7.85, 2.05, [2.1, 2.55], 0.43, { fontSize: 7.2, headerFill: "E8EDF0" });
  addFooter(slide, 6);
  addSpeakerNotes(slide, 6);
}

function slideQueries() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 7, "Demonstrační SQL dotazy", "Dotazy ukazují provozní i analytické pohledy nad ADT a kolekcemi.");
  const rows = [
    ["Konstrukce", "Ukázka v projektu"],
    ["projekce + selekce", "návštěvníci starší 30 let, metoda vek()"],
    ["spojení", "inscenace s režisérem a rolemi"],
    ["ALL / ANY / IN", "maximální hodnocení, role režiséra, množina inscenací"],
    ["seskupení", "počty představení, průměrné hodnocení, top sály"],
    ["NOT EXISTS", "budoucí představení bez rezervací a univerzální kvantifikace"],
    ["ADT + kolekce", "adresa.cela_adresa(), TABLE(r.oceneni), TABLE(h.zanry)"],
  ];
  addTable(slide, rows, 0.72, 1.82, [3.05, 6.15], 0.51, { fontSize: 7.9, headerFill: "E8EDF0" });
  sectionLabel(slide, "ukázky výstupů", 0.8, 5.68, 2.4, COLORS.red);
  addCallout(slide, "V aplikaci jsou dotazy v katalogu. U každého je vidět SQL a pod ním výsledek.", 0.8, 5.98, 5.55, 0.68, COLORS.red);
  addCallout(slide, "Použil jsem je hlavně na obsazenost, tržby, hodnocení a aktivitu návštěvníků.", 6.65, 5.98, 4.95, 0.68, COLORS.teal);
  addOpenMetric(slide, "12", "dotazů v aplikaci", 10.35, 2.15, COLORS.teal, 1.8);
  addFooter(slide, 7);
  addSpeakerNotes(slide, 7);
}

function slideApplication() {
  const slide = pptx.addSlide();
  addBg(slide);
  title(slide, 8, "Desktopová aplikace", "Tkinter aplikace umožňuje CRUD, spouštění dotazů i volání PL/SQL funkcí.");
  addFlow(slide, ["Připojení", "Přehled", "Návštěvníci", "Rezervace", "Dotazy", "Procedury"], 0.72, 1.9, 10.75, COLORS.teal);
  sectionLabel(slide, "funkcionality aplikace", 0.72, 3.05, 4);
  addCheckList(slide, [
    "automatické připojení k Oracle podle .env",
    "CRUD nad návštěvníky včetně adresy a telefonů",
    "vytvoření a zrušení rezervace přes PL/SQL procedury",
    "katalog 12 dotazů s SQL náhledem a výsledkovou tabulkou",
    "výpočet tržby, obsazenosti a TOP návštěvníků přes funkce",
  ], 0.8, 3.48, 7.1, 0.42, COLORS.green);
  addCallout(slide, "Aplikace není jen prohlížeč tabulek: demonstruje objektové atributy, kolekce a aplikační PL/SQL logiku.", 8.55, 3.35, 3.65, 1.28, COLORS.red);
  slide.addText("run_app.sh", {
    x: 8.65,
    y: 5.08,
    w: 1.5,
    h: 0.22,
    fontFace: "Courier New",
    fontSize: 10,
    bold: true,
    color: COLORS.ink,
    margin: 0,
  });
  slide.addText("spustí Docker databázi, nainstaluje závislosti a otevře aplikaci", {
    x: 8.65,
    y: 5.42,
    w: 3.5,
    h: 0.42,
    fontSize: 8.6,
    color: COLORS.muted,
    margin: 0,
    fit: "shrink",
  });
  addFooter(slide, 8);
  addSpeakerNotes(slide, 8);
}

function slideVerification() {
  const slide = pptx.addSlide();
  addBg(slide, true);
  title(slide, 9, "Závěr", "Projekt je postavený kolem běžného provozu divadla.", { inverse: true, accent: COLORS.gold });
  slide.addText("Od představení přes rezervaci až po platbu.", {
    x: 0.9,
    y: 1.92,
    w: 9.0,
    h: 0.58,
    fontFace: "Aptos Display",
    fontSize: 27,
    bold: true,
    color: COLORS.white,
    margin: 0,
    fit: "shrink",
    breakLine: false,
  });
  const pillars = [
    ["Model", "drží pohromadě osoby, představení, sedadla, rezervace a platby"],
    ["Databáze", "obsahuje typy, kolekce, triggery, procedury a výpočty"],
    ["Aplikace", "umožňuje data spravovat, rezervovat místa a spouštět dotazy"],
  ];
  pillars.forEach((p, i) => {
    const x = 0.92 + i * 4.05;
    slide.addShape(pptx.ShapeType.line, {
      x,
      y: 3.55,
      w: 2.2,
      h: 0,
      line: { color: i === 0 ? COLORS.gold : i === 1 ? COLORS.teal : COLORS.red, width: 2 },
    });
    slide.addText(p[0], {
      x,
      y: 3.82,
      w: 3.15,
      h: 0.28,
      fontSize: 13,
      bold: true,
      color: COLORS.white,
      margin: 0,
    });
    slide.addText(p[1], {
      x,
      y: 4.23,
      w: 3.45,
      h: 0.75,
      fontSize: 10,
      color: "DCE5EA",
      margin: 0,
      fit: "shrink",
      breakLine: false,
    });
  });
  slide.addText("Děkuji za pozornost.", {
    x: 0.92,
    y: 6.03,
    w: 4.4,
    h: 0.34,
    fontSize: 15,
    bold: true,
    color: COLORS.gold,
    margin: 0,
  });
  addFooter(slide, 9, true);
  addSpeakerNotes(slide, 9);
}

function buildDeck() {
  cover();
  slideDomain();
  slideConceptual();
  slideObjectTypes();
  slideOracleModel();
  slideIntegrityPlsql();
  slideQueries();
  slideApplication();
  slideVerification();
}

async function renderPreviews() {
  const artifact = await import(pathToFileURL(artifactModulePath).href);
  const skia = await import(pathToFileURL(skiaModulePath).href);
  const { PresentationFile, drawSlideToCtx } = artifact;
  const { Canvas } = skia;
  const buffer = await fs.readFile(pptxPath);
  const presentation = await PresentationFile.importPptx(buffer);

  await fs.rm(previewDir, { recursive: true, force: true });
  await fs.mkdir(previewDir, { recursive: true });
  for (let i = 0; i < presentation.slides.items.length; i += 1) {
    const slide = presentation.slides.items[i];
    const width = Math.ceil(slide.frame?.width || 1280);
    const height = Math.ceil(slide.frame?.height || 720);
    const canvas = new Canvas(width, height);
    const ctx = canvas.getContext("2d");
    await drawSlideToCtx(
      slide,
      presentation,
      ctx,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      undefined,
      { clearBeforeDraw: true },
    );
    await canvas.toFile(path.join(previewDir, `slide-${String(i + 1).padStart(2, "0")}.png`));
  }
}

async function main() {
  await fs.mkdir(outDir, { recursive: true });
  buildDeck();
  await pptx.writeFile({ fileName: pptxPath });
  await fs.writeFile(notesPath, renderNotesMarkdown(), "utf8");
  await renderPreviews();
  console.log(pptxPath);
  console.log(notesPath);
  console.log(previewDir);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
