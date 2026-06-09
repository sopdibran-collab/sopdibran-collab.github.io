#!/usr/bin/env python3
"""Generate Sopjani Tech static site pages."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://www.sopjanitech.ch"
PHONE = "+41799326862"
PHONE_DISP = "+41 79 932 68 62"
EMAIL = "sopjanitech@gmail.com"
WA = "https://wa.me/41799326862"
ADDRESS_STREET = "Rue Pierre de Savoie 9"
ADDRESS_POSTAL = "1680"
ADDRESS_LOCALITY = "Romont FR"
ADDRESS_FULL = "Rue Pierre de Savoie 9, 1680 Romont FR"
HOURS = "Lundi au vendredi, 8h00 – 16h30"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Rue+Pierre+de+Savoie+9,+1680+Romont"

SERVICES = [
    ("chauffage", "Chauffage", "Installation, entretien et dépannage de systèmes de chauffage."),
    ("ventilation", "Ventilation", "Ventilation et traitement de l'air pour bâtiments."),
    ("climatisation", "Climatisation", "Étude et installation de systèmes de climatisation."),
    ("depannage-sav", "Dépannage SAV", "Maintenance et dépannage de vos installations CVC."),
    ("sprinkler-protection-incendie", "Sprinkler / protection incendie", "Réseaux sprinkler en sous-traitance spécialisée."),
    ("sanitaire", "Sanitaire", "Travaux sanitaires et interventions sur réseaux existants."),
]

ZONES = [
    ("geneve", "Genève", "la région de Genève"),
    ("vaud", "Vaud", "le canton de Vaud"),
    ("lausanne", "Lausanne", "Lausanne et environs"),
    ("nyon", "Nyon", "la région de Nyon"),
    ("valais", "Valais", "le canton du Valais"),
    ("fribourg", "Fribourg", "le canton de Fribourg"),
]

ORG_SCHEMA = {
    "@type": "HVACBusiness",
    "@id": f"{SITE}/#organization",
    "name": "Sopjani Tech Sàrl",
    "url": SITE,
    "telephone": PHONE,
    "email": EMAIL,
    "address": {
        "@type": "PostalAddress",
        "streetAddress": ADDRESS_STREET,
        "postalCode": ADDRESS_POSTAL,
        "addressLocality": ADDRESS_LOCALITY,
        "addressCountry": "CH",
    },
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "08:00",
        "closes": "16:30",
    }],
    "areaServed": [
        {"@type": "AdministrativeArea", "name": n} for _, n, _ in ZONES
    ],
    "priceRange": "$$",
    "currenciesAccepted": "CHF",
    "inLanguage": "fr-CH",
}


def extract_css():
    css_path = ROOT / "css" / "main.css"
    if css_path.exists() and ":root" in css_path.read_text(encoding="utf-8"):
        return
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<style>(.*?)</style>", idx, re.DOTALL)
    css = m.group(1).strip() if m else ""
    if not css:
        import subprocess
        try:
            old = subprocess.check_output(["git", "show", "HEAD:index.html"], text=True, cwd=ROOT)
            m2 = re.search(r"<style>(.*?)</style>", old, re.DOTALL)
            css = m2.group(1).strip() if m2 else ""
        except Exception:
            css = ""
    extra = """
.breadcrumbs { padding: 16px 0 0; font-size: 13px; color: var(--c-muted); }
.breadcrumbs ol { list-style: none; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.breadcrumbs li + li::before { content: "/"; margin-right: 6px; color: var(--c-faint); }
.breadcrumbs a:hover { color: var(--c-accent); }
.page-hero { padding: 56px 0 48px; }
.page-hero .hero-sub { max-width: 640px; }
.hub-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--c-border); border: 1px solid var(--c-border); border-radius: var(--radius); overflow: hidden; margin-top: 40px; }
.hub-card { background: var(--c-surface); padding: 28px 24px; display: flex; flex-direction: column; gap: 12px; transition: background .2s; }
.hub-card:hover { background: var(--c-bg3); }
.hub-card h3 { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--c-text); }
.hub-card p { font-size: 14px; color: var(--c-muted); line-height: 1.65; flex: 1; }
.hub-card .link-arrow { font-size: 13px; font-weight: 600; color: var(--c-accent); }
.content-section { padding: 64px 0; }
.content-section.alt { background: var(--c-bg3); }
.prose-block { max-width: 720px; }
.prose-block p { margin-bottom: 16px; color: var(--c-muted); font-size: 16px; line-height: 1.7; }
.prose-block h3 { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--c-text); margin: 28px 0 12px; }
.bullet-list { list-style: none; display: grid; gap: 10px; margin-top: 16px; }
.bullet-list li { padding-left: 18px; position: relative; color: var(--c-muted); font-size: 15px; line-height: 1.65; }
.bullet-list li::before { content: ""; position: absolute; left: 0; top: 11px; width: 8px; height: 2px; background: var(--c-accent); border-radius: 2px; }
.cta-band { background: var(--c-dark); color: #fff; padding: 48px 0; text-align: center; }
.cta-band h2 { font-family: var(--font-display); font-size: clamp(24px, 3vw, 36px); font-weight: 700; margin-bottom: 12px; }
.cta-band p { color: rgba(255,255,255,.75); margin-bottom: 24px; max-width: 520px; margin-left: auto; margin-right: auto; }
.cta-band .btn-primary { margin: 0 6px 8px; }
.zone-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
.zone-pill { display: inline-flex; padding: 10px 18px; background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius); font-size: 14px; font-weight: 600; transition: border-color .2s; }
.zone-pill:hover { border-color: var(--c-accent); color: var(--c-accent); }
.contact-form { display: grid; gap: 16px; max-width: 520px; margin-top: 24px; }
.contact-form label { display: block; font-size: 13px; font-weight: 600; color: var(--c-text); margin-bottom: 6px; }
.contact-form input, .contact-form select, .contact-form textarea { width: 100%; padding: 12px 14px; border: 1px solid var(--c-border); border-radius: var(--radius); font-family: var(--font-body); font-size: 15px; background: var(--c-surface); }
.contact-form textarea { min-height: 120px; resize: vertical; }
header .header-inner { height: 56px; gap: 16px; }
header .logo-wrap img { width: 48px !important; height: auto; }
header .logo-text { font-size: 15px; }
header .logo-sub { font-size: 9px; }
header .header-cta { gap: 8px; }
header .tel-btn { font-size: 13px; gap: 6px; }
header .header-cta .btn-primary { padding: 9px 14px; font-size: 11px; letter-spacing: 0.06em; }
header .nav-main { display: flex; align-items: center; gap: 18px; }
header .nav-item { position: relative; }
header .nav-main > a, header .nav-trigger {
  font-family: var(--font-display); font-size: 12px; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--c-muted); transition: color 0.2s; white-space: nowrap;
}
header .nav-main > a { padding: 6px 0; }
header .nav-trigger {
  background: none; border: none; cursor: pointer; padding: 6px 0;
  display: inline-flex; align-items: center; gap: 5px;
}
header .nav-trigger::after {
  content: ""; width: 0; height: 0; border-left: 3px solid transparent; border-right: 3px solid transparent;
  border-top: 4px solid currentColor; margin-top: 1px; opacity: 0.65; transition: transform 0.2s;
}
header .nav-item.is-open .nav-trigger::after { transform: rotate(180deg); }
header .nav-main > a:hover, header .nav-trigger:hover, header .nav-item.is-open .nav-trigger { color: var(--c-accent); }
header .nav-submenu {
  display: none; position: absolute; top: calc(100% + 6px); left: 0; min-width: 220px;
  background: var(--c-bg2); border: 1px solid var(--c-border); border-radius: var(--radius);
  box-shadow: 0 8px 24px rgba(16, 32, 43, 0.1); padding: 6px 0; z-index: 300;
}
header .nav-item.is-open .nav-submenu { display: block; }
header .nav-submenu a {
  display: block; padding: 8px 14px; font-family: var(--font-body); font-size: 13px; font-weight: 500;
  letter-spacing: normal; text-transform: none; color: var(--c-muted);
}
header .nav-submenu a:hover { background: var(--c-bg3); color: var(--c-accent); }
header .nav-submenu-all { font-weight: 600; border-bottom: 1px solid var(--c-border2); margin-bottom: 2px; padding-bottom: 8px; }
.mobile-nav-group { border-bottom: 1px solid var(--c-border2); }
.mobile-nav-toggle {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  font-family: var(--font-display); font-size: 14px; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--c-muted); background: none; border: none; cursor: pointer;
  padding: 12px 0; text-align: left;
}
.mobile-nav-toggle::after {
  content: ""; width: 0; height: 0; border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-top: 5px solid currentColor; opacity: 0.6; transition: transform 0.2s;
}
.mobile-nav-group.is-open .mobile-nav-toggle { color: var(--c-accent); }
.mobile-nav-group.is-open .mobile-nav-toggle::after { transform: rotate(180deg); }
.mobile-nav-panel { display: none; padding: 0 0 10px 10px; }
.mobile-nav-group.is-open .mobile-nav-panel { display: flex; flex-direction: column; gap: 2px; }
.mobile-nav-panel a {
  font-size: 13px !important; text-transform: none !important; letter-spacing: normal !important;
  padding: 8px 0 !important; border-bottom: none !important; color: var(--c-muted);
}
.mobile-nav-panel a:hover { color: var(--c-accent); }
@media (max-width: 1024px) { header .nav-main { display: none !important; } .hub-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 768px) { .hub-grid { grid-template-columns: 1fr; } .page-hero { padding: 40px 0 32px; } }
"""
    (ROOT / "css" / "main.css").write_text(css + extra, encoding="utf-8")


def schema_json(graph):
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def breadcrumbs_html(items):
    lis = []
    for i, (label, url) in enumerate(items):
        if i < len(items) - 1:
            lis.append(f'<li><a href="{url}">{label}</a></li>')
        else:
            lis.append(f"<li aria-current=\"page\">{label}</li>")
    return f'<nav class="breadcrumbs" aria-label="Fil d\'Ariane"><ol>{"".join(lis)}</ol></nav>'


def header():
    svc_sub = '<a href="/prestations/" class="nav-submenu-all">Toutes les prestations</a>' + "".join(
        f'<a href="/{s}/" role="menuitem">{n}</a>' for s, n, _ in SERVICES
    )
    zone_sub = '<a href="/zones-intervention/" class="nav-submenu-all">Toutes les zones</a>' + "".join(
        f'<a href="/{z}/" role="menuitem">{n}</a>' for z, n, _ in ZONES
    )
    mobile_svc_panel = '<a href="/prestations/">Toutes les prestations</a>' + "".join(
        f'<a href="/{s}/">{n}</a>' for s, n, _ in SERVICES
    )
    mobile_zones_panel = '<a href="/zones-intervention/">Toutes les zones</a>' + "".join(
        f'<a href="/{z}/">{n}</a>' for z, n, _ in ZONES
    )
    mobile_svc = f"""<div class="mobile-nav-group">
      <button type="button" class="mobile-nav-toggle" aria-expanded="false">Prestations</button>
      <div class="mobile-nav-panel">{mobile_svc_panel}</div>
    </div>"""
    mobile_zones = f"""<div class="mobile-nav-group">
      <button type="button" class="mobile-nav-toggle" aria-expanded="false">Zones d'intervention</button>
      <div class="mobile-nav-panel">{mobile_zones_panel}</div>
    </div>"""
    return f"""<header>
  <div class="container">
    <div class="header-inner">
      <a href="/" class="logo-wrap" aria-label="Sopjani Tech Sàrl – Accueil">
        <img src="/assets/logo.png" alt="Logo Sopjani Tech Sàrl" width="48" height="48" loading="eager">
        <div>
          <div class="logo-text">SOPJANI TECH</div>
          <div class="logo-sub">Sàrl · Suisse</div>
        </div>
      </a>
      <nav class="nav-main" aria-label="Navigation principale">
        <a href="/">Accueil</a>
        <div class="nav-item">
          <button type="button" class="nav-trigger" aria-expanded="false" aria-haspopup="true">Prestations</button>
          <div class="nav-submenu" role="menu">{svc_sub}</div>
        </div>
        <div class="nav-item">
          <button type="button" class="nav-trigger" aria-expanded="false" aria-haspopup="true">Zones d'intervention</button>
          <div class="nav-submenu" role="menu">{zone_sub}</div>
        </div>
        <a href="/a-propos/">À propos</a>
        <a href="/contact/">Contact</a>
      </nav>
      <div class="header-cta">
        <a href="tel:{PHONE}" class="tel-btn" aria-label="Appeler Sopjani Tech">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 014.69 12 19.79 19.79 0 011.61 3.4 2 2 0 013.6 1.22h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L7.91 8.8a16 16 0 006.29 6.29l.96-.96a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
          {PHONE_DISP}
        </a>
        <a href="/contact/" class="btn btn-primary">Demander un devis</a>
      </div>
      <button class="burger" id="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobileNav" aria-label="Navigation mobile">
    <a href="/">Accueil</a>
    {mobile_svc}
    {mobile_zones}
    <a href="/a-propos/">À propos</a>
    <a href="/contact/">Contact</a>
    <a href="tel:{PHONE}" style="color:var(--c-accent)">{PHONE_DISP}</a>
  </nav>
</header>"""


def footer():
    svc = "".join(f'<li><a href="/{s}/">{n}</a></li>' for s, n, _ in SERVICES)
    zones = '<li><a href="/zones-intervention/">Toutes les zones</a></li>' + "".join(
        f'<li><a href="/{z}/">{n}</a></li>' for z, n, _ in ZONES
    )
    return f"""<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="footer-col-title">Services</div>
        <ul class="footer-links">{svc}</ul>
      </div>
      <div>
        <div class="footer-col-title">Zones</div>
        <ul class="footer-links">{zones}</ul>
      </div>
      <div>
        <div class="footer-col-title">Entreprise</div>
        <ul class="footer-links">
          <li><a href="/">Accueil</a></li>
          <li><a href="/a-propos/">À propos</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">Contact</div>
        <ul class="footer-contact-list">
          <li><a href="tel:{PHONE}">{PHONE_DISP}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="{WA}" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
          <li style="margin-top:8px;font-size:13px;"><a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a></li>
          <li style="font-size:13px;color:var(--c-faint);">{HOURS}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-copy">© 2024 Sopjani Tech Sàrl · Suisse · Tous droits réservés</p>
      <p class="footer-seo">Chauffage · Ventilation · Climatisation · Dépannage SAV · Sprinkler · Sanitaire · Suisse romande</p>
    </div>
  </div>
</footer>"""


def faq_html(items):
    blocks = []
    for q, a in items:
        blocks.append(f"""<div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
  <button class="faq-q" aria-expanded="false"><span itemprop="name">{q}</span><span class="faq-icon" aria-hidden="true"></span></button>
  <div class="faq-a" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer"><span itemprop="text">{a}</span></div>
</div>""")
    return f'<div class="faq-list" itemscope itemtype="https://schema.org/FAQPage">{"".join(blocks)}</div>'


def cta_band(title="Besoin d'un devis ou d'un dépannage ?", text="Contactez-nous pour décrire votre besoin. Nous vous répondrons dans les meilleurs délais."):
    return f"""<section class="cta-band" aria-label="Appel à l'action">
  <div class="container">
    <h2>{title}</h2>
    <p>{text}</p>
    <a href="tel:{PHONE}" class="btn btn-primary">{PHONE_DISP}</a>
    <a href="/contact/" class="btn btn-ghost" style="border-color:rgba(255,255,255,.3);color:#fff;">Demander un devis</a>
  </div>
</section>"""


def page_shell(title, description, canonical, schema_graph, body, crumbs=None):
    crumbs_html = breadcrumbs_html(crumbs) if crumbs else ""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Sopjani Tech Sàrl">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/main.css">
  <script type="application/ld+json">{schema_json(schema_graph)}</script>
</head>
<body>
{header()}
<main>
{crumbs_html}
{body}
</main>
{footer()}
<script src="/js/main.js"></script>
</body>
</html>"""


def write_page(path_parts, content):
    d = ROOT.joinpath(*path_parts[:-1])
    d.mkdir(parents=True, exist_ok=True)
    (d / path_parts[-1]).write_text(content, encoding="utf-8")


def breadcrumb_schema(crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs, 1):
        items.append({
            "@type": "ListItem", "position": i, "name": name,
            "item": SITE + url if url != "/" else SITE + "/"
        })
    return {"@type": "BreadcrumbList", "itemListElement": items}


def service_page(slug, name, title, desc, h1, intro, problems, interventions, clients, process, zone_slugs, related_svc, faq):
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (name, url)]
    zones_html = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES if z in zone_slugs)
    related = "".join(f'<a class="zone-pill" href="/{s}/">{n}</a>' for s, n, _ in SERVICES if s in related_svc)
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Prestation</span>
    <div class="rule"></div>
    <h1 id="page-h1">{h1}</h1>
    <p class="hero-sub">{intro}</p>
    <div class="hero-ctas" style="margin-top:24px;">
      <a href="tel:{PHONE}" class="btn btn-primary">{PHONE_DISP}</a>
      <a href="/contact/" class="btn btn-ghost">Demander un devis</a>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section" aria-labelledby="problems-title">
  <div class="container prose-block">
    <h2 class="section-title" id="problems-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:20px;">Problématiques traitées</h2>
    {problems}
  </div>
</section>
<section class="content-section alt" aria-labelledby="interventions-title">
  <div class="container prose-block">
    <h2 class="section-title" id="interventions-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:20px;">Types d'interventions</h2>
    {interventions}
  </div>
</section>
<section class="content-section" aria-labelledby="clients-title">
  <div class="container prose-block">
    <h2 class="section-title" id="clients-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:20px;">Pour quels bâtiments</h2>
    {clients}
    <h3 style="margin-top:28px;">Déroulement d'une intervention</h3>
    {process}
  </div>
</section>
<section class="content-section alt" aria-labelledby="zones-title">
  <div class="container">
    <h2 class="section-title" id="zones-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:12px;">Zones desservies</h2>
    <p class="section-lead">Sopjani Tech Sàrl intervient en Suisse romande. Contactez-nous pour vérifier la disponibilité dans votre secteur.</p>
    <div class="zone-links">{zones_html}</div>
    <p style="margin-top:20px;"><a href="/zones-intervention/">Voir toutes les zones d'intervention →</a></p>
  </div>
</section>
<section class="content-section" aria-labelledby="related-title">
  <div class="container">
    <h2 class="section-title" id="related-title" style="font-size:clamp(22px,2.5vw,32px);margin-bottom:12px;">Prestations connexes</h2>
    <div class="zone-links">{related}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:24px;">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>
{cta_band()}"""
    graph = [
        ORG_SCHEMA,
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": SITE, "name": "Sopjani Tech Sàrl", "publisher": {"@id": f"{SITE}/#organization"}},
        breadcrumb_schema(crumbs),
        {"@type": "Service", "name": name, "provider": {"@id": f"{SITE}/#organization"}, "areaServed": {"@type": "AdministrativeArea", "name": "Suisse romande"}, "description": desc, "url": SITE + url},
    ]
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def zone_page(slug, name, region, title, desc, h1, local_text, faq, svc_slugs, related_zones):
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/"), (name, url)]
    svc = "".join(f'<a class="zone-pill" href="/{s}/">{n}</a>' for s, n, _ in SERVICES if s in svc_slugs)
    rz = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES if z in related_zones)
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Zone d'intervention</span>
    <div class="rule"></div>
    <h1 id="page-h1">{h1}</h1>
    <p class="hero-sub">Sopjani Tech Sàrl intervient dans {region} pour vos projets et dépannages en chauffage, ventilation, climatisation et installations techniques. Contactez-nous pour vérifier la disponibilité selon votre localisation.</p>
    <div class="hero-ctas" style="margin-top:24px;">
      <a href="tel:{PHONE}" class="btn btn-primary">{PHONE_DISP}</a>
      <a href="/contact/" class="btn btn-ghost">Demander un devis</a>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section" aria-labelledby="local-title">
  <div class="container prose-block">
    <h2 class="section-title" id="local-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:20px;">Interventions dans {region}</h2>
    {local_text}
    <p><strong>Note :</strong> il ne s'agit pas d'une agence locale mais d'une zone desservie par notre équipe mobile en Suisse romande.</p>
  </div>
</section>
<section class="content-section alt" aria-labelledby="svc-title">
  <div class="container">
    <h2 class="section-title" id="svc-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:12px;">Services disponibles</h2>
    <div class="zone-links">{svc}</div>
  </div>
</section>
<section class="content-section" aria-labelledby="near-title">
  <div class="container">
    <h2 class="section-title" id="near-title" style="font-size:clamp(22px,2.5vw,32px);margin-bottom:12px;">Autres zones proches</h2>
    <div class="zone-links">{rz}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:24px;">FAQ — {name}</h2>
    {faq_html(faq)}
  </div>
</section>
{cta_band(f"Un projet à {name} ?", "Décrivez votre besoin par téléphone, email ou WhatsApp.")}"""
    graph = [
        ORG_SCHEMA,
        breadcrumb_schema(crumbs),
    ]
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def build_home():
    svc_cards = "".join(
        f'<a class="hub-card" href="/{s}/"><h3>{n}</h3><p>{d}</p><span class="link-arrow">En savoir plus →</span></a>'
        for s, n, d in SERVICES
    )
    zone_pills = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES)
    faq = [
        ("Quels services proposez-vous ?", "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler en sous-traitance et sanitaire. Consultez nos pages prestations pour le détail."),
        ("Dans quelles zones intervenez-vous ?", "Principalement en Suisse romande : Genève, Vaud, Lausanne, Nyon, Valais et Fribourg. D'autres cantons peuvent être couverts selon la nature du projet."),
        ("Comment obtenir un devis ?", f"Par téléphone ({PHONE_DISP}), email ({EMAIL}) ou WhatsApp. Indiquez le type de bâtiment, la localisation et la nature du besoin."),
        ("Intervenez-vous en dépannage ?", "Oui. Contactez-nous pour évaluer votre situation. La disponibilité dépend de la nature de la panne et du secteur."),
    ]
    body = f"""
<section class="hero" aria-labelledby="hero-h1">
  <div class="container">
    <div class="hero-grid">
      <div class="hero-content">
        <div class="hero-eyebrow"><span class="label">Étude · Installation · Maintenance · Dépannage</span></div>
        <h1 id="hero-h1">Chauffage, ventilation, climatisation et dépannage en Suisse romande</h1>
        <p class="hero-sub">Nous assurons l'étude, l'installation, la maintenance et le dépannage de vos équipements techniques avec rigueur et fiabilité.</p>
        <div class="hero-ctas">
          <a href="tel:{PHONE}" class="btn btn-primary">{PHONE_DISP}</a>
          <a href="/contact/" class="btn btn-ghost">Demander un devis</a>
        </div>
        <div class="hero-stats">
          <div class="stat"><div class="stat-val">6</div><div class="stat-label">Domaines de prestations</div></div>
          <div class="stat"><div class="stat-val">CH</div><div class="stat-label">Suisse romande</div></div>
          <div class="stat"><div class="stat-val">24h</div><div class="stat-label">Réactivité dépannage</div></div>
        </div>
      </div>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="services content-section" aria-labelledby="svc-title">
  <div class="container">
    <span class="label">Nos prestations</span>
    <div class="rule"></div>
    <h2 class="section-title" id="svc-title">Services techniques du bâtiment</h2>
    <p class="section-lead" style="margin-top:16px;">Installation, maintenance et dépannage pour bâtiments résidentiels, commerciaux et industriels.</p>
    <div class="hub-grid">{svc_cards}</div>
    <p style="margin-top:24px;"><a href="/prestations/">Voir toutes les prestations →</a></p>
  </div>
</section>
<div class="section-divider"></div>
<section class="expertise content-section alt" aria-labelledby="why-title">
  <div class="container">
    <span class="label">Pourquoi nous choisir</span>
    <div class="rule"></div>
    <h2 class="section-title" id="why-title">Une exécution technique rigoureuse</h2>
    <div class="expertise-grid" style="margin-top:32px;">
      <div class="prose-block">
        <p>En Suisse, les exigences d'installation technique sont élevées. Sopjani Tech Sàrl y répond avec méthode, transparence et engagement.</p>
        <h3>Rigueur d'exécution</h3>
        <p>Nos travaux sont réalisés dans le respect des normes en vigueur (SIA, SUVA, AEAI selon le type d'installation). Documentation et traçabilité des interventions.</p>
        <h3>Interlocuteur direct</h3>
        <p>Vous échangez directement avec l'équipe technique qui réalise les travaux.</p>
        <h3>Devis transparent</h3>
        <p>Offres claires et détaillées, adaptées à votre budget et à vos contraintes techniques.</p>
      </div>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="zones content-section" aria-labelledby="zones-title">
  <div class="container">
    <span class="label">Zones d'intervention</span>
    <div class="rule"></div>
    <h2 class="section-title" id="zones-title">Suisse romande et alentours</h2>
    <p class="section-lead" style="margin-top:16px;">Nous intervenons principalement en Suisse romande et pouvons nous déplacer dans d'autres cantons selon la nature des travaux.</p>
    <div class="zone-links">{zone_pills}</div>
    <p style="margin-top:20px;"><a href="/zones-intervention/">Toutes nos zones d'intervention →</a></p>
  </div>
</section>
<div class="section-divider"></div>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>
{cta_band()}"""
    graph = [ORG_SCHEMA, {"@type": "WebSite", "@id": f"{SITE}/#website", "url": SITE, "name": "Sopjani Tech Sàrl", "publisher": {"@id": f"{SITE}/#organization"}}]
    write_page(["index.html"], page_shell(
        "Sopjani Tech Sàrl | Chauffage, ventilation, climatisation et dépannage en Suisse romande",
        "Sopjani Tech Sàrl : étude, installation, maintenance et dépannage en chauffage, ventilation, climatisation et protection incendie en Suisse romande.",
        SITE + "/", graph, body))


def build_prestations():
    cards = "".join(f'<a class="hub-card" href="/{s}/"><h3>{n}</h3><p>{d}</p><span class="link-arrow">Voir la prestation →</span></a>' for s, n, d in SERVICES)
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Prestations</span>
    <div class="rule"></div>
    <h1 id="page-h1">Nos prestations en chauffage, ventilation et climatisation</h1>
    <p class="hero-sub">Sopjani Tech Sàrl conçoit, installe, entretient et dépanne vos installations techniques en Suisse romande.</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container">
    <div class="hub-grid">{cards}</div>
  </div>
</section>
{cta_band()}"""
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/")]
    graph = [ORG_SCHEMA, breadcrumb_schema(crumbs)]
    write_page(["prestations", "index.html"], page_shell(
        "Prestations CVC | Chauffage, ventilation, climatisation | Sopjani Tech Sàrl",
        "Découvrez les prestations de Sopjani Tech Sàrl : chauffage, ventilation, climatisation, dépannage SAV, sprinkler et sanitaire en Suisse romande.",
        SITE + "/prestations/", graph, body, crumbs))


def build_zones_hub():
    cards = "".join(f'<a class="hub-card" href="/{z}/"><h3>{n}</h3><p>Interventions CVC dans {r}</p><span class="link-arrow">Voir la zone →</span></a>' for z, n, r in ZONES)
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Géographie</span>
    <div class="rule"></div>
    <h1 id="page-h1">Nos zones d'intervention en Suisse romande</h1>
    <p class="hero-sub">Sopjani Tech Sàrl intervient dans les cantons et agglomérations ci-dessous. Contactez-nous pour vérifier la disponibilité dans votre secteur.</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container">
    <div class="hub-grid">{cards}</div>
    <div class="prose-block" style="margin-top:40px;">
      <p>Nous pouvons également étudier des demandes en Neuchâtel, Berne ou ailleurs en Suisse selon la nature du projet. [À COMPLÉTER : périmètre exact hors zones listées]</p>
    </div>
  </div>
</section>
{cta_band("Votre commune n'est pas listée ?", "Contactez-nous pour vérifier la faisabilité d'une intervention.")}"""
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/")]
    graph = [ORG_SCHEMA, breadcrumb_schema(crumbs)]
    write_page(["zones-intervention", "index.html"], page_shell(
        "Zones d'intervention | Suisse romande | Sopjani Tech Sàrl",
        "Sopjani Tech Sàrl intervient en Suisse romande : Genève, Vaud, Lausanne, Nyon, Valais, Fribourg. Vérifiez la disponibilité pour votre secteur.",
        SITE + "/zones-intervention/", graph, body, crumbs))


def build_about():
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Entreprise</span>
    <div class="rule"></div>
    <h1 id="page-h1">À propos de Sopjani Tech Sàrl</h1>
    <p class="hero-sub">Entreprise technique spécialisée en chauffage, ventilation, climatisation, sanitaire, sprinkler et dépannage en Suisse romande.</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container prose-block">
    <h2 class="section-title" style="font-size:clamp(26px,3vw,40px);">Qui sommes-nous</h2>
    <p>[À COMPLÉTER : histoire de l'entreprise, fondateur, année de création]</p>
    <h3>Notre mission</h3>
    <p>Accompagner les maîtres d'ouvrage, régies et propriétaires dans l'installation, la maintenance et le dépannage de leurs équipements CVC avec une approche rigoureuse et transparente.</p>
    <h3>Notre approche</h3>
    <p>Analyse du besoin, proposition technique claire, exécution soignée et suivi des installations. Respect des normes en vigueur selon le type de travaux (SIA, SUVA, AEAI).</p>
    <h3>Zones couvertes</h3>
    <p>Principalement Suisse romande : Genève, Vaud, Lausanne, Nyon, Valais, Fribourg. Autres cantons possibles selon projet.</p>
    <h3>Coordonnées</h3>
    <p>Téléphone : <a href="tel:{PHONE}">{PHONE_DISP}</a><br>Email : <a href="mailto:{EMAIL}">{EMAIL}</a><br>Adresse : <a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a><br>Horaires : {HOURS}</p>
  </div>
</section>
{cta_band()}"""
    crumbs = [("Accueil", "/"), ("À propos", "/a-propos/")]
    graph = [ORG_SCHEMA, {"@type": "AboutPage", "name": "À propos", "url": SITE + "/a-propos/"}, breadcrumb_schema(crumbs)]
    write_page(["a-propos", "index.html"], page_shell(
        "À propos | Sopjani Tech Sàrl — CVC en Suisse romande",
        "Sopjani Tech Sàrl : entreprise technique en chauffage, ventilation, climatisation et dépannage en Suisse romande.",
        SITE + "/a-propos/", graph, body, crumbs))


def build_contact():
    faq = [
        ("Comment nous joindre ?", f"Par téléphone ({PHONE_DISP}), email ({EMAIL}) ou WhatsApp."),
        ("Quelles informations fournir pour un devis ?", "Type de bâtiment, localisation (canton/commune), nature du besoin (installation, maintenance, dépannage) et urgence éventuelle."),
        ("Horaires de contact", HOURS + ". Pour un dépannage, contactez-nous par téléphone ou WhatsApp."),
    ]
    body = f"""
<section class="contact page-hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Contact</span>
    <div class="rule"></div>
    <h1 id="page-h1">Contactez Sopjani Tech Sàrl</h1>
    <p class="section-lead" style="margin-top:16px;">Devis, maintenance ou dépannage : décrivez votre besoin et nous vous orienterons vers la solution adaptée.</p>
    <div class="contact-inner" style="grid-template-columns:1fr 1fr;gap:48px;margin-top:40px;">
      <div>
        <div class="contact-methods">
          <a href="tel:{PHONE}" class="contact-method" aria-label="Appeler Sopjani Tech">
            <div><div class="cm-label">Téléphone</div><div class="cm-value">{PHONE_DISP}</div></div>
          </a>
          <a href="mailto:{EMAIL}" class="contact-method" aria-label="Envoyer un email">
            <div><div class="cm-label">Email</div><div class="cm-value">{EMAIL}</div></div>
          </a>
          <a href="{WA}" class="contact-method" target="_blank" rel="noopener noreferrer" aria-label="Contacter via WhatsApp">
            <div><div class="cm-label">WhatsApp</div><div class="cm-value">Envoyer un message</div></div>
          </a>
          <a href="{MAP_URL}" class="contact-method" target="_blank" rel="noopener noreferrer" aria-label="Voir l'adresse sur la carte">
            <div><div class="cm-label">Adresse</div><div class="cm-value">{ADDRESS_FULL}</div></div>
          </a>
          <div class="contact-method" style="cursor:default;">
            <div><div class="cm-label">Horaires</div><div class="cm-value">{HOURS}</div></div>
          </div>
        </div>
        <p style="margin-top:24px;font-size:14px;color:var(--c-muted);">Zone desservie : Suisse romande et alentours selon projet.</p>
      </div>
      <div>
        <h2 class="section-title" style="font-size:24px;margin-bottom:8px;">Formulaire de demande</h2>
        <p style="font-size:14px;color:var(--c-muted);margin-bottom:16px;">[À COMPLÉTER : branchement formulaire — Formspree, Netlify Forms, etc.]</p>
        <form class="contact-form" action="#" method="post">
          <div><label for="name">Nom</label><input id="name" name="name" type="text" required autocomplete="name"></div>
          <div><label for="phone">Téléphone</label><input id="phone" name="phone" type="tel" required autocomplete="tel"></div>
          <div><label for="canton">Canton / Commune</label><input id="canton" name="canton" type="text" required></div>
          <div><label for="need">Type de besoin</label>
            <select id="need" name="need" required>
              <option value="">Choisir…</option>
              <option>Devis installation</option>
              <option>Maintenance / entretien</option>
              <option>Dépannage</option>
              <option>Autre</option>
            </select>
          </div>
          <div><label for="message">Message</label><textarea id="message" name="message" required></textarea></div>
          <button type="submit" class="btn btn-primary">Envoyer la demande</button>
        </form>
      </div>
    </div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>"""
    crumbs = [("Accueil", "/"), ("Contact", "/contact/")]
    graph = [ORG_SCHEMA, {"@type": "ContactPage", "name": "Contact", "url": SITE + "/contact/"}, breadcrumb_schema(crumbs)]
    write_page(["contact", "index.html"], page_shell(
        "Contact et devis | Sopjani Tech Sàrl",
        f"Contactez Sopjani Tech Sàrl par téléphone, email ou WhatsApp pour un devis ou un dépannage en Suisse romande. {PHONE_DISP}.",
        SITE + "/contact/", graph, body, crumbs))


def build_services():
    bullets = lambda items: "<ul class=\"bullet-list\">" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    process = "<ol class=\"bullet-list\">" + "".join(f"<li>{s}</li>" for s in [
        "Prise de contact et description du besoin",
        "Visite ou diagnostic sur place si nécessaire",
        "Proposition technique et devis détaillé",
        "Réalisation des travaux et mise en service",
        "Suivi et maintenance si souhaitée",
    ]) + "</ol>"
    clients = "<p>Résidentiel (immeubles, villas, PPE), commercial (bureaux, commerces, hôtels), industriel et public (ERP), selon faisabilité technique.</p>"

    service_page("chauffage", "Chauffage",
        "Chauffage | Installation, entretien et dépannage | Sopjani Tech Sàrl",
        "Sopjani Tech Sàrl : étude, installation, maintenance et dépannage de systèmes de chauffage en Suisse romande.",
        "Chauffage : installation, entretien et dépannage",
        "Nous prenons en charge vos besoins en chauffage, de l'étude à la maintenance, pour assurer le confort thermique et la fiabilité de vos installations.",
        "<p>Pannes de chauffage, baisse de rendement, remplacement d'équipement, rénovation de réseaux ou mise en service de nouvelles installations.</p>",
        bullets(["Étude et dimensionnement", "Installation de chaudières et pompes à chaleur [À COMPLÉTER : équipements précis]", "Entretien et maintenance", "Dépannage et remise en service", "Rénovation de réseaux existants"]),
        clients, process, ["geneve", "lausanne", "vaud", "valais", "fribourg"], ["ventilation", "climatisation", "depannage-sav"],
        [("Intervenez-vous en dépannage chauffage ?", "Oui. Contactez-nous pour évaluer la situation. La disponibilité dépend du secteur et de la nature de la panne."),
         ("Proposez-vous des contrats d'entretien ?", "[À COMPLÉTER : formules d'entretien proposées]")])

    service_page("ventilation", "Ventilation",
        "Ventilation | Traitement de l'air et dépannage | Sopjani Tech Sàrl",
        "Étude, installation et maintenance de systèmes de ventilation pour bâtiments en Suisse romande.",
        "Ventilation et traitement de l'air",
        "Mise en place et suivi de systèmes de ventilation pour le confort, la qualité de l'air et la maîtrise énergétique de votre bâtiment.",
        "<p>Qualité d'air insuffisante, dysfonctionnements VMC, besoin de renouvellement d'air ou rénovation de réseaux existants.</p>",
        bullets(["Conception et dimensionnement", "Installation de gaines et équipements", "Réglages et mise en service", "Maintenance et contrôles", "Réhabilitation de réseaux"]),
        clients, process, ["geneve", "lausanne", "nyon", "vaud"], ["chauffage", "climatisation", "depannage-sav"],
        [("Réalisez-vous des travaux de rénovation de ventilation ?", "Oui. Nous évaluons l'existant et proposons une solution adaptée au bâtiment et au budget."),
         ("Comment obtenir un devis ventilation ?", "Contactez-nous avec le type de bâtiment, la surface et l'état des installations existantes.")])

    service_page("climatisation", "Climatisation",
        "Climatisation | Étude et installation | Sopjani Tech Sàrl",
        "Étude et installation de systèmes de climatisation adaptés à votre bâtiment en Suisse romande.",
        "Climatisation : étude et installation",
        "Nous réalisons l'étude et l'installation de systèmes de climatisation adaptés aux besoins des particuliers et des professionnels.",
        "<p>Besoin de confort estival, remplacement d'installation, extension ou dépannage de système existant.</p>",
        bullets(["Dimensionnement des besoins", "Installation et raccordements", "Mise en service et réglages", "Maintenance périodique", "Dépannage"]),
        clients, process, ["geneve", "nyon", "lausanne", "valais"], ["ventilation", "chauffage", "depannage-sav"],
        [("Quels types de bâtiments équipez-vous ?", "Résidentiel et tertiaire selon faisabilité. [À COMPLÉTER : limites techniques]"),
         ("Intervenez-vous en dépannage climatisation ?", "Oui, contactez-nous pour diagnostiquer votre installation.")])

    service_page("depannage-sav", "Dépannage SAV",
        "Dépannage SAV CVC | Maintenance et urgence | Sopjani Tech Sàrl",
        "Dépannage et maintenance de vos installations CVC en Suisse romande. Contactez Sopjani Tech Sàrl.",
        "Dépannage et maintenance (SAV) de vos installations CVC",
        "Intervention sur vos installations en panne ou en fin de vie, avec une approche orientée remise en service et fiabilisation.",
        "<p>Panne de chauffage, ventilation ou climatisation, fuite, dysfonctionnement ou besoin de maintenance préventive.</p>",
        bullets(["Diagnostic de panne", "Intervention corrective", "Maintenance préventive", "Contrats d'entretien [À COMPLÉTER]", "Optimisation des réglages"]),
        clients, process, ["geneve", "lausanne", "fribourg", "vaud", "valais"], ["chauffage", "ventilation", "sanitaire"],
        [("Comment signaler une urgence ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la situation."),
         ("Quel délai d'intervention ?", "La disponibilité dépend de la nature de la panne et du secteur. Nous évaluons chaque demande au cas par cas.")])

    service_page("sprinkler-protection-incendie", "Sprinkler / protection incendie",
        "Sprinkler et protection incendie | Sopjani Tech Sàrl",
        "Installation de réseaux sprinkler en sous-traitance spécialisée. Sopjani Tech Sàrl, Suisse romande.",
        "Sprinkler et protection incendie",
        "Intervention en sous-traitance sur des installations sprinkler, avec exécution soignée et coordination chantier.",
        "<p>Montage de réseaux sprinkler, coordination avec autres corps de métier, conformité aux exigences du chantier.</p>",
        bullets(["Pose de réseaux sprinkler", "Sous-traitance spécialisée", "Coordination chantier", "Respect des exigences applicables", "Supportage et finitions techniques"]),
        "<p>Bâtiments soumis à des exigences de protection incendie (ERP, hôtels, industriel, logistique), selon obligations applicables.</p>",
        process, ["geneve", "vaud", "valais"], ["ventilation", "depannage-sav"],
        [("Les travaux sprinkler sont-ils réalisés directement ?", "Les interventions sont assurées en sous-traitance spécialisée, selon la nature du projet."),
         ("Un sprinkler est-il obligatoire ?", "Selon les directives AEAI, certaines catégories de bâtiments peuvent être concernées. Nous pouvons analyser votre situation sur demande.")])

    service_page("sanitaire", "Sanitaire",
        "Sanitaire | Travaux et dépannage | Sopjani Tech Sàrl",
        "Travaux sanitaires, adaptation de réseaux et dépannage en Suisse romande. Sopjani Tech Sàrl.",
        "Travaux sanitaires et dépannage",
        "Travaux sanitaires, adaptation de réseaux et interventions sur installations existantes en résidentiel et professionnel.",
        "<p>Fuites, remplacement d'équipements, rénovation de réseaux eau chaude/froide et évacuations.</p>",
        bullets(["Réseaux eau froide et eau chaude", "Pose de robinetterie et équipements", "Réparation et remise en état", "Recherche de fuites", "Maintenance des installations"]),
        clients, process, ["geneve", "lausanne", "nyon", "fribourg"], ["depannage-sav", "chauffage"],
        [("Intervenez-vous en dépannage sanitaire ?", "Oui, contactez-nous pour décrire le problème et organiser une intervention si faisable."),
         ("Réalisez-vous des rénovations complètes de salle de bain ?", "[À COMPLÉTER : périmètre exact des travaux sanitaires]")])


def build_zones():
    p = lambda t: f"<p>{t}</p>"
    zone_page("geneve", "Genève", "la région de Genève",
        "Chauffage et climatisation à Genève | Sopjani Tech Sàrl",
        "Sopjani Tech Sàrl intervient dans la région de Genève pour chauffage, ventilation, climatisation et dépannage.",
        "Chauffage, ventilation, climatisation et dépannage dans la région de Genève",
        p("Le canton de Genève présente un parc bâti dense, des immeubles résidentiels, des commerces et des bâtiments tertiaires aux contraintes techniques variées. Nous pouvons prendre en charge des besoins en installation, maintenance et dépannage selon la nature du projet.") +
        p("Que vous soyez propriétaire, régie ou responsable technique, contactez-nous pour vérifier la disponibilité d'intervention dans votre secteur."),
        [("Intervenez-vous bien à Genève ?", "Oui, Genève fait partie de nos zones d'intervention prioritaires en Suisse romande."),
         ("Quels services sont disponibles à Genève ?", "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler et sanitaire, selon faisabilité.")],
        ["chauffage", "ventilation", "climatisation", "depannage-sav", "sanitaire"], ["vaud", "nyon", "lausanne"])

    zone_page("vaud", "Vaud", "le canton de Vaud",
        "CVC dans le canton de Vaud | Sopjani Tech Sàrl",
        "Chauffage, ventilation et climatisation dans le canton de Vaud. Sopjani Tech Sàrl.",
        "Chauffage, ventilation, climatisation et dépannage dans le canton de Vaud",
        p("Le canton de Vaud couvre un territoire étendu, de Lausanne à la région lémanique. Nous intervenons pour des projets d'installation, d'entretien et de dépannage sur différents types de bâtiments.") +
        p("Pour les communes hors axes principaux, contactez-nous afin de confirmer la faisabilité et la planification."),
        [("Couvrez-vous tout le canton de Vaud ?", "Nous intervenons principalement sur les axes où nos équipes sont actives. Contactez-nous avec votre commune."),
         ("Travaillez-vous avec des régies ?", "[À COMPLÉTER : types de clients confirmés]")],
        ["chauffage", "ventilation", "climatisation", "depannage-sav"], ["lausanne", "nyon", "geneve", "fribourg"])

    zone_page("lausanne", "Lausanne", "Lausanne et environs",
        "Chauffage et dépannage à Lausanne | Sopjani Tech Sàrl",
        "Chauffage, ventilation, climatisation et dépannage à Lausanne et environs.",
        "Chauffage, ventilation, climatisation et dépannage à Lausanne",
        p("L'agglomération lausannoise concentre immeubles résidentiels, bâtiments tertiaires et équipements techniques nécessitant un suivi régulier. Nous intervenons pour l'installation, la maintenance et le dépannage CVC.") +
        p("Indiquez le quartier ou la commune exacte lors de votre demande pour une réponse adaptée."),
        [("Intervenez-vous en urgence à Lausanne ?", "Contactez-nous par téléphone pour évaluer la situation et la disponibilité."),
         ("Quels types de bâtiments couvrez-vous ?", "Résidentiel, tertiaire et industriel selon faisabilité technique.")],
        ["chauffage", "ventilation", "climatisation", "depannage-sav", "sanitaire"], ["nyon", "vaud", "geneve"])

    zone_page("nyon", "Nyon", "la région de Nyon",
        "Climatisation et chauffage à Nyon | Sopjani Tech Sàrl",
        "Chauffage, ventilation et climatisation dans la région de Nyon.",
        "Chauffage, ventilation et climatisation dans la région de Nyon",
        p("La région de Nyon, entre Genève et Lausanne, comprend des zones résidentielles et des activités commerciales. Nous pouvons intervenir pour des projets CVC et des dépannages selon disponibilité.") +
        p("Contactez-nous en précisant l'adresse et la nature des travaux."),
        [("Couvrez-vous Nyon et environs ?", "Oui, Nyon fait partie de nos zones d'intervention en Suisse romande."),
         ("Proposez-vous la climatisation à Nyon ?", "Oui, étude et installation de systèmes de climatisation selon le projet.")],
        ["climatisation", "chauffage", "ventilation", "sanitaire"], ["geneve", "lausanne", "vaud"])

    zone_page("valais", "Valais", "le canton du Valais",
        "Chauffage et climatisation en Valais | Sopjani Tech Sàrl",
        "Chauffage et climatisation en Valais. Sopjani Tech Sàrl intervient selon la nature du projet.",
        "Chauffage, ventilation et climatisation en Valais",
        p("Le Valais présente des spécificités climatiques et altitudinales qui influencent les besoins en chauffage et climatisation. Nous intervenons pour des installations et dépannages selon la localisation et la faisabilité.") +
        p("[À COMPLÉTER : communes ou secteurs du Valais prioritairement couverts]"),
        [("Intervenez-vous pour des hôtels ou bâtiments touristiques ?", "[À COMPLÉTER : secteurs effectivement couverts en Valais]"),
         ("Le dépannage est-il possible en Valais ?", "Contactez-nous pour évaluer la demande et la planification.")],
        ["chauffage", "climatisation", "depannage-sav", "sprinkler-protection-incendie"], ["geneve", "vaud", "fribourg"])

    zone_page("fribourg", "Fribourg", "le canton de Fribourg",
        "Dépannage CVC à Fribourg | Sopjani Tech Sàrl",
        "Chauffage, ventilation et dépannage dans le canton de Fribourg.",
        "Chauffage, ventilation et dépannage dans le canton de Fribourg",
        p("Le canton de Fribourg, à cheval sur les régions linguistiques, compte un parc bâti varié. Nous pouvons prendre en charge des interventions en chauffage, ventilation et dépannage selon la nature du projet.") +
        p("Précisez la commune et l'urgence de votre demande lors du premier contact."),
        [("Intervenez-vous à Fribourg-ville et en campagne ?", "Contactez-nous avec votre localisation pour confirmer la faisabilité."),
         ("Quels services proposez-vous à Fribourg ?", "Chauffage, ventilation, climatisation, dépannage SAV et sanitaire, selon projet.")],
        ["chauffage", "ventilation", "depannage-sav", "sanitaire"], ["vaud", "lausanne", "valais"])


def build_redirect(old_name, new_path):
    content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0;url={new_path}">
  <link rel="canonical" href="{SITE}{new_path}">
  <title>Redirection…</title>
  <script>location.replace("{new_path}");</script>
</head>
<body><p><a href="{new_path}">Continuer vers la nouvelle page</a></p></body>
</html>"""
    (ROOT / old_name).write_text(content, encoding="utf-8")


def build_sitemap():
    urls = ["/", "/prestations/", "/a-propos/", "/contact/", "/zones-intervention/"]
    urls += [f"/{s}/" for s, _, _ in SERVICES]
    urls += [f"/{z}/" for z, _, _ in ZONES]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{SITE}{u}</loc></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def build_robots():
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def build_js():
    js = """const burger = document.getElementById('burger');
const mobileNav = document.getElementById('mobileNav');
if (burger && mobileNav) {
  burger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    burger.setAttribute('aria-expanded', isOpen);
  });
  mobileNav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      mobileNav.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });
}
function closeNavDropdowns() {
  document.querySelectorAll('.nav-item.is-open').forEach(item => {
    item.classList.remove('is-open');
    item.querySelector('.nav-trigger')?.setAttribute('aria-expanded', 'false');
  });
}
document.querySelectorAll('.nav-item').forEach(item => {
  const trigger = item.querySelector('.nav-trigger');
  const submenu = item.querySelector('.nav-submenu');
  if (!trigger || !submenu) return;
  trigger.addEventListener('click', e => {
    e.stopPropagation();
    const isOpen = item.classList.contains('is-open');
    closeNavDropdowns();
    if (!isOpen) {
      item.classList.add('is-open');
      trigger.setAttribute('aria-expanded', 'true');
    }
  });
  submenu.addEventListener('click', e => e.stopPropagation());
});
document.addEventListener('click', closeNavDropdowns);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeNavDropdowns(); });
document.querySelectorAll('.mobile-nav-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const group = btn.closest('.mobile-nav-group');
    if (!group) return;
    const isOpen = group.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', isOpen);
  });
});
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const answer = btn.nextElementSibling;
    const isActive = btn.classList.contains('active');
    document.querySelectorAll('.faq-q').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-expanded', 'false');
      b.nextElementSibling.classList.remove('open');
    });
    if (!isActive) {
      btn.classList.add('active');
      btn.setAttribute('aria-expanded', 'true');
      answer.classList.add('open');
    }
  });
});
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});
"""
    (ROOT / "js" / "main.js").write_text(js, encoding="utf-8")


def main():
    extract_css()
    build_js()
    build_home()
    build_prestations()
    build_services()
    build_zones_hub()
    build_zones()
    build_about()
    build_contact()
    build_redirect("prestations.html", "/prestations/")
    build_redirect("contact.html", "/contact/")
    build_sitemap()
    build_robots()
    print("Site generated successfully.")


if __name__ == "__main__":
    main()
