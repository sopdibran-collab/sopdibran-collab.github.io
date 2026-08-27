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
# Formulaire contact → info@sopjanitech.ch via FormSubmit (AJAX).
# 1ʳᵉ soumission : confirmer le lien reçu dans la boîte info@ (activation FormSubmit).
FORM_ENDPOINT = f"https://formsubmit.co/ajax/{EMAIL}"
FORM_SUBJECT = "Demande de devis — Sopjani Tech"
# Logos — variantes officielles Alpë → assets/brand/
# PRINCIPALE · RESPONSIVE · SUBMARK · FAVICON · grayscale · mono noir/blanc · couleur inversée
LOGO_HEADER = "/assets/brand/logo-responsive.svg"
LOGO_FOOTER = "/assets/brand/logo-responsive.svg"
LOGO_SUBMARK = "/assets/brand/logo-submark.svg"
LOGO_FULL = "/assets/logo-full.png"
FAVICON_PATH = "/assets/favicon.png"
FAVICON_SVG = "/assets/favicon.svg"
APPLE_TOUCH_ICON = "/assets/apple-touch-icon.png"
OG_IMAGE = f"{SITE}/assets/og-default.jpg"
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
OG_IMAGE_TYPE = "image/jpeg"
LOGO_SCHEMA = f"{SITE}/assets/og-logo.png"  # carré PRINCIPALE pour schema.org
FAVICON = f"{SITE}{FAVICON_PATH}"
THEME_COLOR = "#0B2545"
ADDRESS_STREET = "Rue Pierre de Savoie 9"
ADDRESS_POSTAL = "1680"
ADDRESS_LOCALITY = "Romont FR"
ADDRESS_FULL = "Rue Pierre de Savoie 9, 1680 Romont FR"
COMPANY_NAME = "Sopjani Tech Sàrl"  # raison sociale canonique (mentions légales / RC)
COMPANY_UID = "CHE-177.567.012"
PUBLICATION_MANAGER = "Shkodran Sopjani"
HOST_NAME = "GitHub, Inc. (GitHub Pages)"
HOST_ADDRESS = "88 Colin P. Kelly Jr. St, San Francisco, CA 94107, États-Unis"
# Horaires canoniques — HTML + JSON-LD (7j/7, 07:00–17:00)
HOURS = "Tous les jours, 7h00 – 17h00"
HOURS_OPENS = "07:00"
HOURS_CLOSES = "17:00"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Rue+Pierre+de+Savoie+9,+1680+Romont"
# Place ID Google (libellé fiche GBP « Sopjani-tech sàrl » — à aligner manuellement côté Google)
MAP_EMBED = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1481964.3806735645!2d5.895466104411914!3d46.67378415677807!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9458f52305e1fe3%3A0x31fd51d876fffe44!2sSopjani-tech%20s%C3%A0rl!5e1!3m2!1sfr!2sch!4v1781214251877!5m2!1sfr!2sch"
GOOGLE_BUSINESS_URL = "https://maps.app.goo.gl/hWWQCXAZzrTCgjFr7"
# Chemins hors contenu éditorial (robots Disallow). Les .txt de vérification restent publics.
JUNK_DISALLOW_PATHS = (
    "/build_site.py",
    "/signature-mail-hostpoint.html",
    "/signature-mail-hostpoint-v2.html",
    "/signature-mail-hostpoint-v3.html",
    "/scripts/",
    "/2a4c1f14188cf21440b6fdbad88d7e38.txt",
    "/4e83fba7d06a413e96b4abe69b2f5256.txt",
)
# Fichiers de vérification Search Console : accessibles, mais X-Robots-Tag noindex via Worker
VERIFICATION_TXT_PATHS = (
    "/2a4c1f14188cf21440b6fdbad88d7e38.txt",
    "/4e83fba7d06a413e96b4abe69b2f5256.txt",
)
# Masqués en HTTP 404 par le Worker Cloudflare (source / anciennes signatures)
WORKER_BLOCK_EXACT = (
    "/build_site.py",
    "/signature-mail-hostpoint.html",
    "/signature-mail-hostpoint-v2.html",
    "/signature-mail-hostpoint-v3.html",
)
WORKER_BLOCK_PREFIXES = (
    "/scripts/",
)

# Avis Google réels affichés sur le site (texte = source Google Business Profile)
GOOGLE_REVIEWS = [
    {
        "author": "Karl Gaming",
        "badge": "Local Guide",
        "rating": 5,
        "date_label": "il y a un mois",
        "date_published": "2026-07-09",
        "body": "Conseil rapide et efficace. Travail de qualité à prix plus que raisonnable ! Je ne peux que recommander.",
        "initial": "K",
    },
    {
        "author": "Sammy Crettenand",
        "badge": "",
        "rating": 5,
        "date_label": "il y a un mois",
        "date_published": "2026-07-09",
        "body": "Travail de qualité à un bon prix, prise en charge rapide de ma panne de chauffage.",
        "initial": "S",
    },
]
COPYRIGHT_YEAR = 2026
IMAGE_LICENSE_URL = f"{SITE}/mentions-legales/#propriete-intellectuelle"
IMAGE_ACQUIRE_LICENSE_URL = f"{SITE}/contact/"
IMAGE_COPYRIGHT_NOTICE = f"© {COPYRIGHT_YEAR} {COMPANY_NAME}"

CVCS_GROUP = "Chauffage, Ventilation, Climatisation, Sanitaire"
CVCS_PROSE = "chauffage, ventilation, climatisation et sanitaire"
CVCS_ALL_PROSE = "chauffage, ventilation, climatisation, sanitaire, dépannage SAV et sprinkler"

META_DESCRIPTIONS = {
    "home": "CVCS en Suisse romande : chauffage, ventilation, climatisation et sanitaire — de l'étude à la réalisation. Villas, immeubles et appels d'offres. Siège à Romont FR.",
    "prestations": "Installation, maintenance et dépannage : chauffage, ventilation, climatisation, sanitaire, sprinkler et SAV en Suisse romande. Devis gratuit et sans engagement.",
    "zones-intervention": f"{COMPANY_NAME} intervient près de vous en Suisse romande : Genève, Vaud, Valais, Fribourg, Romont, Neuchâtel et agglomérations. Siège à {ADDRESS_LOCALITY}.",
    "a-propos": "Entreprise technique à Romont FR : chauffage, ventilation, climatisation, sanitaire, SAV et sprinkler en Suisse romande. Un interlocuteur unique, normes SIA, SUVA et AEAI.",
    "contact": f"Demandez un devis gratuit ou un dépannage urgent (chauffage, clim, ventilation, sanitaire) en Suisse romande. Réponse rapide — {PHONE_DISP}.",
    "depannage-sav": f"Panne de chauffage, clim, ventilation ou sanitaire ? Dépannage CVCS urgent en Suisse romande, 7j/7 de 7h à 17h. Appelez le {PHONE_DISP}.",
    "chauffage": "Chauffagiste en Suisse romande : chaudières, pompes à chaleur, entretien et dépannage. Villas, immeubles, PPE. Devis gratuit et sans engagement.",
    "ventilation": "VMC, gaines et traitement de l'air : étude, pose et dépannage en Suisse romande (Genève, Vaud, Fribourg, Valais). Urgence ventilation 7j/7. Devis gratuit.",
    "climatisation": f"Climatisation à Nyon, Lausanne et Genève : étude, pose et dépannage de splits, multi-splits et PAC air-air. Devis gratuit — {PHONE_DISP}.",
    "sprinkler-protection-incendie": "Réseaux sprinkler en sous-traitance spécialisée : étude et installation pour ERP, parkings et bâtiments industriels en Suisse romande. Normes AEAI respectées.",
    "sanitaire": "Installations, rénovations et dépannages sanitaires : réseaux eau chaude/froide, fuites, chauffe-eau. Intervention en Suisse romande. Devis gratuit.",
    "geneve": f"Chauffagiste à Genève et environs : installation, entretien et dépannage de chauffage et de climatisation (split, multi-split, PAC). Devis gratuit — {PHONE_DISP}.",
    "vaud": "Chauffagiste dans le canton de Vaud : Lausanne, Nyon, Riviera, Chablais, Nord vaudois. Chauffage, PAC, entretien et dépannage. Devis gratuit.",
    "lausanne": f"Chauffagiste à Lausanne et environs : dépannage chauffage, pompes à chaleur, chaudières. Intervention rapide, devis gratuit — {PHONE_DISP}.",
    "nyon": "Climatisation (split, multi-split, PAC air-air) et chauffage à Nyon, Gland, Rolle et Coppet : installation, entretien, dépannage. Devis gratuit.",
    "valais": f"Chauffagiste en Valais : Sion, Martigny, Monthey, Sierre et stations. Chaudières, PAC, remise en service après hiver. Devis gratuit — {PHONE_DISP}.",
    "fribourg": "Chauffagiste à Fribourg, Glâne, Gruyère et Broye : installation, entretien, dépannage, aides aux subventions PAC. Devis gratuit. Siège à Romont.",
    "romont": f"CVCS à Romont FR (siège) : chauffage, ventilation, climatisation, sanitaire et dépannage SAV pour villas, immeubles, PPE et entreprises. Devis gratuit — {PHONE_DISP}.",
    "neuchatel": "Chauffagiste dans le canton de Neuchâtel : littoral et Jura (La Chaux-de-Fonds, Le Locle). Chauffage, CVCS, entretien et dépannage. Devis gratuit.",
    "mentions-legales": f"Mentions légales de {COMPANY_NAME} : raison sociale, siège à {ADDRESS_FULL}, UID {COMPANY_UID} et contact.",
    "politique-confidentialite": f"Politique de confidentialité de {COMPANY_NAME} : traitement des données, cookies et droits selon la nLPD suisse.",
    "plan-du-site": f"Plan du site {COMPANY_NAME} : accès à toutes les pages prestations, zones d'intervention et contact en Suisse romande.",
    "realisations": "Cas chantiers réels : centrale sprinkler, poste d'alarme sous air, conduits de ventilation, locaux techniques sanitaires. Photos de nos interventions en Suisse romande.",
    "404": f"Page introuvable — {COMPANY_NAME}, chauffagiste CVCS et sprinkler à Romont (Suisse romande).",
}

PAGE_TITLES = {
    "home": "CVCS en Suisse romande : étude et installation | Sopjani Tech Sàrl",
    "a-propos": "Sopjani Tech Sàrl : entreprise CVCS & sprinkler à Romont",
    "contact": "Devis gratuit & dépannage CVCS | Sopjani Tech Sàrl",
    "prestations": "Prestations CVCS & sprinkler — Suisse romande | Sopjani Tech",
    "zones-intervention": "Zones d'intervention | Suisse romande | Sopjani Tech Sàrl",
    "plan-du-site": "Plan du site | Sopjani Tech Sàrl",
    "chauffage": "Chauffagiste en Suisse romande | Sopjani Tech Sàrl",
    "ventilation": "Ventilation & VMC en Suisse romande | Sopjani Tech Sàrl",
    "climatisation": "Climatisation à Nyon, Lausanne & Genève | Sopjani Tech Sàrl",
    "depannage-sav": "Dépannage CVCS urgent en Suisse romande | Sopjani Tech",
    "sanitaire": "Sanitaire en Suisse romande : installation & dépannage | Sopjani Tech",
    "sprinkler-protection-incendie": "Sprinkler & protection incendie en Suisse romande | Sopjani Tech",
    "geneve": "Chauffagiste à Genève — chauffage & climatisation | Sopjani Tech",
    "vaud": "Chauffagiste dans le canton de Vaud | Sopjani Tech Sàrl",
    "lausanne": "Chauffagiste à Lausanne — chauffage & dépannage | Sopjani Tech",
    "nyon": "Climatisation & chauffagiste à Nyon | Sopjani Tech Sàrl",
    "valais": "Chauffagiste en Valais : chauffage & climatisation | Sopjani Tech",
    "fribourg": "Chauffagiste à Fribourg (canton) | Sopjani Tech Sàrl",
    "romont": "CVCS à Romont — siège Sopjani Tech | chauffage & dépannage",
    "neuchatel": "Chauffagiste Neuchâtel & La Chaux-de-Fonds | Sopjani Tech",
    "realisations": "Nos réalisations CVCS & sprinkler — Sopjani Tech Sàrl",
    "404": f"Page introuvable | {COMPANY_NAME}",
}

SERVICES = [
    ("chauffage", "Chauffage", "Installation, entretien et dépannage de systèmes de chauffage."),
    ("ventilation", "Ventilation", "Ventilation et traitement de l'air pour bâtiments."),
    ("climatisation", "Climatisation", "Étude et installation de systèmes de climatisation."),
    ("sanitaire", "Sanitaire", "Installations sanitaires, dépannage et rénovations en Suisse romande."),
    ("depannage-sav", "Dépannage SAV", "Maintenance et dépannage de vos installations CVCS."),
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
    ("romont", "Romont", "Romont et la Glâne"),
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
    ("Romont", "/romont/"),
    ("Neuchâtel", "/neuchatel/"),
    ("La Chaux-de-Fonds", "/neuchatel/"),
)

ALL_ZONE_SLUGS = tuple(z for z, _, _ in ZONES)


def service_zones_block():
    """Cantons + villes — bloc dense (hub zones / usages ponctuels)."""
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


def service_zones_compact(zone_slugs=None):
    """Version allégée pour pages prestations : liens texte + hub (SEO sans pastilles)."""
    parts = []
    seen = set()
    # Cantons (signal SEO principal)
    for z, n, _ in ZONES:
        if z not in CANTON_ZONE_SLUGS or z in seen:
            continue
        seen.add(z)
        parts.append(f'<a href="/{z}/">{n}</a>')
    # Villes / zones locales du service (ex. Nyon, Lausanne)
    if zone_slugs:
        for z, n, _ in ZONES:
            if z not in zone_slugs or z in seen:
                continue
            seen.add(z)
            parts.append(f'<a href="/{z}/">{n}</a>')
    joined = ", ".join(parts)
    return f"""<p class="zones-compact">Couverture : {joined}. Vérifiez la disponibilité pour votre commune sur la page zones.</p>
<p class="svc-section__link"><a href="/zones-intervention/" class="text-link">Toutes les zones</a></p>"""


def service_area_served_schema(zone_slugs=None):
    """areaServed JSON-LD détaillé — signal SEO sans UI lourde."""
    areas = [{"@type": "AdministrativeArea", "name": "Suisse romande"}]
    seen = {"Suisse romande"}
    for z, n, _ in ZONES:
        include = z in CANTON_ZONE_SLUGS or (zone_slugs and z in zone_slugs)
        if not include or n in seen:
            continue
        seen.add(n)
        areas.append({"@type": "AdministrativeArea", "name": n, "url": f"{SITE}/{z}/"})
    for label, href in CITY_COVERAGE_LINKS:
        if label in seen:
            continue
        seen.add(label)
        areas.append({"@type": "City", "name": label, "url": f"{SITE}{href}"})
    return areas

ORG_SCHEMA = {
    "@type": ["HVACBusiness", "LocalBusiness"],
    "@id": f"{SITE}/#organization",
    "name": COMPANY_NAME,
    "legalName": COMPANY_NAME,
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
        "hoursAvailable": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": HOURS_OPENS,
            "closes": HOURS_CLOSES,
        },
    }],
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": HOURS_OPENS,
        "closes": HOURS_CLOSES,
    }],
    "areaServed": [
        {"@type": "AdministrativeArea", "name": n} for _, n, _ in ZONES
    ] + [{"@type": "AdministrativeArea", "name": "Suisse romande"}],
    "priceRange": "$$",
    "currenciesAccepted": "CHF",
    "inLanguage": "fr-CH",
    "logo": LOGO_SCHEMA,
    "image": OG_IMAGE,
    "sameAs": [GOOGLE_BUSINESS_URL],
}

WEBSITE_SCHEMA = {
    "@type": "WebSite",
    "@id": f"{SITE}/#website",
    "url": SITE,
    "name": COMPANY_NAME,
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
<p>{COMPANY_NAME} est une entreprise active dans les domaines du chauffage, de la ventilation, de la climatisation, du sanitaire, du dépannage SAV et du sprinkler / protection incendie en Suisse romande. Notre siège se trouve à {ADDRESS_FULL}, dans le canton de Fribourg.</p>
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
  <p style="margin-top:20px;"><a href="{GOOGLE_BUSINESS_URL}" class="text-link track-google" target="_blank" rel="noopener noreferrer">Fiche Google et avis</a></p>
</div>
<p>Vous avez une demande en {CVCS_PROSE} ou en dépannage SAV ? <a href="/contact/">Contactez-nous</a> pour échanger sur votre besoin et vérifier la disponibilité d'intervention dans votre zone.</p>
"""

HOME_ABOUT_TEASER = """
<p>Entreprise technique en Suisse romande, nous réalisons installations, maintenance et dépannage CVCS pour bâtiments résidentiels, tertiaires et industriels.</p>
<p><a href="/a-propos/" class="text-link">Présentation</a></p>
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
        f"Basés à {ADDRESS_FULL}, nous intervenons en Suisse romande pour l'installation, la maintenance et le dépannage CVCS."
        if not compact else
        f"Entreprise CVCS basée à {ADDRESS_LOCALITY}, active en Suisse romande."
    )
    return f"""<section class="geo-presence content-section{' alt' if not compact else ''}" aria-labelledby="geo-title">
  <div class="container">
    <span class="label">Proximité</span>
    <div class="rule"></div>
    <h2 class="section-title" id="geo-title">Une entreprise CVCS près de vous en Suisse romande</h2>
    <p class="section-lead">{lead} Contactez-nous pour vérifier la disponibilité dans votre commune.</p>
    <div class="zone-links">{zones}</div>
    <p style="margin-top:16px;"><a href="/contact/" class="text-link">Devis ou dépannage</a></p>
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
    """FAQ locale compacte (3 items) — laisse de la place aux FAQ spécifiques zone (max 5 au total)."""
    return [
        (f"Qui appeler pour un chauffagiste à {name} ?", f"{COMPANY_NAME} intervient comme chauffagiste dans {region} : installation, entretien et dépannage de chaudières et pompes à chaleur. Appelez le {PHONE_DISP} ou passez par la page contact."),
        (f"Qui appeler pour un dépannage CVCS à {name} ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp. Indiquez votre commune, le type de bâtiment et la nature de la panne."),
        (f"Comment obtenir un devis à {name} ?", f"Par téléphone au {PHONE_DISP} ou via la page contact : décrivez le bâtiment, la localisation et le type de travaux (installation, maintenance ou dépannage)."),
    ]


def chauffagiste_local_block():
    """Maillage interne pour requêtes « chauffagiste + ville » (GSC)."""
    links = (
        ("Nyon", "/nyon/"),
        ("Lausanne", "/lausanne/"),
        ("Genève", "/geneve/"),
        ("Fribourg", "/fribourg/"),
        ("Romont", "/romont/"),
        ("Valais", "/valais/"),
        ("Vaud", "/vaud/"),
        ("Neuchâtel", "/neuchatel/"),
    )
    pills = "".join(f'<a class="zone-pill" href="{href}">Chauffagiste {label}</a>' for label, href in links)
    return f"""<h3>Chauffagiste près de chez vous</h3>
<p>Vous cherchez un chauffagiste à Nyon, Lausanne, Genève, Romont ou ailleurs en Suisse romande ? Nous intervenons pour l'installation, l'entretien et le dépannage — pompes à chaleur, chaudières et réseaux de chauffage.</p>
<div class="zone-links">{pills}</div>
<p style="margin-top:16px;"><a href="/climatisation/" class="text-link">Climatisation (Nyon, Lausanne, Genève)</a></p>"""


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

# Cas chantiers — titres concrets (lieux réels uniquement quand connus dans les légendes)
CASE_STUDIES = [
    {
        "title": "Centrale sprinkler sous eau",
        "location": "Suisse romande",
        "service": "Sprinkler",
        "href": "/sprinkler-protection-incendie/",
        "summary": "Collecteurs rouges, postes d'alarme et manomètres en local technique.",
        "image": "sprinkler-collecteur-rouges.jpg",
    },
    {
        "title": "Poste d'alarme sous air",
        "location": "Parking Nord",
        "service": "Sprinkler",
        "href": "/sprinkler-protection-incendie/",
        "summary": "Station sprinkler sous air avec vanne et contrôles d'alarme.",
        "image": "sprinkler-vanne-seche-victaulic.jpg",
    },
    {
        "title": "Conduits de ventilation galvanisés",
        "location": "Suisse romande",
        "service": "Ventilation",
        "href": "/ventilation/",
        "summary": "Pose de gaines en acier galvanisé sur chantier tertiaire.",
        "image": "ventilation-conduit-galvanise-chantier.jpg",
    },
    {
        "title": "Local technique sanitaire",
        "location": "Suisse romande",
        "service": "Sanitaire",
        "href": "/sanitaire/",
        "summary": "Collecteurs, réseaux métalliques et distribution en local technique.",
        "image": "sanitaire-local-technique-collecteurs.jpg",
    },
    {
        "title": "Tuyauterie sanitaire plafond",
        "location": "Suisse romande",
        "service": "Sanitaire",
        "href": "/sanitaire/",
        "summary": "Réseaux au plafond avec collecteurs laiton et supportage.",
        "image": "sanitaire-tuyauterie-plafond-collecteurs.jpg",
    },
    {
        "title": "Fabrication tuyauterie chauffage",
        "location": "Atelier",
        "service": "Chauffage",
        "href": "/chauffage/",
        "summary": "Assemblage de tuyauterie de chauffage préparé en atelier.",
        "image": "tuyauterie-fabrication-atelier.jpg",
    },
    {
        "title": "Unité de ventilation HVAC",
        "location": "Suisse romande",
        "service": "Ventilation",
        "href": "/ventilation/",
        "summary": "Unité HVAC raccordée à une gaine souple en local technique.",
        "image": "ventilation-unite-hvac-gaine.jpg",
    },
    {
        "title": "Bâti-support WC Geberit",
        "location": "Suisse romande",
        "service": "Sanitaire",
        "href": "/sanitaire/",
        "summary": "Installation bâti-support Geberit Sigma avec colonne d'évacuation.",
        "image": "sanitaire-bati-wc-geberit-sigma.jpg",
    },
]


def case_card_html(case, *, heading="h3"):
    img = case["image"]
    title = case["title"]
    loc = case["location"]
    svc = case["service"]
    summary = case["summary"]
    href = case["href"]
    return f"""<article class="case-card">
  <a class="case-card__media" href="/realisations/#cas-chantiers" tabindex="-1">
    <img src="/assets/realisations/{img}" alt="{title.replace(chr(34), '&quot;')} — {svc}, {loc}" width="640" height="480" loading="lazy" decoding="async">
  </a>
  <div class="case-card__body">
    <p class="case-card__meta"><span>{svc}</span> · <span>{loc}</span></p>
    <{heading} class="case-card__title"><a href="{href}">{title}</a></{heading}>
    <p class="case-card__summary">{summary}</p>
  </div>
</article>"""


def case_studies_grid(cases, *, limit=None, heading="h3"):
    items = cases[:limit] if limit else cases
    cards = "".join(case_card_html(c, heading=heading) for c in items)
    return f'<div class="case-grid">{cards}</div>'


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
    "chauffage": ["chauffage", "ventilation"],
    "ventilation": ["ventilation"],
    "climatisation": [],  # pas de photos dédiées pour l'instant (voir /realisations/)
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
    """FAQPage JSON-LD — plain text only (strip markup from answers used also in HTML)."""
    def plain(text):
        return re.sub(r"<[^>]+>", "", text)
    return {
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": plain(q),
            "acceptedAnswer": {"@type": "Answer", "text": plain(a)},
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


def mobile_quick_bar(*, sticky=False):
    cls = "mobile-quick-bar mobile-quick-bar--sticky" if sticky else "mobile-quick-bar"
    return f"""<div class="{cls}" role="group" aria-label="Actions de contact rapides">
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
    <p class="topbar-left">Société basée à <a href="/romont/">{ADDRESS_LOCALITY}</a> — Interventions en Suisse romande</p>
    <p class="topbar-right">
      <a href="tel:{PHONE}" class="track-phone topbar-phone">{PHONE_DISP}</a>
      <span class="topbar-extra">
        <span aria-hidden="true">·</span>
        <a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a>
        <span aria-hidden="true">·</span>
        <span>Horaires&nbsp;: {HOURS}</span>
      </span>
    </p>
  </div>
</div>
<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="/" class="logo-wrap">
        <img class="logo-img logo-img--responsive" src="{LOGO_HEADER}" alt="{COMPANY_NAME}" width="160" height="78" loading="eager" decoding="async">
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
        <a href="/contact/" class="btn btn-brand track-devis">Demander un devis</a>
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
    svc_chips = "".join(
        f'<li><a href="/{s}/">{n}</a></li>' for s, n, _ in SERVICES
    )
    zone_chips = (
        '<li><a href="/zones-intervention/">Toutes</a></li>'
        + "".join(f'<li><a href="/{z}/">{n}</a></li>' for z, n, _ in ZONES)
    )
    return f"""<footer class="site-footer" role="contentinfo">
  <div class="container site-footer__inner">
    <div class="site-footer__top">
      <a href="/" class="footer-logo-wrap">
        <img class="logo-img logo-img--responsive" src="{LOGO_FOOTER}" alt="{COMPANY_NAME}" width="120" height="36" loading="lazy" decoding="async">
      </a>
      <p class="site-footer__tagline">{CVCS_GROUP} · Dépannage SAV · Suisse romande</p>
    </div>
    <div class="site-footer__rows">
      <div class="site-footer__row">
        <p class="site-footer__label">Services</p>
        <ul class="site-footer__chips">{svc_chips}</ul>
      </div>
      <div class="site-footer__row">
        <p class="site-footer__label">Zones</p>
        <ul class="site-footer__chips">{zone_chips}</ul>
      </div>
      <div class="site-footer__row">
        <p class="site-footer__label">Entreprise</p>
        <ul class="site-footer__chips">
          <li><a href="/">Accueil</a></li>
          <li><a href="/a-propos/">À propos</a></li>
          <li><a href="/realisations/">Réalisations</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
      <div class="site-footer__row site-footer__row--contact">
        <p class="site-footer__label">Contact</p>
        <ul class="site-footer__contact">
          <li><a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a></li>
          <li><a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a></li>
          <li><a href="{WA}" class="track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
          <li><a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a></li>
          <li>{HOURS}</li>
          <li><a href="{GOOGLE_BUSINESS_URL}" class="track-google" target="_blank" rel="noopener noreferrer">Avis Google</a></li>
        </ul>
      </div>
    </div>
    <div class="site-footer__bottom">
      <p class="site-footer__copy">© {COPYRIGHT_YEAR} {COMPANY_NAME}</p>
      <nav class="site-footer__legal" aria-label="Informations légales">
        <a href="/mentions-legales/">Mentions légales</a>
        <a href="/politique-confidentialite/">Confidentialité</a>
        <a href="/plan-du-site/">Plan du site</a>
      </nav>
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


def faq_html(items, group_name="faq"):
    """FAQ en <details> natif (NN/g : progressive disclosure). JSON-LD FAQPage à part."""
    blocks = []
    for i, (q, a) in enumerate(items, start=1):
        blocks.append(f"""<details class="faq-details" name="{group_name}">
  <summary class="faq-summary">
    <span class="faq-idx" aria-hidden="true">{i:02d}</span>
    <span class="faq-q-text">{q}</span>
    <span class="faq-icon" aria-hidden="true"></span>
  </summary>
  <div class="faq-a-panel"><p>{a}</p></div>
</details>""")
    return f'<div class="faq-list faq-list--details">{"".join(blocks)}</div>'


def details_accordion(items, heading="Détails réglementaires et techniques", group_name="expertise"):
    """Accordéon normes / détails denses — hors JSON-LD FAQPage."""
    if not items:
        return ""
    blocks = []
    for i, (q, a) in enumerate(items, start=1):
        blocks.append(f"""<details class="details-item" name="{group_name}">
  <summary class="details-summary">
    <span class="faq-idx" aria-hidden="true">{i:02d}</span>
    <span class="faq-q-text">{q}</span>
    <span class="faq-icon" aria-hidden="true"></span>
  </summary>
  <div class="details-panel"><p>{a}</p></div>
</details>""")
    return f"""<div class="details-accordion">
  <h3 class="details-accordion__title">{heading}</h3>
  <p class="details-accordion__hint">Ouvrez un volet uniquement si vous souhaitez le détail.</p>
  <div class="details-accordion__list">{"".join(blocks)}</div>
</div>"""


def z_interventions(items):
    """Grille Z-pattern (NN/g) : lecture gauche→droite alternée pour Types d'interventions."""
    rows = []
    for i, text in enumerate(items):
        flip = " z-row--flip" if i % 2 else ""
        rows.append(f"""<article class="z-row{flip}">
  <div class="z-row__visual" aria-hidden="true"><span class="z-row__num">{i + 1:02d}</span></div>
  <div class="z-row__body"><p>{text}</p></div>
</article>""")
    return f'<div class="z-grid">{"".join(rows)}</div>'


def problem_chips(items):
    """Liste scannable de problématiques (pastilles / puces)."""
    if isinstance(items, str):
        return items
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="problem-list">{lis}</ul>'


def problems_interventions_section(tone, problems, interventions):
    """Section fusionnée 2 colonnes : problématiques | interventions (Z-pattern)."""
    alt = " svc-section--alt" if tone % 2 else ""
    problems_html = problem_chips(problems)
    interventions_html = z_interventions(interventions) if isinstance(interventions, (list, tuple)) else interventions
    return f"""<section class="content-section svc-section{alt}" id="diagnostic-interventions" aria-labelledby="problems-title">
  <div class="container svc-section__inner">
    <div class="svc-split">
      <div class="svc-split__col svc-split__col--problems">
        <h2 class="section-title" id="problems-title">Problématiques traitées</h2>
        {problems_html}
      </div>
      <div class="svc-split__col svc-split__col--interventions">
        <h2 class="section-title" id="interventions-title">Types d'interventions</h2>
        {interventions_html}
      </div>
    </div>
  </div>
</section>"""


def svc_section(tone, section_id, title, inner, lead="", narrow=True, heading_id=None):
    """Section prestation avec fond alterné (tone pair = clair, impair = alt)."""
    alt = " svc-section--alt" if tone % 2 else ""
    hid = heading_id or f"{section_id}-title"
    lead_html = f'<p class="prose-lead">{lead}</p>' if lead else ""
    body_cls = "svc-section__body prose-block" if narrow else "svc-section__body"
    return f"""<section class="content-section svc-section{alt}" id="{section_id}" aria-labelledby="{hid}">
  <div class="container svc-section__inner">
    <div class="svc-section__head">
      <h2 class="section-title" id="{hid}">{title}</h2>
      {lead_html}
    </div>
    <div class="{body_cls}">{inner}</div>
  </div>
</section>"""


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


def _stars_svg(rating=5):
    """Étoiles accessibles (5 max) — SVG inline, pas d’emoji."""
    full = max(0, min(5, int(rating)))
    star = (
        '<svg class="g-review__star" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">'
        '<path fill="currentColor" d="M12 2.5l2.9 5.88 6.49.94-4.7 4.58 1.11 6.47L12 17.77l-5.8 3.05 1.11-6.47-4.7-4.58 6.49-.94L12 2.5z"/>'
        "</svg>"
    )
    return f'<span class="g-review__stars" aria-label="{full} sur 5">{star * full}</span>'


def google_g_mark():
    return (
        '<svg class="g-review__g" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">'
        '<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>'
        '<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>'
        '<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>'
        '<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>'
        "</svg>"
    )


def google_reviews_section(*, heading_id="avis-google-title"):
    """Bloc avis Google — citations éditoriales + lien fiche (pas de widget générique)."""
    n = len(GOOGLE_REVIEWS)
    avg = round(sum(r["rating"] for r in GOOGLE_REVIEWS) / n, 1) if n else 0
    avg_disp = str(avg).replace(".", ",")
    items = []
    for r in GOOGLE_REVIEWS:
        badge = f'<span class="g-review__badge">{r["badge"]}</span>' if r.get("badge") else ""
        items.append(
            f"""<blockquote class="g-review" cite="{GOOGLE_BUSINESS_URL}">
  <div class="g-review__top">
    <span class="g-review__avatar" aria-hidden="true">{r["initial"]}</span>
    <div class="g-review__who">
      <cite class="g-review__name">{r["author"]}</cite>
      {badge}
      <p class="g-review__when"><time datetime="{r["date_published"]}">{r["date_label"]}</time> · via Google</p>
    </div>
    {_stars_svg(r["rating"])}
  </div>
  <p class="g-review__body">« {r["body"]} »</p>
</blockquote>"""
        )
    return f"""<section class="g-reviews" aria-labelledby="{heading_id}">
  <div class="container">
    <div class="g-reviews__head">
      <div class="g-reviews__brand">
        {google_g_mark()}
        <div>
          <h2 class="section-title" id="{heading_id}">Avis clients Google</h2>
          <p class="g-reviews__score"><strong>{avg_disp}/5</strong> · {n} avis affichés · source Google</p>
        </div>
      </div>
      <a href="{GOOGLE_BUSINESS_URL}" class="btn btn-secondary track-google" target="_blank" rel="noopener noreferrer">Voir la fiche Google</a>
    </div>
    <div class="g-reviews__grid">{"".join(items)}</div>
  </div>
</section>"""


def hero_image_for(key):
    """Chemin hero 16:9 (2000×1125). Sources stock + équipe réelle (a-propos/contact)."""
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
        alt = (image_alt or h1).replace('"', "&quot;")
        return f"""<section class="page-hero hero hero--photo" aria-labelledby="page-h1">
  <div class="hero-media">
    <img src="{image}" alt="{alt}" width="2000" height="1125" fetchpriority="high" decoding="async">
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


def cta_band(title="Besoin d'un devis ou d'un dépannage ?", text="Contactez-nous pour décrire votre besoin. Nous vous répondrons dans les meilleurs délais.", *, phone_first=False):
    if phone_first:
        buttons = f"""<a href="tel:{PHONE}" class="btn btn-urgence track-phone">Appeler · {PHONE_DISP}</a>
    <a href="/contact/#contact-form" class="btn btn-brand btn-brand--on-dark track-devis">Demander un devis</a>"""
    else:
        buttons = f"""<a href="/contact/" class="btn btn-brand track-devis">Demander un devis</a>
    <a href="tel:{PHONE}" class="btn btn-secondary-on-dark track-phone">{PHONE_DISP}</a>"""
    return f"""<section class="cta-band" aria-label="Appel à l'action">
  <div class="container">
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="cta-band__actions">
    {buttons}
    </div>
  </div>
</section>"""


def gsc_verification_meta():
    if GOOGLE_SITE_VERIFICATION:
        return f'  <meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">\n'
    return "  <!-- TODO GSC : renseigner GOOGLE_SITE_VERIFICATION dans build_site.py -->\n"


def analytics_head():
    return """  <script>window.dataLayer = window.dataLayer || []; function gtag(){ dataLayer.push(arguments); }</script>"""


def page_shell(title, description, canonical, schema_graph, body, crumbs=None, *, robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"):
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
  <meta name="robots" content="{robots}">
  <meta name="geo.region" content="CH-FR">
  <meta name="geo.placename" content="Suisse romande">
  <meta name="geo.position" content="46.6917;6.9119">
  <meta name="ICBM" content="46.6917, 6.9119">
  <meta name="theme-color" content="{THEME_COLOR}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="{FAVICON_SVG}" type="image/svg+xml">
  <link rel="icon" href="{FAVICON_PATH}" type="image/png" sizes="32x32">
  <link rel="apple-touch-icon" href="{APPLE_TOUCH_ICON}" sizes="180x180">
{gsc_verification_meta()}  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_CH">
  <meta property="og:title" content="{safe_title}">
  <meta property="og:description" content="{safe_desc}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="{COMPANY_NAME}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:secure_url" content="{OG_IMAGE}">
  <meta property="og:image:type" content="{OG_IMAGE_TYPE}">
  <meta property="og:image:width" content="{OG_IMAGE_WIDTH}">
  <meta property="og:image:height" content="{OG_IMAGE_HEIGHT}">
  <meta property="og:image:alt" content="{COMPANY_NAME} — Chauffage, ventilation, climatisation et sanitaire en Suisse romande">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{safe_title}">
  <meta name="twitter:description" content="{safe_desc}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <meta name="twitter:image:alt" content="{COMPANY_NAME} — CVCS Suisse romande">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
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
    """Pages Prestations — layout densifié (6 blocs), fusion problèmes/interventions, FAQ <details>."""
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (name, url)]
    related = "".join(f'<a class="zone-pill" href="/{s}/">{n}</a>' for s, n, _ in SERVICES if s in related_svc)
    urgence_html = urgence_band() if show_urgence else ""
    carousel_imgs = carousel_images_for_service(slug, gallery_cat=gallery_cat, limit=8)

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

    tone = 0
    sections = []

    # 1. Problématiques + Types d'interventions (2 col + Z-pattern)
    sections.append(problems_interventions_section(tone, problems, interventions))
    tone += 1

    # 2. Équipements et cadre suisse (optionnel)
    if expertise_html:
        sections.append(svc_section(tone, "expertise", "Équipements et cadre suisse", expertise_html))
        tone += 1

    # 3. Pour quels bâtiments (+ déroulement)
    buildings_inner = f"""{clients}
<h3>Déroulement d'une intervention</h3>
{process}"""
    sections.append(svc_section(tone, "clients", "Pour quels bâtiments", buildings_inner))
    tone += 1

    # 4. Réalisations
    if carousel_imgs:
        gallery_inner = f"""{magnetic_carousel_html(carousel_imgs, name)}
<p class="svc-section__link"><a href="/realisations/" class="text-link">Toutes les réalisations</a></p>"""
        sections.append(svc_section(
            tone, "realisations", f"Réalisations — {name}", gallery_inner,
            lead=f"Survolez ou touchez une photo pour l'agrandir. Aperçu d'interventions réalisées par {COMPANY_NAME}.",
            narrow=False,
            heading_id="real-title",
        ).replace('class="content-section svc-section', 'class="content-section magnetic-section svc-section', 1))
        tone += 1

    # 5. Zones (compact) + prestations connexes — pastilles retirées, SEO via liens + JSON-LD
    zones_inner = f"""{service_zones_compact(zone_slugs)}
<div class="svc-related">
  <h3 class="svc-related__title">Prestations connexes</h3>
  <div class="zone-links">{related}</div>
</div>"""
    sections.append(svc_section(
        tone, "zones", "Zones desservies", zones_inner,
        narrow=True,
    ))
    tone += 1

    # 6. FAQ — même structure de tête que les autres sections
    faq_alt = " svc-section--alt" if tone % 2 else ""
    sections.append(f"""<section class="faq content-section svc-section{faq_alt}" id="faq" aria-labelledby="faq-title">
  <div class="container svc-section__inner">
    <div class="svc-section__head">
      <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    </div>
    <div class="faq-prose">{faq_html(faq)}</div>
  </div>
</section>""")

    body = f"""
{hero}
{urgence_html}
{"".join(sections)}
{trust_strip()}
{norms_bar()}
{cta_band()}"""
    service_schema = {
        "@type": "Service",
        "name": name,
        "serviceType": name,
        "provider": {"@id": f"{SITE}/#organization"},
        "areaServed": service_area_served_schema(zone_slugs),
        "description": desc,
        "url": SITE + url,
    }
    graph = base_graph(title, desc, SITE + url, crumbs, faq, service_schema)
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def zone_action_paths(name):
    """3 rangées d'action (pas de cards) — pages zone."""
    paths = [
        (
            "Climatisation",
            "Étude, pose et entretien — split, multi-split, PAC air-air.",
            "/climatisation/",
            "Voir",
            "",
        ),
        (
            "Chauffage",
            "Installation, entretien et dépannage — chaudières et pompes à chaleur.",
            "/chauffage/",
            "Voir",
            "",
        ),
        (
            "Dépannage",
            "Panne en cours ? Appelez pour une intervention rapide.",
            f"tel:{PHONE}",
            "Appeler",
            "zone-action--urgent",
        ),
    ]
    rows = []
    for title, lead, href, cta, mod in paths:
        track = "track-phone" if href.startswith("tel:") else "track-devis"
        mod_cls = f" {mod}" if mod else ""
        rows.append(
            f'<a class="zone-action{mod_cls} {track}" href="{href}">'
            f'<span class="zone-action__body">'
            f'<span class="zone-action__title">{title}</span>'
            f'<span class="zone-action__lead">{lead}</span>'
            f"</span>"
            f'<span class="zone-action__cta">{cta} <span aria-hidden="true">→</span></span>'
            f"</a>"
        )
    return f"""<section class="zone-actions" aria-labelledby="zone-actions-title">
  <div class="container">
    <h2 class="zone-actions__title" id="zone-actions-title">Votre besoin à {name}</h2>
    <div class="zone-actions__list">{"".join(rows)}</div>
  </div>
</section>"""


def zone_proof_quote():
    """Pull-quote d'un avis Google réel — pas de bandeau compteur."""
    if not GOOGLE_REVIEWS:
        return ""
    # Préférer un avis qui mentionne le chantier / dépannage si possible
    review = next((r for r in GOOGLE_REVIEWS if "panne" in r["body"].lower() or "chauffage" in r["body"].lower()), GOOGLE_REVIEWS[0])
    return f"""<figure class="zone-quote">
  {_stars_svg(review["rating"])}
  <blockquote cite="{GOOGLE_BUSINESS_URL}">
    <p>« {review["body"]} »</p>
  </blockquote>
  <figcaption class="zone-quote__cap">
    <cite>{review["author"]}</cite>
    <span aria-hidden="true">·</span>
    <a href="{GOOGLE_BUSINESS_URL}" class="track-google" target="_blank" rel="noopener noreferrer">Avis Google</a>
  </figcaption>
</figure>"""


def zone_page(slug, name, region, title, desc, h1, local_text, faq, svc_slugs, related_zones, hero_sub=None):
    """Page zone mobile-first : hero, local+preuve, actions, FAQ+CTA."""
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/"), (name, url)]
    sub = hero_sub or f"Chauffagiste et CVCS dans {region}. Appelez le {PHONE_DISP} pour un devis ou un dépannage."
    hero = page_hero(
        "Zone d'intervention",
        h1,
        sub,
        primary_href=f"tel:{PHONE}",
        primary_label=f"Appeler · {PHONE_DISP}",
        primary_class="btn-urgence track-phone",
        secondary_href="/contact/#contact-form",
        secondary_label="Demander un devis",
        secondary_class="btn-brand btn-brand--on-dark track-devis",
        image=hero_image_for("zones"),
        image_alt=h1,
    )
    # FAQ ≤ 5, dédupliquée par question
    seen_q = set()
    faq_trim = []
    for q, a in faq:
        if q in seen_q:
            continue
        seen_q.add(q)
        faq_trim.append((q, a))
        if len(faq_trim) >= 5:
            break
    body = f"""
{hero}
{mobile_quick_bar(sticky=True)}
<section class="content-section zone-local" aria-labelledby="local-title">
  <div class="container prose-block">
    <h2 class="section-title" id="local-title">Interventions dans {region}</h2>
    {local_text}
    {zone_proof_quote()}
    <p class="geo-local-note">Siège à <strong>{ADDRESS_FULL}</strong> — équipe mobile. <a href="tel:{PHONE}" class="track-phone">Appelez le {PHONE_DISP}</a> pour vérifier la disponibilité à {name}.</p>
  </div>
</section>
{zone_action_paths(name)}
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head(f"FAQ — {name}")}
    {faq_html(faq_trim)}
  </div>
</section>
{cta_band(f"Un projet à {name} ?", f"Appelez le {PHONE_DISP} ou décrivez votre besoin par WhatsApp / formulaire.", phone_first=True)}"""
    graph = base_graph(title, desc, SITE + url, crumbs, faq_trim)
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def svc_strip_card(slug, name, tag):
    return (
        f'<a class="svc-strip-card" data-svc="{slug}" href="/{slug}/">'
        f'{service_icon(slug, "card")}'
        f'<span class="svc-strip-card__title">{name}</span>'
        f'<span class="svc-strip-card__tag">{tag}</span>'
        f'<span class="svc-strip-card__arrow" aria-hidden="true">→</span></a>'
    )


def path_strip_html():
    """3 chemins clairs : Installation / Maintenance / Dépannage."""
    paths = [
        (
            "Installation",
            "Étude, pose et mise en service de vos systèmes CVCS.",
            "/contact/?need=installation#contact-form",
            "Demander un devis",
            "path-card--install",
        ),
        (
            "Maintenance",
            "Entretien préventif pour fiabilité et conformité.",
            "/contact/?need=maintenance#contact-form",
            "Planifier un entretien",
            "path-card--maint",
        ),
        (
            "Dépannage",
            "Intervention rapide en cas de panne — appelez-nous.",
            f"tel:{PHONE}",
            f"Appeler · {PHONE_DISP}",
            "path-card--urgent",
        ),
    ]
    cards = []
    for title, lead, href, cta, mod in paths:
        track = "track-phone" if href.startswith("tel:") else "track-devis"
        cards.append(
            f'<a class="path-card {mod} {track}" href="{href}">'
            f'<span class="path-card__title">{title}</span>'
            f'<span class="path-card__lead">{lead}</span>'
            f'<span class="path-card__cta">{cta} →</span></a>'
        )
    return f"""<section class="path-strip" aria-label="Comment pouvons-nous vous aider ?">
  <div class="container">
    <div class="path-strip__head">
      <h2 class="section-title">Installation · Maintenance · Dépannage</h2>
      <p class="section-lead">Choisissez votre besoin — on vous oriente immédiatement.</p>
    </div>
    <div class="path-grid">{"".join(cards)}</div>
    <p class="path-strip__more"><a href="/prestations/" class="text-link">Toutes les prestations</a></p>
  </div>
</section>"""


def smart_contact_form_html():
    """Formulaire multi-étapes : bâtiment → besoin → urgence → coordonnées."""
    return f"""<form class="contact-form contact-form--smart track-form" action="{FORM_ENDPOINT or '#'}" method="post" data-form-endpoint="{FORM_ENDPOINT}" novalidate>
  <input type="hidden" name="_subject" value="{FORM_SUBJECT}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="text" name="_honey" class="form-honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="form-progress" role="group" aria-label="Progression du formulaire">
    <div class="form-progress__bar" data-form-progress style="--progress: 25%"></div>
    <ol class="form-progress__steps">
      <li class="is-active" data-step-label="1">Bâtiment</li>
      <li data-step-label="2">Besoin</li>
      <li data-step-label="3">Urgence</li>
      <li data-step-label="4">Contact</li>
    </ol>
  </div>

  <fieldset class="form-step is-active" data-step="1">
    <legend class="form-step__legend">Type de bâtiment</legend>
    <div class="form-choice-grid" role="radiogroup" aria-label="Type de bâtiment">
      <label class="form-choice"><input type="radio" name="building" value="Maison individuelle" required><span>Maison</span></label>
      <label class="form-choice"><input type="radio" name="building" value="Appartement"><span>Appartement</span></label>
      <label class="form-choice"><input type="radio" name="building" value="Immeuble"><span>Immeuble</span></label>
      <label class="form-choice"><input type="radio" name="building" value="Commerce / tertiaire"><span>Commerce / tertiaire</span></label>
      <label class="form-choice"><input type="radio" name="building" value="Autre"><span>Autre</span></label>
    </div>
    <div class="form-step__nav">
      <button type="button" class="btn btn-brand" data-form-next>Continuer</button>
    </div>
  </fieldset>

  <fieldset class="form-step" data-step="2" hidden>
    <legend class="form-step__legend">Type de besoin</legend>
    <div class="form-choice-grid" role="radiogroup" aria-label="Type de besoin">
      <label class="form-choice"><input type="radio" name="need" value="Devis installation" required><span>Installation</span></label>
      <label class="form-choice"><input type="radio" name="need" value="Maintenance / entretien"><span>Maintenance</span></label>
      <label class="form-choice"><input type="radio" name="need" value="Dépannage"><span>Dépannage</span></label>
      <label class="form-choice"><input type="radio" name="need" value="Sprinkler / incendie"><span>Sprinkler</span></label>
      <label class="form-choice"><input type="radio" name="need" value="Autre"><span>Autre</span></label>
    </div>
    <div class="form-step__nav">
      <button type="button" class="btn btn-secondary" data-form-back>Retour</button>
      <button type="button" class="btn btn-brand" data-form-next>Continuer</button>
    </div>
  </fieldset>

  <fieldset class="form-step" data-step="3" hidden>
    <legend class="form-step__legend">Est-ce urgent ?</legend>
    <div class="form-choice-grid form-choice-grid--2" role="radiogroup" aria-label="Urgence">
      <label class="form-choice form-choice--urgent"><input type="radio" name="urgency" value="Urgent" required><span>Oui — panne en cours</span></label>
      <label class="form-choice"><input type="radio" name="urgency" value="Non urgent"><span>Non — devis / planification</span></label>
    </div>
    <div class="form-urgent-cta" data-urgent-cta hidden>
      <p>Pour une panne en cours, appelez-nous directement :</p>
      <a href="tel:{PHONE}" class="btn btn-urgence track-phone">Appeler · {PHONE_DISP}</a>
      <a href="{WA}" class="btn btn-secondary track-whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>
    </div>
    <div class="form-step__nav">
      <button type="button" class="btn btn-secondary" data-form-back>Retour</button>
      <button type="button" class="btn btn-brand" data-form-next>Continuer</button>
    </div>
  </fieldset>

  <fieldset class="form-step" data-step="4" hidden>
    <legend class="form-step__legend">Vos coordonnées</legend>
    <div class="form-field"><label for="name">Nom</label><input id="name" name="name" type="text" required autocomplete="name" placeholder="Votre nom"></div>
    <div class="form-field"><label for="phone">Téléphone</label><input id="phone" name="phone" type="tel" required autocomplete="tel" placeholder="+41 79 …"></div>
    <div class="form-field"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email" placeholder="vous@exemple.ch"></div>
    <div class="form-field"><label for="canton">Canton / Commune</label><input id="canton" name="canton" type="text" required placeholder="Ex. Lausanne, Vaud"></div>
    <div class="form-field"><label for="message">Message <span class="form-optional">(optionnel)</span></label><textarea id="message" name="message" placeholder="Précisez le bâtiment, la panne ou le projet…"></textarea></div>
    <div class="form-step__nav">
      <button type="button" class="btn btn-secondary" data-form-back>Retour</button>
      <button type="submit" class="btn btn-brand track-form-submit">Envoyer la demande</button>
    </div>
  </fieldset>

  <p class="form-feedback" role="status" aria-live="polite" hidden></p>
</form>"""


def build_home():
    cases_html = case_studies_grid(CASE_STUDIES, limit=4, heading="h3")
    faq = [
        ("Comment obtenir un devis ?", "Via le formulaire contact (quelques questions) ou par téléphone. Le devis est gratuit et sans engagement."),
        ("Intervenez-vous en dépannage ?", f"Oui, en {CVCS_PROSE} en Suisse romande. Appelez le {PHONE_DISP} pour une panne en cours. Horaires : {HOURS}."),
        ("Dans quelles zones intervenez-vous ?", f"Genève, Vaud, Lausanne, Nyon, Valais, Fribourg et alentours. Siège à <a href=\"/romont/\">{ADDRESS_LOCALITY}</a>."),
    ]
    body = f"""
<section class="hero hero--photo" aria-labelledby="hero-h1">
  <div class="hero-media">
    <img src="/assets/heroes/home.jpg" alt="Centrale sprinkler installée par Sopjani Tech Sàrl — chantier réel en Suisse romande" width="2000" height="1125" fetchpriority="high" decoding="async">
  </div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="container hero-inner">
    <div class="hero-content">
      <p class="hero-eyebrow">Suisse romande</p>
      <h1 id="hero-h1">Chauffage, ventilation, climatisation et sanitaire.</h1>
      <p class="hero-sub">Projets CVCS de l'étude à la réalisation — villas, immeubles et appels d'offres en Suisse romande.</p>
      <div class="hero-ctas">
        <a href="/contact/#contact-form" class="btn btn-brand btn-brand--on-dark track-devis">Demander un devis</a>
        <a href="tel:{PHONE}" class="btn btn-urgence track-phone">Dépannage urgent</a>
      </div>
      <ul class="hero-trust">
        <li>Devis gratuit</li>
        <li><a href="{GOOGLE_BUSINESS_URL}" class="track-google" target="_blank" rel="noopener noreferrer">Avis Google 5/5</a></li>
        <li>Normes suisses</li>
      </ul>
    </div>
  </div>
</section>

{path_strip_html()}

<section class="home-cases" aria-labelledby="cases-title">
  <div class="container">
    <div class="home-realisations__head">
      <h2 class="section-title" id="cases-title">Cas chantiers</h2>
      <a href="/realisations/#cas-chantiers" class="text-link">Toutes les réalisations</a>
    </div>
    {cases_html}
  </div>
</section>

{google_reviews_section()}

<section class="about-split about-split--compact" aria-labelledby="about-title">
  <div class="container about-split-grid">
    <div class="about-copy">
      <span class="label label--brand">À propos</span>
      <h2 class="section-title" id="about-title">Un interlocuteur, du devis à la mise en service.</h2>
      <p>Étude, installation et suivi avec devis clairs et respect des normes suisses (SIA, SUVA, AEAI).</p>
      <p>Siège à <a href="/romont/">{ADDRESS_FULL}</a> — équipe mobile en Suisse romande.</p>
      <p class="about-copy-links">
        <a href="/a-propos/" class="text-link">Présentation</a>
        <a href="/contact/#contact-form" class="text-link track-devis">Demander un devis</a>
      </p>
    </div>
    <div class="about-photo-duo" aria-label="Équipe Sopjani Tech">
      <figure class="about-photo">
        <img src="/assets/equipe/equipe-soudure-logo-dos.jpg" alt="Technicien Sopjani Tech Sàrl en intervention" width="900" height="900" loading="lazy" decoding="async">
      </figure>
      <figure class="about-photo">
        <img src="/assets/equipe/equipe-formation-logo-dos.jpg" alt="Collaborateur Sopjani Tech Sàrl en formation" width="775" height="1024" loading="lazy" decoding="async">
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
{cta_band()}"""
    home_title = PAGE_TITLES["home"]
    home_desc = META_DESCRIPTIONS["home"]
    graph = base_graph(home_title, home_desc, SITE + "/", faq=faq)
    write_page(["index.html"], page_shell(home_title, home_desc, SITE + "/", graph, body))



def build_prestations():
    faq = [
        ("Quelles prestations CVCS proposez-vous ?", f"{CVCS_GROUP}, ainsi que dépannage SAV et sprinkler en sous-traitance."),
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
{svc_reassure_band()}
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
        ("Avez-vous une agence dans chaque canton ?", f"Non. Nos interventions sont assurées par une équipe mobile depuis notre <a href=\"/romont/\">siège à {ADDRESS_LOCALITY}</a>."),
    ]
    cards = "".join(f'<a class="hub-card" href="/{z}/"><h3>{n}</h3><p>Interventions CVCS dans {r}</p><span class="link-arrow">Voir la zone →</span></a>' for z, n, r in ZONES)
    hero = page_hero(
        "Géographie",
        "Nos zones d'intervention en Suisse romande",
        f"Choisissez votre secteur — ou appelez le {PHONE_DISP} pour vérifier la disponibilité.",
        primary_href=f"tel:{PHONE}",
        primary_label=f"Appeler · {PHONE_DISP}",
        primary_class="btn-urgence track-phone",
        secondary_href="/contact/#contact-form",
        secondary_label="Demander un devis",
        secondary_class="btn-brand btn-brand--on-dark track-devis",
        image=hero_image_for("zones-intervention"),
    )
    body = f"""
{hero}
{mobile_quick_bar(sticky=True)}
<section class="content-section zone-hub">
  <div class="container">
    <p class="section-lead zone-hub__lead">Basés à {ADDRESS_LOCALITY}, équipe mobile en Suisse romande — pas d'agences locales dans chaque canton.</p>
    <div class="hub-grid">{cards}</div>
  </div>
</section>
<section class="faq content-section alt" aria-labelledby="faq-title">
  <div class="container">
    {faq_section_head()}
    {faq_html(faq)}
  </div>
</section>
{cta_band("Votre commune n'est pas listée ?", f"Appelez le {PHONE_DISP} pour vérifier la faisabilité d'une intervention.", phone_first=True)}"""
    crumbs = [("Accueil", "/"), ("Zones d'intervention", "/zones-intervention/")]
    zones_title = PAGE_TITLES["zones-intervention"]
    zones_desc = META_DESCRIPTIONS["zones-intervention"]
    graph = base_graph(zones_title, zones_desc, SITE + "/zones-intervention/", crumbs, faq)
    write_page(["zones-intervention", "index.html"], page_shell(zones_title, zones_desc, SITE + "/zones-intervention/", graph, body, crumbs))


def build_about():
    faq = [
        (f"Où est située {COMPANY_NAME} ?", f"Notre siège est à <a href=\"/romont/\">{ADDRESS_FULL}</a>. Nous intervenons en Suisse romande pour le {CVCS_PROSE} et le dépannage CVCS."),
        ("Quels services propose l'entreprise ?", f"{CVCS_GROUP}, ainsi que dépannage SAV et sprinkler en sous-traitance."),
        (f"Comment contacter {COMPANY_NAME} ?", f"Par téléphone au {PHONE_DISP}, par email ({EMAIL}) ou via WhatsApp. Horaires : {HOURS}."),
    ]
    hero = page_hero(
        "Entreprise",
        f"À propos de {COMPANY_NAME}",
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
        <p>Basés à <a href="/romont/"><strong>{ADDRESS_FULL}</strong></a>, nous couvrons le {CVCS_PROSE}, le dépannage SAV et le sprinkler / protection incendie. Approche simple : comprendre le besoin, proposer une solution adaptée, intervenir avec sérieux.</p>
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
    <header class="about-engagements-head">
      <span class="label">Engagements</span>
      <div class="rule"></div>
      <h2 class="section-title" id="engagements-title">Ce que vous pouvez attendre</h2>
    </header>
    <p class="section-lead about-engagements-lead">Des échanges nets, un interlocuteur unique et une entreprise enregistrée en Suisse.</p>
    <ul class="check-list about-check">
      <li>Devis gratuit et sans engagement</li>
      <li>Un interlocuteur unique, du premier contact à la fin des travaux</li>
      <li>Échanges clairs sur la nature et le coût avant intervention</li>
      <li>Sàrl inscrite au registre du commerce (UID {COMPANY_UID} · <a href="https://www.zefix.ch" target="_blank" rel="noopener noreferrer">Zefix</a>)</li>
    </ul>
    <p class="about-google"><a href="{GOOGLE_BUSINESS_URL}" class="text-link track-google" target="_blank" rel="noopener noreferrer">Fiche Google et avis</a></p>
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
{google_reviews_section(heading_id="about-avis-title")}
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
    graph = base_graph(
        about_title,
        about_desc,
        SITE + "/a-propos/",
        crumbs,
        faq,
        extra={"@type": "AboutPage", "name": "À propos", "url": SITE + "/a-propos/"},
    )
    write_page(["a-propos", "index.html"], page_shell(about_title, about_desc, SITE + "/a-propos/", graph, body, crumbs))


def build_contact():
    faq = [
        ("Comment nous joindre ?", f"Par téléphone ({PHONE_DISP}), email ({EMAIL}) ou WhatsApp."),
        ("Quelles informations fournir pour un devis ?", "Type de bâtiment, localisation (canton/commune), nature du besoin (installation, maintenance, dépannage) et urgence éventuelle."),
        ("Horaires de contact", HOURS + ". Pour un dépannage, contactez-nous par téléphone ou WhatsApp."),
        ("Qui appeler en cas de panne CVCS ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la panne et votre adresse."),
        ("Proposez-vous un devis gratuit ?", "Oui, le devis est gratuit et sans engagement. Décrivez votre projet via le formulaire ci-dessus ou par téléphone : nous confirmons la faisabilité et les prochaines étapes."),
    ]
    body = f"""
{urgence_band()}
{page_hero(
        "Contact",
        f"Contactez {COMPANY_NAME}",
        "Devis, maintenance ou dépannage : décrivez votre besoin et nous vous orienterons vers la solution adaptée.",
        image=hero_image_for("contact"),
    )}
<section class="contact content-section" aria-labelledby="contact-form-title">
  <div class="container contact-page">
    {mobile_quick_bar()}
    <div class="contact-inner">
      <div class="contact-form-section" id="contact-form">
        <h2 class="contact-block-title" id="contact-form-title">Formulaire de demande</h2>
        <p class="contact-block-lead">Quatre questions rapides — on vous recontacte avec la bonne orientation.</p>
        {smart_contact_form_html()}
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
{google_reviews_section(heading_id="contact-avis-title")}
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
    graph = base_graph(
        contact_title,
        contact_desc,
        SITE + "/contact/",
        faq=faq,
        extra={"@type": "ContactPage", "name": "Contact", "url": SITE + "/contact/"},
    )
    write_page(["contact", "index.html"], page_shell(contact_title, contact_desc, SITE + "/contact/", graph, body))


def _card_icon(kind):
    """Petite icône technique SVG (stroke) pour cartes prestations."""
    paths = {
        "boiler": '<path d="M8 2v3M16 2v3M6 8h12v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8z"/><path d="M10 12h4M10 16h4"/>',
        "radiator": '<path d="M5 8h14v10H5z"/><path d="M8 8v10M12 8v10M16 8v10M5 11h14"/>',
        "water": '<path d="M12 3c0 0-6 7-6 11a6 6 0 0 0 12 0c0-4-6-11-6-11z"/>',
        "noise": '<path d="M11 5 6 9H3v6h3l5 4V5z"/><path d="M15.5 8.5a4 4 0 0 1 0 7"/><path d="M18 6a7 7 0 0 1 0 12"/>',
        "gauge": '<circle cx="12" cy="12" r="8"/><path d="M12 12 16 8M12 8v1"/>',
        "pac": '<path d="M4 10h16v8H4z"/><path d="M8 10V7a4 4 0 0 1 8 0v3M8 18v2M16 18v2"/>',
        "study": '<path d="M4 19V5a1 1 0 0 1 1-1h10l5 5v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z"/><path d="M14 4v5h5"/>',
        "install": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94z"/>',
        "maintain": '<path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/><circle cx="12" cy="12" r="3"/>',
        "balance": '<path d="M12 3v18M5 8h14M8 8l-3 8h6M16 8l-3 8h6"/>',
        "repair": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94z"/>',
        "fan": '<path d="M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0"/><path d="M12 4c2 2 2 5 0 6M12 20c-2-2-2-5 0-6M4 12c2-2 5-2 6 0M20 12c-2 2-5 2-6 0"/>',
        "duct": '<path d="M3 8h18v4H3zM3 14h10v4H3zM15 14h6v4h-6z"/>',
        "filter": '<path d="M4 5h16l-5 7v6l-6 2v-8L4 5z"/>',
        "humidity": '<path d="M12 3c0 0-5 6-5 10a5 5 0 0 0 10 0c0-4-5-10-5-10z"/><path d="M9 14h6"/>',
        "snow": '<path d="M12 2v20M4.9 6.5l14.2 11M4.9 17.5l14.2-11"/>',
        "leak": '<path d="M7 3v8a5 5 0 0 0 10 0V3"/><path d="M12 16v5M9 19h6"/>',
        "flush": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
        "pipe": '<path d="M4 10h16v4H4zM8 6v4M16 14v4"/>',
        "fire": '<path d="M12 22c4-2 6-5 6-9 0-4-3-6-3-6s1 3-1 5c0 0-1-4-5-7 0 0-1 5-3 7-2 2-2 5 0 7 1 1 3 2 6 3z"/>',
        "valve": '<path d="M12 3v6M8 9h8l2 12H6L8 9z"/><circle cx="12" cy="6" r="2"/>',
        "coord": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        "alert": '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
    }
    d = paths.get(kind, paths["boiler"])
    return f'<span class="svc-card__icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{d}</svg></span>'


def svc_reassure_band():
    """Bandeau stats immédiat sous le hero — réassurance compacte."""
    return """<section class="svc-reassure" aria-label="Preuves de confiance">
  <div class="container svc-reassure__grid">
    <div class="svc-reassure__item"><strong>100+</strong><span>Interventions réalisées</span></div>
    <div class="svc-reassure__item"><strong>80+</strong><span>Clients satisfaits</span></div>
    <div class="svc-reassure__item"><strong>10+</strong><span>Années d'expérience</span></div>
  </div>
</section>"""


RELATED_SERVICE_BLURBS = {
    "chauffage": "Installation, entretien et dépannage",
    "ventilation": "VMC et qualité de l'air",
    "climatisation": "Confort été et PAC air-air",
    "sanitaire": "Réseaux eau et dépannage",
    "depannage-sav": "Remise en service rapide",
    "sprinkler-protection-incendie": "Réseaux sprinkler",
}

DEFAULT_PROCESS_STEPS = [
    "Prise de contact et description du besoin",
    "Visite ou diagnostic sur place si nécessaire",
    "Proposition technique et devis détaillé",
    "Réalisation des travaux et mise en service",
    "Suivi et maintenance si souhaitée",
]

DEFAULT_BUILDINGS_NOTE = (
    "Pour villas, immeubles, PPE, commerces, bureaux, hôtels, sites industriels "
    "et bâtiments publics, selon faisabilité technique."
)


def _premium_cards(items, service_class=False):
    cls = "svc-card svc-card--service" if service_class else "svc-card"
    return "".join(
        f'<article class="{cls}"><h3 class="svc-card__title">{_card_icon(ic)}{t}</h3>'
        f'<p class="svc-card__text">{tx}</p></article>'
        for ic, t, tx in items
    )


def _premium_timeline(steps):
    return "".join(
        f'<li class="svc-timeline__item"><span class="svc-timeline__num" aria-hidden="true">{i:02d}</span>'
        f'<span class="svc-timeline__text">{s}</span></li>'
        for i, s in enumerate(steps, 1)
    )


def _premium_gallery_block(slug, gallery_cat):
    gallery_imgs = carousel_images_for_service(slug, gallery_cat=gallery_cat, limit=6)
    if not gallery_imgs:
        return (
            '<p class="section-lead">Galerie en cours de mise à jour — '
            '<a href="/realisations/" class="text-link">toutes les réalisations</a></p>'
        ), gallery_imgs
    featured, rest = gallery_imgs[0], gallery_imgs[1:5]
    fn, w, h, alt, cap = featured
    featured_html = f"""<figure class="svc-gallery__featured">
  <img src="/assets/realisations/{fn}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">
  <figcaption>{cap}</figcaption>
</figure>"""
    rest_html = "".join(
        f'<figure class="svc-gallery__item"><img src="/assets/realisations/{fn}" alt="{alt}" '
        f'width="{w}" height="{h}" loading="lazy" decoding="async"><figcaption>{cap}</figcaption></figure>'
        for fn, w, h, alt, cap in rest
    )
    block = f"""<div class="svc-gallery">{featured_html}<div class="svc-gallery__grid">{rest_html}</div></div>
<p class="svc-section__link"><a href="/realisations/" class="text-link">Toutes les réalisations</a></p>"""
    return block, gallery_imgs


def _premium_equip_visual(gallery_imgs):
    if gallery_imgs:
        fn, w, h, alt, cap = gallery_imgs[min(1, len(gallery_imgs) - 1)]
        return f"""<figure class="svc-equip__visual">
  <img src="/assets/realisations/{fn}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">
</figure>"""
    return """<aside class="svc-equip__panel" aria-label="Cadre suisse">
  <p class="svc-equip__panel-label">Cadre suisse</p>
  <ul class="svc-equip__panel-list"><li>SIA</li><li>suva</li><li>AEAI</li></ul>
  <p class="svc-equip__panel-note">Professionnels qualifiés · Assurance RC</p>
</aside>"""


def write_premium_service_page(cfg):
    """Page prestation — composition premium post-hero (même structure pour tous les services)."""
    slug = cfg["slug"]
    name = cfg["name"]
    title = PAGE_TITLES[slug]
    desc = META_DESCRIPTIONS[slug]
    url = f"/{slug}/"
    crumbs = [("Accueil", "/"), ("Prestations", "/prestations/"), (name, url)]
    zone_slugs = cfg["zone_slugs"]
    related_svc = cfg["related_svc"]
    faq = cfg["faq"]
    process_steps = cfg.get("process_steps", DEFAULT_PROCESS_STEPS)
    buildings_note = cfg.get("buildings_note", DEFAULT_BUILDINGS_NOTE)
    gallery_cat = cfg.get("gallery_cat")
    show_urgence = cfg.get("show_urgence", False)
    reg_items = cfg.get("regulatory", [])
    show_gallery = cfg.get("show_gallery", True)

    hero = page_hero(
        "Prestation",
        cfg["h1"],
        cfg["intro"],
        icon_html=service_icon(slug, "hero"),
        image=hero_image_for(slug),
        image_alt=cfg["h1"],
    )

    problem_cards = _premium_cards(cfg["problems"])
    service_cards = _premium_cards(cfg["services"], service_class=True)
    timeline = _premium_timeline(process_steps)

    if show_gallery:
        gallery_block, gallery_imgs = _premium_gallery_block(slug, gallery_cat)
        gallery_section = f"""
<section class="content-section svc-premium svc-premium--alt magnetic-section" id="realisations" aria-labelledby="real-title">
  <div class="container">
    <div class="svc-premium__head">
      <h2 class="section-title" id="real-title">{cfg["gallery_title"]}</h2>
      <p class="section-lead">{cfg["gallery_lead"]}</p>
    </div>
    {gallery_block}
  </div>
</section>"""
    else:
        # Pas de galerie : ne pas emprunter d'images d'autres prestations
        gallery_imgs = []
        gallery_section = ""

    equip_list = "".join(f"<li>{x}</li>" for x in cfg["equip"])
    equip_visual = _premium_equip_visual(gallery_imgs)

    if reg_items:
        accordion_inner = "".join(
            f"""<details class="details-item" name="{slug}-reg">
  <summary class="details-summary"><span class="faq-q-text">{t}</span><span class="faq-icon" aria-hidden="true"></span></summary>
  <div class="details-panel"><p>{tx}</p></div>
</details>"""
            for t, tx in reg_items
        )
        accordion = f'<div class="details-accordion"><div class="details-accordion__list">{accordion_inner}</div></div>'
        reg_section = f"""
<section class="content-section svc-premium svc-premium--alt" id="reglementaire" aria-labelledby="reg-title">
  <div class="container svc-premium__narrow">
    <div class="svc-premium__head">
      <h2 class="section-title" id="reg-title">{cfg["reg_title"]}</h2>
      <p class="section-lead">{cfg["reg_lead"]}</p>
    </div>
    {accordion}
  </div>
</section>"""
    else:
        reg_section = ""

    zone_chips = "".join(
        f'<a class="zone-pill" href="/{z}/">{n}</a>'
        for z, n, _ in ZONES if z in zone_slugs
    )

    related_cards = "".join(
        f'<a class="svc-related-card" href="/{s}/"><h3>{n}</h3><p>{RELATED_SERVICE_BLURBS.get(s, "")}</p></a>'
        for s, n, _ in SERVICES if s in related_svc
    )

    urgence = urgence_band() if show_urgence else ""
    # Alternance : problems plain → services alt → process plain → [gallery alt] → expertise → [reg alt] → zones → related → faq
    expertise_alt = "" if show_gallery else " svc-premium--alt"
    if show_gallery:
        zones_alt, related_alt, faq_alt = ("", " svc-premium--alt", "")
    else:
        zones_alt = "" if reg_section else " svc-premium--alt"
        related_alt = " svc-premium--alt" if reg_section else ""
        faq_alt = "" if related_alt else " svc-premium--alt"

    body = f"""
{hero}
{urgence}
{svc_reassure_band()}

<section class="content-section svc-premium" id="problems" aria-labelledby="problems-title" data-svc="{slug}">
  <div class="container">
    <div class="svc-premium__head">
      <h2 class="section-title" id="problems-title">{cfg["problems_title"]}</h2>
      <p class="section-lead">{cfg["problems_lead"]}</p>
    </div>
    <div class="svc-card-grid">{problem_cards}</div>
  </div>
</section>

<section class="content-section svc-premium svc-premium--alt" id="services" aria-labelledby="services-title" data-svc="{slug}">
  <div class="container">
    <div class="svc-premium__head">
      <h2 class="section-title" id="services-title">{cfg["services_title"]}</h2>
      <p class="section-lead">{cfg["services_lead"]}</p>
    </div>
    <div class="svc-card-grid">{service_cards}</div>
    <p class="svc-premium__note">{buildings_note}</p>
    <p class="svc-premium__cta"><a href="/contact/" class="btn btn-secondary track-devis">Demander un devis</a></p>
  </div>
</section>

<section class="content-section svc-premium" id="process" aria-labelledby="process-title">
  <div class="container">
    <div class="svc-premium__head svc-premium__head--center">
      <h2 class="section-title" id="process-title">{cfg.get("process_title", "Une intervention claire, de A à Z")}</h2>
    </div>
    <ol class="svc-timeline">{timeline}</ol>
  </div>
</section>

{gallery_section}

<section class="content-section svc-premium{expertise_alt}" id="expertise" aria-labelledby="expertise-title">
  <div class="container svc-equip">
    <div class="svc-equip__copy">
      <h2 class="section-title" id="expertise-title">{cfg["expertise_title"]}</h2>
      <p class="section-lead">{cfg["expertise_lead"]}</p>
      <ul class="svc-equip__list">{equip_list}</ul>
    </div>
    {equip_visual}
  </div>
</section>

{reg_section}

<section class="content-section svc-premium{zones_alt}" id="zones" aria-labelledby="zones-title">
  <div class="container">
    <div class="svc-premium__head">
      <h2 class="section-title" id="zones-title">{cfg["zones_title"]}</h2>
      <p class="section-lead">{cfg["zones_lead"]}</p>
    </div>
    <div class="zone-links">{zone_chips}</div>
    <p class="svc-section__link"><a href="/zones-intervention/" class="text-link">Toutes les zones</a></p>
  </div>
</section>

<section class="content-section svc-premium{related_alt}" id="related" aria-labelledby="related-title">
  <div class="container">
    <div class="svc-premium__head">
      <h2 class="section-title" id="related-title">Nos autres services</h2>
    </div>
    <div class="svc-related-grid">{related_cards}</div>
  </div>
</section>

<section class="faq content-section svc-premium{faq_alt}" id="faq" aria-labelledby="faq-title">
  <div class="container svc-premium__narrow">
    <div class="svc-premium__head">
      <h2 class="section-title" id="faq-title">Questions fréquentes</h2>
    </div>
    {faq_html(faq, group_name=f"faq-{slug}")}
  </div>
</section>

{norms_bar()}
{cta_band(cfg.get("cta_title", "Besoin d'un devis ou d'un dépannage ?"), cfg.get("cta_text", "Décrivez-nous votre besoin. Nous vous répondrons dans les meilleurs délais."))}
"""

    service_schema = {
        "@type": "Service",
        "name": name,
        "serviceType": name,
        "provider": {"@id": f"{SITE}/#organization"},
        "areaServed": service_area_served_schema(zone_slugs),
        "description": desc,
        "url": SITE + url,
    }
    graph = base_graph(title, desc, SITE + url, crumbs, faq, service_schema)
    write_page([slug, "index.html"], page_shell(title, desc, SITE + url, graph, body, crumbs))


def _premium_service_configs():
    """Contenus premium pour toutes les pages prestations."""
    return [
        {
            "slug": "chauffage",
            "name": "Chauffage",
            "h1": "Chauffagiste en Suisse romande : installation, entretien et dépannage",
            "intro": "Installation, entretien et dépannage de chauffage — de l'étude à la maintenance — pour le confort thermique et la fiabilité de vos installations.",
            "problems_title": "Un problème de chauffage ?",
            "problems_lead": "Nous intervenons pour diagnostiquer, réparer, entretenir ou remplacer votre installation de chauffage en Suisse romande.",
            "problems": [
                ("boiler", "Chaudière qui ne démarre plus", "Panne au démarrage ou arrêt en cours de cycle."),
                ("radiator", "Radiateurs froids ou déséquilibrés", "Circuit mal équilibré ou émetteurs froids."),
                ("water", "Boiler sans eau chaude", "Production d'ECS insuffisante ou à l'arrêt."),
                ("noise", "Bruit anormal au démarrage", "Bruit de brûleur, circulateur ou chaudière."),
                ("gauge", "Consommation en hausse", "Mazout ou gaz — rendement à vérifier."),
                ("pac", "Chaudière vétuste à remplacer", "Passage possible vers une pompe à chaleur."),
            ],
            "services_title": "Installation, entretien et dépannage",
            "services_lead": "Une prise en charge complète, de l'étude technique à la mise en service.",
            "services": [
                ("study", "Étude et dimensionnement thermique", "Calcul de puissance et choix des émetteurs."),
                ("pac", "Installation de pompe à chaleur", "Air/eau ou sol/eau, selon le bâtiment."),
                ("install", "Installation ou remplacement de chaudière", "Gaz, mazout ou bois / pellets."),
                ("water", "Entretien et détartrage de boiler", "Entretien pour préserver le rendement."),
                ("balance", "Désembouage et équilibrage", "Circuits nettoyés et débits réglés."),
                ("repair", "Dépannage et remise en service", "Diagnostic et réparation sur site."),
            ],
            "gallery_cat": "chauffage",
            "gallery_title": "Nos réalisations en chauffage",
            "gallery_lead": f"Découvrez quelques interventions réalisées par {COMPANY_NAME} en Suisse romande.",
            "expertise_title": "Des solutions adaptées à votre installation",
            "expertise_lead": "Nous intervenons sur les principaux générateurs de chaleur utilisés en Suisse romande.",
            "equip": [
                "Pompes à chaleur air/eau",
                "Pompes à chaleur sol/eau",
                "Chaudières à mazout",
                "Chaudières à gaz",
                "Chaudières à bois et pellets",
            ],
            "reg_title": "Subventions et exigences techniques",
            "reg_lead": "Nous pouvons vous orienter selon votre projet et votre canton.",
            "regulatory": [
                ("Subventions pour le remplacement par une pompe à chaleur",
                 "Le remplacement d'une chaudière à mazout ou à gaz par une pompe à chaleur peut être subventionné dans le cadre du Programme Bâtiments, avec un barème propre à chaque canton (Genève, Vaud, Valais, Fribourg, Neuchâtel). Les conditions évoluent chaque année : vérifiez les montants en vigueur avant le début des travaux."),
                ("Contrôle de combustion et exigences OPair",
                 "Le contrôle périodique officiel des installations à combustion reste du ressort du maître ramoneur agréé de votre secteur, selon l'ordonnance fédérale sur la protection de l'air (OPair), tous les 2 à 4 ans selon le combustible. Nous intervenons en complément pour l'entretien, le réglage du brûleur et la remise en conformité suite à un contrôle."),
            ],
            "zones_title": "Chauffagiste en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient dans plusieurs cantons et villes de Suisse romande.",
            "zone_slugs": ["geneve", "lausanne", "nyon", "vaud", "valais", "fribourg", "neuchatel"],
            "related_svc": ["ventilation", "climatisation", "sanitaire", "depannage-sav"],
            "faq": [
                ("Qui appeler pour un chauffagiste à Nyon ou Lausanne ?", f"{COMPANY_NAME} intervient comme chauffagiste à Nyon, Lausanne et dans toute la Suisse romande. Appelez le {PHONE_DISP} ou consultez nos pages zones Nyon et Lausanne."),
                ("Intervenez-vous en dépannage chauffage ?", "Oui, nous intervenons sur chaudières, pompes à chaleur et radiateurs : absence de chauffage, bruit anormal, fuite ou baisse de rendement. Appelez-nous directement pour une panne en cours."),
                ("Proposez-vous des contrats d'entretien ?", "Oui, un entretien régulier de votre chaudière ou pompe à chaleur (contrôle, réglage, détartrage du boiler) permet de limiter les pannes. Contactez-nous pour une fréquence adaptée."),
                ("Combien coûte un devis chauffage ?", "Le devis est gratuit. Il dépend du type d'installation, de la surface et de l'état de l'existant."),
                ("Qui effectue le contrôle officiel de combustion ?", "Le contrôle périodique OPair (tous les 2 à 4 ans selon le combustible) est réalisé par le maître ramoneur agréé de votre secteur. Nous intervenons en complément pour l'entretien, le réglage du brûleur et la remise en conformité."),
                ("Une pompe à chaleur peut-elle être subventionnée ?", "Oui, sous conditions, dans le cadre du Programme Bâtiments (leprogrammebatiments.ch), avec un barème propre à chaque canton. Contactez-nous pour évaluer votre projet."),
                ("Dans quelles zones intervenez-vous ?", f"Depuis {ADDRESS_LOCALITY}, nous intervenons notamment à Genève, Vaud (Nyon, Lausanne), Valais, Fribourg et Neuchâtel. Vérifiez la disponibilité via notre page zones."),
            ],
        },
        {
            "slug": "ventilation",
            "name": "Ventilation",
            "h1": "Entreprise de ventilation en Suisse romande",
            "intro": "Entreprise de ventilation pour particuliers et professionnels : installation VMC, entretien des gaines, dépannage et urgence — Nyon, Fribourg, Valais, Vaud et Genève.",
            "problems_title": "Un problème de ventilation ?",
            "problems_lead": "Nous diagnostiquons et intervenons sur les VMC et réseaux d'air en Suisse romande.",
            "problems": [
                ("noise", "VMC bruyante ou peu performante", "Débit insuffisant ou nuisance sonore."),
                ("humidity", "Condensation et humidité", "Renouvellement d'air insuffisant."),
                ("filter", "Filtres encrassés", "Perte de débit et surconsommation."),
                ("duct", "Gaines mal isolées ou obstruées", "Réseau à contrôler ou réhabiliter."),
                ("fan", "Moteur ou caisson en panne", "Arrêt partiel ou total de la VMC."),
                ("balance", "Mise en conformité locale", "Local technique, parking ou cuisine pro."),
            ],
            "services_title": "Installation, entretien et réhabilitation",
            "services_lead": "De l'installation neuve au nettoyage des réseaux existants.",
            "services": [
                ("install", "Installation VMC simple ou double flux", "Avec récupération de chaleur si adapté."),
                ("duct", "Nettoyage et désinfection de gaines", "Bouches et réseaux d'extraction."),
                ("filter", "Remplacement filtres, moteurs, caissons", "Pièces et entretien courant."),
                ("balance", "Réglage et équilibrage des débits", "Confort et efficacité énergétique."),
                ("fan", "Ventilation locaux techniques", "Parkings et cuisines professionnelles."),
                ("repair", "Réhabilitation de réseaux existants", "Remise à niveau d'installations anciennes."),
            ],
            "gallery_cat": "ventilation",
            "gallery_title": "Nos réalisations en ventilation",
            "gallery_lead": f"Quelques interventions VMC et traitement de l'air réalisées par {COMPANY_NAME}.",
            "expertise_title": "Des systèmes adaptés à votre bâtiment",
            "expertise_lead": "Nous intervenons sur les principales architectures de ventilation en Suisse romande.",
            "equip": [
                "VMC simple flux",
                "VMC double flux avec récupération de chaleur",
                "Ventilation de locaux techniques",
                "Ventilation de parkings",
                "Cuisines professionnelles",
            ],
            "reg_title": "Exigences techniques et entretien",
            "reg_lead": "Qualité de l'air, étanchéité et maintenance des réseaux.",
            "regulatory": [
                ("Bâtiments Minergie et étanchéité à l'air",
                 "Les constructions récentes ou labellisées Minergie reposent sur une bonne étanchéité à l'air et nécessitent une ventilation mécanique contrôlée correctement dimensionnée et entretenue, pour garantir la qualité de l'air intérieur et éviter les problèmes d'humidité."),
                ("Entretien et nettoyage des réseaux",
                 "Un nettoyage périodique des gaines, bouches et filtres permet de préserver le débit d'air prévu à l'installation et d'éviter la surconsommation électrique des moteurs encrassés."),
            ],
            "zones_title": "Entreprise de ventilation en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient notamment à Nyon, Fribourg, en Valais, à Genève, Lausanne et dans le canton de Vaud.",
            "zone_slugs": ["nyon", "fribourg", "valais", "geneve", "lausanne", "vaud"],
            "related_svc": ["chauffage", "climatisation", "sanitaire", "depannage-sav"],
            "faq": [
                ("Quelle entreprise de ventilation (ventiliste) contacter en Suisse romande ?", f"{COMPANY_NAME} intervient pour l'installation, la maintenance et le dépannage de ventilation à Nyon, Fribourg, Valais, Vaud et Genève."),
                ("Intervenez-vous en urgence pour une panne VMC ?", f"Oui — urgence ventilation : appelez le {PHONE_DISP}. Nous évaluons la disponibilité selon le secteur et la nature de la panne."),
                ("Réalisez-vous des travaux de rénovation de ventilation ?", "Oui, nous rénovons les VMC existantes : remplacement de moteurs, filtres et gaines, ou passage à une VMC double flux avec récupération de chaleur. Contactez-nous avec le type de bâtiment et l'état de l'installation actuelle."),
                ("Comment obtenir un devis ventilation ?", "Contactez-nous avec le type de bâtiment, la surface et l'état des installations existantes."),
            ],
        },
        {
            "slug": "climatisation",
            "name": "Climatisation",
            "h1": "Climatisation à Nyon, Lausanne et Genève : étude et installation",
            "intro": "Besoin d'une climatisation à Nyon ou ailleurs en Suisse romande ? Nous réalisons l'étude et l'installation de systèmes adaptés aux particuliers et aux professionnels — split, multi-split et pompes à chaleur air-air.",
            "problems_title": "Un problème de climatisation ?",
            "problems_lead": "Diagnostic, entretien et installation de climatisations en Suisse romande.",
            "problems": [
                ("snow", "Climatiseur qui ne refroidit plus", "Perte de froid ou arrêt de production."),
                ("noise", "Unité extérieure bruyante ou givrée", "Fonctionnement anormal du groupe."),
                ("leak", "Fuite de gaz réfrigérant", "Circuit frigorifique à contrôler."),
                ("balance", "Mauvaise répartition du froid", "Pièces trop chaudes ou trop froides."),
                ("pac", "Besoin d'une PAC air-air", "Appoint chaud/froid réversible."),
                ("filter", "Filtres et entretien à faire", "Rendement et qualité d'air à préserver."),
            ],
            "services_title": "Étude, installation et entretien",
            "services_lead": "Du dimensionnement au dépannage, pour le confort d'été et d'hiver.",
            "services": [
                ("study", "Dimensionnement selon les pièces", "Volume, exposition et besoins de confort."),
                ("install", "Installation split et multi-split", "Pose soignée et mise en service."),
                ("pac", "PAC air-air réversibles", "Chauffage et rafraîchissement."),
                ("gauge", "Contrôle et recharge de fluide", "Circuit frigorifique conforme."),
                ("maintain", "Entretien filtres et unités", "Contrôle de performance annuel."),
                ("repair", "Dépannage climatisation", "Perte de froid, fuite, unité à l'arrêt."),
            ],
            "show_gallery": False,
            "gallery_cat": None,
            "expertise_title": "Des solutions adaptées à votre usage",
            "expertise_lead": "Nous intervenons sur climatisations split, multi-split et PAC air-air — notamment à Nyon, Lausanne et Genève.",
            "equip": [
                "Climatiseurs split",
                "Systèmes multi-split",
                "Pompes à chaleur air-air réversibles",
                "Unités murales et consoles",
                "Groupes extérieurs",
            ],
            "reg_title": "Cadre technique et entretien",
            "reg_lead": "Fluides frigorigènes et bonnes pratiques d'entretien.",
            "regulatory": [
                ("Fluides frigorigènes — cadre suisse",
                 "La manipulation des fluides réfrigérants est strictement encadrée par la législation suisse sur la protection de l'environnement. Toute intervention sur le circuit frigorifique (recharge, détection de fuite) est réalisée avec le soin et les précautions requises par ce cadre."),
                ("Entretien recommandé",
                 "Un contrôle annuel (nettoyage des filtres et de l'unité extérieure, vérification du bon fonctionnement) permet de préserver le rendement énergétique de l'installation et sa durée de vie."),
            ],
            "zones_title": "Climatisation en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient notamment à Nyon, Lausanne, Genève, en Valais et à Fribourg.",
            "zone_slugs": ["geneve", "nyon", "lausanne", "valais", "vaud", "fribourg"],
            "related_svc": ["chauffage", "ventilation", "sanitaire", "depannage-sav"],
            "faq": [
                ("Installez-vous la climatisation à Nyon ?", "Oui. Nous étudions et installons la climatisation (split, multi-split, PAC air-air) à Nyon et dans les communes voisines (Gland, Rolle, Coppet, Prangins…). Consultez aussi notre page zone Nyon."),
                ("Quels types de bâtiments équipez-vous ?", "Résidentiel et tertiaire selon faisabilité — villas, appartements, bureaux et commerces."),
                ("Intervenez-vous en dépannage climatisation ?", "Oui, nous diagnostiquons et réparons les pannes courantes : perte de froid, fuite de fluide réfrigérant, unité extérieure givrée ou bruyante. Contactez-nous avec le modèle de l'appareil si possible."),
                ("Installez-vous la climatisation près de chez moi ?", f"Nous intervenons en Suisse romande depuis {ADDRESS_LOCALITY}, notamment à Nyon, Lausanne, Genève et en Valais. Contactez-nous avec votre commune."),
                ("Comment obtenir un devis climatisation ?", "Via notre page contact : précisez le type de bâtiment, la surface et vos besoins de confort."),
            ],
        },
        {
            "slug": "sanitaire",
            "name": "Sanitaire",
            "h1": "Installations et dépannages sanitaires en Suisse romande",
            "intro": f"{COMPANY_NAME} intervient également pour vos installations et dépannages sanitaires en Suisse romande.",
            "problems_title": "Un problème sanitaire ?",
            "problems_lead": "Fuites, évacuations, chauffe-eau et rénovations — nous intervenons rapidement.",
            "problems": [
                ("leak", "Fuite sous évier ou en chape", "Recherche et réparation de conduites."),
                ("flush", "WC qui fuit ou se bouche", "Remise en service des appareils."),
                ("water", "Chauffe-eau en panne ou qui fuit", "Remplacement ou entretien."),
                ("gauge", "Pression d'eau insuffisante", "Diagnostic du réseau."),
                ("pipe", "Canalisation bouchée", "Débouchage des évacuations."),
                ("study", "Rénovation de salle de bains", "Réseaux et appareils sanitaires."),
            ],
            "services_title": "Installation, dépannage et rénovation",
            "services_lead": "De l'étude des réseaux à la remise en service.",
            "services": [
                ("study", "Étude et dimensionnement", "Installations sanitaires adaptées."),
                ("pipe", "Réseaux EF / EC / évacuation", "Pose et remplacement de conduites."),
                ("install", "Appareils et robinetterie", "Pose et remplacement soignés."),
                ("water", "Chauffe-eau et boilers", "Installation et entretien."),
                ("leak", "Recherche de fuites", "Localisation et réparation."),
                ("repair", "SAV et dépannage", "Remise en service rapide."),
            ],
            "gallery_cat": "sanitaire",
            "gallery_title": "Nos réalisations sanitaires",
            "gallery_lead": f"Interventions sanitaires réalisées par {COMPANY_NAME} en Suisse romande.",
            "expertise_title": "Des réseaux adaptés à votre bâtiment",
            "expertise_lead": "Nous intervenons sur les réseaux eau froide et eau chaude, évacuations, robinetterie et chauffe-eau.",
            "equip": [
                "Réseaux cuivre, PER et multicouche",
                "Évacuations et colonnes",
                "Robinetterie et appareils sanitaires",
                "Chauffe-eau et boilers",
                "Recherche de fuites",
            ],
            "reg_title": "Méthodes et bonnes pratiques",
            "reg_lead": "Limiter les dégâts et cibler l'intervention.",
            "regulatory": [
                ("Recherche de fuite non destructive",
                 "Avant d'ouvrir une chape ou un mur, une recherche de fuite non destructive (contrôle de pression, écoute) permet souvent de localiser précisément le point de fuite et de limiter les travaux de reprise."),
            ],
            "zones_title": "Sanitaire en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient notamment à Genève, Lausanne, Nyon, Fribourg et dans le canton de Vaud.",
            "zone_slugs": ["geneve", "lausanne", "nyon", "fribourg", "vaud"],
            "related_svc": ["chauffage", "ventilation", "climatisation", "depannage-sav"],
            "faq": [
                ("Intervenez-vous en dépannage sanitaire ?", "Oui, nous intervenons sur les fuites, canalisations bouchées, chauffe-eau en panne et robinetterie défectueuse. Décrivez le problème lors de votre appel pour évaluer l'urgence."),
                ("Réalisez-vous des rénovations complètes de salle de bain ?", "Oui pour la partie sanitaire d'une rénovation (réseaux eau chaude/froide, évacuations, robinetterie, WC, douche). Contactez-nous pour décrire votre projet et vérifier la faisabilité selon son ampleur."),
                ("Comment obtenir un devis sanitaire ?", "Via notre page contact ou par téléphone : précisez le type de bâtiment, la localisation et la nature des travaux."),
            ],
        },
        {
            "slug": "depannage-sav",
            "name": "Dépannage SAV",
            "h1": "Dépannage CVCS et SAV en Suisse romande",
            "intro": "Panne de chauffage, ventilation, climatisation ou sanitaire ? Intervention SAV pour diagnostiquer et remettre en service — y compris en urgence.",
            "problems_title": "Une panne sur votre installation ?",
            "problems_lead": "Urgence ventilation, chauffage, climatisation ou sanitaire — nous diagnostiquons et remettons en service.",
            "problems": [
                ("boiler", "Panne de chaudière ou de PAC", "Absence de chaleur ou arrêt inattendu."),
                ("fan", "VMC à l'arrêt", "Plus de renouvellement d'air."),
                ("snow", "Climatiseur hors service", "Plus de froid ou unité bloquée."),
                ("leak", "Fuite sur réseau sanitaire", "Dégât des eaux ou pression anormale."),
                ("alert", "Anomalie après un contrôle", "Remise en conformité nécessaire."),
                ("maintain", "Besoin d'un contrat d'entretien", "Maintenance préventive planifiée."),
            ],
            "services_title": "Diagnostic, remise en service et maintenance",
            "services_lead": "Une intervention claire, du constat à la fiabilisation.",
            "services": [
                ("study", "Diagnostic de panne sur site", "Chauffage, VMC, clim, sanitaire."),
                ("gauge", "Devis avant travaux", "Sauf urgence nécessitant une action immédiate."),
                ("repair", "Remise en service", "Chaudières, PAC, VMC et climatisateurs."),
                ("leak", "Intervention fuites sanitaires", "Réseaux et dysfonctionnements."),
                ("maintain", "Contrats de maintenance", "Prévention et suivi régulier."),
                ("balance", "Optimisation des réglages", "Réduction de la consommation d'énergie."),
            ],
            "show_urgence": True,
            "show_gallery": True,
            "gallery_cat": None,
            "gallery_title": "Nos interventions sur site",
            "gallery_lead": f"Exemples d'interventions CVCS réalisées par {COMPANY_NAME}.",
            "expertise_title": "Un SAV multi-techniques",
            "expertise_lead": "Nos dépannages couvrent le chauffage, la ventilation, la climatisation et les réseaux sanitaires.",
            "equip": [
                "Chaudières et pompes à chaleur",
                "VMC et caissons de ventilation",
                "Climatisateurs et PAC air-air",
                "Réseaux sanitaires",
                "Contrats de maintenance préventive",
            ],
            "reg_title": "Diagnostic avant travaux",
            "reg_lead": "Transparence sur le coût et la nature de l'intervention.",
            "regulatory": [
                ("Devis avant intervention corrective",
                 "Sauf urgence nécessitant une action immédiate, nous établissons un diagnostic et un devis avant toute intervention corrective, afin que vous validiez le coût et la nature des travaux avant leur réalisation."),
            ],
            "zones_title": "Dépannage en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient notamment à Genève, Lausanne, Fribourg, en Vaud et en Valais.",
            "zone_slugs": ["geneve", "lausanne", "fribourg", "vaud", "valais"],
            "related_svc": ["chauffage", "ventilation", "climatisation", "sanitaire"],
            "cta_title": "Besoin d'un dépannage ?",
            "cta_text": f"Appelez le {PHONE_DISP} ou décrivez-nous la panne. Nous évaluons la disponibilité selon l'urgence.",
            "faq": [
                ("Qui appeler en urgence ventilation ?", f"Appelez {COMPANY_NAME} au {PHONE_DISP} ou WhatsApp : indiquez votre adresse et si la VMC / ventilation est totalement à l'arrêt."),
                ("Comment signaler une urgence ?", f"Appelez le {PHONE_DISP} ou contactez-nous via WhatsApp en décrivant la situation."),
                ("Quel délai d'intervention ?", "Le délai dépend de la nature de la panne (une absence totale de chauffage en hiver ou une VMC arrêtée est traitée en priorité) et du secteur. Un appel direct permet une évaluation immédiate de la disponibilité."),
                ("Qui appeler pour un dépannage chauffage ou climatisation ?", f"{COMPANY_NAME} au {PHONE_DISP}. Indiquez votre adresse et le type de panne — notamment à Lausanne, Nyon ou Genève."),
                ("Intervenez-vous le week-end ?", f"Oui, nos horaires sont : {HOURS}, y compris le week-end. Appelez-nous pour évaluer la disponibilité selon la nature de la panne."),
            ],
        },
        {
            "slug": "sprinkler-protection-incendie",
            "name": "Sprinkler / protection incendie",
            "h1": "Sprinkler et protection incendie",
            "intro": "Intervention en sous-traitance sur des installations sprinkler, avec exécution soignée et coordination chantier.",
            "problems_title": "Un besoin sprinkler sur chantier ?",
            "problems_lead": "Nous exécutons les réseaux selon plans et spécifications du mandant.",
            "problems": [
                ("fire", "Montage de réseaux sprinkler", "Sous eau, sous air ou à préaction."),
                ("coord", "Coordination multi-corps de métier", "Planning et interfaces chantier."),
                ("study", "Respect des plans du mandant", "Spécifications techniques à suivre."),
                ("valve", "Finitions et supportage", "Conformité aux exigences du projet."),
                ("gauge", "Essais avant mise en service", "Pression et débit à valider."),
                ("install", "Sous-traitance spécialisée", "Pour bureaux d'ingénieurs et EG."),
            ],
            "services_title": "Exécution et coordination chantier",
            "services_lead": "Pose, raccordements, essais et finitions techniques.",
            "services": [
                ("valve", "Collecteurs et postes de contrôle", "Vannes d'alarme et équipements."),
                ("pipe", "Raccordements et supportage", "Dont raccords Victaulic."),
                ("coord", "Sous-traitance pour ingénieurs / EG", "Exécution selon mandats."),
                ("study", "Coordination chantier", "Interfaces avec les autres corps."),
                ("gauge", "Essais de pression et de débit", "Avant mise en service."),
                ("install", "Finitions et mise en conformité", "Selon plans du projet."),
            ],
            "buildings_note": "Bâtiments soumis à des exigences de protection incendie (ERP, hôtels, industriel, logistique), selon obligations applicables.",
            "gallery_cat": "sprinkler",
            "gallery_title": "Nos réalisations sprinkler",
            "gallery_lead": f"Exemples d'exécutions sprinkler réalisées par {COMPANY_NAME}.",
            "expertise_title": "Réseaux sprinkler sous-traités",
            "expertise_lead": "Nous intervenons sur des réseaux sous eau, sous air ou à préaction.",
            "equip": [
                "Réseaux sous eau",
                "Réseaux sous air",
                "Systèmes à préaction",
                "Postes de contrôle et vannes d'alarme",
                "Supportage et raccords Victaulic",
            ],
            "reg_title": "Cadre AEAI et exécution",
            "reg_lead": "Exécution selon plans du mandant et directives applicables.",
            "regulatory": [
                ("Normes AEAI et classes de risque",
                 "Les exigences de protection incendie applicables (classes de risque, catégories de bâtiments concernées) sont définies par les directives de l'Association des établissements cantonaux d'assurance incendie (AEAI). Nous exécutons les réseaux selon les plans et spécifications du mandant et du bureau d'ingénieurs en charge du projet."),
            ],
            "zones_title": "Intervention sprinkler en Suisse romande",
            "zones_lead": f"Basée à {ADDRESS_LOCALITY}, {COMPANY_NAME} intervient notamment à Genève, en Vaud et en Valais.",
            "zone_slugs": ["geneve", "vaud", "valais"],
            "related_svc": ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"],
            "faq": [
                ("Les travaux sprinkler sont-ils réalisés directement ?", "Les interventions sont assurées en sous-traitance spécialisée, selon la nature du projet."),
                ("Un sprinkler est-il obligatoire ?", "Selon les directives AEAI, certaines catégories de bâtiments peuvent être concernées selon leur classe de risque. Nous pouvons analyser votre situation sur demande."),
            ],
        },
    ]


def build_services():
    for cfg in _premium_service_configs():
        write_premium_service_page(cfg)



def communes_block(names):
    """Communes en ligne typo — pas d'accordéon ni pastilles."""
    line = " · ".join(names)
    return (
        '<p class="zone-communes">'
        '<span class="zone-communes__label">Communes desservies</span>'
        f'<span class="zone-communes__line">{line}</span>'
        '<span class="zone-communes__hint">Liste non exhaustive — contactez-nous pour toute autre commune du secteur.</span>'
        "</p>"
    )


SUBSIDY_NOTE = (
    '<details class="zone-details zone-details--subsidy">'
    "<summary>Aides et subventions</summary>"
    '<div class="zone-details__body">'
    "<p>Le remplacement d'un chauffage à mazout, à gaz ou électrique par une pompe à chaleur peut être subventionné "
    'dans le cadre du <strong>Programme Bâtiments</strong>, sur <a href="https://www.leprogrammebatiments.ch" target="_blank" rel="noopener noreferrer">leprogrammebatiments.ch</a>. '
    "{extra} Les barèmes et conditions varient chaque année : nous vous recommandons de déposer votre demande "
    "auprès du service cantonal de l'énergie <strong>avant le début des travaux</strong>, et de vérifier les montants en vigueur sur le portail officiel. "
    "Nous pouvons vous accompagner dans cette démarche.</p>"
    "</div>"
    "</details>"
)


def build_zones():
    p = lambda t: f"<p>{t}</p>"
    zone_page("geneve", "Genève", "la région de Genève",
        PAGE_TITLES["geneve"],
        META_DESCRIPTIONS["geneve"],
        "Chauffagiste et CVCS dans la région de Genève",
        p("Vous cherchez un chauffagiste à Genève ? Le canton présente un parc bâti dense — immeubles, PPE, commerces et tertiaire — avec des contraintes techniques variées (chauffage à distance, GeniLac, remplacement des chauffages fossiles).") +
        p("Contactez-nous pour vérifier la disponibilité d'intervention dans votre secteur.") +
        communes_block(["Genève", "Vernier", "Lancy", "Meyrin", "Carouge", "Onex", "Thônex", "Plan-les-Ouates", "Veyrier", "Grand-Saconnex", "Chêne-Bougeries", "Confignon"]) +
        SUBSIDY_NOTE.format(extra="À Genève, les demandes passent par l'Office cantonal de l'énergie (OCEN) et peuvent se combiner avec le programme SIG-éco21 des Services industriels de Genève."),
        zone_aeo_faq("Genève", "la région de Genève") + [
            ("Existe-t-il des aides pour rénover le chauffage à Genève ?", "Oui, via le Programme Bâtiments et le programme SIG-éco21 (Services industriels de Genève), sous conditions d'éligibilité et selon le barème en vigueur. Contactez-nous pour évaluer votre projet."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["vaud", "nyon", "lausanne"],
        hero_sub=f"Chauffagiste et CVCS à Genève. Appelez le {PHONE_DISP} pour un devis ou un dépannage.")

    zone_page("vaud", "Vaud", "le canton de Vaud",
        PAGE_TITLES["vaud"],
        META_DESCRIPTIONS["vaud"],
        "Chauffagiste dans le canton de Vaud",
        p("Chauffagiste dans le canton de Vaud : rives du Léman, Lausanne, Nyon, Riviera, Chablais et Nord vaudois. Du villa à l'immeuble locatif ou PPE, selon l'altitude et l'exposition.") +
        p("Pour les communes hors axes principaux, contactez-nous afin de confirmer la faisabilité.") +
        communes_block(["Morges", "Yverdon-les-Bains", "Vevey", "Montreux", "Renens", "Pully", "Rolle", "Aigle", "Payerne", "Echallens", "Cossonay", "Orbe"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Vaud, les demandes sont instruites par la Direction générale de l'environnement (DGE) / Direction de l'énergie."),
        zone_aeo_faq("Vaud", "le canton de Vaud") + [
            ("Le canton de Vaud subventionne-t-il les pompes à chaleur ?", "Oui, sous conditions, dans le cadre du Programme Bâtiments géré par la Direction de l'énergie du canton de Vaud. Les certificats de qualité requis (PAC système-module) et les barèmes évoluent chaque année : vérifiez les conditions en vigueur avant de commander votre matériel."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["lausanne", "nyon", "geneve", "fribourg"],
        hero_sub=f"Chauffagiste dans le canton de Vaud. Appelez le {PHONE_DISP} pour un devis ou un dépannage.")

    zone_page("lausanne", "Lausanne", "Lausanne et environs",
        PAGE_TITLES["lausanne"],
        META_DESCRIPTIONS["lausanne"],
        "Chauffagiste à Lausanne : dépannage chauffage et CVCS",
        p("Vous cherchez un chauffagiste à Lausanne ? L'agglomération concentre immeubles, tertiaire et parc ancien — souvent à adapter lors d'une rénovation. Une partie de la ville est desservie par le chauffage à distance (SiL).") +
        p('Nous intervenons aussi en dépannage chauffage. Pour la climatisation ou une pompe à chaleur, voir <a href="/climatisation/">climatisation</a> et <a href="/chauffage/">chauffage</a>.') +
        communes_block(["Renens", "Prilly", "Le Mont-sur-Lausanne", "Épalinges", "Pully", "Chavannes-près-Renens", "Ecublens", "Crissier"]) +
        SUBSIDY_NOTE.format(extra="Les demandes pour l'agglomération lausannoise sont instruites par la Direction de l'énergie du canton de Vaud."),
        zone_aeo_faq("Lausanne", "Lausanne et environs") + [
            ("Proposez-vous le dépannage chauffage à Lausanne ?", f"Oui. Appelez {COMPANY_NAME} au {PHONE_DISP} en indiquant votre adresse lausannoise et le type de panne (chaudière, PAC, radiateurs)."),
            ("Mon immeuble est raccordé au chauffage à distance (CAD), intervenez-vous quand même ?", "Oui : nous intervenons sur les sous-stations, la distribution interne (radiateurs, vannes, régulation) et les réseaux sanitaires, même si la production de chaleur est assurée par un réseau CAD."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["nyon", "vaud", "geneve"],
        hero_sub=f"Chauffagiste et dépannage à Lausanne. Appelez le {PHONE_DISP}.")

    zone_page("nyon", "Nyon", "la région de Nyon",
        PAGE_TITLES["nyon"],
        META_DESCRIPTIONS["nyon"],
        "Climatisation et chauffagiste à Nyon",
        p("Climatisation à Nyon et chauffagiste local : la région entre Genève et Lausanne combine constructions récentes (villas, PPE autour du lac) et bâti plus ancien dans les villages. Standards énergétiques élevés (Minergie) fréquents sur les neuves.") +
        p('Nous installons et entretenons la climatisation (split, multi-split, PAC air-air) ainsi que le chauffage (pompes à chaleur, chaudières) à Nyon, Gland, Rolle, Coppet et environs. Devis via <a href="/climatisation/">climatisation</a>, <a href="/chauffage/">chauffage</a> ou téléphone.') +
        communes_block(["Gland", "Rolle", "Prangins", "Founex", "Coppet", "Genolier", "Duillier", "Trélex"]) +
        SUBSIDY_NOTE.format(extra="La région de Nyon dépend du barème et du guichet du canton de Vaud (Direction de l'énergie)."),
        zone_aeo_faq("Nyon", "la région de Nyon") + [
            ("Installez-vous la climatisation à Nyon ?", f"Oui. {COMPANY_NAME} étudie et installe la climatisation à Nyon et communes voisines (Gland, Rolle, Coppet…). Devis via la page contact ou au {PHONE_DISP}."),
            ("Intervenez-vous sur des bâtiments Minergie récents ?", "Oui. Les constructions Minergie demandent une ventilation mécanique contrôlée bien réglée et un entretien régulier : nous pouvons intervenir sur ces installations comme sur du bâti plus ancien."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["geneve", "lausanne", "vaud"],
        hero_sub=f"Climatisation et chauffagiste à Nyon — devis ou appel au {PHONE_DISP}.")

    zone_page("valais", "Valais", "le canton du Valais",
        PAGE_TITLES["valais"],
        META_DESCRIPTIONS["valais"],
        "Chauffagiste en Valais : chauffage, CVCS et climatisation",
        p("Chauffagiste en Valais : de la plaine du Rhône aux stations, l'altitude influence le dimensionnement du chauffage. Résidences secondaires et chalets demandent souvent une attention hors gel / remise en service.") +
        p("Contactez-nous avec votre commune (Sion, Martigny, Monthey, Sierre…) pour vérifier la disponibilité.") +
        communes_block(["Sion", "Martigny", "Monthey", "Sierre", "Crans-Montana", "Verbier", "Saint-Maurice", "Conthey"]) +
        SUBSIDY_NOTE.format(extra="En Valais, les demandes sont instruites par le Service de l'énergie et des forces hydrauliques (SEFH) de l'État du Valais."),
        zone_aeo_faq("Valais", "le canton du Valais") + [
            ("Intervenez-vous sur un chalet ou une résidence secondaire ?", "Oui, en tenant compte des contraintes propres à ces logements (occupation partielle, altitude, risque de gel). Précisez l'altitude et le mode d'occupation lors de votre demande."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav", "sprinkler-protection-incendie"], ["geneve", "vaud", "fribourg"],
        hero_sub=f"Chauffagiste en Valais. Appelez le {PHONE_DISP} pour un devis ou un dépannage.")

    zone_page("fribourg", "Fribourg", "le canton de Fribourg",
        PAGE_TITLES["fribourg"],
        META_DESCRIPTIONS["fribourg"],
        "Chauffagiste dans le canton de Fribourg",
        p(f'Chauffagiste dans le canton de Fribourg : Fribourg-ville, Gruyère, Broye et Glâne. Notre <a href="/romont/">siège est à Romont</a> ({ADDRESS_LOCALITY}) — équipe mobile sur tout le canton.') +
        p("Précisez la commune et l'urgence lors du premier contact.") +
        communes_block(["Fribourg", "Bulle", "Châtel-Saint-Denis", "Estavayer-le-Lac", "Domdidier", "Marly", "Villars-sur-Glâne", "Romont"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Fribourg, les demandes sont instruites par le Service de l'énergie (SdE)."),
        zone_aeo_faq("Fribourg", "le canton de Fribourg") + [
            ("Où se trouve le siège de Sopjani Tech Sàrl ?", f'À <a href="/romont/">{ADDRESS_FULL}</a>, dans le district de la Glâne. La page Romont détaille nos prestations CVCS locales.'),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["romont", "vaud", "lausanne", "neuchatel"],
        hero_sub=f"Chauffagiste dans le canton de Fribourg. Appelez le {PHONE_DISP}.")

    zone_page("romont", "Romont", "Romont et la Glâne",
        PAGE_TITLES["romont"],
        META_DESCRIPTIONS["romont"],
        "CVCS à Romont — siège Sopjani Tech Sàrl",
        p(f'<strong>{COMPANY_NAME}</strong> a son siège à <a href="{MAP_URL}" target="_blank" rel="noopener noreferrer">{ADDRESS_FULL}</a>. Depuis Romont, nous répondons aux demandes de devis et d\'appels d\'offres en chauffage, ventilation, climatisation, sanitaire et dépannage SAV — villas, immeubles, PPE, entreprises et collectivités.') +
        p(f'Téléphone <a href="tel:{PHONE}" class="track-phone">{PHONE_DISP}</a> · <a href="mailto:{EMAIL}" class="track-email">{EMAIL}</a> · Horaires {HOURS}.') +
        p('Prestations locales : <a href="/chauffage/">chauffage</a>, <a href="/ventilation/">ventilation</a>, <a href="/climatisation/">climatisation</a>, <a href="/sanitaire/">sanitaire</a> et <a href="/depannage-sav/">dépannage SAV</a>. Pour le canton élargi, voir aussi <a href="/fribourg/">chauffagiste Fribourg</a>.') +
        p('Activité complémentaire : exécution sprinkler en <a href="/sprinkler-protection-incendie/">sous-traitance spécialisée</a>, selon mandat.') +
        communes_block(["Romont", "Siviriez", "Ursy", "Mézières", "Vuisternens-devant-Romont", "Billens-Hennens", "Massonnens", "Villaz-Saint-Pierre"]) +
        SUBSIDY_NOTE.format(extra="À Romont et dans la Glâne, les demandes d'aides passent par le Service de l'énergie (SdE) du canton de Fribourg."),
        [
            (f"Qui appeler pour un chauffagiste à Romont ?", f"{COMPANY_NAME} est basée à Romont : installation, entretien et dépannage de chaudières et pompes à chaleur. Appelez le {PHONE_DISP} ou passez par la page contact."),
            (f"Qui appeler pour un dépannage CVCS à Romont ?", f"Contactez {COMPANY_NAME} au {PHONE_DISP}, par email ({EMAIL}) ou WhatsApp. Indiquez l'adresse à Romont ou dans la Glâne, le type de bâtiment et la nature de la panne."),
            ("Comment obtenir un devis à Romont ?", f"Par téléphone au {PHONE_DISP} ou via la <a href=\"/contact/#contact-form\">page contact</a> : décrivez le bâtiment, la localisation et le type de travaux (installation, maintenance ou dépannage)."),
            ("Intervenez-vous aussi ailleurs dans le canton de Fribourg ?", f'Oui. Pour le canton (Fribourg-ville, Gruyère, Broye…), voir la page <a href="/fribourg/">chauffagiste Fribourg</a>. Le siège et les interventions locales Glâne sont détaillés ici.'),
            ("Proposez-vous aussi le sprinkler ?", "Oui, en sous-traitance spécialisée selon le mandat — ce n'est pas notre canal commercial principal. Pour un devis CVCS (chauffage, clim, ventilation, sanitaire, dépannage), contactez-nous directement."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["fribourg", "vaud", "neuchatel"],
        hero_sub=f"Siège à Romont — devis CVCS et dépannage. Appelez le {PHONE_DISP}.")

    zone_page("neuchatel", "Neuchâtel", "le canton de Neuchâtel",
        PAGE_TITLES["neuchatel"],
        META_DESCRIPTIONS["neuchatel"],
        "Chauffagiste à Neuchâtel et La Chaux-de-Fonds",
        p("Chauffagiste dans le canton de Neuchâtel : du littoral du lac aux hauteurs du Jura (La Chaux-de-Fonds, Le Locle). Immeubles, villas et bâtiments industriels ou horlogers.") +
        p("Contactez-nous en précisant votre commune pour vérifier la disponibilité.") +
        communes_block(["Neuchâtel", "La Chaux-de-Fonds", "Le Locle", "Peseux", "Boudry", "Cortaillod", "Saint-Blaise", "Val-de-Ruz"]) +
        SUBSIDY_NOTE.format(extra="Dans le canton de Neuchâtel, les demandes sont instruites par le Service de l'énergie et de l'environnement (SENE)."),
        zone_aeo_faq("Neuchâtel", "le canton de Neuchâtel") + [
            ("Intervenez-vous à La Chaux-de-Fonds et dans le Haut ?", "Oui, sous réserve de planification. Précisez l'adresse et l'urgence lors du premier contact."),
        ],
        ["chauffage", "ventilation", "climatisation", "sanitaire", "depannage-sav"], ["vaud", "fribourg", "geneve"],
        hero_sub=f"Chauffagiste à Neuchâtel et La Chaux-de-Fonds. Appelez le {PHONE_DISP}.")


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
    <p style="margin-top:28px;"><a href="/politique-confidentialite/" class="text-link">Politique de confidentialité</a></p>
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
      <li><strong>FormSubmit</strong> — transmission sécurisée des messages du formulaire de contact vers {EMAIL}.</li>
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
    <p style="margin-top:28px;"><a href="/mentions-legales/" class="text-link">Mentions légales</a></p>
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
    """Worker Cloudflare : redirections 301 + masquage des URLs junk (404) + noindex fichiers vérif."""
    redirects = {f"/{old_name}": new_path for old_name, new_path in LEGACY_REDIRECTS.items()}
    redirects_js = json.dumps(redirects, indent=2, ensure_ascii=False)
    block_exact_js = json.dumps(list(WORKER_BLOCK_EXACT), ensure_ascii=False)
    block_prefixes_js = json.dumps(list(WORKER_BLOCK_PREFIXES), ensure_ascii=False)
    verify_js = json.dumps(list(VERIFICATION_TXT_PATHS), ensure_ascii=False)
    content = f"""/**
 * Redirections HTTP 301 + SEO junk URLs — généré par build_site.py
 * Déploiement : push sur main (workflow) ou npx wrangler deploy
 * Prérequis : domaine sopjanitech.ch géré par Cloudflare (DNS proxy activé).
 */
const REDIRECTS = {redirects_js};
const BLOCK_EXACT = new Set({block_exact_js});
const BLOCK_PREFIXES = {block_prefixes_js};
const VERIFICATION_TXT = new Set({verify_js});
const APEX_HOST = "sopjanitech.ch";

function needsTrailingSlash(pathname) {{
  if (pathname === "/" || pathname.endsWith("/")) return false;
  const last = pathname.split("/").pop() || "";
  return !last.includes(".");
}}

function isBlocked(pathname) {{
  if (BLOCK_EXACT.has(pathname)) return true;
  return BLOCK_PREFIXES.some((p) => pathname === p.slice(0, -1) || pathname.startsWith(p));
}}

async function branded404(request, url) {{
  const res = await fetch(new URL("/404.html", url.origin), request);
  const headers = new Headers(res.headers);
  headers.set("Cache-Control", "public, max-age=300");
  headers.set("X-Robots-Tag", "noindex, nofollow");
  return new Response(res.body, {{ status: 404, statusText: "Not Found", headers }});
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
    if (isBlocked(url.pathname)) {{
      return branded404(request, url);
    }}
    if (needsTrailingSlash(url.pathname)) {{
      return Response.redirect(`${{url.origin}}${{url.pathname}}/`, 301);
    }}
    const originRes = await fetch(request);
    if (VERIFICATION_TXT.has(url.pathname)) {{
      const headers = new Headers(originRes.headers);
      headers.set("X-Robots-Tag", "noindex, nofollow");
      return new Response(originRes.body, {{
        status: originRes.status,
        statusText: originRes.statusText,
        headers,
      }});
    }}
    return originRes;
  }},
}};
"""
    (ROOT / "redirect-worker.mjs").write_text(content, encoding="utf-8")


def build_404():
    """Page 404 GitHub Pages (404.html) — noindex, charte site."""
    title = PAGE_TITLES["404"]
    desc = META_DESCRIPTIONS["404"]
    body = f"""
<section class="page-hero hero" aria-labelledby="page-h1">
  <div class="container">
    <p class="hero-eyebrow">Erreur 404</p>
    <h1 id="page-h1">Cette page n'existe pas.</h1>
    <p class="hero-sub">Le lien est peut-être obsolète, ou l'adresse comporte une faute de frappe. Retrouvez {COMPANY_NAME} — CVCS et sprinkler à Romont.</p>
    <div class="hero-ctas">
      <a href="/" class="btn btn-brand">Retour à l'accueil</a>
      <a href="/contact/" class="btn btn-secondary track-devis">Contact / devis</a>
    </div>
  </div>
</section>
<section class="content-section">
  <div class="container">
    <h2 class="section-title">Pages utiles</h2>
    <ul class="bullet-list">
      <li><a href="/prestations/">Prestations CVCS &amp; sprinkler</a></li>
      <li><a href="/depannage-sav/">Dépannage SAV</a></li>
      <li><a href="/zones-intervention/">Zones d'intervention</a></li>
      <li><a href="/contact/">Demander un devis</a></li>
    </ul>
  </div>
</section>
"""
    graph = [
        {
            "@type": "WebPage",
            "@id": f"{SITE}/404.html#webpage",
            "url": f"{SITE}/404.html",
            "name": title,
            "description": desc,
            "isPartOf": {"@id": f"{SITE}/#website"},
            "about": {"@id": f"{SITE}/#organization"},
            "inLanguage": "fr-CH",
        }
    ]
    write_page(
        ["404.html"],
        page_shell(title, desc, f"{SITE}/404.html", graph, body, robots="noindex, follow"),
    )


def build_sitemap():
    today = date.today().isoformat()
    # Preserve lastmod for URLs already listed (avoid date-only noise on regenerate).
    sitemap_path = ROOT / "sitemap.xml"
    existing_lastmod = {}
    if sitemap_path.exists():
        existing_lastmod = dict(
            re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", sitemap_path.read_text(encoding="utf-8"))
        )
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
        loc = f"{SITE}{path}"
        lastmod = existing_lastmod.get(loc, today)
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>")
    lines.append("</urlset>")
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_robots():
    lines = [
        "User-agent: *",
        "Allow: /",
    ]
    for path in JUNK_DISALLOW_PATHS:
        lines.append(f"Disallow: {path}")
    lines.append(f"Sitemap: {SITE}/sitemap.xml")
    lines.append("")
    (ROOT / "robots.txt").write_text("\n".join(lines), encoding="utf-8")


def build_realisations():
    def collect_images(cat):
        imgs = REALISATIONS_BY_CAT.get(cat, [])
        return imgs

    def cat_block(cat, label):
        imgs = collect_images(cat)
        if not imgs:
            return ""
        carousel = magnetic_carousel_html(imgs, label)
        return f"""<div class="realisations-cat" id="real-{cat}-block">
  <span class="label">{label}</span>
  <div class="rule"></div>
  <h2 class="section-title" id="real-{cat}">{label}</h2>
  <p class="section-lead">Survolez ou touchez une photo pour l'agrandir. Faites défiler pour voir la suite.</p>
  {carousel}
</div>"""

    def duo_section(left, right, aria_label, alt=False):
        left_block = cat_block(*left) if left else ""
        right_block = cat_block(*right) if right else ""
        if not left_block and not right_block:
            return ""
        alt_cls = " alt" if alt else ""
        return f"""<section class="content-section magnetic-section realisations-duo-section{alt_cls}" aria-label="{aria_label}">
  <div class="container realisations-duo">
    {left_block}
    {right_block}
  </div>
</section>
"""

    image_objects = []
    for cat in ("chauffage", "ventilation", "sanitaire", "sprinkler"):
        for fn, w, h, alt, cap in collect_images(cat):
            image_objects.append(image_object_ld(fn, w, h, alt, cap))

    duo_hvac = duo_section(
        ("chauffage", "Chauffage"),
        ("ventilation", "Ventilation"),
        "Chauffage et ventilation",
    )
    duo_san_spr = duo_section(
        ("sanitaire", "Sanitaire"),
        ("sprinkler", "Sprinkler"),
        "Sanitaire et sprinkler",
        alt=True,
    )

    body = f"""
{page_hero(
        "Réalisations",
        "Nos réalisations CVCS et sprinkler",
        f"Projets réalisés par {COMPANY_NAME} en Suisse romande — photos de chantiers réels.",
        image=hero_image_for("realisations"),
    )}
<section class="content-section home-cases" id="cas-chantiers" aria-labelledby="cases-h2">
  <div class="container">
    <h2 class="section-title" id="cases-h2">Cas chantiers</h2>
    <p class="section-lead">Quelques interventions représentatives — titres concrets, photos prises sur site.</p>
    {case_studies_grid(CASE_STUDIES, heading="h3")}
  </div>
</section>
{duo_hvac}
{duo_san_spr}
<p class="gallery-legal-note container"><a href="{IMAGE_LICENSE_URL}">Droits et utilisation des images</a> · {IMAGE_COPYRIGHT_NOTICE}</p>
{trust_strip()}
{norms_bar()}
{cta_band()}"""
    crumbs = [("Accueil", "/"), ("Réalisations", "/realisations/")]
    title = PAGE_TITLES.get("realisations", f"Réalisations CVCS, sprinkler et sanitaire | {COMPANY_NAME}")
    desc = META_DESCRIPTIONS.get("realisations", f"Réalisations de {COMPANY_NAME} en Suisse romande : installations sprinkler, ventilation et tuyauterie sanitaire. Photos de chantiers réels.")
    gallery_schema = {
        "@type": "ImageGallery",
        "name": f"Réalisations {COMPANY_NAME}",
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
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const endpoint = form.getAttribute('data-form-endpoint') || form.getAttribute('action') || '';
    const feedback = form.querySelector('.form-feedback');
    const submitBtn = form.querySelector('[type="submit"]');
    trackEvent('generate_lead', { method: 'contact_form', event_category: 'conversion' });
    trackEvent('form_submit', { event_category: 'conversion', event_label: 'contact_form' });

    function resetSmartForm() {
      form.reset();
      if (form.classList.contains('contact-form--smart')) {
        const steps = form.querySelectorAll('.form-step');
        steps.forEach((s, i) => {
          s.hidden = i !== 0;
          s.classList.toggle('is-active', i === 0);
        });
        const urgent = form.querySelector('[data-urgent-cta]');
        if (urgent) urgent.hidden = true;
        updateSmartFormProgress(form, 1);
      }
    }

    if (!endpoint || endpoint === '#') {
      if (feedback) {
        feedback.textContent = 'Merci pour votre message. Nous vous recontacterons dans les meilleurs délais.';
        feedback.hidden = false;
      }
      resetSmartForm();
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
    }
    if (feedback) {
      feedback.textContent = 'Envoi en cours…';
      feedback.hidden = false;
    }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });
      const data = await res.json().catch(() => ({}));
      const ok = data.success === true || data.success === 'true';
      if (!res.ok || !ok) {
        const raw = String((data && data.message) || '');
        if (/activat/i.test(raw)) {
          throw new Error('activation');
        }
        throw new Error(raw || 'send_failed');
      }
      if (feedback) {
        feedback.textContent = 'Merci pour votre message. Nous vous recontacterons dans les meilleurs délais.';
        feedback.hidden = false;
      }
      resetSmartForm();
    } catch (err) {
      if (feedback) {
        if (err && err.message === 'activation') {
          feedback.textContent = 'Le formulaire n’est pas encore activé. Ouvrez la boîte info@sopjanitech.ch (et les indésirables), cherchez l’e-mail FormSubmit « Activate Form », puis cliquez le lien. Ensuite renvoyez une demande.';
        } else {
          feedback.textContent = 'Envoi impossible pour le moment. Appelez-nous au +41 79 932 68 62 ou écrivez à info@sopjanitech.ch.';
        }
        feedback.hidden = false;
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
      }
    }
  });
});

function updateSmartFormProgress(form, step) {
  const bar = form.querySelector('[data-form-progress]');
  const labels = form.querySelectorAll('[data-step-label]');
  if (bar) bar.style.setProperty('--progress', (step / 4 * 100) + '%');
  labels.forEach(li => {
    const n = Number(li.getAttribute('data-step-label'));
    li.classList.toggle('is-active', n === step);
    li.classList.toggle('is-done', n < step);
  });
}

function validateSmartStep(stepEl) {
  const required = stepEl.querySelectorAll('[required]');
  for (const el of required) {
    if (el.type === 'radio') {
      const name = el.name;
      if (!stepEl.querySelector(`input[name="${name}"]:checked`)) {
        const first = stepEl.querySelector(`input[name="${name}"]`);
        if (first) first.focus();
        return false;
      }
    } else if (!el.value.trim()) {
      el.focus();
      return false;
    }
  }
  return true;
}

document.querySelectorAll('.contact-form--smart').forEach(form => {
  const steps = Array.from(form.querySelectorAll('.form-step'));
  let current = 1;
  updateSmartFormProgress(form, current);

  // Prefill from ?need=installation|maintenance|depannage
  try {
    const params = new URLSearchParams(window.location.search);
    const needMap = {
      installation: 'Devis installation',
      maintenance: 'Maintenance / entretien',
      depannage: 'Dépannage',
      sprinkler: 'Sprinkler / incendie',
    };
    const needKey = (params.get('need') || '').toLowerCase();
    if (needMap[needKey]) {
      const radio = form.querySelector(`input[name="need"][value="${needMap[needKey]}"]`);
      if (radio) radio.checked = true;
    }
  } catch (_) {}

  form.addEventListener('change', e => {
    if (e.target && e.target.name === 'urgency') {
      const urgent = form.querySelector('[data-urgent-cta]');
      if (urgent) urgent.hidden = e.target.value !== 'Urgent';
    }
  });

  form.querySelectorAll('[data-form-next]').forEach(btn => {
    btn.addEventListener('click', () => {
      const stepEl = form.querySelector(`.form-step[data-step="${current}"]`);
      if (!stepEl || !validateSmartStep(stepEl)) return;
      if (current >= steps.length) return;
      stepEl.hidden = true;
      stepEl.classList.remove('is-active');
      current += 1;
      const next = form.querySelector(`.form-step[data-step="${current}"]`);
      if (next) {
        next.hidden = false;
        next.classList.add('is-active');
      }
      updateSmartFormProgress(form, current);
    });
  });

  form.querySelectorAll('[data-form-back]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (current <= 1) return;
      const stepEl = form.querySelector(`.form-step[data-step="${current}"]`);
      if (stepEl) {
        stepEl.hidden = true;
        stepEl.classList.remove('is-active');
      }
      current -= 1;
      const prev = form.querySelector(`.form-step[data-step="${current}"]`);
      if (prev) {
        prev.hidden = false;
        prev.classList.add('is-active');
      }
      updateSmartFormProgress(form, current);
    });
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
    build_404()
    build_nojekyll()
    build_sitemap()
    build_robots()
    print("Site generated successfully.")


if __name__ == "__main__":
    main()
