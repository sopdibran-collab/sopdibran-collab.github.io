/**
 * Redirections HTTP 301 — généré par build_site.py
 * Déploiement (une fois) : npx wrangler deploy
 * Prérequis : domaine sopjanitech.ch géré par Cloudflare (DNS proxy activé).
 */
const REDIRECTS = {
  "/prestations.html": "/prestations/",
  "/contact.html": "/contact/",
  "/mentions-legales.html": "/mentions-legales/",
  "/politique-confidentialite.html": "/politique-confidentialite/"
};
const APEX_HOST = "sopjanitech.ch";

function needsTrailingSlash(pathname) {
  if (pathname === "/" || pathname.endsWith("/")) return false;
  const last = pathname.split("/").pop() || "";
  return !last.includes(".");
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
    if (needsTrailingSlash(url.pathname)) {
      return Response.redirect(`${url.origin}${url.pathname}/`, 301);
    }
    return fetch(request);
  },
};
