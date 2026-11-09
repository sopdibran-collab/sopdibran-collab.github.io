const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const base = "http://127.0.0.1:8000";
const MIN_PX = 12;
const PATHS = [
  "/",
  "/contact/",
  "/prestations/",
  "/zones-intervention/",
  "/a-propos/",
  "/realisations/",
  "/plan-du-site/",
  "/mentions-legales/",
  "/politique-confidentialite/",
  "/chauffage/",
  "/ventilation/",
  "/climatisation/",
  "/sanitaire/",
  "/depannage-sav/",
  "/sprinkler-protection-incendie/",
  "/geneve/",
  "/vaud/",
  "/lausanne/",
  "/nyon/",
  "/valais/",
  "/fribourg/",
  "/romont/",
  "/neuchatel/",
];
const WIDTHS = [1440, 390, 320];

function selectorHint(el) {
  const bits = [];
  if (el.id) bits.push("#" + el.id);
  if (el.className && typeof el.className === "string") {
    const c = el.className.trim().split(/\s+/).slice(0, 3).join(".");
    if (c) bits.push("." + c);
  }
  return (el.tagName.toLowerCase() + (bits.length ? bits.join("") : "")).slice(0, 120);
}

(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();
  await page.addInitScript(() => {
    try {
      localStorage.setItem("sopjanitech_cookie_consent", "1");
    } catch (e) {}
  });
  const all = [];
  for (const w of WIDTHS) {
    await page.setViewportSize({ width: w, height: w >= 1000 ? 900 : 844 });
    for (const p of PATHS) {
      await page.goto(base + p, { waitUntil: "networkidle", timeout: 60000 });
      const found = await page.evaluate((min) => {
        function visible(el) {
          const s = getComputedStyle(el);
          if (s.display === "none" || s.visibility === "hidden" || s.opacity === "0") return false;
          if (el.closest('[hidden],[aria-hidden="true"]')) return false;
          const r = el.getBoundingClientRect();
          if (r.width < 1 || r.height < 1) return false;
          if (r.bottom < 0 || r.top > innerHeight + 200) return false;
          return true;
        }
        const out = [];
        const nodes = document.querySelectorAll(
          "a, button, p, span, li, label, h1, h2, h3, h4, h5, h6, figcaption, th, td, dt, dd, small, .label, .site-footer__tagline"
        );
        for (const el of nodes) {
          if (!visible(el)) continue;
          const text = (el.innerText || "").replace(/\s+/g, " ").trim();
          if (!text || text.length < 2) continue;
          const fs = parseFloat(getComputedStyle(el).fontSize);
          if (fs + 0.05 < min) {
            out.push({
              sel: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).trim().split(/\s+/).slice(0, 2).join(".") : ""),
              fs: Math.round(fs * 100) / 100,
              sample: text.slice(0, 48),
            });
          }
        }
        return out;
      }, MIN_PX);
      for (const row of found) {
        all.push({ path: p, width: w, ...row });
      }
    }
  }
  const key = (r) => `${r.width}|${r.sel}|${r.fs}`;
  const uniq = new Map();
  for (const r of all) {
    const k = key(r);
    if (!uniq.has(k)) uniq.set(k, { ...r, pages: new Set() });
    uniq.get(k).pages.add(r.path);
  }
  const report = [...uniq.values()].map((r) => ({
    width: r.width,
    selector: r.sel,
    fontSizePx: r.fs,
    sample: r.sample,
    pages: [...r.pages].sort(),
  }));
  report.sort((a, b) => a.width - b.width || a.fontSizePx - b.fontSizePx);
  const outPath = "/opt/cursor/artifacts/font-size-scan.json";
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify({ minPx: MIN_PX, violations: report }, null, 2));
  console.log(JSON.stringify({ count: report.length, violations: report }, null, 2));
  await browser.close();
  process.exit(report.length ? 2 : 0);
})();
