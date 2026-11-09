const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const OUT = process.env.OUT_DIR || "/opt/cursor/artifacts";
const base = "http://127.0.0.1:8000";

async function cookieShot(page, w, tag) {
  await page.setViewportSize({ width: w, height: 844 });
  await page.goto(base + "/", { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.removeItem("sopjanitech_cookie_consent"));
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForSelector("#cookieBanner:not([hidden])");
  const h = await page.locator("#cookieBanner").evaluate((el) => el.offsetHeight);
  const text = await page.locator(".cookie-banner__text").innerText();
  const hasLink = await page.locator('.cookie-banner__text a[href*="politique"]').isVisible();
  await page.locator("#cookieBanner").screenshot({
    path: path.join(OUT, `cookie-banner-${w}-${tag}.png`),
  });
  return { w, h, text: text.trim(), hasLink };
}

async function contactMetrics(page, w, tag) {
  await page.setViewportSize({ width: w, height: w < 500 ? 844 : 900 });
  await page.goto(base + "/contact/", { waitUntil: "networkidle" });
  const sw = await page.evaluate(() => document.documentElement.scrollWidth);
  await page.screenshot({
    path: path.join(OUT, `contact-${w}-${tag}.png`),
    fullPage: false,
  });
  return { w, scrollWidth: sw, ok: sw <= w };
}

let tag = process.argv[2] || "after";
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext()).newPage();
  const cookies = [];
  for (const w of [320, 360, 390, 414]) {
    cookies.push(await cookieShot(page, w, tag));
  }
  const contacts = [];
  for (const w of [320, 390, 1440]) {
    contacts.push(await contactMetrics(page, w, tag));
  }
  fs.writeFileSync(
    path.join(OUT, `qa-metrics-${tag}.json`),
    JSON.stringify({ cookies, contacts }, null, 2)
  );
  console.log(JSON.stringify({ cookies, contacts }, null, 2));
  await browser.close();
})();
