#!/usr/bin/env python3
"""Generator statycznej strony kontrola-sanepidu.com (ZIĘBUD EXPERT Sp. z o.o.) — silnik ze spawanie-wroclaw.

Adresy BEZ końcowego ukośnika (vercel.json: cleanUrls + trailingSlash false). /a/b -> a/b.html.

    python3 build.py            # HTML, sitemap.xml, robots.txt
    python3 tests/seo-check.py  # kontrola SEO przed deployem

Treść podstron: pages/*.py (słownik PAGE). Wspólne dane: CONFIG niżej — telefon, e-mail
i stawki zmieniasz TYLKO tutaj. W treści stron używaj znaczników:
  {TEL} {TEL_DISPLAY} {EMAIL} {DOJAZD} {IMG:klucz} {PRICE_TABLE} {LINK:/sciezka/|anchor}
"""
import importlib.util, json, pathlib, re, html as _html

ROOT = pathlib.Path(__file__).parent
BASE = "https://kontrola-sanepidu.com"
DATE = "2026-11-19"

# ======================= KONFIGURACJA (jedno miejsce) =======================
CONFIG = {
    "tel": "+48602481688",
    "tel_display": "602 481 688",
    "email": "biuro@ex-pert.pl",
    "hours_text": "całą dobę, 7 dni w tygodniu",
    "firm": {
        "name": "ZIĘBUD EXPERT Sp. z o.o.",
        "street": "ul. Polna 2F",
        "zip": "51-180",
        "city": "Krzyżanowice",
        "nip": "9151833889",
        "krs": "0001158935",
        "regon": "541055479",
    },
}

# Cennik — podmień None na kwotę netto w zł, a tabela sama się zaktualizuje.
# None = na stronie „wycena po oględzinach”. Nie wpisuj kwot, których nie zatwierdził właściciel.
PRICES = [
    ("Przegląd instalacji wentylacji", "Oględziny kanałów, kratek, central i wentylatorów, ocena czystości i drożności, zalecenia w protokole. Zależy od wielkości instalacji i liczby urządzeń.", None),
    ("Przegląd i serwis klimatyzacji", "Sprawdzenie jednostek wewnętrznych i zewnętrznych, filtrów, tacy i odpływu skroplin. Zależy od liczby i rodzaju urządzeń.", None),
    ("Czyszczenie kanałów wentylacyjnych", "Czyszczenie mechaniczne kanałów nawiewnych i wyciągowych, kratek i anemostatów, inspekcja kamerą przed i po. Zależy od długości i przekroju kanałów, liczby otworów rewizyjnych i stopnia zabrudzenia.", None),
    ("Czyszczenie rekuperacji", "Kanały, filtry i wymiennik centrali z odzyskiem ciepła. Zależy od typu centrali i długości kanałów.", None),
    ("Dezynfekcja instalacji", "Dezynfekcja kanałów i urządzeń preparatem przeznaczonym do instalacji wentylacyjnych, po czyszczeniu mechanicznym.", None),
    ("Ozonowanie pomieszczeń", "Zabieg w pustym pomieszczeniu, z wietrzeniem po zakończeniu. Zależy od kubatury i liczby pomieszczeń.", None),
    ("Pomiary wentylacji", "Pomiar strumieni powietrza na kratkach i anemostatach, porównanie z projektem lub założeniami, wyniki w protokole. Zależy od liczby punktów pomiarowych.", None),
    ("Badania mikrobiologiczne", "Pobór próbek powietrza i wymazów z instalacji, analiza w laboratorium, wyniki dołączone do protokołu. Zależy od liczby próbek i zakresu oznaczeń.", None),
    ("Dojazd", "Dojazd na terenie Wrocławia. Poza Wrocławiem koszt dojazdu podajemy w wycenie.", "100 zł netto"),
]
VAT_NOTE = ("Ceny podajemy netto. Wycenę każdej pozycji podajemy po oględzinach albo po rozmowie i zdjęciach instalacji — przed rozpoczęciem pracy. "
            "Stawkę VAT podajemy w wycenie, zależnie od rodzaju obiektu i zakresu prac.")

# Zdjęcia: klucz -> (plik bez rozszerzenia, szer., wys., alt). Brak pliku w img/ = sekcja bez zdjęcia.
IMAGES = {}  # bez zdjęć: tylko własne schematy SVG (zdjęcia z kreatora AI usunięte — niejasna licencja)
OG_IMG = "/img/og-kontrola-sanepidu-wroclaw.png"
SVGS = {
    "sanepid": ("co-sprawdza-sanepid-wentylacja.svg", 960, 560,
                "Co sprawdza sanepid w wentylacji: czystość kratek i kanałów, działanie nawiewu i wyciągu, filtry, klimatyzacja i dokumentacja"),
    "czyszczenie": ("etapy-czyszczenia-kanalu-wentylacyjnego.svg", 960, 520,
                    "Etapy czyszczenia kanału wentylacyjnego: inspekcja kamerą, zabezpieczenie, czyszczenie szczotką z odciągiem, dezynfekcja, kontrola i protokół"),
    "ozon": ("ozonowanie-pomieszczenia-krok-po-kroku.svg", 960, 520,
             "Ozonowanie pomieszczenia krok po kroku: przygotowanie, puste pomieszczenie, zabieg, rozpad ozonu, wietrzenie i powrót do użytkowania"),
    "protokol": ("protokol-przegladu-wentylacji-zawartosc.svg", 960, 600,
                 "Co zawiera protokół z przeglądu i czyszczenia wentylacji: dane obiektu, zakres prac, zdjęcia przed i po, pomiary, wyniki badań i zalecenia"),
    "plesn": ("gdzie-rozwija-sie-plesn-w-wentylacji.svg", 960, 520,
              "Gdzie w instalacji wentylacji i klimatyzacji najczęściej rozwija się pleśń: taca skroplin, wymiennik, filtry, kanały przy wilgotnych pomieszczeniach"),
}

# Nawigacja (jeden rząd na ≥1025 px)
NAV = [
    ("/#uslugi", "Usługi"),
    ("/strefa-wiedzy/kontrola-sanepidu-gabinet-stomatologiczny", "Gabinety"),
    ("/strefa-wiedzy/kontrola-sanepidu-w-restauracji", "Gastronomia"),
    ("/strefa-wiedzy", "Strefa wiedzy"),
    ("/cennik", "Cennik"),
    ("/kontakt", "Kontakt"),
]
SERVICES_FOOT = [
    ("/strefa-wiedzy/czyszczenie-kanalow-wentylacyjnych", "Czyszczenie kanałów wentylacyjnych"),
    ("/strefa-wiedzy/przeglady-wentylacji-obowiazkowe", "Przeglądy wentylacji"),
    ("/strefa-wiedzy/wymogi-wentylacji-sanepid", "Pomiary i badania mikrobiologiczne"),
    ("/strefa-wiedzy/ozonowanie-dezynfekcja-powietrza", "Ozonowanie i dezynfekcja"),
    ("/strefa-wiedzy/kontrola-sanepidu-checklista", "Checklista przed kontrolą"),
]

# ============================== HELPERS =====================================
C = CONFIG
F = C["firm"]

def esc(s):
    return _html.escape(s, quote=True)

def img_exists(key):
    if key not in IMAGES:
        return False
    return (ROOT / "img" / f"{IMAGES[key][0]}.webp").exists()

def img_tag(key, hero=False, sizes="(max-width: 900px) 100vw, 50vw", cls=""):
    if not img_exists(key):
        return ""
    name, w, h, alt = IMAGES[key]
    srcset = f"/img/{name}-800.webp 800w, /img/{name}.webp {w}w" if w > 800 else f"/img/{name}.webp {w}w"
    loading = 'fetchpriority="high" decoding="async"' if hero else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/img/{name}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{esc(alt)}" width="{w}" height="{h}" {loading}>')

_HERO_KEY = {"key": None}  # zdjęcie z nagłówka strony nie powtarza się w treści

def figure(key, caption=""):
    if key == _HERO_KEY["key"]:
        return ""
    t = img_tag(key)
    if not t:
        return ""
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="photo">{t}{cap}</figure>'

def svg_figure(key, caption=""):
    f, w, h, alt = SVGS[key]
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (f'<figure class="photo diagram"><img src="/img/{f}" alt="{esc(alt)}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async">{cap}</figure>')

def price_table():
    rows = []
    for item, scope, price in PRICES:
        p = price or "wycena po oględzinach"
        rows.append(f"<tr><th scope=\"row\">{item}</th><td>{scope}</td><td class=\"price\">{p}</td></tr>")
    return ('<div class="tbl"><table><caption>Pozycje rozliczeniowe — wentylacja i klimatyzacja, Wrocław</caption>'
            '<thead><tr><th scope="col">Co wyceniamy</th><th scope="col">Od czego zależy koszt</th><th scope="col">Stawka netto</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><p class="note">{VAT_NOTE}</p>')

def expand(s):
    s = (s.replace("{TEL}", C["tel"]).replace("{TEL_DISPLAY}", C["tel_display"])
          .replace("{EMAIL}", C["email"])
          .replace("{HOURS}", C["hours_text"]))
    if "{PRICE_TABLE}" in s:
        s = s.replace("{PRICE_TABLE}", price_table())
    s = re.sub(r"\{IMG:(\w+)(?:\|([^}]*))?\}", lambda m: figure(m.group(1), m.group(2) or ""), s)
    s = re.sub(r"\{SVG:(\w+)(?:\|([^}]*))?\}", lambda m: svg_figure(m.group(1), m.group(2) or ""), s)
    s = re.sub(r"\{LINK:([^|}]+)\|([^}]+)\}", lambda m: f'<a href="{m.group(1)}">{m.group(2)}</a>', s)
    return s

def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

# ----------------------------- JSON-LD --------------------------------------
def org_ld():
    return {
        "@type": "HVACBusiness",
        "@id": BASE + "/#firma",
        "name": "ZIĘBUD – kontrola sanepidu Wrocław",
        "legalName": F["name"],
        "url": BASE + "/",
        "telephone": "+48 " + C["tel_display"],
        "email": C["email"],
        "taxID": F["nip"],
        "image": BASE + OG_IMG,
        "address": {"@type": "PostalAddress", "streetAddress": F["street"], "postalCode": F["zip"],
                    "addressLocality": F["city"], "addressRegion": "dolnośląskie", "addressCountry": "PL"},
        "areaServed": [{"@type": "City", "name": "Wrocław"},
                       {"@type": "AdministrativeArea", "name": "powiat wrocławski"}] +
                      [{"@type": "AdministrativeArea", "name": "Dolny Śląsk"}],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "00:00", "closes": "23:59"}],
    }

def breadcrumb_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": label, "item": BASE + path}
        for i, (label, path) in enumerate(items)]}

def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip_tags(q),
         "acceptedAnswer": {"@type": "Answer", "text": strip_tags(expand(a))}} for q, a in items]}

# ----------------------------- layout ---------------------------------------
PHONE_SVG = ('<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" '
             'd="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>')

DL_SCRIPT = ("<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^=\"tel:\"],a[href^=\"mailto:\"]');"
             "if(!a)return;window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:a.href.indexOf('tel:')===0?'click_phone':'click_email',"
             "placement:a.getAttribute('data-placement')||'inline',page_path:location.pathname});});</script>")

def head(title, desc, path, ld, robots="index, follow, max-image-preview:large", preload_hero=None):
    canon = BASE + path
    graph = json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False)
    pre = ""
    if preload_hero and img_exists(preload_hero):
        n, w = IMAGES[preload_hero][0], IMAGES[preload_hero][1]
        ss = f"/img/{n}-800.webp 800w, /img/{n}.webp {w}w" if w > 800 else f"/img/{n}.webp {w}w"
        pre = (f'<link rel="preload" as="image" href="/img/{n}.webp" imagesrcset="{ss}" '
               f'imagesizes="(max-width: 1024px) 100vw, 40vw" fetchpriority="high">\n')
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0f172a">
<meta name="google-site-verification" content="-RfLzKCXLspr_SvjdJiWg1xsmiQoiKFLkNxq8w02mP8">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Kontrola Sanepidu Wrocław – ZIĘBUD Expert">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}{OG_IMG}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{pre}<link rel="stylesheet" href="/assets/site.css?v={DATE}">
<script type="application/ld+json">{graph}</script>
</head>
<body>
<a class="skip" href="#tresc">Przejdź do treści</a>
"""

def topbar(path):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if (path == href or (href == "/strefa-wiedzy" and path.startswith("/strefa-wiedzy/") and path not in [h for h, _ in NAV])) else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    return f"""<header class="top">
<div class="wrap top-in">
<a class="brand" href="/" aria-label="ZIĘBUD – kontrola sanepidu Wrocław, strona główna">ZIĘBUD<span>kontrola sanepidu</span></a>
<nav aria-label="Menu główne">{''.join(links)}</nav>
<a class="btn call" href="tel:{C['tel']}" data-placement="header" aria-label="Zadzwoń {C['tel_display']}">{PHONE_SVG}<span>{C['tel_display']}</span></a>
</div>
</header>
"""

def firm_block():
    return f"""<p><strong>{F['name']}</strong><br>{F['street']}, {F['zip']} {F['city']}<br>
NIP {F['nip']} · KRS {F['krs']} · REGON {F['regon']}</p>
<p>Telefon {C['hours_text']}: <a href="tel:{C['tel']}" data-placement="footer">{C['tel_display']}</a><br>
E-mail: <a href="mailto:{C['email']}" data-placement="footer">{C['email']}</a></p>"""

def footer():
    svc = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in SERVICES_FOOT)
    return f"""<footer class="foot">
<div class="wrap foot-grid">
<div><p class="foot-brand">ZIĘBUD <span>kontrola sanepidu</span></p>
<p>Przeglądy, czyszczenie, dezynfekcja i pomiary wentylacji oraz klimatyzacji przed kontrolą sanepidu — gabinety, gastronomia, hotele. Wrocław i Dolny Śląsk.</p>
<p>Telefon odbieramy {C['hours_text']}. Prace planowe umawiamy tak, żeby nie zatrzymać obiektu.</p></div>
<div><p class="foot-h">Usługi</p><ul>{svc}</ul></div>
<div><p class="foot-h">Firma</p>{firm_block()}
<ul><li><a href="/cennik">Cennik</a></li><li><a href="/kontakt">Kontakt</a></li><li><a href="/polityka-prywatnosci">Polityka prywatności</a></li></ul>
<p class="foot-h">Inne usługi ZIĘBUD</p>
<ul><li><a href="https://www.wuko-wroclaw.pl/" rel="noopener">wuko-wroclaw.pl — czyszczenie kanalizacji</a></li><li><a href="https://awarie24h.pl/" rel="noopener">awarie24h.pl — awarie wod-kan</a></li><li><a href="https://uslugi-elektryczne-wroclaw.pl/" rel="noopener">uslugi-elektryczne-wroclaw.pl — elektryk</a></li></ul></div>
</div>
<div class="wrap copy"><p>© 2026 {F['name']}. Ceny i terminy potwierdzamy przed rozpoczęciem pracy.</p></div>
</footer>
{DL_SCRIPT}
</body>
</html>
"""

def crumbs(items):
    out = ['<nav class="crumbs" aria-label="Ścieżka"><ol>']
    for i, (label, path) in enumerate(items):
        out.append(f'<li><a href="{path}">{label}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{label}</li>')
    out.append("</ol></nav>")
    return "".join(out)

def faq_html(items, heading="Najczęstsze pytania"):
    out = [f'<section class="alt" id="faq"><div class="wrap narrow"><h2>{heading}</h2><div class="faq">']
    for q, a in items:
        out.append(f"<details><summary>{q}</summary><div class=\"ans\"><p>{expand(a)}</p></div></details>")
    out.append("</div></div></section>")
    return "\n".join(out)

def cta_band(title="Kontrola sanepidu za pasem?", text=None):
    text = text or (f"Zadzwoń — odbieramy {C['hours_text']} — albo opisz obiekt i instalację na {C['email']}. "
                    "Termin przeglądu lub czyszczenia ustalamy tak, żeby nie zatrzymać gabinetu ani lokalu.")
    return f"""<section class="cta-band"><div class="wrap cta-in">
<div><h2>{title}</h2><p>{text}</p></div>
<a class="btn big" href="tel:{C['tel']}" data-placement="cta">Zadzwoń {C['tel_display']}</a>
</div></section>"""

def related_html(paths, titles):
    if not paths:
        return ""
    lis = "".join(f'<li><a href="{p}">{titles.get(p, p)}</a></li>' for p in paths)
    return f'<section><div class="wrap narrow"><h2>Zobacz także</h2><ul class="links">{lis}</ul></div></section>'

# ----------------------------- page render ----------------------------------
def load_pages():
    pages = []
    for f in sorted((ROOT / "pages").glob("*.py")):
        if f.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        if hasattr(m, "PAGES"):
            pages.extend(m.PAGES)
        else:
            pages.append(m.PAGE)
    return pages

def render(P, titles):
    path = P["path"]
    _HERO_KEY["key"] = P.get("hero_image")
    kind = P.get("kind", "service")
    crumb_items = [("Strona główna", "/")]
    if kind == "blog":
        crumb_items.append(("Strefa wiedzy", "/strefa-wiedzy"))
    if path != "/":
        crumb_items.append((P["crumb"], path))
    ld = [org_ld()]
    if path != "/":
        ld.append(breadcrumb_ld(crumb_items))
    if kind == "service" and P.get("service"):
        ld.append({"@type": "Service", "@id": BASE + path + "#usluga", "name": P["service"],
                   "serviceType": P["service"], "provider": {"@id": BASE + "/#firma"},
                   "areaServed": P.get("area_ld") or [{"@type": "City", "name": "Wrocław"},
                                  {"@type": "AdministrativeArea", "name": "powiat wrocławski"}],
                   "url": BASE + path})
    if kind == "blog":
        ld.append({"@type": "Article", "headline": P["h1"], "datePublished": P.get("date", DATE),
                   "dateModified": P.get("date", DATE), "inLanguage": "pl-PL",
                   "author": {"@id": BASE + "/#firma"}, "publisher": {"@id": BASE + "/#firma"},
                   "mainEntityOfPage": BASE + path, "image": BASE + OG_IMG})
    if P.get("faq"):
        ld.append(faq_ld(P["faq"]))
    ld.extend(P.get("extra_ld", []))
    out = head(P["title"], P["desc"], path, ld, robots=P.get("robots", "index, follow, max-image-preview:large"),
               preload_hero=P.get("hero_image") if P.get("custom_hero") else None) + topbar(path)
    out += '<main id="tresc">\n'
    if P.get("custom_hero"):
        out += expand(P["custom_hero"].replace("{HERO_IMG}", img_tag(P.get("hero_image") or "hero", hero=True, sizes="(max-width: 1024px) 100vw, 40vw")))
    else:
        hero_img = img_tag(P["hero_image"], hero=True, sizes="(max-width: 900px) 100vw, 40vw") if P.get("hero_image") else ""
        fig = f'<figure class="head-fig">{hero_img}</figure>' if hero_img else ""
        out += f"""<section class="page-head{' with-fig' if fig else ''}"><div class="wrap head-grid">
<div>{crumbs(crumb_items) if path != '/' else ''}
<p class="kicker">{P.get('kicker','Kontrola sanepidu · Wrocław')}</p>
<h1>{P['h1']}</h1>
<p class="lead">{expand(P.get('lead',''))}</p>
<div class="actions"><a class="btn big" href="tel:{C['tel']}" data-placement="page-head">Zadzwoń {C['tel_display']}</a>
<a class="btn ghost-dark big" href="/kontakt">Napisz e-mail</a></div>
</div>{fig}</div></section>
"""
    out += expand(P["body"])
    if P.get("faq"):
        out += faq_html(P["faq"], P.get("faq_heading", "Najczęstsze pytania"))
    out += related_html(P.get("related", []), titles)
    if P.get("cta", True):
        out += cta_band()
    out += "</main>\n" + footer()
    return out

def out_file(path):
    if path == "/":
        return ROOT / "index.html"
    if path == "/404":
        return ROOT / "404.html"
    assert not path.endswith("/"), f"ścieżka z ukośnikiem: {path}"
    return ROOT / (path.strip("/") + ".html")

def blog_list(pages):
    posts = sorted([p for p in pages if p.get("kind") == "blog"], key=lambda p: (p.get("date", DATE), p["path"]), reverse=True)
    lis = "".join(f'<li class="card"><h3><a href="{p["path"]}">{p.get("crumb_long", p["crumb"])}</a></h3>'
                  f'<p>{p.get("teaser", strip_tags(expand(p.get("lead", ""))))}</p><a class="more" href="{p["path"]}">Czytaj artykuł →</a></li>'
                  for p in posts)
    return f'<ul class="cards">{lis}</ul>'

def main():
    pages = load_pages()
    titles = {p["path"]: p.get("crumb_long", p["crumb"]) for p in pages if p["path"] not in ("/", "/404")}
    bl = blog_list(pages)
    for P in pages:
        P["body"] = P["body"].replace("{BLOG_LIST}", bl)
    for P in pages:
        f = out_file(P["path"])
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(render(P, titles), encoding="utf-8")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for P in sorted(pages, key=lambda p: -p.get("priority", 0.5)):
        if P["path"] == "/404" or "noindex" in P.get("robots", ""):
            continue
        sm.append(f"<url><loc>{BASE}{P['path']}</loc><lastmod>{P.get('date', DATE)}</lastmod><priority>{P.get('priority', 0.6)}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"zbudowano {len(pages)} stron + sitemap.xml, robots.txt")

if __name__ == "__main__":
    main()
