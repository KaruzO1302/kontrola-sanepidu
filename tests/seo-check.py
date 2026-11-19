#!/usr/bin/env python3
"""Kontrola SEO przed deployem kontrola-sanepidu.com (adresy bez końcowego ukośnika).

    python3 tests/seo-check.py                 # pliki lokalne (po build.py)
    python3 tests/seo-check.py --live URL      # dodatkowo HTTP 200 dla stron, linków i obrazów pod URL (np. podgląd Vercel)

Sprawdza: title ≤60, description 120–155, 1×H1, self-canonical bez ukośnika, OG/Twitter, poprawny JSON-LD (HVACBusiness na każdej
stronie, BreadcrumbList na podstronach, FAQPage zgodny z widocznym FAQ), linki wewnętrzne (bez ukośnika na końcu) i obrazy,
sitemap.xml, robots.txt, telefon z konfiguracji, brak placeholderów, starych marek, kar/mandatów i kwot innych niż 100 zł,
CSS bez czcionek < 14 px.
"""
import json, pathlib, re, sys, urllib.request, urllib.error
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

BASE = build.BASE
TEL = build.CONFIG["tel"]
fails = []

def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("FAIL", msg)

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.title = ""; s.in_title = False; s.meta = {}; s.canon = None; s.h1 = 0; s.imgs = []; s.links = []
        s.ld = []; s.in_ld = False; s.buf = ""; s.skip = 0; s.text = []; s.summaries = []; s.in_sum = False; s.sum = ""
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "title" and not s.title: s.in_title = True
        if t == "meta":
            k = a.get("name") or a.get("property")
            if k: s.meta[k] = a.get("content", "")
        if t == "link" and a.get("rel") == "canonical": s.canon = a.get("href")
        if t == "h1": s.h1 += 1
        if t == "img": s.imgs.append(a)
        if t == "a" and a.get("href"): s.links.append(a["href"])
        if t == "summary": s.in_sum = True; s.sum = ""
        if t in ("script", "style"):
            s.skip += 1
            if a.get("type") == "application/ld+json": s.in_ld = True; s.buf = ""
    def handle_endtag(s, t):
        if t == "title": s.in_title = False
        if t == "summary": s.in_sum = False; s.summaries.append(s.sum.strip())
        if t in ("script", "style"):
            s.skip = max(0, s.skip - 1)
            if t == "script" and s.in_ld:
                s.in_ld = False
                try: s.ld.append(json.loads(s.buf))
                except Exception: s.ld.append(None)
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld: s.buf += d
        if s.in_sum: s.sum += d
        if not s.skip: s.text.append(d)

def file_for(path):
    return build.out_file(path)

def local_target_exists(href):
    pth = href.split("#")[0].split("?")[0]
    if pth in ("", "/"): return (ROOT / "index.html").exists()
    return (ROOT / (pth.strip("/") + ".html")).is_file() or (ROOT / pth.lstrip("/")).is_file()

# ---------- sitemap / robots ----------
sm_raw = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
sm = re.findall(r"<loc>([^<]+)</loc>", sm_raw)
check(len(sm) >= 15, f"sitemap: tylko {len(sm)} URL")
robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
check(f"Sitemap: {BASE}/sitemap.xml" in robots and "Disallow: /\n" not in robots, "robots.txt niepoprawny")
for u in sm:
    check(u == BASE + "/" or not u.endswith("/"), f"sitemap: ukośnik na końcu {u}")
OLD = ["/", "/strefa-wiedzy"] + ["/strefa-wiedzy/" + x for x in (
    "czyszczenie-kanalow-wentylacyjnych", "kontrola-sanepidu-2026-nowe-wymagania", "kontrola-sanepidu-checklista",
    "kontrola-sanepidu-gabinet-stomatologiczny", "kontrola-sanepidu-w-restauracji", "obowiazki-prawne-wentylacja-hotele-restauracje",
    "ozonowanie-dezynfekcja-powietrza", "plesn-w-wentylacji", "przeglady-wentylacji-obowiazkowe", "wymogi-wentylacji-sanepid")]
for o in OLD:
    check(BASE + o in sm, f"sitemap: brak starego adresu {o}")
print(f"sitemap: {len(sm)} URL\n")

pages = {u.replace(BASE, ""): file_for(u.replace(BASE, "")) for u in sm}
pages["/404"] = ROOT / "404.html"
all_links, all_imgs = set(), set()
seen_titles, seen_desc = {}, {}
for path, f in pages.items():
    check(f.exists(), f"brak pliku {f}")
    if not f.exists(): continue
    raw = f.read_text(encoding="utf-8"); p = P(); p.feed(raw)
    title = p.title.strip(); desc = p.meta.get("description", "")
    check(len(title) <= 60, f"{path}: title {len(title)} zn. „{title}”")
    check(120 <= len(desc) <= 155, f"{path}: description {len(desc)} zn.")
    check(not re.search(r"(?:\b[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\s){3,}[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+", title), f"{path}: title w Title Case?")
    if path != "/404":
        check(p.canon == BASE + path, f"{path}: canonical {p.canon}")
        check(title not in seen_titles, f"{path}: zduplikowany title z {seen_titles.get(title)}")
        check(desc not in seen_desc, f"{path}: zduplikowany description")
        seen_titles[title] = path; seen_desc[desc] = path
    check(p.h1 == 1, f"{path}: H1 = {p.h1}")
    check(all(k in p.meta for k in ("og:title", "og:description", "og:image", "og:url", "twitter:card")), f"{path}: brak OG/Twitter")
    check(p.ld and all(x is not None for x in p.ld), f"{path}: JSON-LD niepoprawny")
    graph = [n for d in p.ld if d for n in d.get("@graph", [d])]
    types = {t for n in graph for t in ([n["@type"]] if isinstance(n.get("@type"), str) else n.get("@type", []))}
    check("HVACBusiness" in types, f"{path}: brak HVACBusiness w JSON-LD")
    if path not in ("/", "/404"):
        check("BreadcrumbList" in types, f"{path}: brak BreadcrumbList")
    faq_nodes = [n for n in graph if n.get("@type") == "FAQPage"]
    if p.summaries or faq_nodes:
        ld_q = [q["name"] for n in faq_nodes for q in n["mainEntity"]]
        check(ld_q == p.summaries, f"{path}: FAQPage JSON-LD ≠ widoczne FAQ ({len(ld_q)} vs {len(p.summaries)})")
    check(f"tel:{TEL}" in p.links, f"{path}: brak linku tel:{TEL}")
    check("/polityka-prywatnosci" in p.links, f"{path}: brak linku do polityki")
    for im in p.imgs:
        check(im.get("alt", "").strip(), f"{path}: img bez alt {im.get('src')}")
        check(im.get("width") and im.get("height"), f"{path}: img bez wymiarów {im.get('src')}")
        for u in [im.get("src", "")] + [x.strip().split(" ")[0] for x in (im.get("srcset") or "").split(",") if x.strip()]:
            all_imgs.add(u)
            check((ROOT / u.lstrip("/")).is_file(), f"{path}: brak pliku obrazu {u}")
    for l in p.links:
        if l.startswith(("mailto:", "tel:", "#")): continue
        if l.startswith("http"):
            if l.startswith(BASE): l = l[len(BASE):] or "/"
            else: continue
        check(l.split("#")[0] in ("", "/") or not l.split("#")[0].endswith("/"), f"{path}: link z ukośnikiem na końcu {l}")
        all_links.add(l)
        check(local_target_exists(l), f"{path}: martwy link {l}")
    txt = re.sub(r"\s+", " ", " ".join(p.text))
    words = len(txt.split())
    low = raw.lower()
    for bad in ("24/7", "24h/7", "w godzinę", "minut", "{tel", "{img", "{link", "{svg", "{email", "{price", "{blog", "{hours", "none</td>",
                "czystawe", "czysta wentylacja", "nurtex", "horizons", "hostinger", "mandat", "10 000", "10000", "kilka tysięcy",
                "zamknięcia placówki", "zamknięcia obiektu", "zamknięcie placówki", "wstrzyman", "lat doświadczenia", "certyfikowan",
                "akredytowan", "pn-en", "dz.u", "dz. u", "§", "100%", "serwis-kanalizacji"):
        check(bad not in low.replace("ochrona24h", ""), f"{path}: zawiera „{bad}”")
    for amt in re.findall(r"(\d[\d\s\u00a0]*)\s*zł", txt):
        check(amt.strip() == "100", f"{path}: kwota inna niż 100 zł: {amt.strip()} zł")
    check(p.canon is None or p.canon == BASE + "/" or not p.canon.endswith("/"), f"{path}: canonical z ukośnikiem")
    for bad in (r"\btodo\b", r"\blorem\b", r"\bipsum\b"):
        check(not re.search(bad, low), f"{path}: zawiera wzorzec {bad}")
    print(f"{path:62s} title {len(title):2d} | desc {len(desc):3d} | słów {words:5d} | img {len(p.imgs)} | faq {len(p.summaries)}")

css = (ROOT / "assets/site.css").read_text(encoding="utf-8")
small = [m for m in re.findall(r"font-size:\s*([0-9.]+)px", css) if float(m) < 14]
check(not small, f"CSS: font-size < 14px: {small}")
check(re.search(r"body\{[^}]*font:16px", css), "CSS: tekst główny ≠ 16 px")
for f in (ROOT / "img").glob("*"):
    check(f.stat().st_size < 400_000, f"obraz za duży {f.name} {f.stat().st_size}")

if "--live" in sys.argv:
    live = sys.argv[sys.argv.index("--live") + 1].rstrip("/")
    print(f"\nHTTP check: {live}")
    targets = sorted(set(pages) - {"/404"} | all_links | all_imgs | {"/sitemap.xml", "/robots.txt", build.OG_IMG})
    for t in targets:
        req = urllib.request.Request(live + t, method="GET", headers={"User-Agent": "ziebud-seo-check/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r: code = r.status
        except urllib.error.HTTPError as e: code = e.code
        check(code == 200, f"HTTP {code} {t}")
    print(f"sprawdzono {len(targets)} adresów")

print("\nWYNIK:", "OK" if not fails else f"{len(fails)} problemów")
sys.exit(1 if fails else 0)
