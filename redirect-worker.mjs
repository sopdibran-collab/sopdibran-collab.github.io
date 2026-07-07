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

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.hostname === `www.${APEX_HOST}`) {
      url.hostname = APEX_HOST;
      return Response.redirect(url.toString(), 301);
    }
    const dest = REDIRECTS[url.pathname];
    if (dest) {
      return Response.redirect(`${url.origin}${dest}`, 301);
    }
    return fetch(request);
  },
};
