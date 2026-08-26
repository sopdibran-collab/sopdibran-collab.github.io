/**
 * Redirections HTTP 301 + SEO junk URLs — généré par build_site.py
 * Déploiement : push sur main (workflow) ou npx wrangler deploy
 * Prérequis : domaine sopjanitech.ch géré par Cloudflare (DNS proxy activé).
 */
const REDIRECTS = {
  "/prestations.html": "/prestations/",
  "/contact.html": "/contact/",
  "/mentions-legales.html": "/mentions-legales/",
  "/politique-confidentialite.html": "/politique-confidentialite/"
};
const BLOCK_EXACT = new Set(["/build_site.py", "/signature-mail-hostpoint.html", "/signature-mail-hostpoint-v2.html", "/signature-mail-hostpoint-v3.html"]);
const BLOCK_PREFIXES = ["/scripts/"];
const VERIFICATION_TXT = new Set(["/2a4c1f14188cf21440b6fdbad88d7e38.txt", "/4e83fba7d06a413e96b4abe69b2f5256.txt"]);
const APEX_HOST = "sopjanitech.ch";

function needsTrailingSlash(pathname) {
  if (pathname === "/" || pathname.endsWith("/")) return false;
  const last = pathname.split("/").pop() || "";
  return !last.includes(".");
}

function isBlocked(pathname) {
  if (BLOCK_EXACT.has(pathname)) return true;
  return BLOCK_PREFIXES.some((p) => pathname === p.slice(0, -1) || pathname.startsWith(p));
}

async function branded404(request, url) {
  const res = await fetch(new URL("/404.html", url.origin), request);
  const headers = new Headers(res.headers);
  headers.set("Cache-Control", "public, max-age=300");
  headers.set("X-Robots-Tag", "noindex, nofollow");
  return new Response(res.body, { status: 404, statusText: "Not Found", headers });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    let changed = false;
    // Un seul hop : http+www → https://apex (évite http://www → https://www → apex)
    if (url.protocol === "http:") {
      url.protocol = "https:";
      changed = true;
    }
    if (url.hostname === `www.${APEX_HOST}`) {
      url.hostname = APEX_HOST;
      changed = true;
    }
    if (changed) {
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === "/index.html") {
      return Response.redirect(`${url.origin}/`, 301);
    }
    const dest = REDIRECTS[url.pathname];
    if (dest) {
      return Response.redirect(`${url.origin}${dest}`, 301);
    }
    if (isBlocked(url.pathname)) {
      return branded404(request, url);
    }
    if (needsTrailingSlash(url.pathname)) {
      return Response.redirect(`${url.origin}${url.pathname}/`, 301);
    }
    const originRes = await fetch(request);
    if (VERIFICATION_TXT.has(url.pathname)) {
      const headers = new Headers(originRes.headers);
      headers.set("X-Robots-Tag", "noindex, nofollow");
      return new Response(originRes.body, {
        status: originRes.status,
        statusText: originRes.statusText,
        headers,
      });
    }
    return originRes;
  },
};
