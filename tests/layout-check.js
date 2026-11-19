// Kontrola układu (Playwright; serwer z cleanUrls na porcie 8795): uruchamiana przez MCP browser_run_code z argumentem page.
// Zasady: pasek w jednym rzędzie ≥1025 px; przy 1280×720 H1 i nadtytuł nie pod paskiem, główne CTA widoczne bez przewijania;
// brak poziomego overflow 390..1920; żaden tekst < 14 px.
async (page) => {
  const BASE = 'http://localhost:8795';
  const paths = ['/', '/strefa-wiedzy', '/strefa-wiedzy/czyszczenie-kanalow-wentylacyjnych', '/strefa-wiedzy/kontrola-sanepidu-gabinet-stomatologiczny',
    '/strefa-wiedzy/ozonowanie-dezynfekcja-powietrza', '/cennik', '/kontakt', '/polityka-prywatnosci'];
  const sizes = [[390, 844], [768, 1024], [1025, 800], [1280, 720], [1440, 900], [1920, 1080]];
  const problems = [];
  for (const [w, h] of sizes) {
    await page.setViewportSize({ width: w, height: h });
    for (const p of paths) {
      await page.goto(BASE + p, { waitUntil: 'load' });
      const r = await page.evaluate(() => {
        const top = document.querySelector('.top'), nav = document.querySelector('.top nav');
        const bar = top.getBoundingClientRect();
        const navLinks = [...nav.querySelectorAll('a')].map(a => a.getBoundingClientRect().top);
        const h1 = document.querySelector('h1').getBoundingClientRect();
        const kick = document.querySelector('.kicker')?.getBoundingClientRect();
        const cta = document.querySelector('main .btn.big')?.getBoundingClientRect();
        const callBtn = document.querySelector('.top .btn.call').getBoundingClientRect();
        const overflow = document.documentElement.scrollWidth - window.innerWidth;
        let tiny = [];
        for (const el of document.querySelectorAll('body *')) {
          if (!el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
          const cs = getComputedStyle(el);
          if (cs.display === 'none' || cs.visibility === 'hidden') continue;
          if (parseFloat(cs.fontSize) < 14) tiny.push(el.tagName + '.' + el.className + ' ' + cs.fontSize);
        }
        return { barH: bar.height, barBottom: bar.bottom, navRows: new Set(navLinks.map(Math.round)).size,
                 callTop: callBtn.top, navTop: navLinks[0], h1Top: h1.top, kickTop: kick ? kick.top : null,
                 ctaBottom: cta ? cta.bottom : null, overflow, tiny: tiny.slice(0, 3) };
      });
      const tag = `${w}x${h} ${p}`;
      if (r.overflow > 0) problems.push(`${tag}: poziomy overflow ${r.overflow}px`);
      if (r.tiny.length) problems.push(`${tag}: tekst <14px ${r.tiny.join(', ')}`);
      if (w >= 1025) {
        if (r.navRows !== 1) problems.push(`${tag}: menu w ${r.navRows} rzędach`);
        if (r.barH > 80) problems.push(`${tag}: pasek ${Math.round(r.barH)}px`);
      }
      if (w === 1280) {
        if (r.h1Top < r.barBottom || (r.kickTop !== null && r.kickTop < r.barBottom)) problems.push(`${tag}: H1/nadtytuł pod paskiem`);
        if (r.ctaBottom === null || r.ctaBottom > h) problems.push(`${tag}: CTA poza ekranem (${Math.round(r.ctaBottom)} > ${h})`);
      }
    }
  }
  return { checked: sizes.length * paths.length, problems };
}
