# Poznámky k prezentaci TeatrumDB

Tyto poznámky slouží jako mluvený tahák ke slidům prezentace.

## Slide 1: TeatrumDB

Dobrý den, představím projekt TeatrumDB.

Je to databázová aplikace pro divadelní provoz. Vybral jsem si divadlo proto, že se tam přirozeně potkávají lidé, představení, sedadla, rezervace i platby.

Snažil jsem se, aby to nebyla jen izolovaná evidence, ale aby jednotlivé části dávaly dohromady jeden použitelný celek.
## Slide 2: Aplikační doména: provoz divadla

Začal jsem aplikační doménou, tedy provozem divadla.

V modelu jsou návštěvníci, umělecký personál, inscenace, představení, sály, sedadla, rezervace, platby i recenze.

Základní tok je jednoduchý: divadlo má inscenaci, ta se hraje v konkrétním termínu, návštěvník si vybere sedadlo, vytvoří rezervaci a ta se následně zaplatí.

Na téhle doméně mi přišlo dobré, že má provozní část i obchodní část a zároveň z ní jdou dělat smysluplné přehledy.
## Slide 3: Konceptuální model

Konceptuální model vychází z toho divadelního toku.

Model má víc než deset entit. Základ tvoří osoby, tedy návštěvník, zaměstnanec, herec a režisér. Vedle toho jsou provozní entity jako inscenace, představení, sál, sedadlo, rezervace, platba, předplatné, recenze a role.

Model využívá několik výraznějších databázových konstrukcí. ISA hierarchie je řešená přes obecnou osobu a její specializace. ARC vztah je u platby, která patří buď k rezervaci, nebo k předplatnému. Non-transferable vztah je u rezervace, protože rezervaci nelze převést na jiného návštěvníka.

Model obsahuje i složené atributy, například adresu, a vícehodnotové atributy, například telefony, jazyky, žánry a ocenění.
## Slide 4: Objektové typy, metody a kolekce

Po konceptuálním modelu jsem část návrhu převedl do objektových typů v Oracle.

V Oracle jsou vytvořené objektové typy. Například osoba_t je nadtyp, ze kterého vychází navstevnik_t, zamestnanec_t, herec_t a reziser_t.

Složený atribut adresa je samostatný typ adresa_t. Vícehodnotové atributy jsou implementované kolekcemi: telefony a jazyky jako nested table, žánry a ocenění jako VARRAY.

Odvoditelné atributy nejsou uložené jako běžné sloupce, ale jako metody objektových typů. Příklady jsou vek(), celkem_utraceno(), prumerne_hodnoceni() a volna_mista(). Díky tomu zůstává výpočet hodnot přímo u dat, kterých se týká.
## Slide 5: Objektově-relační schéma v Oracle

Tento slide ukazuje fyzický objektově-relační model v Oracle.

Schéma je rozdělené do několika SQL souborů. První soubor vytváří typy, tabulky, sekvence a objektové metody. Druhý soubor obsahuje triggery. Třetí soubor obsahuje procedury a funkce. Čtvrtý soubor vkládá testovací data a pátý obsahuje demonstrační dotazy.

Projekt kombinuje objektové tabulky a klasické relační vazby. Objektové prvky používám hlavně u osob, adres a metod. Provozní vazby jako rezervace, role nebo platby jsou modelované relačně.

Celé schéma se dá vytvořit v Oracle kontejneru přes Docker.
## Slide 6: Integrita a PL/SQL funkcionalita

Databáze tady nehlídá jen běžné cizí klíče.

Triggery hlídají doménovou a referenční integritu nad rámec běžných cizích klíčů. Například rezervace musí být na existující budoucí představení a na sedadlo ve správném sále. Další trigger hlídá, že rezervaci nelze převést na jiného návštěvníka. U plateb se kontroluje ARC pravidlo, tedy že platba patří buď k rezervaci, nebo k předplatnému, ne k oběma najednou.

PL/SQL část obsahuje procedury pro vytvoření rezervace, zrušení rezervace a generování sedadel. Funkce potom počítají tržbu inscenace, obsazenost představení a TOP návštěvníky podle útraty.

Tyto procedury a funkce nejsou jen ve schématu, ale aplikace je skutečně volá.
## Slide 7: Demonstrační SQL dotazy

Dotazy jsem bral jako způsob, jak ukázat, co se z těch dat dá získat.

Je jich dvanáct a týkají se návštěvníků, obsazenosti, hodnocení, rolí, plateb i práce s objektovými atributy.

Vedle běžných spojení a agregací jsou tam i dotazy s ALL, ANY, IN a NOT EXISTS. Příklad práce s objektovým typem je volání metody vek() nebo adresa.cela_adresa(). Příklad práce s kolekcí je TABLE(r.oceneni) nebo TABLE(h.zanry).
## Slide 8: Desktopová aplikace

Aplikační část je jednoduché desktopové rozhraní v Pythonu.

Aplikace je vytvořená v Pythonu pomocí Tkinteru a připojuje se k Oracle databázi. Má několik částí: připojení, přehled, návštěvníky, rezervace, dotazy a procedury.

U návštěvníků je možné vkládat, upravovat a mazat data. Aplikace pracuje i se složenou adresou a telefony. U rezervací aplikace neprovádí logiku sama ručně, ale volá PL/SQL procedury v databázi.

Samostatná část aplikace umožňuje spouštět připravené SQL dotazy a zobrazovat výsledky. Další část volá funkce pro tržby, obsazenost a TOP návštěvníky.
## Slide 9: Závěr

Na závěr bych to shrnul jednoduše.

Projekt vychází z jedné konkrétní domény a kolem ní jsou postavené všechny části: model, databázová logika, dotazy i aplikace.

Nechtěl jsem dělat jen sadu nesouvisejících tabulek. Cílem bylo, aby šlo projít celý proces od představení přes rezervaci až po platbu a následné přehledy.

Tím bych prezentaci uzavřel a dál můžu ukázat konkrétní část projektu.
