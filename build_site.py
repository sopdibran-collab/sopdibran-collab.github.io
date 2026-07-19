#!/usr/bin/env python3
"""Generate Sopjani Tech static site pages."""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://sopjanitech.ch"
# Anciennes URLs .html → chemins canoniques (slash final). _redirects = 301 sur Cloudflare/Netlify.
LEGACY_REDIRECTS = {
    "prestations.html": "/prestations/",
    "contact.html": "/contact/",
    "mentions-legales.html": "/mentions-legales/",
    "politique-confidentialite.html": "/politique-confidentialite/",
}
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
# Logos (interim) — sources: Documents/SopjaniTechSàrl/Logo → assets/brand/
# Remplacer par les SVG vectorisés complets dès qu'ils sont prêts.
LOGO_HEADER = "/assets/brand/logo-primary-64.png"
LOGO_FOOTER = "/assets/brand/logo-primary-64.png"
LOGO_FULL = "/assets/logo-full.png"
FAVICON_PATH = "/assets/favicon.png"
APPLE_TOUCH_ICON = "/assets/apple-touch-icon.png"
OG_IMAGE = f"{SITE}/assets/og-logo.png"
FAVICON = f"{SITE}{FAVICON_PATH}"
THEME_COLOR = "#0B2545"
ADDRESS_STREET = "Rue Pierre de Savoie 9"
ADDRESS_POSTAL = "1680"
ADDRESS_LOCALITY = "Romont FR"
ADDRESS_FULL = "Rue Pierre de Savoie 9, 1680 Romont FR"
COMPANY_NAME = "Sopjani Tech Sàrl"
COMPANY_UID = "CHE-177.567.012"
PUBLICATION_MANAGER = "Shkodran Sopjani"
HOST_NAME = "GitHub, Inc. (GitHub Pages)"
HOST_ADDRESS = "88 Colin P. Kelly Jr. St, San Francisco, CA 94107, États-Unis"
HOURS = "Tous les jours, 7h00 – 17h00"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Rue+Pierre+de+Savoie+9,+1680+Romont"
MAP_EMBED = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1481964.3806735645!2d5.895466104411914!3d46.67378415677807!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9458f52305e1fe3%3A0x31fd51d876fffe44!2sSopjani-tech%20s%C3%A0rl!5e1!3m2!1sfr!2sch!4v1781214251877!5m2!1sfr!2sch"
GOOGLE_BUSINESS_URL = "https://maps.app.goo.gl/hWWQCXAZzrTCgjFr7"
COPYRIGHT_YEAR = 2026
IMAGE_LICENSE_URL = f"{SITE}/mentions-legales/#propriete-intellectuelle"
IMAGE_ACQUIRE_LICENSE_URL = f"{SITE}/contact/"
IMAGE_COPYRIGHT_NOTICE = f"© {COPYRIGHT_YEAR} {COMPANY_NAME}"

CVCS_GROUP = "Chauffage, Ventilation, Climatisation, Sanitaire"
CVCS_PROSE = "chauffage, ventilation, climatisation et sanitaire"
CVCS_ALL_PROSE = "chauffage, ventilation, climatisation, sanitaire, dépannage SAV et sprinkler"

META_DESCRIPTIONS = {
    "home": f"Sopjani Tech Sàrl : étude, installation et dépannage en {CVCS_PROSE} en Suisse romande. Devis gratuit.",
    "prestations": f"{CVCS_GROUP}, dépannage SAV et sprinkler en Suisse romande. Découvrez toutes les prestations CVC de Sopjani Tech Sàrl.",
    "zones-intervention": f"{COMPANY_NAME} intervient près de vous en Suisse romande : Genève, Vaud, Valais, Fribourg, Neuchâtel et agglomérations. Siège à {ADDRESS_LOCALITY}.",
    "a-propos": f"{COMPANY_NAME}, entreprise CVC basée à {ADDRESS_FULL}. {CVCS_GROUP}, sprinkler et dépannage en Suisse romande.",
    "contact": f"Devis gratuit et dépannage CVC urgent. {COMPANY_NAME} — {PHONE_DISP} · {EMAIL} · {ADDRESS_FULL}.",
    "depannage-sav": f"Dépannage en {CVCS_PROSE} en Suisse romande. Urgence : appelez le {PHONE_DISP}.",
    "chauffage": "Chauffagiste en Suisse romande (Nyon, Lausanne, Genève, Fribourg, Valais) : installation, entretien et dépannage. Pompes à chaleur et chaudières. Devis gratuit.",
    "ventilation": "Entreprise de ventilation en Suisse romande. VMC, traitement de l'air, dépannage et maintenance.",
    "climatisation": "Climatisation à Nyon, Lausanne et Genève : étude, pose et dépannage. Split, multi-split et PAC air-air. Devis gratuit — Sopjani Tech Sàrl.",
    "sprinkler-protection-incendie": "Installation de réseaux sprinkler en sous-traitance en Suisse romande. Protection incendie pour ERP et bâtiments industriels.",
    "sanitaire": "Installations et dépannages sanitaires en Suisse romande. Réseaux eau chaude/froide, fuites, chauffe-eau et rénovations.",
    "geneve": "Chauffagiste à Genève : installation, entretien et dépannage chauffage, climatisation et CVC. Devis gratuit — Sopjani Tech Sàrl.",
    "vaud": "Chauffagiste dans le canton de Vaud (Nyon, Lausanne, Morges) : chauffage, climatisation et dépannage CVC. Devis gratuit.",
    "lausanne": "Chauffagiste à Lausanne : installation, entretien et dépannage chauffage. Pompes à chaleur, chaudières et CVC. Devis gratuit.",
    "nyon": "Climatisation et chauffagiste à Nyon : installation, entretien et dépannage CVC. Devis gratuit — Sopjani Tech Sàrl.",
    "valais": "Chauffagiste en Valais (Sion, Martigny, Monthey) : chauffage, climatisation et dépannage CVC. Devis gratuit.",
    "fribourg": "Chauffagiste Fribourg et Romont : installation, entretien et dépannage chauffage et CVC. Siège à Romont — devis gratuit.",
    "neuchatel": "Chauffagiste à Neuchâtel et La Chaux-de-Fonds : chauffage, climatisation et dépannage CVC. Devis gratuit.",
    "mentions-legales": f"Mentions légales de {COMPANY_NAME} : raison sociale, siège à {ADDRESS_FULL}, UID {COMPANY_UID} et contact.",
    "politique-confidentialite": f"Politique de confidentialité de {COMPANY_NAME} : traitement des données, cookies et droits selon la nLPD suisse.",
    "plan-du-site": "Plan du site Sopjani Tech Sàrl : accès à toutes les pages prestations, zones d'intervention et contact en Suisse romande.",
    "realisations": f"Réalisations de {COMPANY_NAME} en Suisse romande : chauffage, ventilation, sanitaire et sprinkler. Photos de chantiers réels.",
}

PAGE_TITLES = {
    "home": f"Sopjani Tech Sàrl | {CVCS_GROUP} et dépannage en Suisse romande",
    "a-propos": "Sopjani Tech Sàrl | Entreprise CVC à Romont, Suisse romande",
    "contact": "Devis et dépannage CVC | Contact | Sopjani Tech Sàrl",
    "prestations": f"Prestations CVC | {CVCS_GROUP} | Sopjani Tech Sàrl",
    "zones-intervention": "Zones d'intervention CVC | Suisse romande | Sopjani Tech Sàrl",
    "plan-du-site": "Plan du site | Sopjani Tech Sàrl",
    "chauffage": "Chauffagiste Suisse romande | Nyon, Lausanne, Genève | Sopjani Tech Sàrl",
    "ventilation": "Entreprise ventilation Suisse romande | Sopjani Tech Sàrl",
    "climatisation": "Climatisation Nyon, Lausanne & Genève | Installation | Sopjani Tech Sàrl",
    "depannage-sav": f"Dépannage {CVCS_PROSE} | Urgence CVC | Sopjani Tech Sàrl",
    "sanitaire": "Sanitaire | Travaux et dépannage | Sopjani Tech Sàrl",
    "sprinkler-protection-incendie": "Sprinkler et protection incendie | Sopjani Tech Sàrl",
    "geneve": "Chauffagiste Genève | Climatisation & CVC | Sopjani Tech Sàrl",
    "vaud": "Chauffagiste Vaud | Nyon, Lausanne | Sopjani Tech Sàrl",
    "lausanne": "Chauffagiste Lausanne | Chauffage & dépannage | Sopjani Tech Sàrl",
    "nyon": "Climatisation & chauffagiste Nyon | Sopjani Tech Sàrl",
    "valais": "Chauffagiste Valais | CVC & climatisation | Sopjani Tech Sàrl",
    "fribourg": "Chauffagiste Fribourg | CVC Romont | Sopjani Tech Sàrl",
    "neuchatel": "Chauffagiste Neuchâtel | CVC & climatisation | Sopjani Tech Sàrl",
    "realisations": "Réalisations CVC : chauffage, sanitaire, ventilation et sprinkler | Sopjani Tech Sàrl",
}

SERVICES = [
    ("chauffage", "Chauffage", "Installation, entretien et dépannage de systèmes de chauffage."),
    ("ventilation", "Ventilation", "Ventilation et traitement de l'air pour bâtiments."),
    ("climatisation", "Climatisation", "Étude et installation de systèmes de climatisation."),
    ("sanitaire", "Sanitaire", "Installations sanitaires, dépannage et rénovations en Suisse romande."),
    ("depannage-sav", "Dépannage SAV", "Maintenance et dépannage de vos installations CVC."),
    ("sprinkler-protection-incendie", "Sprinkler / protection incendie", "Réseaux sprinkler en sous-traitance spécialisée."),
]

# Icônes SVG identiques sur desktop, mobile et pages prestations (Lucide, stroke linéaire).
SERVICE_SVGS = {
    "chauffage": (
        '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>'
    ),
    "ventilation": (
        '<path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/>'
        '<path d="M9.6 4.6A2 2 0 1 1 11 8H2"/>'
        '<path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>'
    ),
    "climatisation": (
        '<path d="M12 2v20"/><path d="M2 12h20"/>'
        '<path d="m4.93 4.93 14.14 14.14"/><path d="m19.07 4.93-14.14 14.14"/>'
    ),
    "sanitaire": (
        '<path d="M7 3v2"/><path d="M17 3v2"/><path d="M7 5h10"/>'
        '<path d="M12 5v7"/><path d="M9 20h6"/><path d="M10 12h4"/>'
    ),
    "depannage-sav": (
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "sprinkler-protection-incendie": (
        '<path d="M12 3v3"/><path d="M8 6h8"/>'
        '<path d="M12 9v5"/><path d="M9 20h6"/>'
        '<path d="M10 14h4"/><path d="M8 17h8"/>'
    ),
}


def service_icon(slug, variant="card"):
    paths = SERVICE_SVGS.get(slug, "")
    svg = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round" stroke-linejoin="round">'
        f"{paths}</svg>"
    )
    if variant in ("nav", "card", "hero", "urgence"):
        badge_mod = {"card": "--card", "hero": "--hero", "urgence": "--urgence"}.get(variant, "")
        badge_cls = f"svc-icon__badge{' svc-icon__badge' + badge_mod if badge_mod else ''}"
        inner = f'<span class="{badge_cls}">{svg}</span>'
    else:
        inner = svg
    return (
        f'<span class="svc-icon svc-icon--{slug} svc-icon--{variant}" aria-hidden="true">'
        f"{inner}</span>"
    )


def service_nav_link(slug, label, submenu=False):
    role = ' role="menuitem"' if submenu else ""
    return f'<a href="/{slug}/"{role}>{service_icon(slug, "nav")}<span>{label}</span></a>'


def hub_card(slug, name, desc, cta="En savoir plus →"):
    return (
        f'<a class="hub-card" data-svc="{slug}" href="/{slug}/">'
        f'{service_icon(slug, "card")}'
        f"<h3>{name}</h3><p>{desc}</p><span class=\"link-arrow\">{cta}</span></a>"
    )

ZONES = [
    ("geneve", "Genève", "la région de Genève"),
    ("vaud", "Vaud", "le canton de Vaud"),
    ("lausanne", "Lausanne", "Lausanne et environs"),
    ("nyon", "Nyon", "la région de Nyon"),
    ("valais", "Valais", "le canton du Valais"),
    ("fribourg", "Fribourg", "le canton de Fribourg"),
    ("neuchatel", "Neuchâtel", "le canton de Neuchâtel"),
]

# Couverture affichée sur les pages prestations (cantons + villes représentatives).
CANTON_ZONE_SLUGS = ("geneve", "vaud", "valais", "fribourg", "neuchatel")
CITY_COVERAGE_LINKS = (
    ("Genève", "/geneve/"),
    ("Lausanne", "/lausanne/"),
    ("Nyon", "/nyon/"),
    ("Morges", "/vaud/"),
    ("Vevey", "/vaud/"),
    ("Yverdon-les-Bains", "/vaud/"),
    ("Sion", "/valais/"),
    ("Martigny", "/valais/"),
    ("Monthey", "/valais/"),
    ("Sierre", "/valais/"),
    ("Fribourg", "/fribourg/"),
    ("Bulle", "/fribourg/"),
    ("Romont", "/fribourg/"),
    ("Neuchâtel", "/neuchatel/"),
    ("La Chaux-de-Fonds", "/neuchatel/"),
)

ALL_ZONE_SLUGS = tuple(z for z, _, _ in ZONES)


def service_zones_block():
    """Cantons + villes pour la section « Zones desservies » des prestations."""
    cantons = "".join(
        f'<a class="zone-pill" href="/{z}/">{n}</a>'
        for z, n, _ in ZONES if z in CANTON_ZONE_SLUGS
    )
    cities = "".join(
        f'<a class="zone-pill zone-pill--city" href="{href}">{label}</a>'
        for label, href in CITY_COVERAGE_LINKS
    )
    return f"""<div class="zone-coverage">
  <p class="zone-coverage__label">Cantons</p>
  <div class="zone-links">{cantons}</div>
  <p class="zone-coverage__label">Villes &amp; agglomérations</p>
  <div class="zone-links">{cities}</div>
</div>"""

ORG_SCHEMA = {
    "@type": ["HVACBusiness", "LocalBusiness"],
    "@id": f"{SITE}/#organization",
    "name": "Sopjani Tech Sàrl",
    "url": SITE,
    "description": f"{CVCS_GROUP}, dépannage SAV et sprinkler en Suisse romande.",
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
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "07:00",
        "closes": "17:00",
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
    "description": f"{CVCS_GROUP} et dépannage en Suisse romande.",
    "publisher": {"@id": f"{SITE}/#organization"},
    "inLanguage": "fr-CH",
    "potentialAction": {
        "@type": "CommunicateAction",
        "name": "Demander un devis",
        "target": SITE + "/contact/",
    },
}

QUI_SOMMES_NOUS_HTML = f"""
<p>Sopjani Tech Sàrl est une entreprise active dans les domaines du chauffage, de la ventilation, de la climatisation, du sanitaire, du dépannage SAV et du sprinkler / protection incendie en Suisse romande. Notre siège se trouve à {ADDRESS_FULL}, dans le canton de Fribourg.</p>
<p>Nous accompagnons nos clients avec une approche simple : comprendre le besoin, proposer une solution adaptée et intervenir avec sérieux selon la nature de la demande.</p>
<p>Nous intervenons principalement à Genève, dans le canton de Vaud, à Lausanne, à Nyon, ainsi qu'en Valais et à Fribourg. Pour d'autres secteurs en Suisse romande, la possibilité d'intervention peut être étudiée selon le projet.</p>
<p>Notre activité couvre différents besoins techniques, qu'il s'agisse d'installation, de maintenance ou de dépannage. Nous accordons une attention particulière à la clarté des échanges, à la réactivité et à l'adaptation aux contraintes du terrain.</p>
<div class="cert-block" style="margin:28px 0;">
  <div class="cert-title">Nos engagements</div>
  <ul class="bullet-list">
    <li>Devis gratuit et sans engagement</li>
    <li>Un interlocuteur unique, du premier contact à la fin des travaux</li>
    <li>Échanges clairs sur la nature et le coût des travaux avant intervention</li>
    <li>Société à responsabilité limitée inscrite au registre du commerce suisse (UID {COMPANY_UID}, vérifiable sur <a href="https://www.zefix.ch" target="_blank" rel="noopener noreferrer">Zefix</a>)</li>
  </ul>
  <p style="margin-top:20px;"><a href="{GOOGLE_BUSINESS_URL}" class="text-link track-google" target="_blank" rel="noopener noreferrer">Voir notre fiche Google et nos avis →</a></p>
</div>
<p>Vous avez une demande en {CVCS_PROSE} ou en dépannage SAV ? <a href="/contact/">Contactez-nous</a> pour échanger sur votre besoin et vérifier la disponibilité d'intervention dans votre zone.</p>
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
    <div class="urgence-band__content">
      {service_icon("depannage-sav", "urgence")}
      <div>
        <p class="urgence-band__label">Dépannage urgent</p>
        <p class="urgence-band__text">Panne de {CVCS_PROSE} ? Contactez-nous pour évaluer la situation et la disponibilité d'intervention.</p>
      </div>
    </div>
    <div class="urgence-band__actions">
      <a href="tel:{PHONE}" class="btn btn-urgence track-phone">Appeler · {PHONE_DISP}</a>
      <a href="{WA}" class="btn btn-secondary track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
    </div>
  </div>
</section>"""


def zone_aeo_faq(name, region):
    """FAQ orientée requêtes locales et moteurs de réponse."""
    return [
        (f"Qui appeler pour un chauffagiste à {name} ?", f"{COMPANY_NAME} intervient comme chauffagiste dans {region} : installation, entretien et dépannage de chaudières et pompes à chaleur. Appelez le {PHONE_DISP} ou passez par la page contact."),
        (f"Qui appeler pour un dépannage CVC à {name} ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp. Indiquez votre commune, le type de bâtiment et la nature de la panne."),
        (f"Intervenez-vous pour la ventilation dans {region} ?", f"Oui, nous réalisons installation, maintenance et dépannage de ventilation dans {region}, selon faisabilité et planning."),
        (f"Proposez-vous le chauffage, la ventilation et la climatisation à {name} ?", f"Oui. Étude, installation, entretien et dépannage en {CVCS_PROSE} selon votre projet."),
        (f"Comment obtenir un devis à {name} ?", "Via notre page contact ou par téléphone : décrivez le bâtiment, la localisation exacte et le type de travaux (installation, maintenance ou dépannage)."),
    ]


def chauffagiste_local_block():
    """Maillage interne pour requêtes « chauffagiste + ville » (GSC)."""
    links = (
        ("Nyon", "/nyon/"),
        ("Lausanne", "/lausanne/"),
        ("Genève", "/geneve/"),
        ("Fribourg", "/fribourg/"),
        ("Valais", "/valais/"),
        ("Vaud", "/vaud/"),
        ("Neuchâtel", "/neuchatel/"),
    )
    pills = "".join(f'<a class="zone-pill" href="{href}">Chauffagiste {label}</a>' for label, href in links)
    return f"""<h3>Chauffagiste près de chez vous</h3>
<p>Vous cherchez un chauffagiste à Nyon, Lausanne, Genève ou ailleurs en Suisse romande ? Nous intervenons pour l'installation, l'entretien et le dépannage — pompes à chaleur, chaudières et réseaux de chauffage.</p>
<div class="zone-links">{pills}</div>
<p style="margin-top:16px;"><a href="/climatisation/" class="text-link">Voir aussi la climatisation (Nyon, Lausanne, Genève) →</a></p>"""


# Photos de chantiers réels (fichier, largeur, hauteur, alt SEO, catégorie, légende)
REALISATIONS = [
    ("sprinkler-poste-controle.jpg", 960, 1280, "Poste de contrôle sprinkler avec tuyauterie rouge, vannes bleues et manomètres installé par Sopjani Tech Sàrl", "sprinkler", "Poste de contrôle sprinkler"),
    ("sprinkler-technicien-brasure.jpg", 720, 1280, "Technicien de Sopjani Tech Sàrl soude au TIG sous station de chauffage à distance sur chantier", "sprinkler", "Soude au TIG sous station chauffage à distance"),
    ("sprinkler-vanne-arret-secteur.jpg", 720, 1280, "Poste d'alarme sous eau d'un réseau sprinkler avec manomètres de contrôle, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous eau"),
    ("sprinkler-collecteur-rouges.jpg", 1280, 720, "Centrale sprinkler sous eau avec tuyauterie rouge et vannes en local technique, par Sopjani Tech Sàrl", "sprinkler", "Centrale sprinkler sous eau"),
    ("sprinkler-vanne-seche-victaulic.jpg", 720, 1280, "Poste d'alarme sous air pour installation sprinkler, station Parking Nord, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous air"),
    ("sprinkler-vanne-alarme-humide.jpg", 720, 1280, "Poste d'alarme sous eau avec pompe de suppression et vanne d'arrêt générale d'un réseau sprinkler, par Sopjani Tech Sàrl", "sprinkler", "Poste d'alarme sous eau avec pompe de suppression"),
    ("sanitaire-collecteur-galvanise.jpg", 1280, 720, "Test de débit sprinkler sur collecteur en acier galvanisé avec raccords laiton et vannes, par Sopjani Tech Sàrl", "sprinkler", "Test débit sprinkler"),
    ("ventilation-unite-hvac-gaine.jpg", 1280, 720, "Unité de ventilation HVAC raccordée à une gaine souple par Sopjani Tech Sàrl", "ventilation", "Unité de ventilation HVAC"),
    ("ventilation-conduit-galvanise-chantier.jpg", 1280, 720, "Conduit de ventilation en acier galvanisé installé sur chantier par Sopjani Tech Sàrl", "ventilation", "Conduit de ventilation galvanisé"),
    ("ventilation-sanitaire-local-technique.jpg", 720, 1280, "Ventilation et pompe à chaleur installées en local technique par Sopjani Tech Sàrl", "ventilation", "Ventilation pompe à chaleur"),
    ("tuyauterie-fabrication-atelier.jpg", 720, 1280, "Fabrication en atelier d'un assemblage de tuyauterie de chauffage par Sopjani Tech Sàrl", "chauffage", "Fabrication de tuyauterie chauffage en atelier"),
    ("sanitaire-tuyauterie-plafond-collecteurs.jpg", 1600, 1200, "Tuyauterie sanitaire au plafond avec collecteurs en laiton installés par Sopjani Tech Sàrl", "sanitaire", "Tuyauterie plafond et collecteurs sanitaires"),
    ("sanitaire-reseau-plafond-tableau.jpg", 1600, 1200, "Réseau technique au plafond et tableau de distribution sur chantier sanitaire Sopjani Tech Sàrl", "sanitaire", "Réseau plafond et tableau technique"),
    ("sanitaire-collecteurs-laiton-isoles.jpg", 1600, 1200, "Collecteurs sanitaires en laiton avec tuyaux isolés raccordés au plafond par Sopjani Tech Sàrl", "sanitaire", "Collecteurs laiton et tuyaux isolés"),
    ("sanitaire-local-technique-collecteurs.jpg", 1200, 1600, "Local technique avec collecteurs sanitaires et réseaux métalliques par Sopjani Tech Sàrl", "sanitaire", "Local technique collecteurs sanitaires"),
    ("sanitaire-reseaux-sol-chantier.jpg", 1600, 1200, "Pose de réseaux sanitaires au sol sur chantier par Sopjani Tech Sàrl", "sanitaire", "Réseaux sanitaires au sol"),
    ("sanitaire-tuyauterie-sol-raccords.jpg", 1600, 1200, "Tuyauterie sanitaire au sol avec raccords et supportage sur chantier Sopjani Tech Sàrl", "sanitaire", "Tuyauterie sanitaire au sol"),
    ("sanitaire-bati-support-geberit.jpg", 1600, 1200, "Bâti-support sanitaire Geberit avec réseaux eau et évacuation installé par Sopjani Tech Sàrl", "sanitaire", "Bâti-support sanitaire Geberit"),
    ("sanitaire-collecteur-bati-metallique.jpg", 1200, 1600, "Collecteur sanitaire sur bâti métallique avec tuyaux isolés par Sopjani Tech Sàrl", "sanitaire", "Collecteur sur bâti métallique"),
    ("sanitaire-bati-technique-boitier.jpg", 1200, 1600, "Bâti technique sanitaire avec boîtier de distribution et raccords laiton par Sopjani Tech Sàrl", "sanitaire", "Bâti technique sanitaire"),
    ("sanitaire-percements-gaines.jpg", 1600, 1200, "Percements béton et gaines pour réseaux sanitaires installés par Sopjani Tech Sàrl", "sanitaire", "Percements et gaines sanitaires"),
    ("sanitaire-bati-wc-geberit-sigma.jpg", 1600, 1200, "Bâti-support WC Geberit Sigma avec colonne d'évacuation installé par Sopjani Tech Sàrl", "sanitaire", "Bâti-support WC Geberit"),
    ("sanitaire-local-technique-tuyauterie.jpg", 1600, 1200, "Local technique sanitaire avec tuyauterie, manomètre et réseaux suspendus par Sopjani Tech Sàrl", "sanitaire", "Local technique sanitaire"),
    ("sanitaire-collecteur-vannes-filtre.jpg", 1200, 1600, "Collecteur sanitaire avec vannes, filtre et compteur d'eau installé par Sopjani Tech Sàrl", "sanitaire", "Collecteur, vannes et filtre"),
]

REALISATIONS_BY_CAT = {}
for _fn, _w, _h, _alt, _cat, _cap in REALISATIONS:
    REALISATIONS_BY_CAT.setdefault(_cat, []).append((_fn, _w, _h, _alt, _cap))


def image_object_ld(fn, w, h, alt, cap):
    return {
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
        "copyrightNotice": IMAGE_COPYRIGHT_NOTICE,
        "license": IMAGE_LICENSE_URL,
        "acquireLicensePage": IMAGE_ACQUIRE_LICENSE_URL,
    }


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


# Categories d'images pour le carousel magnétique par prestation.
SERVICE_CAROUSEL_CATS = {
    "chauffage": ["chauffage"],
    "ventilation": ["ventilation"],
    "climatisation": ["ventilation", "chauffage"],
    "sanitaire": ["sanitaire"],
    "depannage-sav": ["chauffage", "ventilation", "sanitaire"],
    "sprinkler-protection-incendie": ["sprinkler"],
}


def carousel_images_for_service(slug, gallery_cat=None, limit=8):
    """Images chantier pour le carousel (catégorie dédiée, sinon fallback)."""
    preferred = list(SERVICE_CAROUSEL_CATS.get(slug, []))
    if gallery_cat:
        cats = [gallery_cat] + [c for c in preferred if c != gallery_cat]
    else:
        cats = preferred
    seen = set()
    out = []
    for cat in cats:
        for item in REALISATIONS_BY_CAT.get(cat, []):
            fn = item[0]
            if fn in seen:
                continue
            seen.add(fn)
            out.append(item)
            if len(out) >= limit:
                return out
    return out


def magnetic_carousel_html(images, service_name):
    """Carousel magnétique type dock macOS — HTML sémantique, JS dans main.js."""
    if not images:
        return ""
    bars = []
    for i, (fn, w, h, alt, cap) in enumerate(images):
        safe_alt = alt.replace('"', "&quot;")
        safe_cap = cap.replace('"', "&quot;")
        bars.append(
            f'<button type="button" class="magnetic-bar" data-index="{i}" '
            f'data-src="/assets/realisations/{fn}" '
            f'aria-label="{safe_cap}" aria-expanded="false" '
            f'style="background-image:url(\'/assets/realisations/{fn}\')">'
            f'<img src="/assets/realisations/{fn}" alt="{safe_alt}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async" class="magnetic-bar__img"></button>'
        )
    return (
        f'<div class="magnetic-carousel" role="group" '
        f'aria-label="Galerie réalisations — {service_name}">'
        f'<div class="magnetic-carousel__track">{"".join(bars)}</div>'
        f'<div class="magnetic-carousel__backdrop" hidden aria-hidden="true"></div>'
        f"</div>"
    )


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
        service_nav_link(s, n, submenu=True) for s, n, _ in SERVICES
    )
    zone_sub = '<a href="/zones-intervention/" class="nav-submenu-all">Toutes les zones</a>' + "".join(
        f'<a href="/{z}/" role="menuitem">{n}</a>' for z, n, _ in ZONES
    )
    mobile_svc_panel = '<a href="/prestations/">Toutes les prestations</a>' + "".join(
        service_nav_link(s, n) for s, n, _ in SERVICES
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
    return f"""<div class="topbar" role="complementary" aria-label="Coordonnées">
  <div class="container topbar-inner">
    <p class="topbar-left">Société basée à {ADDRESS_LOCALITY} — Interventions en Suisse romande</p>
    <p class="topbar-right">
      <a href="tel:{PHONE}" class="track-phone topbar-phone">{PHONE_DISP}</a>
      <span class="topbar-extra">
        <span aria-hidden="true">·</span>
        <a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a>
        <span aria-hidden="true">·</span>
        <span>Heures&nbsp;: 7h00 – 17h00</span>
      </span>
    </p>
  </div>
</div>
<header>
  <div class="container">
    <div class="header-inner">
      <a href="/" class="logo-wrap">
        <img src="{LOGO_HEADER}" alt="Sopjani Tech Sàrl" width="48" height="48" loading="eager" decoding="async">
        <div>
          <div class="logo-text">SOPJANI TECH</div>
          <div class="logo-sub">Sàrl · Suisse</div>
        </div>
        <span class="sr-only"> – Accueil</span>
      </a>
      <nav class="nav-main" aria-label="Navigation principale">
        <a href="/">Accueil</a>
        <div class="nav-item">
          <button type="button" class="nav-trigger" aria-expanded="false" aria-haspopup="true">Prestations</button>
          <div class="nav-submenu" role="menu">{svc_sub}</div>
        </div>
        <a href="/realisations/">Réalisations</a>
        <div class="nav-item">
          <button type="button" class="nav-trigger" aria-expanded="false" aria-haspopup="true">Zones</button>
          <div class="nav-submenu" role="menu">{zone_sub}</div>
        </div>
        <a href="/a-propos/">À propos</a>
        <a href="/contact/">Contact</a>
      </nav>
      <div class="header-cta">
        <a href="tel:{PHONE}" class="tel-btn track-phone">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 014.69 12 19.79 19.79 0 011.61 3.4 2 2 0 013.6 1.22h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L7.91 8.8a16 16 0 006.29 6.29l.96-.96a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
          {PHONE_DISP}
        </a>
        <a href="/contact/" class="btn btn-brand track-devis">Demander un devis →</a>
      </div>
      <button class="burger" id="burger" type="button" aria-label="Ouvrir le menu" aria-controls="mobileNav" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-nav-overlay" id="mobileNavOverlay" hidden></div>
<nav class="mobile-nav" id="mobileNav" aria-label="Navigation mobile" aria-hidden="true">
  <div class="mobile-nav-inner">
    <div class="mobile-nav-toolbar">
      <p class="mobile-nav-title">Menu</p>
      <button type="button" class="mobile-nav-close" id="mobileNavClose" aria-label="Fermer le menu">
        <span aria-hidden="true"></span><span aria-hidden="true"></span>
      </button>
    </div>
    <a href="/" class="mobile-nav-link">Accueil</a>
    {mobile_svc}
    <a href="/realisations/" class="mobile-nav-link">Réalisations</a>
    {mobile_zones}
    <a href="/a-propos/" class="mobile-nav-link">À propos</a>
    <a href="/contact/" class="mobile-nav-link">Contact</a>
    <div class="mobile-nav-cta">
      <a href="/contact/#contact-form" class="btn btn-brand track-devis">Demander un devis</a>
      <a href="tel:{PHONE}" class="btn btn-secondary track-phone">Appeler · {PHONE_DISP}</a>
      <a href="{WA}" class="btn btn-secondary track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
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
    <div class="footer-brand">
      <a href="/" class="footer-logo-wrap">
        <img src="{LOGO_FOOTER}" alt="Sopjani Tech Sàrl" width="48" height="48" loading="lazy" decoding="async">
        <div>
          <div class="footer-logo-text">SOPJANI TECH</div>
          <div class="footer-logo-sub">Sàrl · Suisse romande</div>
        </div>
      </a>
    </div>
    <div class="footer-grid">
      <div class="footer-col footer-col--services">
        <div class="footer-col-title">Services</div>
        <ul class="footer-links">{svc}</ul>
      </div>
      <div class="footer-col footer-col--zones">
        <div class="footer-col-title">Zones</div>
        <ul class="footer-links">{zones}</ul>
      </div>
      <div class="footer-col footer-col--entreprise">
        <div class="footer-col-title">Entreprise</div>
        <ul class="footer-links">
          <li><a href="/">Accueil</a></li>
          <li><a href="/a-propos/">À propos</a></li>
          <li><a href="/realisations/">Réalisations</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li class="footer-dup-legal"><a href="/plan-du-site/">Plan du site</a></li>
          <li class="footer-dup-legal"><a href="/mentions-legales/">Mentions légales</a></li>
          <li class="footer-dup-legal"><a href="/politique-confidentialite/">Politique de confidentialité</a></li>
        </ul>
      </div>
      <div class="footer-col footer-col--contact">
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
      <p class="footer-seo">{CVCS_GROUP} · Dépannage SAV · Sprinkler · Suisse romande</p>
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


def faq_section_head(title="Questions fréquentes", label="FAQ"):
    return f"""<div class="faq-head">
    <span class="label">{label}</span>
    <div class="rule"></div>
    <h2 class="section-title" id="faq-title">{title}</h2>
  </div>"""


def faq_html(items):
    # FAQ visible uniquement — le balisage FAQPage est fourni en JSON-LD (évite le doublon GSC).
    blocks = []
    for i, (q, a) in enumerate(items, start=1):
        blocks.append(f"""<div class="faq-item">
  <button class="faq-q" aria-expanded="false"><span class="faq-idx" aria-hidden="true">{i:02d}</span><span class="faq-q-text">{q}</span><span class="faq-icon" aria-hidden="true"></span></button>
  <div class="faq-a"><p>{a}</p></div>
</div>""")
    return f'<div class="faq-list">{"".join(blocks)}</div>'



def norms_bar():
    """Bandeau normes — toutes les pages marketing."""
    return """<section class="norms-bar site-norms" aria-label="Cadre normatif">
  <div class="container norms-bar-inner">
    <div class="norms-logos">
      <span>SIA</span>
      <span>suva</span>
      <span>AEAI</span>
    </div>
    <ul class="norms-tags">
      <li>Certifié / Conformité</li>
      <li>Professionnels qualifiés</li>
      <li>Assurance RC</li>
    </ul>
  </div>
</section>"""


def trust_strip():
    """Preuves de confiance compactes — pages internes."""
    zone_list = "".join(f'<li><a href="/{z}/">{n}</a></li>' for z, n, _ in ZONES)
    return f"""<section class="trust-bar site-trust" aria-label="Preuves de confiance">
  <div class="container trust-bar-grid">
    <div class="trust-item"><strong>100+</strong><span>Interventions réalisées</span></div>
    <div class="trust-item"><strong>80+</strong><span>Clients satisfaits</span></div>
    <div class="trust-item"><strong>10+</strong><span>Années d'expérience</span></div>
    <div class="trust-item trust-item--zones">
      <strong>Zones d'intervention</strong>
      <ul>{zone_list}</ul>
    </div>
  </div>
</section>"""


def hero_image_for(key):
    """Chemin hero généré (provisoire jusqu'au shooting)."""
    path = f"/assets/heroes/{key}.jpg"
    return path


def page_hero(label, h1, sub, *, icon_html="", primary_href="/contact/", primary_label="Demander un devis", primary_class="btn-brand track-devis", secondary_href=None, secondary_label=None, secondary_class="btn-secondary-on-dark track-phone", show_ctas=True, image=None, image_alt=""):
    """Hero unifié — photo plein cadre + fondu navy si `image` fourni."""
    if secondary_href is None:
        secondary_href = f"tel:{PHONE}"
    if secondary_label is None:
        secondary_label = PHONE_DISP
    # Sur fond photo, CTA secondaire = outline clair (sauf urgence)
    if image and secondary_class == "btn-secondary track-phone":
        secondary_class = "btn-secondary-on-dark track-phone"
    if image and primary_class == "btn-brand track-devis":
        primary_class = "btn-brand btn-brand--on-dark track-devis"
    icon_block = f"\n      {icon_html}" if icon_html else ""
    ctas = ""
    if show_ctas:
        ctas = f"""
      <div class="hero-ctas">
        <a href="{primary_href}" class="btn {primary_class}">{primary_label}</a>
        <a href="{secondary_href}" class="btn {secondary_class}">{secondary_label}</a>
      </div>"""
    if image:
        alt = image_alt or h1
        return f"""<section class="page-hero hero hero--photo" aria-labelledby="page-h1">
  <div class="hero-media" aria-hidden="true">
    <img src="{image}" alt="" width="1536" height="1024" fetchpriority="high" decoding="async">
  </div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="container hero-inner">
    <div class="hero-content">
      <p class="hero-eyebrow">{label}</p>{icon_block}
      <h1 id="page-h1">{h1}</h1>
      <p class="hero-sub">{sub}</p>{ctas}
    </div>
  </div>
</section>"""
    return f"""<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <p class="hero-eyebrow">{label}</p>{icon_block}
    <h1 id="page-h1">{h1}</h1>
    <p class="hero-sub">{sub}</p>{ctas}
  </div>
</section>"""


def cta_band(title="Besoin d'un devis ou d'un dépannage ?", text="Contactez-nous pour décrire votre besoin. Nous vous répondrons dans les meilleurs délais."):
    return f"""<section class="cta-band" aria-label="Appel à l'action">
  <div class="container">
    <h2>{title}</h2>
    <p>{text}</p>
    <a href="/contact/" class="btn btn-brand track-devis">Demander un devis</a>
    <a href="tel:{PHONE}" class="btn btn-secondary-on-dark track-phone">{PHONE_DISP}</a>
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
  <link rel="icon" href="{FAVICON_PATH}" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="{APPLE_TOUCH_ICON}" sizes="192x192">
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
  <link rel="stylesheet" href="/css/main.css?v={int((ROOT / 'css' / 'main.css').stat().st_mtime)}">
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


def service_page(slug, name, title, desc, h1, intro, problems, interventions, clients, process, zone_slugs, related_svc, faq, show_urgence=False, gallery_cat=None, expertise_html=""):
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (name, url)]
    related = "".join(f'<a class="zone-pill" href="/{s}/">{n}</a>' for s, n, _ in SERVICES if s in related_svc)
    urgence_html = urgence_band() if show_urgence else ""
    carousel_imgs = carousel_images_for_service(slug, gallery_cat=gallery_cat, limit=8)
    gallery_block = ""
    if carousel_imgs:
        gallery_block = f"""
<section class="content-section magnetic-section" aria-labelledby="real-title">
  <div class="container">
    <span class="label">Chantiers</span>
    <div class="rule"></div>
    <h2 class="section-title" id="real-title">Réalisations — {name}</h2>
    <p class="section-lead">Survolez ou touchez une photo pour l'agrandir. Aperçu d'interventions réalisées par {COMPANY_NAME}.</p>
    {magnetic_carousel_html(carousel_imgs, name)}
    <p style="margin-top:24px;"><a href="/realisations/" class="text-link">Voir toutes nos réalisations →</a></p>
  </div>
</section>"""
    if slug == "depannage-sav":
        hero = page_hero(
            "Prestation", h1, intro,
            icon_html=service_icon(slug, "hero"),
            primary_href=f"tel:{PHONE}", primary_label=PHONE_DISP, primary_class="btn-urgence track-phone",
            secondary_href="/contact/", secondary_label="Demander un devis", secondary_class="btn-brand btn-brand--on-dark track-devis",
            image=hero_image_for(slug),
            image_alt=h1,
        )
    else:
        hero = page_hero("Prestation", h1, intro, icon_html=service_icon(slug, "hero"), image=hero_image_for(slug), image_alt=h1)
    body = f"""
{hero}
{urgence_html}
<section class="content-section" aria-labelledby="problems-title">
  <div class="container prose-block">
    <h2 class="section-title" id="problems-title">Problématiques traitées</h2>
    {problems}
  </div>
</section>
<section class="content-section alt" aria-labelledby="interventions-title">
  <div class="container prose-block">
    <h2 class="section-title" id="interventions-title">Types d'interventions</h2>
    {interventions}
  </div>
</section>
{f'''<section class="content-section" aria-labelledby="expertise-title">
  <div class="container prose-block">
    <h2 class="section-title" id="expertise-title">Équipements et cadre suisse</h2>
    {expertise_html}
  </div>
</section>''' if expertise_html else ''}
<section class="content-section {'alt' if expertise_html else ''}" aria-labelledby="clients-title">
  <div class="container prose-block">
    <h2 class="section-title" id="clients-title">Pour quels bâtiments</h2>
    {clients}
    <h3 style="margin-top:28px;">Déroulement d'une intervention</h3>
    {process}
  </div>
</section>
{gallery_block}
<section class="content-section alt" aria-labelledby="zones-title">
  <div class="container">
    <h2 class="section-title" id="zones-title">Zones desservies</h2>
    <p class="section-lead">Sopjani Tech Sàrl intervient en Suisse romande — cantons de Genève, Vaud, Valais, Fribourg et Neuchâtel, ainsi que les principales villes de ces cantons. Contactez-nous pour vérifier la disponibilité dans votre secteur.</p>
    {service_zones_block()}
    <p style="margin-top:20px;"><a href="/zones-intervention/" class="text-link">Voir toutes les zones d'intervention →</a></p>
  </div>
</section>
<section class="content-section" aria-labelledby="related-title">
  <div class="container">
    <h2 class="section-title" id="related-title">Prestations connexes</h2>
    <div class="zone-links">{related}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
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
    hero = page_hero(
        "Zone d'intervention",
        h1,
        f"Chauffagiste et CVC dans {region} : chauffage, ventilation, climatisation et sanitaire. Contactez Sopjani Tech Sàrl pour vérifier la disponibilité selon votre localisation.",
        image=hero_image_for("zones"),
        image_alt=h1,
    )
    body = f"""
{hero}
<section class="content-section" aria-labelledby="local-title">
  <div class="container prose-block">
    <h2 class="section-title" id="local-title">Interventions dans {region}</h2>
    {local_text}
    <p class="geo-local-note">Siège à <strong>{ADDRESS_FULL}</strong> — équipe mobile en Suisse romande. <a href="/contact/">Contactez-nous</a> pour vérifier la disponibilité à {name}.</p>
  </div>
</section>
<section class="content-section alt" aria-labelledby="svc-title">
  <div class="container">
    <h2 class="section-title" id="svc-title">Services disponibles</h2>
    <div class="zone-links">{svc}</div>
  </div>
</section>
<section class="content-section" aria-labelledby="near-title">
  <div class="container">
    <h2 class="section-title" id="near-title">Autres zones proches</h2>
    <div class="zone-links">{rz}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head(f"FAQ — {name}")}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
{cta_band(f"Un projet à {name} ?", "Décrivez votre besoin par téléphone, email ou WhatsApp.")}"""
    graph = base_graph(title, desc, SITE + url, crumbs, faq)
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def svc_strip_card(slug, name, tag):
    return (
        f'<a class="svc-strip-card" data-svc="{slug}" href="/{slug}/">'
        f'{service_icon(slug, "card")}'
        f'<span class="svc-strip-card__title">{name}</span>'
        f'<span class="svc-strip-card__tag">{tag}</span>'
        f'<span class="svc-strip-card__arrow" aria-hidden="true">→</span></a>'
    )


def build_home():
    strip = [
        ("chauffage", "Chauffage", "Installation & entretien"),
        ("ventilation", "Ventilation", "Traitement de l'air"),
        ("climatisation", "Climatisation", "Étude & installation"),
        ("sanitaire", "Sanitaire", "Rénovation & dépannage"),
        ("sprinkler-protection-incendie", "Sprinkler", "Protection incendie"),
        ("depannage-sav", "Dépannage SAV", "Intervention rapide"),
    ]
    svc_strip = "".join(svc_strip_card(s, n, t) for s, n, t in strip)
    real_tiles = [
        ("sprinkler-collecteur-rouges.jpg", "Réseau Sprinkler", "Protection incendie"),
        ("tuyauterie-fabrication-atelier.jpg", "Centrale de chauffage", "Installation complète"),
        ("ventilation-conduit-galvanise-chantier.jpg", "Ventilation", "Conduits chantier tertiaire"),
        ("sanitaire-local-technique-collecteurs.jpg", "Sanitaire", "Rénovation"),
        ("ventilation-unite-hvac-gaine.jpg", "Climatisation", "Installation"),
    ]
    real_html = "".join(
        f'<a class="real-tile" href="/realisations/">'
        f'<img src="/assets/realisations/{fn}" alt="{title} — {sub} · Sopjani Tech Sàrl" width="480" height="640" loading="lazy" decoding="async">'
        f'<span class="real-tile__cap"><strong>{title}</strong><em>{sub}</em></span></a>'
        for fn, title, sub in real_tiles
    )
    faq = [
        ("Quels services proposez-vous ?", f"{CVCS_GROUP}, ainsi que dépannage SAV et sprinkler / protection incendie en Suisse romande."),
        ("Dans quelles zones intervenez-vous ?", f"Principalement Genève, Vaud, Lausanne, Nyon, Valais et Fribourg. Siège à {ADDRESS_LOCALITY}."),
        ("Comment obtenir un devis ?", "Via notre page contact ou par téléphone : décrivez le type de bâtiment, la localisation et la nature du besoin. Le devis est gratuit et sans engagement."),
        ("Intervenez-vous en dépannage ?", f"Oui, nous intervenons en dépannage en {CVCS_PROSE} en Suisse romande. Nos horaires : {HOURS}. Appelez-nous directement pour une panne en cours."),
        ("Qui contacter pour un dépannage CVC en Suisse romande ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp."),
        ("Combien de temps pour obtenir un devis ?", f"Pour une réponse immédiate, appelez-nous au {PHONE_DISP} ; pour une demande non urgente, utilisez le formulaire. Horaires : {HOURS}."),
        ("Intervenez-vous près de chez moi ?", f"Nous sommes basés à {ADDRESS_FULL} et intervenons en Suisse romande. Contactez-nous pour vérifier la disponibilité dans votre commune."),
    ]
    body = f"""
<section class="hero hero--photo" aria-labelledby="hero-h1">
  <div class="hero-media" aria-hidden="true">
    <img src="/assets/heroes/home.jpg" alt="" width="1536" height="1024" fetchpriority="high" decoding="async">
  </div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="container hero-inner">
    <div class="hero-content">
      <p class="hero-eyebrow">Étude · Installation · Maintenance · Dépannage</p>
      <h1 id="hero-h1">Solutions CVC fiables pour vos bâtiments.</h1>
      <p class="hero-sub">{CVCS_GROUP} et protection incendie en Suisse romande.</p>
      <div class="hero-ctas">
        <a href="/contact/" class="btn btn-brand btn-brand--on-dark track-devis">Demander un devis</a>
        <a href="tel:{PHONE}" class="btn btn-urgence track-phone">Dépannage urgent</a>
      </div>
      <ul class="hero-trust">
        <li>Devis gratuit</li>
        <li>Intervention rapide</li>
        <li>Normes suisses</li>
      </ul>
    </div>
  </div>
</section>

<section class="svc-strip" aria-label="Prestations">
  <div class="container">
    <div class="svc-strip-grid">{svc_strip}</div>
  </div>
</section>

{trust_strip()}

<section class="home-realisations" aria-labelledby="real-title">
  <div class="container">
    <div class="home-realisations__head">
      <h2 class="section-title" id="real-title">Nos réalisations</h2>
      <a href="/realisations/" class="text-link">Voir toutes les réalisations →</a>
    </div>
    <div class="real-tiles">{real_html}</div>
  </div>
</section>

<section class="about-split" aria-labelledby="about-title">
  <div class="container about-split-grid">
    <div class="about-copy">
      <span class="label label--brand">À propos de Sopjani Tech</span>
      <h2 class="section-title" id="about-title">Rigueur, transparence et proximité.</h2>
      <p>Nous concevons, installons et assurons la mise en service avec un interlocuteur unique et un suivi clair à chaque étape.</p>
      <ul class="check-list">
        <li>Devis clairs et détaillés</li>
        <li>Respect des normes suisses (SIA, SUVA, AEAI…)</li>
        <li>Interlocuteur direct et réactif</li>
        <li>Qualité d'exécution et traçabilité</li>
      </ul>
      <p class="about-copy-links">
        <a href="/a-propos/" class="text-link">Présentation de l'entreprise →</a>
        <a href="/contact/" class="text-link track-devis">Demander un devis →</a>
      </p>
    </div>
    <div class="about-photo-duo" aria-label="Équipe Sopjani Tech">
      <figure class="about-photo">
        <img src="/assets/equipe/equipe-soudure-logo-dos.jpg" alt="Technicien Sopjani Tech Sàrl en intervention — logo visible sur la tenue" width="900" height="900" loading="lazy" decoding="async">
      </figure>
      <figure class="about-photo">
        <img src="/assets/equipe/equipe-formation-logo-dos.jpg" alt="Collaborateur Sopjani Tech Sàrl en formation — tenue aux couleurs de l'entreprise" width="775" height="1024" loading="lazy" decoding="async">
      </figure>
    </div>
  </div>
</section>

{norms_bar()}

<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
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
        ("Quelles prestations CVC proposez-vous ?", f"{CVCS_GROUP}, ainsi que dépannage SAV et sprinkler en sous-traitance."),
        ("Comment choisir la bonne prestation ?", "Chaque page prestation détaille les problématiques traitées et les interventions courantes. En cas de doute, décrivez votre bâtiment et votre besoin via notre page contact : nous vous orienterons vers la prestation adaptée."),
        ("Intervenez-vous en Suisse romande ?", f"Oui, principalement à Genève, Vaud, Lausanne, Nyon, Valais et Fribourg. Siège à {ADDRESS_LOCALITY}."),
    ]
    cards = "".join(hub_card(s, n, d, cta="Voir la prestation →") for s, n, d in SERVICES)
    hero = page_hero(
        "Prestations",
        f"Nos prestations en {CVCS_PROSE}",
        "Sopjani Tech Sàrl conçoit, installe, entretient et dépanne vos installations techniques en Suisse romande.",
        image=hero_image_for("prestations"),
    )
    body = f"""
{hero}
<section class="content-section">
  <div class="container">
    <div class="hub-grid">{cards}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
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
    hero = page_hero(
        "Géographie",
        "Nos zones d'intervention en Suisse romande",
        "Sopjani Tech Sàrl intervient dans les cantons et agglomérations ci-dessous. Contactez-nous pour vérifier la disponibilité dans votre secteur.",
        image=hero_image_for("zones-intervention"),
    )
    body = f"""
{hero}
{geo_presence_block(compact=True)}
<section class="content-section">
  <div class="container">
    <div class="hub-grid">{cards}</div>
    <div class="prose-block" style="margin-top:40px;">
      <p>Pour d'autres secteurs en Suisse romande, contactez-nous afin de vérifier la faisabilité d'une intervention selon la nature du projet.</p>
      <p style="margin-top:12px;font-size:14px;color:var(--c-muted);">Nos interventions sont assurées par une équipe mobile : il ne s'agit pas d'agences locales dans chaque canton.</p>
    </div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
{cta_band("Votre commune n'est pas listée ?", "Contactez-nous pour vérifier la faisabilité d'une intervention.")}"""
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/")]
    zones_title = PAGE_TITLES["zones-intervention"]
    zones_desc = META_DESCRIPTIONS["zones-intervention"]
    graph = base_graph(zones_title, zones_desc, SITE + "/zones-intervention/", crumbs, faq)
    write_page(["zones-intervention", "index.html"], page_shell(zones_title, zones_desc, SITE + "/zones-intervention/", graph, body, crumbs))


def build_about():
    faq = [
        (f"Où est située {COMPANY_NAME} ?", f"Notre siège est à {ADDRESS_FULL}. Nous intervenons en Suisse romande pour le {CVCS_PROSE} et le dépannage CVC."),
        ("Quels services propose l'entreprise ?", f"{CVCS_GROUP}, ainsi que dépannage SAV et sprinkler en sous-traitance."),
        ("Comment contacter Sopjani Tech Sàrl ?", f"Par téléphone au {PHONE_DISP}, par email ({EMAIL}) ou via WhatsApp. Horaires : {HOURS}."),
    ]
    hero = page_hero(
        "Entreprise",
        "À propos de Sopjani Tech Sàrl",
        f"Entreprise technique spécialisée en {CVCS_ALL_PROSE} en Suisse romande.",
        image=hero_image_for("a-propos"),
    )
    zone_pills = "".join(f'<a class="zone-pill" href="/{z}/">{n}</a>' for z, n, _ in ZONES)
    body = f"""
{hero}
<section class="about-intro content-section" aria-labelledby="about-who">
  <div class="container">
    <div class="about-intro-grid">
      <div class="about-intro-copy">
        <span class="label">Entreprise</span>
        <div class="rule"></div>
        <h2 class="section-title" id="about-who">Qui sommes-nous</h2>
        <p class="about-lead">Sopjani Tech Sàrl accompagne les bâtiments résidentiels, tertiaires et techniques en Suisse romande — du premier échange à la mise en service.</p>
        <p>Basés à <strong>{ADDRESS_FULL}</strong>, nous couvrons le {CVCS_PROSE}, le dépannage SAV et le sprinkler / protection incendie. Approche simple : comprendre le besoin, proposer une solution adaptée, intervenir avec sérieux.</p>
        <p>Nous privilégions la clarté des échanges, la réactivité et l'adaptation aux contraintes du terrain — installation, maintenance ou dépannage.</p>
        <div class="about-zones">
          <p class="about-zones-label">Zones prioritaires</p>
          <div class="zone-links">{zone_pills}</div>
        </div>
      </div>
      <aside class="about-contact-rail" aria-label="Coordonnées">
        <p class="about-contact-rail__title">Coordonnées</p>
        <a href="tel:{PHONE}" class="about-contact-row track-phone">
          <span class="about-contact-row__k">Téléphone</span>
          <span class="about-contact-row__v">{PHONE_DISP}</span>
        </a>
        <a href="mailto:{EMAIL}" class="about-contact-row track-email">
          <span class="about-contact-row__k">Email</span>
          <span class="about-contact-row__v">{EMAIL}</span>
        </a>
        <a href="{MAP_URL}" class="about-contact-row" target="_blank" rel="noopener noreferrer">
          <span class="about-contact-row__k">Adresse</span>
          <span class="about-contact-row__v">{ADDRESS_FULL}</span>
        </a>
        <div class="about-contact-row about-contact-row--static">
          <span class="about-contact-row__k">Horaires</span>
          <span class="about-contact-row__v">{HOURS}</span>
        </div>
        <a href="/contact/" class="btn btn-brand btn-block track-devis" style="margin-top:8px;">Demander un devis</a>
      </aside>
    </div>
  </div>
</section>
<section class="about-engagements content-section alt" aria-labelledby="engagements-title">
  <div class="container about-engagements-inner">
    <div>
      <span class="label">Engagements</span>
      <div class="rule"></div>
      <h2 class="section-title" id="engagements-title">Ce que vous pouvez attendre</h2>
      <p class="section-lead">Des échanges nets, un interlocuteur unique et une entreprise enregistrée en Suisse.</p>
    </div>
    <ul class="check-list about-check">
      <li>Devis gratuit et sans engagement</li>
      <li>Un interlocuteur unique, du premier contact à la fin des travaux</li>
      <li>Échanges clairs sur la nature et le coût avant intervention</li>
      <li>Sàrl inscrite au registre du commerce (UID {COMPANY_UID} · <a href="https://www.zefix.ch" target="_blank" rel="noopener noreferrer">Zefix</a>)</li>
    </ul>
    <p class="about-google"><a href="{GOOGLE_BUSINESS_URL}" class="text-link track-google" target="_blank" rel="noopener noreferrer">Voir notre fiche Google et nos avis →</a></p>
  </div>
</section>
<section class="content-section" aria-labelledby="equipe-title">
  <div class="container">
    <span class="label">Équipe</span>
    <div class="rule"></div>
    <h2 class="section-title" id="equipe-title">Sur le terrain et en formation</h2>
    <p class="section-lead">Des professionnels Sopjani Tech Sàrl, identifiable à notre tenue — intervention technique et formation continue.</p>
    <div class="equipe-grid">
      <figure class="gallery-card">
        <img src="/assets/equipe/equipe-soudure-logo-dos.jpg" alt="Technicien Sopjani Tech Sàrl en soudure — logo sur la tenue" width="900" height="900" loading="lazy" decoding="async">
        <figcaption>Intervention terrain — tenue Sopjani Tech Sàrl</figcaption>
      </figure>
      <figure class="gallery-card">
        <img src="/assets/equipe/equipe-formation-logo-dos.jpg" alt="Collaborateur Sopjani Tech Sàrl en formation sécurité" width="775" height="1024" loading="lazy" decoding="async">
        <figcaption>Formation continue — normes et sécurité</figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
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
        ("Proposez-vous un devis gratuit ?", "Oui, le devis est gratuit et sans engagement. Décrivez votre projet via le formulaire ci-dessus ou par téléphone : nous confirmons la faisabilité et les prochaines étapes."),
    ]
    body = f"""
{urgence_band()}
{page_hero(
        "Contact",
        "Contactez Sopjani Tech Sàrl",
        "Devis, maintenance ou dépannage : décrivez votre besoin et nous vous orienterons vers la solution adaptée.",
        image=hero_image_for("contact"),
    )}
<section class="contact content-section" aria-labelledby="contact-form-title">
  <div class="container contact-page">
    {mobile_quick_bar()}
    <div class="contact-inner">
      <div class="contact-form-section" id="contact-form">
        <h2 class="contact-block-title" id="contact-form-title">Formulaire de demande</h2>
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
          <button type="submit" class="btn btn-brand btn-block track-form-submit">Envoyer la demande</button>
          <p class="form-feedback" role="status" aria-live="polite" hidden></p>
        </form>
      </div>
      <div class="contact-details-section">
        <h2 class="contact-block-title">Coordonnées</h2>
        <div class="contact-methods">
          <a href="tel:{PHONE}" class="contact-method track-phone">
            <div><div class="cm-label">Téléphone</div><div class="cm-value">{PHONE_DISP}</div></div>
          </a>
          <a href="mailto:{EMAIL}" class="contact-method track-email">
            <div><div class="cm-label">Email</div><div class="cm-value">{EMAIL}</div></div>
          </a>
          <a href="{WA}" class="contact-method track-whatsapp" target="_blank" rel="noopener noreferrer">
            <div><div class="cm-label">WhatsApp</div><div class="cm-value">Envoyer un message</div></div>
          </a>
          <a href="{MAP_URL}" class="contact-method" target="_blank" rel="noopener noreferrer">
            <div><div class="cm-label">Adresse</div><div class="cm-value">{ADDRESS_FULL}</div></div>
          </a>
          <div class="contact-method contact-method--static" aria-label="Horaires">
            <div><div class="cm-label">Horaires</div><div class="cm-value">{HOURS}</div></div>
          </div>
          <a href="{GOOGLE_BUSINESS_URL}" class="contact-method contact-google-link track-google" target="_blank" rel="noopener noreferrer">
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
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{trust_strip()}
{norms_bar()}
{cta_band()}"""
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
        "Chauffagiste en Suisse romande : installation, entretien et dépannage",
        "Vous cherchez un chauffagiste à Nyon, Lausanne, Genève, Fribourg ou en Valais ? Nous prenons en charge vos besoins en chauffage — de l'étude à la maintenance — pour assurer le confort thermique et la fiabilité de vos installations.",
        "<p>Chaudière qui ne démarre plus ou qui s'arrête en cours de cycle, radiateurs froids ou circuit déséquilibré, boiler qui ne produit plus d'eau chaude, bruit anormal au démarrage, consommation de mazout ou de gaz en hausse, chaudière vétuste à remplacer par une pompe à chaleur.</p>",
        bullets(["Étude et dimensionnement thermique (calcul de puissance, choix des émetteurs)",
                 "Installation de pompes à chaleur air/eau ou sol/eau, chaudières à gaz, mazout ou bois",
                 "Désembouage et équilibrage de circuits de chauffage",
                 "Détartrage et entretien de boiler et chauffe-eau",
                 "Remplacement de circulateurs, vannes thermostatiques et vase d'expansion",
                 "Dépannage et remise en service",
                 "Accompagnement pour le remplacement d'une chaudière mazout ou gaz par une pompe à chaleur"]),
        clients, process, ["geneve", "lausanne", "nyon", "vaud", "valais", "fribourg", "neuchatel"], ["ventilation", "climatisation", "sanitaire", "depannage-sav"],
        [("Qui appeler pour un chauffagiste à Nyon ou Lausanne ?", f"{COMPANY_NAME} intervient comme chauffagiste à Nyon, Lausanne et dans toute la Suisse romande. Appelez le {PHONE_DISP} ou consultez nos pages zones Nyon et Lausanne."),
         ("Intervenez-vous en dépannage chauffage ?", "Oui, nous intervenons sur chaudières, pompes à chaleur et radiateurs en Suisse romande : absence de chauffage, bruit anormal, fuite ou baisse de rendement. Appelez-nous directement pour une panne en cours."),
         ("Proposez-vous des contrats d'entretien ?", "Oui, un entretien régulier de votre chaudière ou pompe à chaleur (contrôle, réglage, détartrage du boiler) permet de limiter les pannes. Contactez-nous pour discuter d'une fréquence adaptée à votre installation."),
         ("Qui appeler pour un chauffagiste en Suisse romande ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP} ou via notre page contact. Nous couvrons notamment Genève, Vaud (Nyon, Lausanne), Valais, Fribourg et Neuchâtel."),
         ("Combien coûte un devis chauffage ?", "Le devis est gratuit. Il dépend du type d'installation, de la surface et de l'état de l'existant."),
         ("Qui effectue le contrôle officiel de combustion de ma chaudière ?", "Le contrôle périodique OPair (tous les 2 à 4 ans selon le combustible) est réalisé par le maître ramoneur agréé de votre secteur. Nous intervenons en complément pour l'entretien, le réglage du brûleur et la remise en conformité de votre installation."),
         ("Le remplacement d'une chaudière par une pompe à chaleur est-il subventionné ?", "Oui, sous conditions, dans le cadre du Programme Bâtiments (leprogrammebatiments.ch), avec un barème propre à chaque canton. Contactez-nous pour évaluer votre projet et vérifier votre éligibilité.")],
        gallery_cat="chauffage",
        expertise_html="""<p>Nous intervenons sur les principaux générateurs de chaleur utilisés en Suisse romande : chaudières à mazout, à gaz et à bois (bûches ou pellets), ainsi que pompes à chaleur air/eau et sol/eau.</p>
""" + chauffagiste_local_block() + """
<h3>Contrôle de combustion (OPair)</h3>
<p>Le contrôle périodique officiel des installations à combustion reste du ressort du maître ramoneur agréé de votre secteur, selon l'ordonnance fédérale sur la protection de l'air (OPair). Nous intervenons en complément pour l'entretien, le réglage du brûleur et la remise en conformité suite à un contrôle.</p>
<h3>Remplacement par une pompe à chaleur</h3>
<p>Le remplacement d'une chaudière à mazout ou à gaz par une pompe à chaleur peut être subventionné dans le cadre du <strong>Programme Bâtiments</strong>, avec un barème propre à chaque canton (Genève, Vaud, Valais, Fribourg, Neuchâtel). Nous pouvons vous orienter dans cette démarche.</p>""")

    service_page("ventilation", "Ventilation",
        PAGE_TITLES["ventilation"],
        META_DESCRIPTIONS["ventilation"],
        "Ventilation et traitement de l'air",
        "Mise en place et suivi de systèmes de ventilation pour le confort, la qualité de l'air et la maîtrise énergétique de votre bâtiment.",
        "<p>VMC bruyante ou peu performante, condensation et traces d'humidité liées à un renouvellement d'air insuffisant, filtres encrassés, gaines mal isolées ou obstruées, mise en conformité de la ventilation d'un local technique, d'un parking ou d'une cuisine professionnelle.</p>",
        bullets(["Installation de VMC simple flux ou double flux avec récupération de chaleur",
                 "Nettoyage et désinfection de gaines et bouches d'extraction",
                 "Remplacement de filtres, moteurs et caissons de ventilation",
                 "Réglage et équilibrage des débits d'air",
                 "Ventilation de locaux techniques, parkings et cuisines professionnelles",
                 "Réhabilitation de réseaux existants"]),
        clients, process, ["geneve", "lausanne", "nyon", "vaud"], ["chauffage", "climatisation", "sanitaire", "depannage-sav"],
        [("Réalisez-vous des travaux de rénovation de ventilation ?", "Oui, nous rénovons les VMC existantes : remplacement de moteurs, filtres et gaines, ou passage à une VMC double flux avec récupération de chaleur. Contactez-nous avec le type de bâtiment et l'état de l'installation actuelle."),
         ("Comment obtenir un devis ventilation ?", "Contactez-nous avec le type de bâtiment, la surface et l'état des installations existantes."),
         ("Quelle entreprise de ventilation (ventiliste) contacter en Suisse romande ?", f"{COMPANY_NAME} intervient pour l'installation, la maintenance et le dépannage de ventilation."),
         ("Intervenez-vous en urgence pour une panne VMC ?", f"Oui, appelez-nous directement au {PHONE_DISP} : nous évaluons la disponibilité selon le secteur et la nature de la panne.")],
        gallery_cat="ventilation",
        expertise_html="""<p>Nous intervenons sur des installations de VMC simple flux, double flux avec récupération de chaleur, ainsi que sur la ventilation de locaux techniques, parkings et cuisines professionnelles.</p>
<h3>Bâtiments performants et Minergie</h3>
<p>Les constructions récentes ou labellisées Minergie reposent sur une bonne étanchéité à l'air et nécessitent une ventilation mécanique contrôlée correctement dimensionnée et entretenue, pour garantir la qualité de l'air intérieur et éviter les problèmes d'humidité.</p>
<h3>Entretien régulier</h3>
<p>Un nettoyage périodique des gaines, bouches et filtres permet de préserver le débit d'air prévu à l'installation et d'éviter la surconsommation électrique des moteurs encrassés.</p>""")

    service_page("climatisation", "Climatisation",
        PAGE_TITLES["climatisation"],
        META_DESCRIPTIONS["climatisation"],
        "Climatisation à Nyon, Lausanne et Genève : étude et installation",
        "Besoin d'une climatisation à Nyon ou ailleurs en Suisse romande ? Nous réalisons l'étude et l'installation de systèmes adaptés aux particuliers et aux professionnels — split, multi-split et pompes à chaleur air-air.",
        "<p>Climatiseur qui ne refroidit plus, unité extérieure bruyante, givrée ou en panne, fuite de gaz réfrigérant, mauvaise répartition du froid entre les pièces, besoin d'une pompe à chaleur air-air réversible pour le chauffage d'appoint.</p>",
        bullets(["Dimensionnement selon le volume et l'exposition des pièces",
                 "Installation de climatiseurs split et multi-split",
                 "Pompes à chaleur air-air réversibles (chaud/froid)",
                 "Contrôle et recharge du fluide réfrigérant",
                 "Entretien : nettoyage des filtres et des unités, contrôle de performance",
                 "Dépannage : perte de froid, fuite, unité qui ne démarre plus"]),
        clients, process, ["geneve", "nyon", "lausanne", "valais", "vaud", "fribourg"], ["chauffage", "ventilation", "sanitaire", "depannage-sav"],
        [("Installez-vous la climatisation à Nyon ?", "Oui. Nous étudions et installons la climatisation (split, multi-split, PAC air-air) à Nyon et dans les communes voisines (Gland, Rolle, Coppet, Prangins…). Consultez aussi notre page zone Nyon."),
         ("Quels types de bâtiments équipez-vous ?", "Résidentiel et tertiaire selon faisabilité — villas, appartements, bureaux et commerces."),
         ("Intervenez-vous en dépannage climatisation ?", "Oui, nous diagnostiquons et réparons les pannes courantes : perte de froid, fuite de fluide réfrigérant, unité extérieure givrée ou bruyante. Contactez-nous avec le modèle de l'appareil si possible."),
         ("Installez-vous la climatisation près de chez moi ?", f"Nous intervenons en Suisse romande depuis {ADDRESS_LOCALITY}, notamment à Nyon, Lausanne, Genève et en Valais. Contactez-nous avec votre commune."),
         ("Comment obtenir un devis climatisation ?", "Via notre page contact : précisez le type de bâtiment, la surface et vos besoins de confort.")],
        gallery_cat="ventilation",
        expertise_html="""<p>Nous intervenons sur climatiseurs split et multi-split, ainsi que sur les pompes à chaleur air-air réversibles (chauffage et rafraîchissement) — en particulier à <a href="/nyon/">Nyon</a>, <a href="/lausanne/">Lausanne</a> et <a href="/geneve/">Genève</a>.</p>
<h3>Fluides frigorigènes</h3>
<p>La manipulation des fluides réfrigérants est strictement encadrée par la législation suisse sur la protection de l'environnement. Toute intervention sur le circuit frigorifique (recharge, détection de fuite) est réalisée avec le soin et les précautions requises par ce cadre.</p>
<h3>Entretien recommandé</h3>
<p>Un contrôle annuel (nettoyage des filtres et de l'unité extérieure, vérification du bon fonctionnement) permet de préserver le rendement énergétique de l'installation et sa durée de vie.</p>""")

    service_page("depannage-sav", "Dépannage SAV",
        PAGE_TITLES["depannage-sav"],
        META_DESCRIPTIONS["depannage-sav"],
        "Dépannage et maintenance (SAV) de vos installations CVC",
        "Intervention sur vos installations en panne ou en fin de vie, avec une approche orientée remise en service et fiabilisation.",
        "<p>Panne de chaudière ou de pompe à chaleur, VMC à l'arrêt, climatiseur qui ne refroidit plus, fuite sur un réseau sanitaire, dysfonctionnement détecté lors d'un contrôle, besoin d'un contrat de maintenance préventive pour éviter les pannes.</p>",
        bullets(["Diagnostic de panne sur site (chauffage, ventilation, climatisation, sanitaire)",
                 "Devis avant travaux, sauf urgence nécessitant une action immédiate",
                 "Remise en service de chaudières, pompes à chaleur, VMC et climatiseurs",
                 "Intervention sur fuites et dysfonctionnements de réseaux sanitaires",
                 "Contrats de maintenance préventive",
                 "Optimisation des réglages pour réduire la consommation d'énergie"]),
        clients, process, ["geneve", "lausanne", "fribourg", "vaud", "valais"], ["chauffage", "ventilation", "climatisation", "sanitaire"],
        [("Comment signaler une urgence ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la situation."),
         ("Quel délai d'intervention ?", "Le délai dépend de la nature de la panne (une absence totale de chauffage en hiver est traitée en priorité) et du secteur. Un appel direct permet une évaluation immédiate de la disponibilité, plus rapide qu'un formulaire."),
         ("Qui appeler pour un dépannage chauffage ou climatisation ?", f"{COMPANY_NAME} au {PHONE_DISP}. Indiquez votre adresse et le type de panne."),
         ("Intervenez-vous le week-end ?", f"Oui, nos horaires sont : {HOURS}, y compris le week-end. Appelez-nous pour évaluer la disponibilité selon la nature de la panne.")],
        show_urgence=True,
        gallery_cat=None,
        expertise_html="""<p>Nos interventions de dépannage couvrent le chauffage (chaudières, pompes à chaleur), la ventilation (VMC), la climatisation et les réseaux sanitaires.</p>
<h3>Diagnostic avant travaux</h3>
<p>Sauf urgence nécessitant une action immédiate, nous établissons un diagnostic et un devis avant toute intervention corrective, afin que vous validiez le coût et la nature des travaux avant leur réalisation.</p>""")

    service_page("sprinkler-protection-incendie", "Sprinkler / protection incendie",
        PAGE_TITLES["sprinkler-protection-incendie"],
        META_DESCRIPTIONS["sprinkler-protection-incendie"],
        "Sprinkler et protection incendie",
        "Intervention en sous-traitance sur des installations sprinkler, avec exécution soignée et coordination chantier.",
        "<p>Montage de réseaux sprinkler sous eau, sous air ou à préaction, coordination avec les autres corps de métier sur chantier, respect des plans et spécifications techniques du mandant, finitions et supportage conformes aux exigences du projet.</p>",
        bullets(["Pose de collecteurs, vannes d'alarme et postes de contrôle",
                 "Raccordements et supportage (dont raccords Victaulic)",
                 "Sous-traitance spécialisée pour bureaux d'ingénieurs et entreprises générales",
                 "Coordination chantier avec les autres corps de métier",
                 "Essais de pression et de débit avant mise en service",
                 "Finitions techniques et mise en conformité selon plans"]),
        "<p>Bâtiments soumis à des exigences de protection incendie (ERP, hôtels, industriel, logistique), selon obligations applicables.</p>",
        process, ["geneve", "vaud", "valais"], ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"],
        [("Les travaux sprinkler sont-ils réalisés directement ?", "Les interventions sont assurées en sous-traitance spécialisée, selon la nature du projet."),
         ("Un sprinkler est-il obligatoire ?", "Selon les directives AEAI, certaines catégories de bâtiments peuvent être concernées selon leur classe de risque. Nous pouvons analyser votre situation sur demande.")],
        gallery_cat="sprinkler",
        expertise_html="""<p>Nous intervenons en sous-traitance sur des réseaux sprinkler sous eau, sous air ou à préaction : postes de contrôle, vannes d'alarme, collecteurs, supportage et raccords (dont raccords Victaulic).</p>
<h3>Normes AEAI</h3>
<p>Les exigences de protection incendie applicables (classes de risque, catégories de bâtiments concernées) sont définies par les directives de l'Association des établissements cantonaux d'assurance incendie (AEAI). Nous exécutons les réseaux selon les plans et spécifications du mandant et du bureau d'ingénieurs en charge du projet.</p>""")

    service_page("sanitaire", "Sanitaire",
        PAGE_TITLES["sanitaire"],
        META_DESCRIPTIONS["sanitaire"],
        "Sanitaire",
        f"{COMPANY_NAME} intervient également pour vos installations et dépannages sanitaires en Suisse romande.",
        "<p>Fuite sous évier, dans une chape ou sur une colonne, WC qui fuit ou se bouche, chauffe-eau qui ne chauffe plus ou qui fuit, pression d'eau insuffisante, canalisation bouchée, projet de rénovation de salle de bains.</p>",
        bullets([
            "Étude et dimensionnement des installations sanitaires",
            "Installation des réseaux d'eau froide, d'eau chaude et d'évacuation",
            "Pose et remplacement d'appareils sanitaires et de robinetterie",
            "Installation et entretien chauffe-eau",
            "Recherche de fuites et réparation de conduites",
            "Débouchage des évacuations",
            "SAV, dépannage et remise en service",
            "Accompagnement pour les rénovations et transformations sanitaires",
        ]),
        clients, process, ["geneve", "lausanne", "nyon", "fribourg", "vaud"], ["chauffage", "ventilation", "climatisation", "depannage-sav"],
        [("Intervenez-vous en dépannage sanitaire ?", "Oui, nous intervenons sur les fuites, canalisations bouchées, chauffe-eau en panne et robinetterie défectueuse. Décrivez le problème lors de votre appel pour évaluer l'urgence."),
         ("Réalisez-vous des rénovations complètes de salle de bain ?", "Oui pour la partie sanitaire d'une rénovation (réseaux eau chaude/froide, évacuations, robinetterie, WC, douche). Contactez-nous pour décrire votre projet et vérifier la faisabilité selon son ampleur."),
         ("Comment obtenir un devis sanitaire ?", "Via notre page contact ou par téléphone : précisez le type de bâtiment, la localisation et la nature des travaux.")],
        gallery_cat="sanitaire",
        expertise_html="""<p>Nous intervenons sur des réseaux eau froide et eau chaude en cuivre, PER ou multicouche, ainsi que sur les évacuations, la robinetterie et les chauffe-eau / boilers.</p>
<h3>Recherche de fuite</h3>
<p>Avant d'ouvrir une chape ou un mur, une recherche de fuite non destructive (contrôle de pression, écoute) permet souvent de localiser précisément le point de fuite et de limiter les travaux de reprise.</p>""")


def communes_block(names):
    pills = "".join(f'<span class="zone-pill">{n}</span>' for n in names)
    return f'<h3>Communes desservies</h3><p class="section-lead" style="margin-bottom:12px;">Liste non exhaustive — contactez-nous pour toute autre commune du secteur.</p><div class="zone-links">{pills}</div>'


SUBSIDY_NOTE = ("<h3>Aides et subventions</h3>"
    "<p>Le remplacement d'un chauffage à mazout, à gaz ou électrique par une pompe à chaleur peut être subventionné "
    "dans le cadre du <strong>Programme Bâtiments</strong>, sur <a href=\"https://www.leprogrammebatiments.ch\" target=\"_blank\" rel=\"noopener noreferrer\">leprogrammebatiments.ch</a>. "
    "{extra} Les barèmes et conditions varient chaque année : nous vous recommandons de déposer votre demande "
    "auprès du service cantonal de l'énergie <strong>avant le début des travaux</strong>, et de vérifier les montants en vigueur sur le portail officiel. "
    "Nous pouvons vous accompagner dans cette démarche.</p>")


def build_zones():
    p = lambda t: f"<p>{t}</p>"
    zone_page("geneve", "Genève", "la région de Genève",
        PAGE_TITLES["geneve"],
        META_DESCRIPTIONS["geneve"],
        "Chauffagiste et CVC dans la région de Genève",
        p("Vous cherchez un chauffagiste à Genève ? Le canton présente un parc bâti dense — immeubles résidentiels, PPE, commerces et bâtiments tertiaires — avec des contraintes techniques variées. Certains quartiers sont raccordés à un réseau de chauffage à distance (dont GeniLac, alimenté par l'eau du lac) ; la loi cantonale sur l'énergie encourage par ailleurs le remplacement des chauffages fossiles par des pompes à chaleur lors de leur renouvellement.") +
        p("Que vous soyez propriétaire, régie ou responsable technique, contactez-nous pour vérifier la disponibilité d'intervention dans votre secteur.") +
        communes_block(["Genève", "Vernier", "Lancy", "Meyrin", "Carouge", "Onex", "Thônex", "Plan-les-Ouates", "Veyrier", "Grand-Saconnex", "Chêne-Bougeries", "Confignon"]) +
        SUBSIDY_NOTE.format(extra="À Genève, les demandes passent par l'Office cantonal de l'énergie (OCEN) et peuvent se combiner avec le programme SIG-éco21 des Services industriels de Genève."),
        zone_aeo_faq("Genève", "la région de Genève") + [
            ("Existe-t-il des aides pour rénover le chauffage à Genève ?", "Oui, via le Programme Bâtiments et le programme SIG-éco21 (Services industriels de Genève), sous conditions d'éligibilité et selon le barème en vigueur. Contactez-nous pour évaluer votre projet."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["vaud", "nyon", "lausanne"])

    zone_page("vaud", "Vaud", "le canton de Vaud",
        PAGE_TITLES["vaud"],
        META_DESCRIPTIONS["vaud"],
        "Chauffagiste dans le canton de Vaud",
        p("Chauffagiste dans le canton de Vaud : nous couvrons un territoire étendu — rives du Léman, agglomérations de Lausanne et Nyon, Riviera vaudoise, Chablais et Nord vaudois jusqu'au pied du Jura. Le bâti va de la villa individuelle à l'immeuble locatif ou à la PPE, avec des besoins très différents selon l'altitude et l'exposition.") +
        p("Pour les communes hors axes principaux, contactez-nous afin de confirmer la faisabilité et la planification.") +
        communes_block(["Morges", "Yverdon-les-Bains", "Vevey", "Montreux", "Renens", "Pully", "Rolle", "Aigle", "Payerne", "Echallens", "Cossonay", "Orbe"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Vaud, les demandes sont instruites par la Direction générale de l'environnement (DGE) / Direction de l'énergie."),
        zone_aeo_faq("Vaud", "le canton de Vaud") + [
            ("Le canton de Vaud subventionne-t-il les pompes à chaleur ?", "Oui, sous conditions, dans le cadre du Programme Bâtiments géré par la Direction de l'énergie du canton de Vaud. Les certificats de qualité requis (PAC système-module) et les barèmes évoluent chaque année : vérifiez les conditions en vigueur avant de commander votre matériel."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["lausanne", "nyon", "geneve", "fribourg"])

    zone_page("lausanne", "Lausanne", "Lausanne et environs",
        PAGE_TITLES["lausanne"],
        META_DESCRIPTIONS["lausanne"],
        "Chauffagiste à Lausanne : chauffage, CVC et dépannage",
        p("Vous cherchez un chauffagiste à Lausanne ? L'agglomération concentre immeubles résidentiels, bâtiments tertiaires et un parc ancien important (quartiers du centre-ville, Sous-Gare, Chailly) qui nécessite souvent une adaptation soignée des installations techniques lors d'une rénovation. Une partie de la ville est desservie par le réseau de chauffage à distance des Services industriels de Lausanne (SiL).") +
        p("Nous intervenons aussi en dépannage chauffage à Lausanne et communes voisines. Indiquez le quartier ou la commune exacte lors de votre demande.") +
        p('Pour la climatisation ou une pompe à chaleur, consultez aussi nos pages <a href="/climatisation/">climatisation</a> et <a href="/chauffage/">chauffage</a>.') +
        communes_block(["Renens", "Prilly", "Le Mont-sur-Lausanne", "Épalinges", "Pully", "Chavannes-près-Renens", "Ecublens", "Crissier"]) +
        SUBSIDY_NOTE.format(extra="Les demandes pour l'agglomération lausannoise sont instruites par la Direction de l'énergie du canton de Vaud."),
        zone_aeo_faq("Lausanne", "Lausanne et environs") + [
            ("Proposez-vous le dépannage chauffage à Lausanne ?", f"Oui. Appelez {COMPANY_NAME} au {PHONE_DISP} en indiquant votre adresse lausannoise et le type de panne (chaudière, PAC, radiateurs)."),
            ("Mon immeuble est raccordé au chauffage à distance (CAD), intervenez-vous quand même ?", "Oui : nous intervenons sur les sous-stations, la distribution interne (radiateurs, vannes, régulation) et les réseaux sanitaires, même si la production de chaleur est assurée par un réseau CAD."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["nyon", "vaud", "geneve"])

    zone_page("nyon", "Nyon", "la région de Nyon",
        PAGE_TITLES["nyon"],
        META_DESCRIPTIONS["nyon"],
        "Climatisation et chauffagiste à Nyon",
        p("Climatisation à Nyon et chauffagiste local : la région entre Genève et Lausanne combine constructions récentes (villas, PPE neuves autour du lac) et bâti plus ancien dans les villages environnants. C'est une zone de forte croissance résidentielle, avec des standards énergétiques élevés (Minergie) fréquents sur les nouvelles constructions.") +
        p("Nous installons et entretenons la climatisation (split, multi-split, PAC air-air) ainsi que le chauffage (pompes à chaleur, chaudières) à Nyon, Gland, Rolle, Coppet et environs.") +
        p('Besoin d\'un devis climatisation ou chauffage ? Consultez nos pages <a href="/climatisation/">climatisation</a> et <a href="/chauffage/">chauffagiste</a>, ou contactez-nous en précisant l\'adresse.') +
        communes_block(["Gland", "Rolle", "Prangins", "Founex", "Coppet", "Genolier", "Duillier", "Trélex"]) +
        SUBSIDY_NOTE.format(extra="La région de Nyon dépend du barème et du guichet du canton de Vaud (Direction de l'énergie)."),
        zone_aeo_faq("Nyon", "la région de Nyon") + [
            ("Installez-vous la climatisation à Nyon ?", f"Oui. {COMPANY_NAME} étudie et installe la climatisation à Nyon et communes voisines (Gland, Rolle, Coppet…). Devis via la page contact."),
            ("Intervenez-vous sur des bâtiments Minergie récents ?", "Oui. Les constructions Minergie demandent une ventilation mécanique contrôlée bien réglée et un entretien régulier : nous pouvons intervenir sur ces installations comme sur du bâti plus ancien."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["geneve", "lausanne", "vaud"])

    zone_page("valais", "Valais", "le canton du Valais",
        PAGE_TITLES["valais"],
        META_DESCRIPTIONS["valais"],
        "Chauffagiste en Valais : chauffage, CVC et climatisation",
        p("Chauffagiste en Valais : le canton présente de fortes variations d'altitude — de la plaine du Rhône aux stations de montagne — qui influencent directement le dimensionnement des installations de chauffage. Les résidences secondaires et chalets, souvent inoccupés une partie de l'année, demandent une attention particulière (protection hors gel, remise en service saisonnière).") +
        p("Contactez-nous avec votre commune (Sion, Martigny, Monthey, Sierre…) pour vérifier la disponibilité d'intervention.") +
        communes_block(["Sion", "Martigny", "Monthey", "Sierre", "Crans-Montana", "Verbier", "Saint-Maurice", "Conthey"]) +
        SUBSIDY_NOTE.format(extra="En Valais, les demandes sont instruites par le Service de l'énergie et des forces hydrauliques (SEFH) de l'État du Valais."),
        zone_aeo_faq("Valais", "le canton du Valais") + [
            ("Intervenez-vous sur un chalet ou une résidence secondaire ?", "Oui, en tenant compte des contraintes propres à ces logements (occupation partielle, altitude, risque de gel). Précisez l'altitude et le mode d'occupation lors de votre demande."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav", "sprinkler-protection-incendie"], ["geneve", "vaud", "fribourg"])

    zone_page("fribourg", "Fribourg", "le canton de Fribourg",
        PAGE_TITLES["fribourg"],
        META_DESCRIPTIONS["fribourg"],
        "Chauffagiste Fribourg et Romont",
        p(f"Chauffagiste à Fribourg et Romont : notre siège est basé à {ADDRESS_LOCALITY}, dans le canton de Fribourg. Nous connaissons bien ce territoire à cheval sur les régions linguistiques, qui compte un parc bâti varié entre la ville de Fribourg, les districts de la Glâne, de la Gruyère et de la Broye.") +
        p("Précisez la commune et l'urgence de votre demande lors du premier contact.") +
        communes_block(["Fribourg", "Bulle", "Romont", "Châtel-Saint-Denis", "Estavayer-le-Lac", "Domdidier", "Marly", "Villars-sur-Glâne"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Fribourg, les demandes sont instruites par le Service de l'énergie (SdE)."),
        zone_aeo_faq("Fribourg", "le canton de Fribourg") + [
            ("Sopjani Tech Sàrl est-elle basée dans le canton de Fribourg ?", f"Oui, notre siège se trouve à {ADDRESS_FULL}, dans le district de la Glâne."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["vaud", "lausanne", "valais", "neuchatel"])

    zone_page("neuchatel", "Neuchâtel", "le canton de Neuchâtel",
        PAGE_TITLES["neuchatel"],
        META_DESCRIPTIONS["neuchatel"],
        "Chauffagiste à Neuchâtel et La Chaux-de-Fonds",
        p("Chauffagiste dans le canton de Neuchâtel : le territoire s'étend du littoral du lac de Neuchâtel aux hauteurs du Jura (La Chaux-de-Fonds, Le Locle). Le parc bâti mêle immeubles en ville, villas sur les coteaux et bâtiments industriels ou horlogers qui demandent souvent des installations CVC adaptées.") +
        p("Contactez-nous en précisant votre commune pour vérifier la disponibilité d'intervention.") +
        communes_block(["Neuchâtel", "La Chaux-de-Fonds", "Le Locle", "Peseux", "Boudry", "Cortaillod", "Saint-Blaise", "Val-de-Ruz"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Neuchâtel, les demandes sont instruites par le Service de l'énergie et de l'environnement (SENE)."),
        zone_aeo_faq("Neuchâtel", "le canton de Neuchâtel") + [
            ("Intervenez-vous à La Chaux-de-Fonds et dans le Haut ?", "Oui, sous réserve de planification. Précisez l'adresse et l'urgence lors du premier contact."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["vaud", "fribourg", "geneve"])


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
{page_hero("Informations légales", "Mentions légales", f"Informations relatives à l'éditeur du site {SITE.replace('https://', '')} et aux conditions d'utilisation.", show_ctas=False)}
<section class="content-section">
  <div class="container prose-block">
    <h2 class="section-title">Éditeur du site</h2>
    {legal_identity_block()}
    <h3>Hébergement</h3>
    <p>Ce site est hébergé par {HOST_NAME}, {HOST_ADDRESS}.</p>
    <h3 id="propriete-intellectuelle">Propriété intellectuelle</h3>
    <p>L'ensemble des contenus présents sur ce site (textes, images, graphismes, logo, structure) est la propriété de {COMPANY_NAME} ou de ses partenaires, sauf mention contraire. Toute reproduction, représentation ou diffusion, totale ou partielle, sans autorisation écrite préalable est interdite.</p>
    <p>Les photographies de réalisations publiées sur ce site sont protégées par le droit d'auteur ({IMAGE_COPYRIGHT_NOTICE}). Crédit photo : {COMPANY_NAME}. Pour demander une autorisation d'utilisation ou obtenir une licence, <a href="{IMAGE_ACQUIRE_LICENSE_URL}">contactez-nous</a>.</p>
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
{page_hero("Protection des données", "Politique de confidentialité", f"Comment {COMPANY_NAME} traite les données personnelles collectées via ce site, conformément à la loi suisse sur la protection des données (nLPD).", show_ctas=False)}
<section class="content-section">
  <div class="container prose-block">
    <h2 class="section-title">Responsable du traitement</h2>
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


def canonical_url(path):
    """URL absolue canonique avec slash final."""
    if path == "/":
        return SITE + "/"
    return SITE + path if path.endswith("/") else SITE + path + "/"


def build_legacy_redirect_stubs():
    """Pages de secours pour GitHub Pages (pas de 301 HTTP natif)."""
    for old_name, new_path in LEGACY_REDIRECTS.items():
        target = canonical_url(new_path)
        content = f"""<!DOCTYPE html>
<html lang="fr-CH">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0;url={target}">
  <link rel="canonical" href="{target}">
  <meta name="robots" content="noindex, nofollow">
  <title>Redirection permanente…</title>
  <script>location.replace("{target}");</script>
</head>
<body><p>Redirection vers <a href="{target}">{target}</a>.</p></body>
</html>"""
        (ROOT / old_name).write_text(content, encoding="utf-8")


def build_redirects_file():
    """Vraies redirections HTTP 301 (Cloudflare Pages, Netlify)."""
    lines = [
        "# Généré par build_site.py — redirections 301 côté serveur",
        "",
        "http://sopjanitech.ch/* https://sopjanitech.ch/:splat 301",
        "http://www.sopjanitech.ch/* https://sopjanitech.ch/:splat 301",
        "/index.html / 301",
    ]
    for old_name, new_path in LEGACY_REDIRECTS.items():
        lines.append(f"/{old_name} {new_path} 301")
    lines.append(f"https://www.sopjanitech.ch/* {SITE}/:splat 301")
    (ROOT / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_nojekyll():
    """Évite que Jekyll ignore des fichiers/dossiers (ex. _redirects)."""
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")


def build_cloudflare_worker():
    """Worker Cloudflare : vraies redirections HTTP 301 devant GitHub Pages."""
    redirects = {f"/{old_name}": new_path for old_name, new_path in LEGACY_REDIRECTS.items()}
    redirects_js = json.dumps(redirects, indent=2, ensure_ascii=False)
    content = f"""/**
 * Redirections HTTP 301 — généré par build_site.py
 * Déploiement (une fois) : npx wrangler deploy
 * Prérequis : domaine sopjanitech.ch géré par Cloudflare (DNS proxy activé).
 */
const REDIRECTS = {redirects_js};
const APEX_HOST = "sopjanitech.ch";

function needsTrailingSlash(pathname) {{
  if (pathname === "/" || pathname.endsWith("/")) return false;
  const last = pathname.split("/").pop() || "";
  return !last.includes(".");
}}

export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    let changed = false;
    // Un seul hop : http+www → https://apex (évite http://www → https://www → apex)
    if (url.protocol === "http:") {{
      url.protocol = "https:";
      changed = true;
    }}
    if (url.hostname === `www.${{APEX_HOST}}`) {{
      url.hostname = APEX_HOST;
      changed = true;
    }}
    if (changed) {{
      return Response.redirect(url.toString(), 301);
    }}
    if (url.pathname === "/index.html") {{
      return Response.redirect(`${{url.origin}}/`, 301);
    }}
    const dest = REDIRECTS[url.pathname];
    if (dest) {{
      return Response.redirect(`${{url.origin}}${{dest}}`, 301);
    }}
    if (needsTrailingSlash(url.pathname)) {{
      return Response.redirect(`${{url.origin}}${{url.pathname}}/`, 301);
    }}
    return fetch(request);
  }},
}};
"""
    (ROOT / "redirect-worker.mjs").write_text(content, encoding="utf-8")


def build_realisations():
    cat_labels = [
        ("chauffage", "Chauffage"),
        ("ventilation", "Ventilation"),
        ("sanitaire", "Sanitaire"),
        ("sprinkler", "Sprinkler et protection incendie"),
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
            image_objects.append(image_object_ld(fn, w, h, alt, cap))
        sections += f"""<section class="content-section" aria-labelledby="real-{cat}">
  <div class="container">
    <span class="label">{label}</span>
    <div class="rule"></div>
    <h2 class="section-title" id="real-{cat}">{label}</h2>
    <div class="gallery gallery-cols-3">{"".join(cards)}</div>
  </div>
</section>
"""
    body = f"""
{page_hero(
        "Réalisations",
        f"Nos réalisations en {CVCS_PROSE} et sprinkler",
        f"Aperçu de chantiers réalisés par {COMPANY_NAME} en Suisse romande : chauffage, ventilation, sanitaire et sprinkler / protection incendie.",
        image=hero_image_for("realisations"),
    )}
{sections}
<p class="gallery-legal-note container"><a href="{IMAGE_LICENSE_URL}">Droits et utilisation des images</a> · {IMAGE_COPYRIGHT_NOTICE}</p>
{trust_strip()}
{norms_bar()}
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
        blocks += f'<div class="sitemap-section"><h2 class="section-title">{sec_title}</h2><ul class="sitemap-list">{items}</ul></div>'
        all_links.extend(links)
    body = f"""
{page_hero("Navigation", "Plan du site", f"Accès direct à toutes les pages de {COMPANY_NAME} : prestations, zones d'intervention et informations de contact.", show_ctas=False)}
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
const mobileNavClose = document.getElementById('mobileNavClose');

function setMobileNav(open) {
  if (!mobileNav || !burger) return;
  mobileNav.classList.toggle('open', open);
  burger.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  burger.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
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
  if (mobileNavClose) {
    mobileNavClose.addEventListener('click', closeMobileNav);
  }
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
    const willOpen = !group.classList.contains('is-open');
    document.querySelectorAll('.mobile-nav-group.is-open').forEach(openGroup => {
      if (openGroup === group) return;
      openGroup.classList.remove('is-open');
      openGroup.querySelector('.mobile-nav-toggle')?.setAttribute('aria-expanded', 'false');
    });
    group.classList.toggle('is-open', willOpen);
    btn.setAttribute('aria-expanded', willOpen);
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

/* Magnetic carousel — dock-style magnify (vanilla, no React) */
(function initMagneticCarousels() {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isCoarse = window.matchMedia('(pointer: coarse)').matches;

  document.querySelectorAll('.magnetic-carousel').forEach(root => {
    const track = root.querySelector('.magnetic-carousel__track');
    const backdrop = root.querySelector('.magnetic-carousel__backdrop');
    const bars = Array.from(root.querySelectorAll('.magnetic-bar'));
    if (!track || bars.length === 0) return;

    const gap = 14;
    const influence = 220;
    const blurPx = 3;
    const openDur = 300;

    function getCollapsedSize() {
      const narrow = window.matchMedia('(max-width: 768px)').matches;
      return narrow
        ? { w: 120, h: 180, hoverW: 160, hoverH: 220 }
        : { w: 148, h: 220, hoverW: 240, hoverH: 280 };
    }

    function getOpenSize() {
      return Math.min(560, Math.floor(window.innerWidth * 0.88));
    }

    let openIndex = null;
    let closing = false;
    let factors = bars.map(() => 0);
    let target = bars.map(() => 0);
    let cur = bars.map(() => 0);
    let loopId = 0;
    let closeTimer = 0;

    function applySizes() {
      const sizes = getCollapsedSize();
      const collapsedW = sizes.w;
      const collapsedH = sizes.h;
      const hoverW = sizes.hoverW;
      const hoverH = sizes.hoverH;
      const openSize = getOpenSize();
      bars.forEach((bar, i) => {
        let w = collapsedW;
        let h = collapsedH;
        if (openIndex !== null) {
          if (i === openIndex) {
            w = openSize;
            h = openSize;
          }
        } else if (!reduceMotion && !isCoarse) {
          const f = factors[i] || 0;
          w = collapsedW + (hoverW - collapsedW) * f;
          h = collapsedH + (hoverH - collapsedH) * f;
        }
        const blurred = openIndex !== null && i !== openIndex;
        bar.style.width = w + 'px';
        bar.style.height = h + 'px';
        bar.style.filter = blurred ? 'blur(' + blurPx + 'px)' : 'none';
        bar.style.opacity = blurred ? '0.55' : '1';
        bar.style.zIndex = i === openIndex ? '3' : '2';
        bar.classList.toggle('is-open', i === openIndex);
        bar.setAttribute('aria-expanded', i === openIndex ? 'true' : 'false');
        const useTransition = openIndex !== null || closing;
        bar.style.transition = useTransition
          ? 'width ' + openDur + 'ms ease-in-out, height ' + openDur + 'ms ease-in-out, filter ' + openDur + 'ms ease-in-out, opacity ' + openDur + 'ms ease-in-out'
          : 'none';
      });
      if (backdrop) {
        backdrop.hidden = openIndex === null;
        backdrop.setAttribute('aria-hidden', openIndex === null ? 'true' : 'false');
      }
      root.classList.toggle('is-expanded', openIndex !== null);
    }

    function startLoop() {
      if (loopId || reduceMotion || isCoarse || openIndex !== null) return;
      const step = () => {
        let moving = false;
        for (let i = 0; i < cur.length; i++) {
          const d = (target[i] || 0) - cur[i];
          if (Math.abs(d) > 0.001) {
            cur[i] += d * 0.2;
            moving = true;
          } else {
            cur[i] = target[i] || 0;
          }
        }
        factors = cur.slice();
        applySizes();
        loopId = moving ? requestAnimationFrame(step) : 0;
      };
      loopId = requestAnimationFrame(step);
    }

    function setTargetFromCursor(clientX) {
      const sizes = getCollapsedSize();
      const collapsedW = sizes.w;
      const rect = track.getBoundingClientRect();
      const cx = clientX - rect.left;
      const n = bars.length;
      const totalBase = n * collapsedW + (n - 1) * gap;
      const startX = (rect.width - totalBase) / 2;
      target = bars.map((_, i) => {
        const center = startX + i * (collapsedW + gap) + collapsedW / 2;
        const dist = Math.abs(cx - center);
        const f = Math.max(0, 1 - dist / influence);
        return f * f * (3 - 2 * f);
      });
      startLoop();
    }

    function close() {
      target = bars.map(() => 0);
      cur = bars.map(() => 0);
      factors = bars.map(() => 0);
      closing = true;
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => { closing = false; applySizes(); }, openDur);
      openIndex = null;
      applySizes();
    }

    function openAt(i) {
      if (openIndex === i) {
        close();
        return;
      }
      openIndex = i;
      target = bars.map(() => 0);
      cur = bars.map(() => 0);
      factors = bars.map(() => 0);
      applySizes();
    }

    track.addEventListener('mousemove', e => {
      if (reduceMotion || isCoarse || openIndex !== null) return;
      setTargetFromCursor(e.clientX);
    });
    track.addEventListener('mouseleave', () => {
      if (openIndex !== null) return;
      target = bars.map(() => 0);
      startLoop();
    });

    bars.forEach((bar, i) => {
      bar.addEventListener('click', e => {
        e.stopPropagation();
        openAt(i);
      });
    });
    if (backdrop) backdrop.addEventListener('click', close);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && openIndex !== null) close();
    });

    applySizes();
  });
})();
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
    build_legacy_redirect_stubs()
    build_redirects_file()
    build_cloudflare_worker()
    build_nojekyll()
    build_sitemap()
    build_robots()
    print("Site generated successfully.")


if __name__ == "__main__":
    main()
