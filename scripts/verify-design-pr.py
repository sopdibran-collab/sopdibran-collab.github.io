#!/usr/bin/env python3
"""Captures + scrollWidth pour la PR design (nécessite serveur localhost:8000)."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/opt/cursor/artifacts/design-pr-captures")
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    "/prestations/",
    "/depannage-sav/",
    "/zones-intervention/",
    "/ventilation/",
    "/chauffage/",
    "/sanitaire/",
    "/climatisation/",
    "/sprinkler-protection-incendie/",
    "/contact/",
    "/geneve/",
]

VIEWPORTS = [(390, 844), (320, 844), (1440, 900)]

JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const base = process.env.BASE_URL || 'http://127.0.0.1:8000';
  const outDir = process.env.OUT_DIR;
  const pages = JSON.parse(process.env.PAGES_JSON);
  const viewports = JSON.parse(process.env.VP_JSON);
  const widths = [320, 360, 390, 414];
  const overflow = {};
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  page.addInitScript(() => {
    try { localStorage.setItem('sopjanitech_cookie_consent', '1'); } catch (e) {}
  });

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp[0], height: vp[1] });
    for (const p of pages) {
      const url = base + p;
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
      const slug = p.replace(/\//g, '_').replace(/^_|_$/g, '') || 'home';
      const file = path.join(outDir, `${slug}-${vp[0]}.png`);
      await page.screenshot({ path: file, fullPage: false });
    }
  }

  for (const w of widths) {
    await page.setViewportSize({ width: w, height: 844 });
    for (const p of pages) {
      await page.goto(base + p, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const sw = await page.evaluate(() => document.documentElement.scrollWidth);
      const key = `${p}@${w}`;
      overflow[key] = { scrollWidth: sw, viewport: w, ok: sw <= w };
    }
  }

  fs.writeFileSync(path.join(outDir, 'overflow-report.json'), JSON.stringify(overflow, null, 2));
  await browser.close();
  const bad = Object.entries(overflow).filter(([, v]) => !v.ok);
  if (bad.length) {
    console.error('OVERFLOW', bad.slice(0, 20));
    process.exit(1);
  }
  console.log('OK overflow checks', Object.keys(overflow).length);
})();
"""


def main():
    env = {
        **dict(subprocess.os.environ),
        "BASE_URL": "http://127.0.0.1:8000",
        "OUT_DIR": str(OUT),
        "PAGES_JSON": json.dumps(PAGES),
        "VP_JSON": json.dumps(VIEWPORTS),
    }
    script = ROOT / "scripts" / "_capture.cjs"
    script.write_text(JS, encoding="utf-8")
    subprocess.run(
        ["npx", "--yes", "playwright", "install", "chromium"],
        check=True,
        cwd=str(ROOT),
    )
    subprocess.run(["node", str(script)], check=True, env=env, cwd=str(ROOT))


if __name__ == "__main__":
    main()
