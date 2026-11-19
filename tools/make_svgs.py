#!/usr/bin/env python3
"""Własne schematy SVG dla kontrola-sanepidu.com (wzór: spawanie-wroclaw). python3 tools/make_svgs.py"""
import pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "img"
OUT.mkdir(exist_ok=True)
FONT = 'font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif"'
NAVY, TEAL, TEAL_D, INK, MUT, RED, LIGHT = "#0f172a", "#2dd4bf", "#0f766e", "#1e293b", "#475569", "#b91c1c", "#f0fdfa"

def save(name, w, h, body, title):
    (OUT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
                            f'<title>{title}</title><rect width="{w}" height="{h}" fill="#fff"/>{body}</svg>\n', encoding="utf-8")

def T(x, y, lines, size=18, weight="400", color=INK, anchor="start"):
    lines = [lines] if isinstance(lines, str) else lines
    t = f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">'
    for i, l in enumerate(lines):
        t += f'<tspan x="{x}" dy="{0 if i == 0 else round(size * 1.3)}">{l}</tspan>'
    return t + "</text>"

def num(cx, cy, n):
    return f'<circle cx="{cx}" cy="{cy}" r="15" fill="{TEAL}"/>' + T(cx, cy + 6, str(n), 16, "700", NAVY, "middle")

def card(x, y, w, h, head, lines, size=16):
    b = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#f8fafc" stroke="#cbd5e1"/>'
    b += f'<rect x="{x}" y="{y}" width="{w}" height="46" rx="12" fill="{NAVY}"/><rect x="{x}" y="{y + 30}" width="{w}" height="16" fill="{NAVY}"/>'
    b += T(x + w / 2, y + 30, head, 18, "700", "#ffffff", "middle")
    for i, l in enumerate(lines):
        yy = y + 82 + i * 52
        b += f'<path d="M{x + 18} {yy - 6} l7 7 l12 -14" fill="none" stroke="{TEAL_D}" stroke-width="4"/>'
        b += T(x + 48, yy, l if isinstance(l, list) else [l], size)
    return b

def sanepid():
    W, H = 960, 560
    b = T(30, 42, "Co inspektor sanitarny ogląda w wentylacji i klimatyzacji", 24, "700", NAVY)
    b += T(30, 70, "Zakres kontroli zależy od rodzaju obiektu — to typowe punkty, o które warto zadbać wcześniej", 16, "400", MUT)
    b += card(30, 96, 290, 380, "Czystość", [["kratki i anemostaty", "bez kurzu i nalotu"], ["kanały bez osadów", "i śladów pleśni"], ["okap i kanał wyciągowy", "w kuchni bez tłuszczu"], ["taca skroplin klimatyzacji", "czysta i drożna"], ["filtry wymieniane", "zgodnie z instrukcją"]])
    b += card(335, 96, 290, 380, "Działanie", [["nawiew i wyciąg pracują", "w każdym pomieszczeniu"], ["wydajność zgodna", "z projektem"], ["brak przepływu powietrza", "ze strefy brudnej do czystej"], ["urządzenia bez usterek", "i nietypowych zapachów"], ["dostęp do otworów", "rewizyjnych"]])
    b += card(640, 96, 290, 380, "Dokumenty", [["protokół z ostatniego", "przeglądu"], ["protokół z czyszczenia", "i dezynfekcji"], ["wyniki pomiarów", "strumieni powietrza"], ["wyniki badań mikrobio-", "logicznych (jeśli były)"], ["wpisy w książce", "obiektu budowlanego"]])
    b += T(30, 520, "Dokumenty przechowuj w jednym segregatorze lub folderze — inspektor może poprosić o nie na początku kontroli.", 16, "400", MUT)
    save("co-sprawdza-sanepid-wentylacja.svg", W, H, b,
         "Co sprawdza sanepid w wentylacji: czystość kratek i kanałów, działanie nawiewu i wyciągu, filtry, klimatyzacja i dokumentacja")

def czyszczenie():
    W, H = 960, 520
    b = T(30, 42, "Etapy czyszczenia kanału wentylacyjnego", 24, "700", NAVY)
    # kanał
    b += f'<rect x="40" y="96" width="880" height="64" rx="6" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>'
    b += f'<rect x="40" y="142" width="420" height="18" fill="#a8a29e" opacity=".8"/>'
    b += T(250, 184, "osad w kanale przed czyszczeniem", 15, "400", MUT, "middle")
    b += f'<rect x="460" y="86" width="34" height="84" rx="4" fill="{NAVY}"/>' + T(477, 78, "szczotka rotacyjna", 15, "700", NAVY, "middle")
    b += f'<line x1="494" y1="128" x2="900" y2="128" stroke="{NAVY}" stroke-width="4"/>'
    b += f'<path d="M880 113 l30 15 l-30 15" fill="{TEAL_D}"/>' + T(780, 184, "odciąg podciśnieniowy z filtrem", 15, "700", TEAL_D, "middle")
    steps = ["Inspekcja kamerą i zdjęcia stanu przed czyszczeniem",
             "Zabezpieczenie pomieszczeń: folie, wyłączenie central, otwarcie rewizji",
             "Czyszczenie mechaniczne szczotką z odciągiem podciśnieniowym, kratki osobno",
             "Dezynfekcja kanałów i urządzeń, jeśli jest potrzebna lub wymagana",
             "Kontrola kamerą po czyszczeniu, zamknięcie rewizji, uruchomienie instalacji",
             "Protokół: zakres, zdjęcia przed i po, zalecenia na kolejny termin"]
    for i, st in enumerate(steps):
        yy = 232 + i * 44
        b += num(46, yy - 6, i + 1) + T(74, yy, st, 17)
    save("etapy-czyszczenia-kanalu-wentylacyjnego.svg", W, H, b,
         "Etapy czyszczenia kanału wentylacyjnego: inspekcja kamerą, zabezpieczenie, czyszczenie szczotką z odciągiem, dezynfekcja, kontrola i protokół")

def ozon():
    W, H = 960, 520
    b = T(30, 42, "Ozonowanie pomieszczenia krok po kroku", 24, "700", NAVY)
    b += T(30, 70, "Ozon jest szkodliwy przy wdychaniu — w trakcie zabiegu w pomieszczeniu nie może być ludzi ani zwierząt", 16, "700", RED)
    cols = [("Przed", ["wyjście ludzi i zwierząt", "wyniesienie roślin", "zamknięcie okien i drzwi", "oznaczenie wejścia"]),
            ("W trakcie", ["generator pracuje sam", "czas dobrany do kubatury", "drzwi zamknięte, bez wejść", "obsługa czeka na zewnątrz"]),
            ("Po zabiegu", ["odczekanie na rozpad ozonu", "wietrzenie pomieszczenia", "powrót dopiero po wietrzeniu", "wpis do protokołu"])]
    for k, (h, lines) in enumerate(cols):
        x = 30 + k * 310
        b += f'<rect x="{x}" y="96" width="290" height="300" rx="12" fill="#f8fafc" stroke="#cbd5e1"/>'
        b += f'<rect x="{x}" y="96" width="290" height="46" rx="12" fill="{NAVY}"/><rect x="{x}" y="126" width="290" height="16" fill="{NAVY}"/>'
        b += T(x + 145, 126, f"{k + 1}. {h}", 19, "700", "#ffffff", "middle")
        for i, l in enumerate(lines):
            yy = 186 + i * 54
            b += f'<path d="M{x + 18} {yy - 6} l7 7 l12 -14" fill="none" stroke="{TEAL_D}" stroke-width="4"/>' + T(x + 48, yy, l, 17)
        if k < 2:
            b += f'<path d="M{x + 292} 246 l14 0 m-6 -7 l7 7 l-7 7" fill="none" stroke="{MUT}" stroke-width="3"/>'
    b += T(30, 440, ["Ozonowanie usuwa zapachy i ogranicza drobnoustroje w powietrzu i na odsłoniętych powierzchniach,",
                     "ale nie zastępuje czyszczenia: kurz i osad w kanałach trzeba najpierw usunąć mechanicznie."], 16, "400", INK)
    save("ozonowanie-pomieszczenia-krok-po-kroku.svg", W, H, b,
         "Ozonowanie pomieszczenia krok po kroku: przygotowanie, puste pomieszczenie, zabieg, rozpad ozonu, wietrzenie i powrót do użytkowania")

def protokol():
    W, H = 960, 600
    b = T(30, 42, "Protokół z przeglądu i czyszczenia — co powinien zawierać", 24, "700", NAVY)
    # kartka
    b += f'<rect x="40" y="80" width="330" height="480" rx="10" fill="{LIGHT}" stroke="{TEAL_D}" stroke-width="2"/>'
    b += f'<rect x="40" y="80" width="330" height="56" rx="10" fill="{TEAL_D}"/><rect x="40" y="116" width="330" height="20" fill="{TEAL_D}"/>'
    b += T(205, 116, "PROTOKÓŁ", 22, "700", "#ffffff", "middle")
    for i in range(11):
        w = 260 if i % 3 else 190
        b += f'<rect x="70" y="{164 + i * 30}" width="{w}" height="10" rx="5" fill="#99f6e4"/>'
    b += f'<rect x="70" y="500" width="120" height="34" rx="6" fill="none" stroke="{TEAL_D}" stroke-dasharray="5 4"/>' + T(130, 523, "podpis", 15, "400", TEAL_D, "middle")
    items = [("Dane obiektu", "adres, rodzaj obiektu, data wykonania prac"),
             ("Wykonawca", "firma, osoba wykonująca, kontakt"),
             ("Zakres", "które instalacje, kanały i urządzenia objęto pracami"),
             ("Stan przed i po", "opis i zdjęcia z kamery inspekcyjnej"),
             ("Pomiary", "strumienie powietrza w punktach pomiarowych"),
             ("Badania", "wyniki z laboratorium, jeśli pobierano próbki"),
             ("Dezynfekcja / ozon", "czy wykonano, jakim środkiem, gdzie"),
             ("Zalecenia", "co poprawić i kiedy następny przegląd")]
    for i, (h, d) in enumerate(items):
        yy = 112 + i * 58
        b += num(420, yy - 6, i + 1) + T(448, yy - 4, f'<tspan font-weight="700">{h}</tspan>', 18) + T(448, yy + 18, d, 16, "400", MUT)
    save("protokol-przegladu-wentylacji-zawartosc.svg", W, H, b,
         "Co zawiera protokół z przeglądu i czyszczenia wentylacji: dane obiektu, zakres prac, zdjęcia przed i po, pomiary, wyniki badań i zalecenia")

def plesn():
    W, H = 960, 520
    b = T(30, 42, "Gdzie w instalacji najczęściej pojawia się pleśń", 24, "700", NAVY)
    b += T(30, 70, "Pleśni sprzyja wilgoć, kurz jako pożywka i brak przepływu powietrza", 16, "400", MUT)
    # schemat: centrala - kanał - kratka; klimatyzator
    b += f'<rect x="40" y="110" width="250" height="150" rx="10" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>' + T(165, 140, "centrala / rekuperator", 16, "700", NAVY, "middle")
    b += f'<rect x="64" y="160" width="60" height="80" fill="#cbd5e1"/>' + T(94, 258, "filtr", 14, "400", MUT, "middle")
    b += f'<rect x="150" y="160" width="110" height="80" fill="#cbd5e1"/>' + T(205, 258, "wymiennik", 14, "400", MUT, "middle")
    b += f'<rect x="290" y="165" width="450" height="40" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>' + T(515, 192, "kanał", 16, "400", MUT, "middle")
    b += f'<rect x="740" y="150" width="30" height="70" fill="#94a3b8"/>' + T(755, 240, "kratka", 14, "400", MUT, "middle")
    b += f'<rect x="600" y="290" width="320" height="80" rx="10" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>' + T(760, 320, "klimatyzator ścienny", 16, "700", NAVY, "middle")
    b += f'<rect x="640" y="342" width="240" height="14" fill="#cbd5e1"/>' + T(760, 390, "taca i odpływ skroplin", 14, "400", MUT, "middle")
    for (cx, cy) in ((94, 200), (205, 200), (420, 190), (760, 349), (755, 185)):
        b += f'<circle cx="{cx}" cy="{cy}" r="11" fill="#65a30d" opacity=".85"/><circle cx="{cx + 9}" cy="{cy - 7}" r="6" fill="#4d7c0f" opacity=".85"/>'
    pts = ["zawilgocone filtry i wymiennik centrali", "kanały przy łazienkach, kuchniach, saunach",
           "taca skroplin i wymiennik klimatyzatora", "kratki w pomieszczeniach z parą wodną"]
    for i, p in enumerate(pts):
        yy = 320 + i * 40
        b += f'<circle cx="46" cy="{yy - 6}" r="9" fill="#65a30d"/>' + T(66, yy, p, 17)
    save("gdzie-rozwija-sie-plesn-w-wentylacji.svg", W, H, b,
         "Gdzie w instalacji wentylacji i klimatyzacji najczęściej rozwija się pleśń: taca skroplin, wymiennik, filtry, kanały przy wilgotnych pomieszczeniach")

def og():
    W, H = 1200, 630
    b = f'<rect width="{W}" height="{H}" fill="{NAVY}"/><rect x="0" y="560" width="{W}" height="70" fill="{TEAL}"/>'
    b += T(80, 150, "ZIĘBUD", 64, "900", "#ffffff") + T(80, 200, "kontrola sanepidu · Wrocław", 30, "600", TEAL)
    b += T(80, 310, ["Przeglądy, czyszczenie i dezynfekcja", "wentylacji i klimatyzacji"], 50, "800", "#ffffff")
    b += T(80, 470, "Gabinety · gastronomia · hotele · Dolny Śląsk", 30, "400", "#cbd5e1")
    b += T(80, 606, "tel. 602 481 688 · kontrola-sanepidu.com", 30, "800", NAVY)
    (OUT / "og-kontrola-sanepidu-wroclaw.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{b}</svg>\n', encoding="utf-8")

sanepid(); czyszczenie(); ozon(); protokol(); plesn(); og()
