#!/usr/bin/env python3
"""Generate Sopjani Tech static site pages."""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://sopjanitech.ch"
PHONE = "+41799326862"
PHONE_DISP = "+41 79 932 68 62"
EMAIL = "info@sopjanitech.ch"
WA = "https://wa.me/41799326862"
# --- MESURE DU TRAFIC (à renseigner puis régénérer : python3 build_site.py) ---
# GA4 : https://analytics.google.com → Admin → Flux de données Web → ID (G-XXXXXXXXXX)
GA4_MEASUREMENT_ID = "G-KXN3RQB89P"
# Search Console : https://search.google.com/search-console → Propriété → Vérification → Balise HTML
GOOGLE_SITE_VERIFICATION = "ESyhz2gRqYIspy2MPXHOD9v4uMjd_KAdkQjRYWHWinw"
# Formulaire contact (ex. https://formspree.io/f/xxxxxxxx) — laisser vide = message local sans envoi
FORM_ENDPOINT = ""
OG_IMAGE = f"{SITE}/assets/logo.png"
FAVICON = f"{SITE}/assets/logo.png"
THEME_COLOR = "#1e2a33"
ADDRESS_STREET = "Rue Pierre de Savoie 9"
ADDRESS_POSTAL = "1680"
ADDRESS_LOCALITY = "Romont FR"
ADDRESS_FULL = "Rue Pierre de Savoie 9, 1680 Romont FR"
COMPANY_NAME = "Sopjani Tech Sàrl"
COMPANY_UID = "CHE-177.567.012"
PUBLICATION_MANAGER = "Shkodran Sopjani"
HOST_NAME = "GitHub, Inc. (GitHub Pages)"
HOST_ADDRESS = "88 Colin P. Kelly Jr. St, San Francisco, CA 94107, États-Unis"
HOURS = "Lundi au vendredi, 8h00 – 16h30"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Rue+Pierre+de+Savoie+9,+1680+Romont"
MAP_EMBED = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1481964.3806735645!2d5.895466104411914!3d46.67378415677807!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9458f52305e1fe3%3A0x31fd51d876fffe44!2sSopjani-tech%20s%C3%A0rl!5e1!3m2!1sfr!2sch!4v1781214251877!5m2!1sfr!2sch"
GOOGLE_BUSINESS_URL = "https://maps.app.goo.gl/hWWQCXAZzrTCgjFr7"
COPYRIGHT_YEAR = 2026

META_DESCRIPTIONS = {
    "home": "Sopjani Tech Sàrl : étude, installation et dépannage en chauffage, ventilation, climatisation et sprinkler en Suisse romande. Devis gratuit.",
    "prestations": "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler et sanitaire en Suisse romande. Découvrez toutes les prestations CVC de Sopjani Tech Sàrl.",
    "zones-intervention": f"{COMPANY_NAME} intervient près de vous en Suisse romande : Genève, Vaud, Lausanne, Nyon, Valais, Fribourg. Siège à {ADDRESS_LOCALITY}.",
    "a-propos": f"{COMPANY_NAME}, entreprise CVC basée à {ADDRESS_FULL}. Chauffage, ventilation, climatisation, sprinkler et dépannage en Suisse romande.",
    "contact": f"Devis gratuit et dépannage CVC urgent. {COMPANY_NAME} — {PHONE_DISP} · {EMAIL} · {ADDRESS_FULL}.",
    "depannage-sav": f"Dépannage chauffage, climatisation et ventilation en Suisse romande. Urgence : appelez le {PHONE_DISP}.",
    "chauffage": "Chauffagiste en Suisse romande : installation, entretien et dépannage. Pompes à chaleur et chaudières. Devis gratuit.",
    "ventilation": "Entreprise de ventilation en Suisse romande. VMC, traitement de l'air, dépannage et maintenance.",
    "climatisation": "Climatisation et installation près de vous en Suisse romande. Étude, pose et dépannage. Devis gratuit.",
    "sprinkler-protection-incendie": "Installation de réseaux sprinkler en sous-traitance en Suisse romande. Protection incendie pour ERP et bâtiments industriels.",
    "sanitaire": "Travaux sanitaires et dépannage en Suisse romande. Réseaux eau chaude/froide, fuites et rénovations.",
    "geneve": "Installation et dépannage CVC dans la région de Genève. Chauffage, ventilation, climatisation et sprinkler pour bâtiments résidentiels et professionnels.",
    "vaud": "Entreprise de ventilation, chauffage et climatisation dans le canton de Vaud. Lausanne, Nyon et environs.",
    "lausanne": "Installation et dépannage CVC à Lausanne et environs. Chauffage, ventilation, climatisation et maintenance en Suisse romande.",
    "nyon": "Chauffagiste, climatisation et ventilation à Nyon et environs. Devis et dépannage CVC par Sopjani Tech Sàrl.",
    "valais": "Entreprise de ventilation et chauffage en Valais. Installation et dépannage CVC selon votre commune.",
    "fribourg": "Installation et dépannage CVC dans le canton de Fribourg. Chauffage, ventilation et maintenance pour bâtiments résidentiels et professionnels.",
    "mentions-legales": f"Mentions légales de {COMPANY_NAME} : raison sociale, siège à {ADDRESS_FULL}, UID {COMPANY_UID} et contact.",
    "politique-confidentialite": f"Politique de confidentialité de {COMPANY_NAME} : traitement des données, cookies et droits selon la nLPD suisse.",
    "plan-du-site": "Plan du site Sopjani Tech Sàrl : accès à toutes les pages prestations, zones d'intervention et contact en Suisse romande.",
    "realisations": f"Réalisations de {COMPANY_NAME} en Suisse romande : installations sprinkler, ventilation et tuyauterie sanitaire. Photos de chantiers réels.",
}

PAGE_TITLES = {
    "home": "Sopjani Tech Sàrl | Chauffage, ventilation, climatisation et dépannage en Suisse romande",
    "a-propos": "Sopjani Tech Sàrl | Entreprise CVC à Romont, Suisse romande",
    "contact": "Devis et dépannage CVC | Contact | Sopjani Tech Sàrl",
    "prestations": "Prestations CVC | Chauffage, ventilation, climatisation | Sopjani Tech Sàrl",
    "zones-intervention": "Zones d'intervention CVC | Suisse romande | Sopjani Tech Sàrl",
    "plan-du-site": "Plan du site | Sopjani Tech Sàrl",
    "chauffage": "Chauffagiste Suisse romande | Installation et dépannage | Sopjani Tech Sàrl",
    "ventilation": "Entreprise ventilation Suisse romande | Sopjani Tech Sàrl",
    "climatisation": "Climatisation et installation | Sopjani Tech Sàrl",
    "depannage-sav": "Dépannage chauffage et climatisation | Urgence CVC | Sopjani Tech Sàrl",
    "sanitaire": "Sanitaire | Travaux et dépannage | Sopjani Tech Sàrl",
    "sprinkler-protection-incendie": "Sprinkler et protection incendie | Sopjani Tech Sàrl",
    "geneve": "Chauffage et climatisation Genève | Sopjani Tech Sàrl",
    "vaud": "Ventilation et climatisation Vaud | Entreprise CVC | Sopjani Tech Sàrl",
    "lausanne": "Chauffagiste et CVC Lausanne | Sopjani Tech Sàrl",
    "nyon": "Chauffagiste et climatisation Nyon | Sopjani Tech Sàrl",
    "valais": "Entreprise ventilation Valais | Chauffage & CVC | Sopjani Tech Sàrl",
    "fribourg": "Dépannage CVC Fribourg | Sopjani Tech Sàrl",
    "realisations": "Réalisations CVC, sprinkler et sanitaire | Sopjani Tech Sàrl",
}

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
    "@type": ["HVACBusiness", "LocalBusiness"],
    "@id": f"{SITE}/#organization",
    "name": "Sopjani Tech Sàrl",
    "url": SITE,
    "description": "Chauffage, ventilation, climatisation, dépannage SAV et sprinkler en Suisse romande.",
    "telephone": PHONE,
    "email": EMAIL,
    "address": {
        "@type": "PostalAddress",
        "streetAddress": ADDRESS_STREET,
        "postalCode": ADDRESS_POSTAL,
        "addressLocality": ADDRESS_LOCALITY,
        "addressRegion": "FR",
        "addressCountry": "CH",
    },
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": 46.6917,
        "longitude": 6.9119,
        "addressCountry": "CH",
        "addressLocality": ADDRESS_LOCALITY,
        "postalCode": ADDRESS_POSTAL,
    },
    "hasMap": MAP_URL,
    "contactPoint": [{
        "@type": "ContactPoint",
        "telephone": PHONE,
        "email": EMAIL,
        "contactType": "customer service",
        "areaServed": "CH",
        "availableLanguage": ["French"],
    }],
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "08:00",
        "closes": "16:30",
    }],
    "areaServed": [
        {"@type": "AdministrativeArea", "name": n} for _, n, _ in ZONES
    ] + [{"@type": "AdministrativeArea", "name": "Suisse romande"}],
    "priceRange": "$$",
    "currenciesAccepted": "CHF",
    "inLanguage": "fr-CH",
    "logo": OG_IMAGE,
    "image": OG_IMAGE,
    "sameAs": [GOOGLE_BUSINESS_URL],
}

WEBSITE_SCHEMA = {
    "@type": "WebSite",
    "@id": f"{SITE}/#website",
    "url": SITE,
    "name": "Sopjani Tech Sàrl",
    "description": "Chauffage, ventilation, climatisation et dépannage en Suisse romande.",
    "publisher": {"@id": f"{SITE}/#organization"},
    "inLanguage": "fr-CH",
    "potentialAction": {
        "@type": "CommunicateAction",
        "name": "Demander un devis",
        "target": SITE + "/contact/",
    },
}

QUI_SOMMES_NOUS_HTML = """
<p>Sopjani Tech Sàrl est une entreprise active dans les domaines du chauffage, de la ventilation, de la climatisation, du dépannage SAV et du sprinkler / protection incendie en Suisse romande.</p>
<p>Nous accompagnons nos clients avec une approche simple : comprendre le besoin, proposer une solution adaptée et intervenir avec sérieux selon la nature de la demande.</p>
<p>Nous intervenons principalement à Genève, dans le canton de Vaud, à Lausanne, à Nyon, ainsi qu'en Valais et à Fribourg. Pour d'autres secteurs en Suisse romande, la possibilité d'intervention peut être étudiée selon le projet.</p>
<p>Notre activité couvre différents besoins techniques, qu'il s'agisse d'installation, de maintenance ou de dépannage. Nous accordons une attention particulière à la clarté des échanges, à la réactivité et à l'adaptation aux contraintes du terrain.</p>
<p>Vous avez une demande en chauffage, ventilation, climatisation ou dépannage SAV ? <a href="/contact/">Contactez-nous</a> pour échanger sur votre besoin et vérifier la disponibilité d'intervention dans votre zone.</p>
"""

HOME_ABOUT_TEASER = """
<p>Entreprise technique en Suisse romande, nous réalisons installations, maintenance et dépannage CVC pour bâtiments résidentiels, tertiaires et industriels.</p>
<p><a href="/a-propos/" class="text-link">Présentation de l'entreprise →</a></p>
"""


def hero_side_panel():
    zone_links = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES[:4])
    return f"""<aside class="hero-panel" aria-label="Contact et zones d'intervention">
  <div class="panel-header"><span class="panel-header-text">Interventions près de vous</span></div>
  <div class="panel-body">
    <div class="panel-item">
      <div>
        <div class="pi-name">Siège — {ADDRESS_LOCALITY}</div>
        <p class="pi-desc">{ADDRESS_FULL}</p>
      </div>
    </div>
    <div class="panel-item">
      <div>
        <div class="pi-name"><a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a></div>
        <p class="pi-desc"><a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a></p>
      </div>
    </div>
    <div class="panel-item">
      <div>
        <div class="pi-name">Zones prioritaires</div>
        <div class="zone-links" style="margin-top:8px;">{zone_links}</div>
        <p class="pi-desc" style="margin-top:8px;"><a href="/zones-intervention/">Toutes les zones →</a></p>
      </div>
    </div>
  </div>
</aside>"""


def geo_presence_block(compact=False):
    zones = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES)
    lead = (
        f"Basés à {ADDRESS_FULL}, nous intervenons en Suisse romande pour l'installation, la maintenance et le dépannage CVC."
        if not compact else
        f"Entreprise CVC basée à {ADDRESS_LOCALITY}, active en Suisse romande."
    )
    return f"""<section class="geo-presence content-section{' alt' if not compact else ''}" aria-labelledby="geo-title">
  <div class="container">
    <span class="label">Proximité</span>
    <div class="rule"></div>
    <h2 class="section-title" id="geo-title">Une entreprise CVC près de vous en Suisse romande</h2>
    <p class="section-lead">{lead} Contactez-nous pour vérifier la disponibilité dans votre commune.</p>
    <div class="zone-links">{zones}</div>
    <p style="margin-top:16px;"><a href="/contact/" class="text-link">Demander un devis ou un dépannage →</a></p>
  </div>
</section>"""


def urgence_band():
    return f"""<section class="urgence-band" aria-label="Dépannage urgent">
  <div class="container urgence-band__inner">
    <div>
      <p class="urgence-band__label">Dépannage urgent</p>
      <p class="urgence-band__text">Panne de chauffage, climatisation ou ventilation ? Contactez-nous pour évaluer la situation et la disponibilité d'intervention.</p>
    </div>
    <div class="urgence-band__actions">
      <a href="tel:{PHONE}" class="btn btn-primary track-phone">{PHONE_DISP}</a>
      <a href="{WA}" class="btn btn-secondary track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
    </div>
  </div>
</section>"""


def zone_aeo_faq(name, region):
    """FAQ orientée requêtes locales et moteurs de réponse."""
    return [
        (f"Qui appeler pour un dépannage CVC à {name} ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp. Indiquez votre commune, le type de bâtiment et la nature de la panne."),
        (f"Intervenez-vous pour la ventilation dans {region} ?", f"Oui, nous réalisons installation, maintenance et dépannage de ventilation dans {region}, selon faisabilité et planning."),
        (f"Proposez-vous la climatisation et le chauffage à {name} ?", "Oui. Étude, installation, entretien et dépannage en chauffage, climatisation et ventilation selon votre projet."),
        (f"Comment obtenir un devis à {name} ?", "Via notre page contact ou par téléphone : décrivez le bâtiment, la localisation exacte et le type de travaux (installation, maintenance ou dépannage)."),
    ]


# Photos de chantiers réels (fichier, largeur, hauteur, alt SEO, catégorie, légende)
REALISATIONS = [
    ("sprinkler-poste-controle.jpg", 960, 1280, "Poste de contrôle sprinkler avec tuyauterie rouge, vannes bleues et manomètres installé par Sopjani Tech Sàrl", "sprinkler", "Poste de contrôle sprinkler"),
    ("sprinkler-technicien-brasure.jpg", 720, 1280, "Technicien de Sopjani Tech Sàrl soude au TIG sous station de chauffage à distance sur chantier", "sprinkler", "Soude au TIG sous station chauffage à distance"),
    ("sprinkler-vanne-arret-secteur.jpg", 720, 1280, "Poste d'alarme sous eau d'un réseau sprinkler avec manomètres de contrôle, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous eau"),
    ("sprinkler-collecteur-rouges.jpg", 1280, 720, "Centrale sprinkler sous eau avec tuyauterie rouge et vannes en local technique, par Sopjani Tech Sàrl", "sprinkler", "Centrale sprinkler sous eau"),
    ("sprinkler-vanne-seche-victaulic.jpg", 720, 1280, "Poste d'alarme sous air pour installation sprinkler, station Parking Nord, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous air"),
    ("sprinkler-vanne-alarme-seche.jpg", 720, 1280, "Vanne d'alarme sèche pour système sprinkler dans un parking", "sprinkler", "Vanne d'alarme sèche"),
    ("sprinkler-vanne-alarme-humide.jpg", 720, 1280, "Poste d'alarme sous eau avec pompe de suppression et vanne d'arrêt générale d'un réseau sprinkler, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous eau avec pompe de suppression"),
    ("sanitaire-collecteur-galvanise.jpg", 1280, 720, "Test de débit sprinkler sur collecteur en acier galvanisé avec raccords laiton et vannes, par Sopjani Tech Sàrl", "sprinkler", "Test débit sprinkler"),
    ("ventilation-unite-hvac-gaine.jpg", 1280, 720, "Unité de ventilation HVAC raccordée à une gaine souple par Sopjani Tech Sàrl", "ventilation", "Unité de ventilation HVAC"),
    ("ventilation-conduit-galvanise-chantier.jpg", 1280, 720, "Conduit de ventilation en acier galvanisé installé sur chantier par Sopjani Tech Sàrl", "ventilation", "Conduit de ventilation galvanisé"),
    ("ventilation-sanitaire-local-technique.jpg", 720, 1280, "Ventilation et pompe à chaleur installées en local technique par Sopjani Tech Sàrl", "ventilation", "Ventilation pompe à chaleur"),
    ("tuyauterie-fabrication-atelier.jpg", 720, 1280, "Fabrication d'un assemblage de tuyauterie en atelier par Sopjani Tech Sàrl", "sanitaire", "Fabrication de tuyauterie en atelier"),
]

REALISATIONS_BY_CAT = {}
for _fn, _w, _h, _alt, _cat, _cap in REALISATIONS:
    REALISATIONS_BY_CAT.setdefault(_cat, []).append((_fn, _w, _h, _alt, _cap))


def gallery_html(images, cols=3):
    cards = []
    for fn, w, h, alt, cap in images:
        cards.append(f"""<figure class="gallery-card">
  <img src="/assets/realisations/{fn}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">
  <figcaption>{cap}</figcaption>
</figure>""")
    return f'<div class="gallery gallery-cols-{cols}">{"".join(cards)}</div>'


def realisations_section(cat, limit=None):
    imgs = REALISATIONS_BY_CAT.get(cat, [])
    if limit:
        imgs = imgs[:limit]
    if not imgs:
        return ""
    return gallery_html(imgs, cols=3)


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


def webpage_schema(title, description, url):
    return {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": title,
        "description": description,
        "isPartOf": {"@id": f"{SITE}/#website"},
        "about": {"@id": f"{SITE}/#organization"},
        "inLanguage": "fr-CH",
    }


def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        } for q, a in items],
    }


def base_graph(title, description, url, crumbs=None, faq=None, extra=None):
    graph = [ORG_SCHEMA, WEBSITE_SCHEMA, webpage_schema(title, description, url)]
    if crumbs:
        graph.append(breadcrumb_schema(crumbs))
    if faq:
        graph.append(faq_schema(faq))
    if extra:
        graph.extend(extra if isinstance(extra, list) else [extra])
    return graph


def breadcrumbs_html(items):
    lis = []
    for i, (label, url) in enumerate(items):
        if i < len(items) - 1:
            lis.append(f'<li><a href="{url}">{label}</a></li>')
        else:
            lis.append(f"<li aria-current=\"page\">{label}</li>")
    return f'<nav class="breadcrumbs" aria-label="Fil d\'Ariane"><ol>{"".join(lis)}</ol></nav>'


def mobile_quick_bar():
    return f"""<div class="mobile-quick-bar" role="group" aria-label="Actions de contact rapides">
  <a href="tel:{PHONE}" class="mobile-quick-btn track-phone">Appeler</a>
  <a href="{WA}" class="mobile-quick-btn track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
  <a href="/contact/#contact-form" class="mobile-quick-btn track-devis">Devis</a>
</div>"""


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
        <a href="tel:{PHONE}" class="tel-btn track-phone" aria-label="Appeler Sopjani Tech">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 014.69 12 19.79 19.79 0 011.61 3.4 2 2 0 013.6 1.22h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L7.91 8.8a16 16 0 006.29 6.29l.96-.96a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
          {PHONE_DISP}
        </a>
        <a href="/contact/" class="btn btn-primary track-devis">Demander un devis</a>
      </div>
      <button class="burger" id="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-nav-overlay" id="mobileNavOverlay" hidden></div>
<nav class="mobile-nav" id="mobileNav" aria-label="Navigation mobile" aria-hidden="true">
  <div class="mobile-nav-inner">
    <a href="/" class="mobile-nav-link">Accueil</a>
    {mobile_svc}
    {mobile_zones}
    <a href="/a-propos/" class="mobile-nav-link">À propos</a>
    <a href="/contact/" class="mobile-nav-link">Contact</a>
    <div class="mobile-nav-cta">
      <a href="tel:{PHONE}" class="btn btn-primary track-phone">Appeler · {PHONE_DISP}</a>
      <a href="{WA}" class="btn btn-secondary track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
      <a href="/contact/#contact-form" class="btn btn-secondary track-devis">Demander un devis</a>
    </div>
  </div>
</nav>"""


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
          <li><a href="/realisations/">Réalisations</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/plan-du-site/">Plan du site</a></li>
          <li><a href="/mentions-legales/">Mentions légales</a></li>
          <li><a href="/politique-confidentialite/">Politique de confidentialité</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-col-title">Contact</div>
        <ul class="footer-contact-list">
          <li><a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a></li>
          <li><a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a></li>
          <li><a href="{WA}" class="track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
          <li class="footer-contact-address"><a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a></li>
          <li class="footer-contact-hours">{HOURS}</li>
          <li><a href="{GOOGLE_BUSINESS_URL}" class="track-google" target="_blank" rel="noopener noreferrer">Voir nos avis sur Google</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-bottom-main">
        <p class="footer-copy">© {COPYRIGHT_YEAR} {COMPANY_NAME} · Tous droits réservés</p>
        <p class="footer-address"><a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a></p>
        <nav class="footer-legal" aria-label="Informations légales">
          <a href="/mentions-legales/">Mentions légales</a>
          <span aria-hidden="true">·</span>
          <a href="/politique-confidentialite/">Politique de confidentialité</a>
          <span aria-hidden="true">·</span>
          <a href="/plan-du-site/">Plan du site</a>
          <span aria-hidden="true">·</span>
          <a href="{GOOGLE_BUSINESS_URL}" class="track-google" target="_blank" rel="noopener noreferrer">Avis Google</a>
        </nav>
      </div>
      <p class="footer-seo">Chauffage · Ventilation · Climatisation · Dépannage SAV · Sprinkler · Sanitaire · Suisse romande</p>
    </div>
  </div>
</footer>"""


def cookie_banner():
    return """<div id="cookieBanner" class="cookie-banner" role="dialog" aria-label="Information sur les cookies" aria-live="polite" hidden>
  <div class="cookie-banner__inner container">
    <p class="cookie-banner__text">Ce site utilise des cookies techniques essentiels. En continuant, vous acceptez leur utilisation.</p>
    <button type="button" class="btn btn-primary cookie-banner__accept" id="cookieAccept">Accepter</button>
  </div>
</div>"""


def faq_html(items):
    # FAQ visible uniquement — le balisage FAQPage est fourni en JSON-LD (évite le doublon GSC).
    blocks = []
    for q, a in items:
        blocks.append(f"""<div class="faq-item">
  <button class="faq-q" aria-expanded="false"><span>{q}</span><span class="faq-icon" aria-hidden="true"></span></button>
  <div class="faq-a"><span>{a}</span></div>
</div>""")
    return f'<div class="faq-list">{"".join(blocks)}</div>'


def cta_band(title="Besoin d'un devis ou d'un dépannage ?", text="Contactez-nous pour décrire votre besoin. Nous vous répondrons dans les meilleurs délais."):
    return f"""<section class="cta-band" aria-label="Appel à l'action">
  <div class="container">
    <h2>{title}</h2>
    <p>{text}</p>
    <a href="tel:{PHONE}" class="btn btn-primary track-phone">{PHONE_DISP}</a>
    <a href="/contact/" class="btn btn-secondary-on-dark track-devis">Demander un devis</a>
  </div>
</section>"""


def gsc_verification_meta():
    if GOOGLE_SITE_VERIFICATION:
        return f'  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">\n'
    return "  <!-- TODO GSC : renseigner GOOGLE_SITE_VERIFICATION dans build_site.py -->\n"


def analytics_head():
    return """  <script>window.dataLayer = window.dataLayer || []; function gtag(){ dataLayer.push(arguments); }</script>"""


def page_shell(title, description, canonical, schema_graph, body, crumbs=None):
    # Fil d'Ariane : conservé en JSON-LD uniquement (pas d'affichage visible)
    crumbs_html = ""
    safe_title = title.replace('"', "&quot;")
    safe_desc = description.replace('"', "&quot;")
    return f"""<!DOCTYPE html>
<html lang="fr-CH">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="geo.region" content="CH-FR">
  <meta name="geo.placename" content="Suisse romande">
  <meta name="geo.position" content="46.6917;6.9119">
  <meta name="ICBM" content="46.6917, 6.9119">
  <meta name="theme-color" content="{THEME_COLOR}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/assets/logo.png" type="image/png">
  <link rel="apple-touch-icon" href="/assets/logo.png">
{gsc_verification_meta()}  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_CH">
  <meta property="og:title" content="{safe_title}">
  <meta property="og:description" content="{safe_desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Sopjani Tech Sàrl">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:alt" content="Logo Sopjani Tech Sàrl">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{safe_title}">
  <meta name="twitter:description" content="{safe_desc}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/main.css">
{analytics_head()}
  <script type="application/ld+json">{schema_json(schema_graph)}</script>
</head>
<body>
{header()}
<main>
{crumbs_html}
{body}
</main>
{footer()}
{cookie_banner()}
<script src="/js/main.js" defer></script>
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


def service_page(slug, name, title, desc, h1, intro, problems, interventions, clients, process, zone_slugs, related_svc, faq, show_urgence=False, gallery_cat=None):
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (name, url)]
    zones_html = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES if z in zone_slugs)
    related = "".join(f'<a class="zone-pill" href="/{s}/">{n}</a>' for s, n, _ in SERVICES if s in related_svc)
    urgence_html = f'<div class="section-divider"></div>{urgence_band()}' if show_urgence else ""
    gallery_block = ""
    if gallery_cat and REALISATIONS_BY_CAT.get(gallery_cat):
        gallery_block = f"""<div class="section-divider"></div>
<section class="content-section" aria-labelledby="real-title">
  <div class="container">
    <span class="label">Chantiers</span>
    <div class="rule"></div>
    <h2 class="section-title" id="real-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:8px;">Réalisations — {name}</h2>
    <p class="section-lead" style="margin-top:8px;">Aperçu d'interventions réalisées par {COMPANY_NAME}.</p>
    {realisations_section(gallery_cat)}
    <p style="margin-top:24px;"><a href="/realisations/" class="text-link">Voir toutes nos réalisations →</a></p>
  </div>
</section>"""
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Prestation</span>
    <div class="rule"></div>
    <h1 id="page-h1">{h1}</h1>
    <p class="hero-sub">{intro}</p>
    <div class="hero-ctas" style="margin-top:24px;">
      <a href="tel:{PHONE}" class="btn btn-primary track-phone">{PHONE_DISP}</a>
      <a href="/contact/" class="btn btn-secondary track-devis">Demander un devis</a>
    </div>
  </div>
</section>
{urgence_html}
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
{gallery_block}
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
    service_schema = {
        "@type": "Service",
        "name": name,
        "serviceType": name,
        "provider": {"@id": f"{SITE}/#organization"},
        "areaServed": {"@type": "AdministrativeArea", "name": "Suisse romande"},
        "description": desc,
        "url": SITE + url,
    }
    graph = base_graph(title, desc, SITE + url, crumbs, faq, service_schema)
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
      <a href="tel:{PHONE}" class="btn btn-primary track-phone">{PHONE_DISP}</a>
      <a href="/contact/" class="btn btn-secondary track-devis">Demander un devis</a>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section" aria-labelledby="local-title">
  <div class="container prose-block">
    <h2 class="section-title" id="local-title" style="font-size:clamp(26px,3vw,40px);margin-bottom:20px;">Interventions dans {region}</h2>
    {local_text}
    <p class="geo-local-note">Siège à <strong>{ADDRESS_FULL}</strong> — équipe mobile en Suisse romande. <a href="/contact/">Contactez-nous</a> pour vérifier la disponibilité à {name}.</p>
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
    graph = base_graph(title, desc, SITE + url, crumbs, faq)
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def build_home():
    svc_cards = "".join(
        f'<a class="hub-card" href="/{s}/"><h3>{n}</h3><p>{d}</p><span class="link-arrow">En savoir plus →</span></a>'
        for s, n, d in SERVICES
    )
    zone_pills = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES)
    faq = [
        ("Quels services proposez-vous ?", "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler en sous-traitance et sanitaire. Consultez nos pages prestations pour le détail."),
        ("Dans quelles zones intervenez-vous ?", f"Principalement en Suisse romande : Genève, Vaud, Lausanne, Nyon, Valais et Fribourg. Siège à {ADDRESS_LOCALITY}. D'autres cantons peuvent être couverts selon la nature du projet."),
        ("Comment obtenir un devis ?", "Via notre page contact ou par téléphone : décrivez le type de bâtiment, la localisation et la nature du besoin."),
        ("Intervenez-vous en dépannage ?", "Oui. Contactez-nous pour évaluer votre situation. La disponibilité dépend de la nature de la panne et du secteur."),
        ("Qui contacter pour un dépannage CVC en Suisse romande ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp. Décrivez votre panne et votre localisation."),
        ("Combien de temps pour obtenir un devis ?", "Après votre demande via le formulaire contact ou par téléphone, nous vous répondons dans les meilleurs délais selon la complexité du projet."),
        ("Intervenez-vous près de chez moi ?", f"Nous sommes basés à {ADDRESS_FULL} et intervenons principalement en Suisse romande. Contactez-nous pour vérifier la disponibilité dans votre commune."),
    ]
    body = f"""
<section class="hero" aria-labelledby="hero-h1">
  <div class="container">
    <div class="hero-grid">
      <div class="hero-content">
        <div class="hero-eyebrow"><span class="label">Étude · Installation · Maintenance · Dépannage</span></div>
        <h1 id="hero-h1">Chauffage, ventilation, climatisation et dépannage en Suisse romande</h1>
        <p class="hero-sub">Installation, maintenance et dépannage CVC pour bâtiments résidentiels, tertiaires et industriels en Suisse romande.</p>
        <div class="hero-ctas">
          <a href="tel:{PHONE}" class="btn btn-primary track-phone">Appeler · {PHONE_DISP}</a>
          <a href="/contact/" class="btn btn-secondary track-devis">Demander un devis</a>
        </div>
      </div>
      {hero_side_panel()}
    </div>
  </div>
</section>
<div class="section-divider"></div>
{geo_presence_block()}
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
<section class="content-section alt" aria-labelledby="about-title">
  <div class="container prose-block">
    <span class="label">Entreprise</span>
    <div class="rule"></div>
    <h2 class="section-title" id="about-title">L'entreprise</h2>
    {HOME_ABOUT_TEASER}
  </div>
</section>
<div class="section-divider"></div>
<section class="expertise content-section" aria-labelledby="why-title">
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
<section class="zones content-section alt" aria-labelledby="zones-title">
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
<section class="content-section" aria-labelledby="real-title">
  <div class="container">
    <span class="label">Chantiers</span>
    <div class="rule"></div>
    <h2 class="section-title" id="real-title">Réalisations récentes</h2>
    <p class="section-lead" style="margin-top:16px;">Aperçu de nos interventions en sprinkler, ventilation et sanitaire en Suisse romande.</p>
    {gallery_html([("sprinkler-collecteur-rouges.jpg", 1280, 720, "Centrale sprinkler sous eau avec tuyauterie rouge et vannes en local technique, par Sopjani Tech Sàrl", "Centrale sprinkler sous eau"), ("ventilation-conduit-galvanise-chantier.jpg", 1280, 720, "Conduit de ventilation en acier galvanisé installé sur chantier par Sopjani Tech Sàrl", "Conduit de ventilation galvanisé"), ("tuyauterie-fabrication-atelier.jpg", 720, 1280, "Fabrication d'un assemblage de tuyauterie en atelier par Sopjani Tech Sàrl", "Fabrication de tuyauterie en atelier")], cols=3)}
    <p style="margin-top:24px;"><a href="/realisations/" class="text-link">Voir toutes nos réalisations →</a></p>
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
    home_title = PAGE_TITLES["home"]
    home_desc = META_DESCRIPTIONS["home"]
    graph = base_graph(home_title, home_desc, SITE + "/", faq=faq)
    write_page(["index.html"], page_shell(home_title, home_desc, SITE + "/", graph, body))


def build_prestations():
    faq = [
        ("Quelles prestations CVC proposez-vous ?", "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler en sous-traitance et sanitaire."),
        ("Comment choisir la bonne prestation ?", "Décrivez votre bâtiment et votre besoin via notre page contact : nous vous orienterons vers la prestation adaptée."),
        ("Intervenez-vous en Suisse romande ?", f"Oui, principalement à Genève, Vaud, Lausanne, Nyon, Valais et Fribourg. Siège à {ADDRESS_LOCALITY}."),
    ]
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
<div class="section-divider"></div>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>
{cta_band()}"""
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/")]
    presta_title = PAGE_TITLES["prestations"]
    presta_desc = META_DESCRIPTIONS["prestations"]
    graph = base_graph(presta_title, presta_desc, SITE + "/prestations/", crumbs, faq)
    write_page(["prestations", "index.html"], page_shell(presta_title, presta_desc, SITE + "/prestations/", graph, body, crumbs))


def build_zones_hub():
    faq = [
        ("Dans quelles zones intervenez-vous ?", "Genève, Vaud, Lausanne, Nyon, Valais et Fribourg, ainsi que d'autres secteurs en Suisse romande selon le projet."),
        ("Comment savoir si vous intervenez chez moi ?", f"Contactez-nous avec votre commune. Nous sommes basés à {ADDRESS_LOCALITY} et nous déplaçons selon la nature des travaux."),
        ("Avez-vous une agence dans chaque canton ?", "Non. Nos interventions sont assurées par une équipe mobile depuis notre siège à Romont FR."),
    ]
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
{geo_presence_block(compact=True)}
<div class="section-divider"></div>
<section class="content-section">
  <div class="container">
    <div class="hub-grid">{cards}</div>
    <div class="prose-block" style="margin-top:40px;">
      <p>Pour d'autres secteurs en Suisse romande, contactez-nous afin de vérifier la faisabilité d'une intervention selon la nature du projet.</p>
      <p style="margin-top:12px;font-size:14px;color:var(--c-muted);">Nos interventions sont assurées par une équipe mobile : il ne s'agit pas d'agences locales dans chaque canton.</p>
    </div>
  </div>
</section>
<div class="section-divider"></div>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>
{cta_band("Votre commune n'est pas listée ?", "Contactez-nous pour vérifier la faisabilité d'une intervention.")}"""
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/")]
    zones_title = PAGE_TITLES["zones-intervention"]
    zones_desc = META_DESCRIPTIONS["zones-intervention"]
    graph = base_graph(zones_title, zones_desc, SITE + "/zones-intervention/", crumbs, faq)
    write_page(["zones-intervention", "index.html"], page_shell(zones_title, zones_desc, SITE + "/zones-intervention/", graph, body, crumbs))


def build_about():
    faq = [
        (f"Où est située {COMPANY_NAME} ?", f"Notre siège est à {ADDRESS_FULL}. Nous intervenons en Suisse romande pour le chauffage, la ventilation, la climatisation et le dépannage CVC."),
        ("Quels services propose l'entreprise ?", "Chauffage, ventilation, climatisation, dépannage SAV, sprinkler en sous-traitance et sanitaire."),
        ("Comment contacter Sopjani Tech Sàrl ?", f"Par téléphone au {PHONE_DISP}, par email ({EMAIL}) ou via WhatsApp. Horaires : {HOURS}."),
    ]
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
    {QUI_SOMMES_NOUS_HTML}
    <h3>Coordonnées</h3>
    <p>Téléphone : <a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a><br>Email : <a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a><br>Adresse : <a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a><br>Horaires : {HOURS}</p>
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
    crumbs = [("Accueil", "/"), ("À propos", "/a-propos/")]
    about_title = PAGE_TITLES["a-propos"]
    about_desc = META_DESCRIPTIONS["a-propos"]
    graph = base_graph(about_title, about_desc, SITE + "/a-propos/", crumbs, faq, extra={"@type": "AboutPage", "name": "À propos", "url": SITE + "/a-propos/"})
    write_page(["a-propos", "index.html"], page_shell(about_title, about_desc, SITE + "/a-propos/", graph, body, crumbs))


def build_contact():
    faq = [
        ("Comment nous joindre ?", f"Par téléphone ({PHONE_DISP}), email ({EMAIL}) ou WhatsApp."),
        ("Quelles informations fournir pour un devis ?", "Type de bâtiment, localisation (canton/commune), nature du besoin (installation, maintenance, dépannage) et urgence éventuelle."),
        ("Horaires de contact", HOURS + ". Pour un dépannage, contactez-nous par téléphone ou WhatsApp."),
        ("Qui appeler en cas de panne CVC ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la panne et votre adresse."),
        ("Proposez-vous un devis gratuit ?", "Oui. Décrivez votre projet via le formulaire ou par téléphone : nous évaluons votre demande et vous répondons dans les meilleurs délais."),
    ]
    body = f"""
{urgence_band()}
<section class="contact page-hero" aria-labelledby="page-h1">
  <div class="container contact-page">
    <div class="contact-intro">
      <span class="label">Contact</span>
      <div class="rule"></div>
      <h1 id="page-h1">Contactez Sopjani Tech Sàrl</h1>
      <p class="section-lead contact-lead">Devis, maintenance ou dépannage : décrivez votre besoin et nous vous orienterons vers la solution adaptée.</p>
    </div>
    {mobile_quick_bar()}
    <div class="contact-inner">
      <div class="contact-form-section" id="contact-form">
        <h2 class="contact-block-title">Formulaire de demande</h2>
        <p class="contact-block-lead">Remplissez ce formulaire — nous vous répondons rapidement.</p>
        <form class="contact-form track-form" action="{FORM_ENDPOINT or '#'}" method="post" data-form-endpoint="{FORM_ENDPOINT}">
          <div class="form-field"><label for="name">Nom</label><input id="name" name="name" type="text" required autocomplete="name" placeholder="Votre nom"></div>
          <div class="form-field"><label for="phone">Téléphone</label><input id="phone" name="phone" type="tel" required autocomplete="tel" placeholder="+41 79 …"></div>
          <div class="form-field"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email" placeholder="vous@exemple.ch"></div>
          <div class="form-field"><label for="canton">Canton / Commune</label><input id="canton" name="canton" type="text" required placeholder="Ex. Lausanne, Vaud"></div>
          <div class="form-field"><label for="need">Type de besoin</label>
            <select id="need" name="need" required>
              <option value="">Choisir…</option>
              <option>Devis installation</option>
              <option>Maintenance / entretien</option>
              <option>Dépannage</option>
              <option>Autre</option>
            </select>
          </div>
          <div class="form-field"><label for="message">Message</label><textarea id="message" name="message" required placeholder="Décrivez votre besoin…"></textarea></div>
          <button type="submit" class="btn btn-primary btn-block track-form-submit">Envoyer la demande</button>
          <p class="form-feedback" role="status" aria-live="polite" hidden></p>
        </form>
      </div>
      <div class="contact-details-section">
        <h2 class="contact-block-title">Coordonnées</h2>
        <div class="contact-methods">
          <a href="tel:{PHONE}" class="contact-method track-phone" aria-label="Appeler Sopjani Tech">
            <div><div class="cm-label">Téléphone</div><div class="cm-value">{PHONE_DISP}</div></div>
          </a>
          <a href="mailto:{EMAIL}" class="contact-method track-email" aria-label="Envoyer un email">
            <div><div class="cm-label">Email</div><div class="cm-value">{EMAIL}</div></div>
          </a>
          <a href="{WA}" class="contact-method track-whatsapp" target="_blank" rel="noopener noreferrer" aria-label="Contacter via WhatsApp">
            <div><div class="cm-label">WhatsApp</div><div class="cm-value">Envoyer un message</div></div>
          </a>
          <a href="{MAP_URL}" class="contact-method" target="_blank" rel="noopener noreferrer" aria-label="Voir l'adresse sur la carte">
            <div><div class="cm-label">Adresse</div><div class="cm-value">{ADDRESS_FULL}</div></div>
          </a>
          <div class="contact-method contact-method--static" aria-label="Horaires">
            <div><div class="cm-label">Horaires</div><div class="cm-value">{HOURS}</div></div>
          </div>
          <a href="{GOOGLE_BUSINESS_URL}" class="contact-method contact-google-link track-google" target="_blank" rel="noopener noreferrer" aria-label="Voir nos avis sur Google">
            <div><div class="cm-label">Google</div><div class="cm-value">Voir nos avis sur Google</div></div>
          </a>
        </div>
        <p class="contact-zone-note">Zone desservie : Suisse romande et alentours selon projet.</p>
      </div>
    </div>
  </div>
  <div class="contact-map-wrap">
    <iframe
      src="{MAP_EMBED}"
      title="Localisation de Sopjani Tech Sàrl — {ADDRESS_FULL}"
      width="1200"
      height="400"
      style="border:0;"
      allowfullscreen=""
      loading="lazy"
      referrerpolicy="no-referrer-when-downgrade"></iframe>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    {faq_html(faq)}
  </div>
</section>"""
    crumbs = [("Accueil", "/"), ("Contact", "/contact/")]
    contact_title = PAGE_TITLES["contact"]
    contact_desc = META_DESCRIPTIONS["contact"]
    graph = base_graph(contact_title, contact_desc, SITE + "/contact/", faq=faq, extra={"@type": "ContactPage", "name": "Contact", "url": SITE + "/contact/"})
    write_page(["contact", "index.html"], page_shell(contact_title, contact_desc, SITE + "/contact/", graph, body))


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
        PAGE_TITLES["chauffage"],
        META_DESCRIPTIONS["chauffage"],
        "Chauffage : installation, entretien et dépannage",
        "Nous prenons en charge vos besoins en chauffage, de l'étude à la maintenance, pour assurer le confort thermique et la fiabilité de vos installations.",
        "<p>Pannes de chauffage, baisse de rendement, remplacement d'équipement, rénovation de réseaux ou mise en service de nouvelles installations.</p>",
        bullets(["Étude et dimensionnement", "Installation de chaudières et pompes à chaleur", "Entretien et maintenance", "Dépannage et remise en service", "Rénovation de réseaux existants"]),
        clients, process, ["geneve", "lausanne", "vaud", "valais", "fribourg"], ["ventilation", "climatisation", "depannage-sav"],
        [("Intervenez-vous en dépannage chauffage ?", "Oui. Contactez-nous pour évaluer la situation. La disponibilité dépend du secteur et de la nature de la panne."),
         ("Proposez-vous des contrats d'entretien ?", "Oui. Contactez-nous pour discuter des options adaptées à votre installation."),
         ("Qui appeler pour un chauffagiste en Suisse romande ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP} ou via notre page contact."),
         ("Combien coûte un devis chauffage ?", "Le devis est gratuit. Il dépend du type d'installation, de la surface et de l'état de l'existant.")])

    service_page("ventilation", "Ventilation",
        PAGE_TITLES["ventilation"],
        META_DESCRIPTIONS["ventilation"],
        "Ventilation et traitement de l'air",
        "Mise en place et suivi de systèmes de ventilation pour le confort, la qualité de l'air et la maîtrise énergétique de votre bâtiment.",
        "<p>Qualité d'air insuffisante, dysfonctionnements VMC, besoin de renouvellement d'air ou rénovation de réseaux existants.</p>",
        bullets(["Conception et dimensionnement", "Installation de gaines et équipements", "Réglages et mise en service", "Maintenance et contrôles", "Réhabilitation de réseaux"]),
        clients, process, ["geneve", "lausanne", "nyon", "vaud"], ["chauffage", "climatisation", "depannage-sav"],
        [("Réalisez-vous des travaux de rénovation de ventilation ?", "Oui. Nous évaluons l'existant et proposons une solution adaptée au bâtiment et au budget."),
         ("Comment obtenir un devis ventilation ?", "Contactez-nous avec le type de bâtiment, la surface et l'état des installations existantes."),
         ("Quelle entreprise de ventilation contacter en Suisse romande ?", f"{COMPANY_NAME} intervient pour l'installation, la maintenance et le dépannage de ventilation."),
         ("Intervenez-vous en urgence pour une panne VMC ?", f"Contactez-nous au {PHONE_DISP} pour évaluer la situation et la disponibilité.")],
        gallery_cat="ventilation")

    service_page("climatisation", "Climatisation",
        PAGE_TITLES["climatisation"],
        META_DESCRIPTIONS["climatisation"],
        "Climatisation : étude et installation",
        "Nous réalisons l'étude et l'installation de systèmes de climatisation adaptés aux besoins des particuliers et des professionnels.",
        "<p>Besoin de confort estival, remplacement d'installation, extension ou dépannage de système existant.</p>",
        bullets(["Dimensionnement des besoins", "Installation et raccordements", "Mise en service et réglages", "Maintenance périodique", "Dépannage"]),
        clients, process, ["geneve", "nyon", "lausanne", "valais"], ["ventilation", "chauffage", "depannage-sav"],
        [("Quels types de bâtiments équipez-vous ?", "Résidentiel et tertiaire selon faisabilité."),
         ("Intervenez-vous en dépannage climatisation ?", "Oui, contactez-nous pour diagnostiquer votre installation."),
         ("Installez-vous la climatisation près de chez moi ?", f"Nous intervenons en Suisse romande depuis {ADDRESS_LOCALITY}. Contactez-nous avec votre commune."),
         ("Comment obtenir un devis climatisation ?", "Via notre page contact : précisez le type de bâtiment, la surface et vos besoins de confort.")])

    service_page("depannage-sav", "Dépannage SAV",
        PAGE_TITLES["depannage-sav"],
        META_DESCRIPTIONS["depannage-sav"],
        "Dépannage et maintenance (SAV) de vos installations CVC",
        "Intervention sur vos installations en panne ou en fin de vie, avec une approche orientée remise en service et fiabilisation.",
        "<p>Panne de chauffage, ventilation ou climatisation, fuite, dysfonctionnement ou besoin de maintenance préventive.</p>",
        bullets(["Diagnostic de panne", "Intervention corrective", "Maintenance préventive", "Contrats d'entretien", "Optimisation des réglages"]),
        clients, process, ["geneve", "lausanne", "fribourg", "vaud", "valais"], ["chauffage", "ventilation", "sanitaire"],
        [("Comment signaler une urgence ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la situation."),
         ("Quel délai d'intervention ?", "La disponibilité dépend de la nature de la panne et du secteur. Nous évaluons chaque demande au cas par cas."),
         ("Qui appeler pour un dépannage chauffage ou climatisation ?", f"{COMPANY_NAME} au {PHONE_DISP}. Indiquez votre adresse et le type de panne."),
         ("Intervenez-vous le week-end ?", f"Contactez-nous par téléphone ({PHONE_DISP}) : nous évaluons chaque demande selon l'urgence et la disponibilité.")],
        show_urgence=True)

    service_page("sprinkler-protection-incendie", "Sprinkler / protection incendie",
        PAGE_TITLES["sprinkler-protection-incendie"],
        META_DESCRIPTIONS["sprinkler-protection-incendie"],
        "Sprinkler et protection incendie",
        "Intervention en sous-traitance sur des installations sprinkler, avec exécution soignée et coordination chantier.",
        "<p>Montage de réseaux sprinkler, coordination avec autres corps de métier, conformité aux exigences du chantier.</p>",
        bullets(["Pose de réseaux sprinkler", "Sous-traitance spécialisée", "Coordination chantier", "Respect des exigences applicables", "Supportage et finitions techniques"]),
        "<p>Bâtiments soumis à des exigences de protection incendie (ERP, hôtels, industriel, logistique), selon obligations applicables.</p>",
        process, ["geneve", "vaud", "valais"], ["ventilation", "depannage-sav"],
        [("Les travaux sprinkler sont-ils réalisés directement ?", "Les interventions sont assurées en sous-traitance spécialisée, selon la nature du projet."),
         ("Un sprinkler est-il obligatoire ?", "Selon les directives AEAI, certaines catégories de bâtiments peuvent être concernées. Nous pouvons analyser votre situation sur demande.")],
        gallery_cat="sprinkler")

    service_page("sanitaire", "Sanitaire",
        PAGE_TITLES["sanitaire"],
        META_DESCRIPTIONS["sanitaire"],
        "Travaux sanitaires et dépannage",
        "Travaux sanitaires, adaptation de réseaux et interventions sur installations existantes en résidentiel et professionnel.",
        "<p>Fuites, remplacement d'équipements, rénovation de réseaux eau chaude/froide et évacuations.</p>",
        bullets(["Réseaux eau froide et eau chaude", "Pose de robinetterie et équipements", "Réparation et remise en état", "Recherche de fuites", "Maintenance des installations"]),
        clients, process, ["geneve", "lausanne", "nyon", "fribourg"], ["depannage-sav", "chauffage"],
        [("Intervenez-vous en dépannage sanitaire ?", "Oui, contactez-nous pour décrire le problème et organiser une intervention si faisable."),
         ("Réalisez-vous des rénovations complètes de salle de bain ?", "Contactez-nous pour décrire votre projet et vérifier la faisabilité.")],
        gallery_cat="sanitaire")


def build_zones():
    p = lambda t: f"<p>{t}</p>"
    zone_page("geneve", "Genève", "la région de Genève",
        PAGE_TITLES["geneve"],
        META_DESCRIPTIONS["geneve"],
        "Chauffage, ventilation, climatisation et dépannage dans la région de Genève",
        p("Le canton de Genève présente un parc bâti dense, des immeubles résidentiels, des commerces et des bâtiments tertiaires aux contraintes techniques variées. Nous pouvons prendre en charge des besoins en installation, maintenance et dépannage selon la nature du projet.") +
        p("Que vous soyez propriétaire, régie ou responsable technique, contactez-nous pour vérifier la disponibilité d'intervention dans votre secteur."),
        zone_aeo_faq("Genève", "la région de Genève"),
        ["chauffage", "ventilation", "climatisation", "depannage-sav", "sanitaire"], ["vaud", "nyon", "lausanne"])

    zone_page("vaud", "Vaud", "le canton de Vaud",
        PAGE_TITLES["vaud"],
        META_DESCRIPTIONS["vaud"],
        "Ventilation, chauffage et climatisation dans le canton de Vaud",
        p("Le canton de Vaud couvre un territoire étendu, de Lausanne à la région lémanique. Nous intervenons pour des projets d'installation, d'entretien et de dépannage sur différents types de bâtiments.") +
        p("Pour les communes hors axes principaux, contactez-nous afin de confirmer la faisabilité et la planification."),
        zone_aeo_faq("Vaud", "le canton de Vaud"),
        ["chauffage", "ventilation", "climatisation", "depannage-sav"], ["lausanne", "nyon", "geneve", "fribourg"])

    zone_page("lausanne", "Lausanne", "Lausanne et environs",
        PAGE_TITLES["lausanne"],
        META_DESCRIPTIONS["lausanne"],
        "Chauffagiste et CVC à Lausanne et environs",
        p("L'agglomération lausannoise concentre immeubles résidentiels, bâtiments tertiaires et équipements techniques nécessitant un suivi régulier. Nous intervenons pour l'installation, la maintenance et le dépannage CVC.") +
        p("Indiquez le quartier ou la commune exacte lors de votre demande pour une réponse adaptée."),
        zone_aeo_faq("Lausanne", "Lausanne et environs"),
        ["chauffage", "ventilation", "climatisation", "depannage-sav", "sanitaire"], ["nyon", "vaud", "geneve"])

    zone_page("nyon", "Nyon", "la région de Nyon",
        PAGE_TITLES["nyon"],
        META_DESCRIPTIONS["nyon"],
        "Chauffagiste et climatisation dans la région de Nyon",
        p("La région de Nyon, entre Genève et Lausanne, comprend des zones résidentielles et des activités commerciales. Nous pouvons intervenir pour des projets CVC et des dépannages selon disponibilité.") +
        p("Contactez-nous en précisant l'adresse et la nature des travaux."),
        zone_aeo_faq("Nyon", "la région de Nyon"),
        ["climatisation", "chauffage", "ventilation", "sanitaire"], ["geneve", "lausanne", "vaud"])

    zone_page("valais", "Valais", "le canton du Valais",
        PAGE_TITLES["valais"],
        META_DESCRIPTIONS["valais"],
        "Ventilation, chauffage et climatisation en Valais",
        p("Le Valais présente des spécificités climatiques et altitudinales qui influencent les besoins en chauffage et climatisation. Nous intervenons pour des installations et dépannages selon la localisation et la faisabilité.") +
        p("Contactez-nous avec votre commune pour vérifier la disponibilité d'intervention."),
        zone_aeo_faq("Valais", "le canton du Valais"),
        ["chauffage", "climatisation", "depannage-sav", "sprinkler-protection-incendie"], ["geneve", "vaud", "fribourg"])

    zone_page("fribourg", "Fribourg", "le canton de Fribourg",
        PAGE_TITLES["fribourg"],
        META_DESCRIPTIONS["fribourg"],
        "Chauffage, ventilation et dépannage dans le canton de Fribourg",
        p("Le canton de Fribourg, à cheval sur les régions linguistiques, compte un parc bâti varié. Nous pouvons prendre en charge des interventions en chauffage, ventilation et dépannage selon la nature du projet.") +
        p("Précisez la commune et l'urgence de votre demande lors du premier contact."),
        zone_aeo_faq("Fribourg", "le canton de Fribourg"),
        ["chauffage", "ventilation", "depannage-sav", "sanitaire"], ["vaud", "lausanne", "valais"])


def legal_identity_block():
    return f"""<dl class="legal-meta">
  <div><dt>Raison sociale</dt><dd>{COMPANY_NAME}</dd></div>
  <div><dt>Forme juridique</dt><dd>Société à responsabilité limitée (Sàrl)</dd></div>
  <div><dt>Siège social</dt><dd>{ADDRESS_FULL}, Suisse</dd></div>
  <div><dt>Numéro IDE (UID)</dt><dd>{COMPANY_UID}</dd></div>
  <div><dt>Responsable de publication</dt><dd>{PUBLICATION_MANAGER}</dd></div>
  <div><dt>Téléphone</dt><dd><a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a></dd></div>
  <div><dt>Email</dt><dd><a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a></dd></div>
</dl>"""


def build_legal_pages():
    mentions_body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Informations légales</span>
    <div class="rule"></div>
    <h1 id="page-h1">Mentions légales</h1>
    <p class="hero-sub">Informations relatives à l'éditeur du site {SITE.replace('https://', '')} et aux conditions d'utilisation.</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container prose-block">
    <h2 class="section-title" style="font-size:clamp(26px,3vw,40px);">Éditeur du site</h2>
    {legal_identity_block()}
    <h3>Hébergement</h3>
    <p>Ce site est hébergé par {HOST_NAME}, {HOST_ADDRESS}.</p>
    <h3>Propriété intellectuelle</h3>
    <p>L'ensemble des contenus présents sur ce site (textes, images, graphismes, logo, structure) est la propriété de {COMPANY_NAME} ou de ses partenaires, sauf mention contraire. Toute reproduction, représentation ou diffusion, totale ou partielle, sans autorisation écrite préalable est interdite.</p>
    <h3>Limitation de responsabilité</h3>
    <p>{COMPANY_NAME} s'efforce d'assurer l'exactitude des informations publiées sur ce site. Toutefois, elle ne peut garantir l'absence d'erreurs ou d'omissions et décline toute responsabilité pour les dommages directs ou indirects résultant de l'accès ou de l'utilisation du site.</p>
    <p>Les informations techniques et commerciales ne constituent pas une offre contractuelle. Seul un devis ou un contrat signé fait foi.</p>
    <h3>Liens hypertextes</h3>
    <p>Le site peut contenir des liens vers des sites tiers. {COMPANY_NAME} n'exerce aucun contrôle sur ces sites et décline toute responsabilité quant à leur contenu.</p>
    <h3>Droit applicable</h3>
    <p>Le présent site et les présentes mentions légales sont soumis au droit suisse. Le for juridique est celui du siège de l'entreprise, sous réserve des dispositions légales impératives.</p>
    <p style="margin-top:28px;"><a href="/politique-confidentialite/" class="text-link">Politique de confidentialité →</a></p>
  </div>
</section>"""
    mentions_title = f"Mentions légales | {COMPANY_NAME}"
    mentions_desc = META_DESCRIPTIONS["mentions-legales"]
    mentions_url = SITE + "/mentions-legales/"
    mentions_crumbs = [("Accueil", "/"), ("Mentions légales", "/mentions-legales/")]
    mentions_graph = base_graph(mentions_title, mentions_desc, mentions_url, mentions_crumbs)
    write_page(["mentions-legales", "index.html"], page_shell(mentions_title, mentions_desc, mentions_url, mentions_graph, mentions_body, mentions_crumbs))

    ga4_note = (
        f"Ce site peut utiliser Google Analytics 4 (ID de mesure : {GA4_MEASUREMENT_ID}) pour mesurer l'audience. "
        "Le script n'est chargé qu'après votre acceptation via le bandeau cookies. "
        "Google peut traiter des données techniques (adresse IP anonymisée, pages consultées, type d'appareil, navigateur). "
        "Pour en savoir plus : <a href=\"https://policies.google.com/privacy\" target=\"_blank\" rel=\"noopener noreferrer\">politique de confidentialité de Google</a>."
        if GA4_MEASUREMENT_ID else
        "Ce site ne dispose actuellement d'aucun outil de mesure d'audience tiers activé."
    )
    privacy_body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Protection des données</span>
    <div class="rule"></div>
    <h1 id="page-h1">Politique de confidentialité</h1>
    <p class="hero-sub">Comment {COMPANY_NAME} traite les données personnelles collectées via ce site, conformément à la loi suisse sur la protection des données (nLPD).</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container prose-block">
    <h2 class="section-title" style="font-size:clamp(26px,3vw,40px);">Responsable du traitement</h2>
    {legal_identity_block()}
    <h3>Données collectées</h3>
    <p>Nous pouvons traiter les catégories de données suivantes :</p>
    <ul class="bullet-list">
      <li><strong>Formulaire de contact</strong> : nom, téléphone, adresse email, canton/commune, type de besoin et message que vous nous transmettez volontairement.</li>
      <li><strong>Données de navigation</strong> : pages consultées, durée de visite, type d'appareil et navigateur, dans le cadre de la mesure d'audience si activée.</li>
      <li><strong>Données techniques</strong> : journaux serveur et cookies strictement nécessaires au fonctionnement du site.</li>
    </ul>
    <h3>Finalités du traitement</h3>
    <p>Les données sont traitées pour : répondre à vos demandes de contact ou de devis, assurer le suivi commercial, améliorer le site et mesurer son audience, et garantir la sécurité technique du site.</p>
    <h3>Base légale</h3>
    <p>Le traitement repose sur l'exécution de mesures précontractuelles à votre demande (formulaire de contact), sur l'intérêt légitime de {COMPANY_NAME} à assurer la sécurité et le bon fonctionnement du site, et sur votre consentement lorsque la loi l'exige (notamment pour certains cookies de mesure).</p>
    <h3>Destinataires et sous-traitants</h3>
    <p>Les données peuvent être accessibles aux collaborateurs habilités de {COMPANY_NAME}, ainsi qu'à nos prestataires techniques dans la mesure nécessaire :</p>
    <ul class="bullet-list">
      <li><strong>{HOST_NAME}</strong> — hébergement du site ({HOST_ADDRESS}).</li>
      {"<li><strong>Google LLC</strong> — mesure d'audience via Google Analytics 4.</li>" if GA4_MEASUREMENT_ID else ""}
    </ul>
    <h3>Durée de conservation</h3>
    <p>Les demandes de contact sont conservées le temps nécessaire au traitement de votre demande et au suivi commercial, puis archivées ou supprimées selon les obligations légales applicables. Les données de mesure d'audience sont conservées selon les paramètres configurés dans l'outil concerné.</p>
    <h3>Cookies et mesure d'audience</h3>
    <p>{ga4_note}</p>
    <p>Vous pouvez limiter le dépôt de cookies via les paramètres de votre navigateur. La désactivation de certains cookies peut affecter le fonctionnement du site.</p>
    <h3>Vos droits</h3>
    <p>Conformément à la nLPD, vous disposez notamment d'un droit d'accès, de rectification et, le cas échéant, d'effacement de vos données personnelles, ainsi que du droit de vous opposer à certains traitements ou de demander leur limitation.</p>
    <p>Pour exercer vos droits, contactez-nous à <a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a> ou par téléphone au <a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a>. Vous pouvez également saisir le Préposé fédéral à la protection des données et à la transparence (PFPDT) en cas de litige.</p>
    <h3>Sécurité</h3>
    <p>Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données contre l'accès non autorisé, la perte ou la divulgation.</p>
    <h3>Modifications</h3>
    <p>Cette politique peut être mise à jour pour refléter l'évolution du site ou de la réglementation. La version en vigueur est celle publiée sur cette page.</p>
    <p style="margin-top:28px;"><a href="/mentions-legales/" class="text-link">Mentions légales →</a></p>
  </div>
</section>"""
    privacy_title = f"Politique de confidentialité | {COMPANY_NAME}"
    privacy_desc = META_DESCRIPTIONS["politique-confidentialite"]
    privacy_url = SITE + "/politique-confidentialite/"
    privacy_crumbs = [("Accueil", "/"), ("Politique de confidentialité", "/politique-confidentialite/")]
    privacy_graph = base_graph(privacy_title, privacy_desc, privacy_url, privacy_crumbs)
    write_page(["politique-confidentialite", "index.html"], page_shell(privacy_title, privacy_desc, privacy_url, privacy_graph, privacy_body, privacy_crumbs))


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


def build_realisations():
    cat_labels = [
        ("sprinkler", "Sprinkler et protection incendie"),
        ("ventilation", "Ventilation"),
        ("sanitaire", "Sanitaire et tuyauterie"),
    ]
    sections = ""
    image_objects = []
    for cat, label in cat_labels:
        imgs = REALISATIONS_BY_CAT.get(cat, [])
        if not imgs:
            continue
        cards = []
        for fn, w, h, alt, cap in imgs:
            cards.append(f"""<figure class="gallery-card">
  <img src="/assets/realisations/{fn}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">
  <figcaption>{cap}</figcaption>
</figure>""")
            image_objects.append({
                "@type": "ImageObject",
                "contentUrl": f"{SITE}/assets/realisations/{fn}",
                "url": f"{SITE}/assets/realisations/{fn}",
                "name": cap,
                "description": alt,
                "width": w,
                "height": h,
                "creditText": COMPANY_NAME,
                "creator": {"@type": "Organization", "name": COMPANY_NAME},
                "copyrightHolder": {"@type": "Organization", "name": COMPANY_NAME},
            })
        sections += f"""<section class="content-section" aria-labelledby="real-{cat}">
  <div class="container">
    <span class="label">{label}</span>
    <div class="rule"></div>
    <h2 class="section-title" id="real-{cat}" style="font-size:clamp(26px,3vw,40px);margin-bottom:24px;">{label}</h2>
    <div class="gallery gallery-cols-3">{"".join(cards)}</div>
  </div>
</section>
<div class="section-divider"></div>
"""
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Réalisations</span>
    <div class="rule"></div>
    <h1 id="page-h1">Nos réalisations en CVC, sprinkler et sanitaire</h1>
    <p class="hero-sub">Aperçu de chantiers réalisés par {COMPANY_NAME} en Suisse romande : sprinkler et protection incendie, ventilation et tuyauterie sanitaire.</p>
  </div>
</section>
<div class="section-divider"></div>
{sections}
{cta_band()}"""
    crumbs = [("Accueil", "/"), ("Réalisations", "/realisations/")]
    title = PAGE_TITLES.get("realisations", "Réalisations CVC, sprinkler et sanitaire | Sopjani Tech Sàrl")
    desc = META_DESCRIPTIONS.get("realisations", f"Réalisations de {COMPANY_NAME} en Suisse romande : installations sprinkler, ventilation et tuyauterie sanitaire. Photos de chantiers réels.")
    gallery_schema = {
        "@type": "ImageGallery",
        "name": "Réalisations Sopjani Tech Sàrl",
        "url": SITE + "/realisations/",
        "image": image_objects,
    }
    graph = base_graph(title, desc, SITE + "/realisations/", crumbs, extra=[gallery_schema])
    write_page(["realisations", "index.html"], page_shell(title, desc, SITE + "/realisations/", graph, body, crumbs))


def build_sitemap_page():
    sections = [
        ("Navigation", [("/", "Accueil"), ("/a-propos/", "À propos"), ("/realisations/", "Réalisations"), ("/contact/", "Contact"), ("/plan-du-site/", "Plan du site")]),
        ("Prestations", [(f"/{s}/", n) for s, n, _ in SERVICES] + [("/prestations/", "Toutes les prestations")]),
        ("Zones d'intervention", [(f"/{z}/", n) for z, n, _ in ZONES] + [("/zones-intervention/", "Toutes les zones")]),
        ("Informations légales", [("/mentions-legales/", "Mentions légales"), ("/politique-confidentialite/", "Politique de confidentialité")]),
    ]
    blocks = ""
    all_links = []
    for sec_title, links in sections:
        items = "".join(f'<li><a href="{u}">{l}</a></li>' for u, l in links)
        blocks += f'<div class="sitemap-section"><h2 class="section-title" style="font-size:clamp(20px,2.5vw,28px);margin-bottom:16px;">{sec_title}</h2><ul class="sitemap-list">{items}</ul></div>'
        all_links.extend(links)
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <span class="label">Navigation</span>
    <div class="rule"></div>
    <h1 id="page-h1">Plan du site</h1>
    <p class="hero-sub">Accès direct à toutes les pages de {COMPANY_NAME} : prestations, zones d'intervention et informations de contact.</p>
  </div>
</section>
<div class="section-divider"></div>
<section class="content-section">
  <div class="container sitemap-grid">{blocks}</div>
</section>"""
    crumbs = [("Accueil", "/"), ("Plan du site", "/plan-du-site/")]
    title = PAGE_TITLES["plan-du-site"]
    desc = META_DESCRIPTIONS["plan-du-site"]
    item_list = {
        "@type": "ItemList",
        "name": "Plan du site",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label, "url": SITE + path}
            for i, (path, label) in enumerate(all_links)
        ],
    }
    graph = base_graph(title, desc, SITE + "/plan-du-site/", crumbs, extra=item_list)
    write_page(["plan-du-site", "index.html"], page_shell(title, desc, SITE + "/plan-du-site/", graph, body, crumbs))


def build_sitemap():
    today = date.today().isoformat()
    entries = [
        ("/", "weekly", "1.0"),
        ("/contact/", "monthly", "0.9"),
        ("/prestations/", "monthly", "0.9"),
        ("/zones-intervention/", "monthly", "0.9"),
        ("/a-propos/", "monthly", "0.8"),
        ("/realisations/", "monthly", "0.8"),
        ("/plan-du-site/", "monthly", "0.5"),
        ("/mentions-legales/", "yearly", "0.3"),
        ("/politique-confidentialite/", "yearly", "0.3"),
    ]
    entries += [(f"/{s}/", "monthly", "0.8") for s, _, _ in SERVICES]
    entries += [(f"/{z}/", "monthly", "0.8") for z, _, _ in ZONES]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, freq, priority in entries:
        lines.append(f"  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def build_robots():
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def build_js():
    ga4_js = ""
    if GA4_MEASUREMENT_ID:
        ga4_js = f"""
const GA4_ID = '{GA4_MEASUREMENT_ID}';
let ga4Loaded = false;

function hasCookieConsent() {{
  try {{ return localStorage.getItem(COOKIE_CONSENT_KEY) === '1'; }} catch (e) {{ return false; }}
}}

function loadGA4() {{
  if (!GA4_ID || ga4Loaded) return;
  ga4Loaded = true;
  const link = document.createElement('link');
  link.rel = 'preconnect';
  link.href = 'https://www.googletagmanager.com';
  document.head.appendChild(link);
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  document.head.appendChild(s);
  s.onload = () => {{
    gtag('js', new Date());
    gtag('config', GA4_ID, {{
      anonymize_ip: true,
      cookie_flags: 'SameSite=None;Secure',
      send_page_view: true
    }});
  }};
}}
"""
    else:
        ga4_js = """
function hasCookieConsent() {
  try { return localStorage.getItem(COOKIE_CONSENT_KEY) === '1'; } catch (e) { return false; }
}
function loadGA4() {}
"""

    js_head = """const COOKIE_CONSENT_KEY = 'sopjanitech_cookie_consent';
const cookieBanner = document.getElementById('cookieBanner');
const cookieAccept = document.getElementById('cookieAccept');
"""
    js_cookie = """
function initCookieBanner() {
  if (!cookieBanner) return;
  if (hasCookieConsent()) return;
  cookieBanner.hidden = false;
}

function acceptCookies() {
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, '1');
  } catch (e) {}
  if (cookieBanner) cookieBanner.hidden = true;
  loadGA4();
}

if (cookieAccept) {
  cookieAccept.addEventListener('click', acceptCookies);
}
initCookieBanner();
if (hasCookieConsent()) loadGA4();
"""
    js_tail = """
const burger = document.getElementById('burger');
const mobileNav = document.getElementById('mobileNav');
const mobileNavOverlay = document.getElementById('mobileNavOverlay');

function setMobileNav(open) {
  if (!mobileNav || !burger) return;
  mobileNav.classList.toggle('open', open);
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  mobileNav.setAttribute('aria-hidden', !open);
  document.body.classList.toggle('nav-open', open);
  if (mobileNavOverlay) {
    mobileNavOverlay.hidden = !open;
  }
}

function closeMobileNav() {
  setMobileNav(false);
}

if (burger && mobileNav) {
  burger.addEventListener('click', () => {
    setMobileNav(!mobileNav.classList.contains('open'));
  });
  mobileNav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', closeMobileNav);
  });
  if (mobileNavOverlay) {
    mobileNavOverlay.addEventListener('click', closeMobileNav);
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && mobileNav.classList.contains('open')) closeMobileNav();
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
function trackEvent(name, params) {
  if (typeof gtag === 'function') gtag('event', name, params || {});
}
document.querySelectorAll('.track-phone').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'phone', event_category: 'contact' });
    trackEvent('click_phone', { event_category: 'contact', event_label: 'phone' });
  });
});
document.querySelectorAll('.track-email').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'email', event_category: 'contact' });
    trackEvent('click_email', { event_category: 'contact', event_label: 'email' });
  });
});
document.querySelectorAll('.track-whatsapp').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('contact', { method: 'whatsapp', event_category: 'contact' });
    trackEvent('click_whatsapp', { event_category: 'contact', event_label: 'whatsapp' });
  });
});
document.querySelectorAll('.track-devis').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('generate_lead', { method: 'devis_button', event_category: 'conversion' });
    trackEvent('click_devis', { event_category: 'conversion', event_label: 'demande_devis' });
  });
});
document.querySelectorAll('.track-form').forEach(form => {
  form.addEventListener('submit', e => {
    const endpoint = form.getAttribute('data-form-endpoint') || form.getAttribute('action') || '';
    trackEvent('generate_lead', { method: 'contact_form', event_category: 'conversion' });
    trackEvent('form_submit', { event_category: 'conversion', event_label: 'contact_form' });
    if (!endpoint || endpoint === '#') {
      e.preventDefault();
      const feedback = form.querySelector('.form-feedback');
      if (feedback) {
        feedback.textContent = 'Merci pour votre message. Nous vous recontacterons dans les meilleurs délais.';
        feedback.hidden = false;
      }
      form.reset();
    }
  });
});
document.querySelectorAll('.track-google').forEach(el => {
  el.addEventListener('click', () => {
    trackEvent('click_google', { event_category: 'contact', event_label: 'google_business' });
  });
});
"""
    js = js_head + ga4_js + js_cookie + js_tail
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
    build_realisations()
    build_sitemap_page()
    build_legal_pages()
    build_redirect("prestations.html", "/prestations/")
    build_redirect("contact.html", "/contact/")
    build_redirect("mentions-legales.html", "/mentions-legales/")
    build_redirect("politique-confidentialite.html", "/politique-confidentialite/")
    build_sitemap()
    build_robots()
    print("Site generated successfully.")


if __name__ == "__main__":
    main()
