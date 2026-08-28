# 01 — Identité & marque — Sopjani-tech Sàrl

## Couleurs (charte CVCS & Sprinkler — mat / corporate)

### Principales
| Nom | Hex | Rôle | Usage |
|-----|-----|------|-------|
| Dominante | `#0B2545` | 60% — structure, sérieux | Header, titres, CTA fond clair, bandes institutionnelles |
| Interaction | `#60C0EC` | 30% — marque / confort | Accents, filets, CTA sur fond sombre, hovers |
| Accent sage | `#8FA89B` | 10% — éco / réassurance | Badges normes, tags discrets |

### Spécifiques & neutres
| Nom | Hex | Usage |
|-----|-----|-------|
| Urgence SAV | `#D32F2F` | **Uniquement** bouton / bandeau dépannage urgent |
| Fond page | `#F8FAFC` | Surfaces de lecture |
| Blanc | `#FFFFFF` | Cartes, surfaces |
| Texte | `#1E293B` | Corps (contraste max) |

### Règles strictes
- Pas de néon / saturé hors palette.
- Rouge = SAV uniquement + texte ou icône explicite.
- CTA fond clair = navy `#0B2545` + texte blanc.
- CTA fond sombre (header, cta-band) = cyan `#60C0EC` + texte navy.
- Labels / titres = navy ; filets décoratifs = cyan.

### Variables CSS
```css
--c-navy: #0b2545;
--c-logo: #60c0ec;
--c-sage: #8fa89b;
--c-urgence: #d32f2f;
--c-bg: #f8fafc;
--c-text: #1e293b;
--c-brand / --c-cta: #0b2545; /* CTA sur fond clair */
```

## Typographie

| Élément | Police | Graisses |
|---------|--------|----------|
| Titres / UI display | Outfit | 500–800 |
| Corps / lecture | Source Sans 3 | 400–700 |

Chargement Google Fonts via `page_shell()` dans `build_site.py`. Variables CSS : `--font-display`, `--font-body`.

## Logo

Cyan logo : ≈ `#62BEE8` / charte `#60C0EC`.

Sources officielles Alpë → `/assets/brand/` (SVG + PNG + JPG) :

| Variante | Fichiers | Usage site |
|----------|----------|------------|
| RESPONSIVE | `logo-responsive.svg` (+ PNG) | Header + footer (lockup horizontal) |
| PRINCIPALE | `logo-principale.*` | OG / `logo-full.png` |
| SUBMARK | `logo-submark.*` | Apple touch, tailles 32–512 |
| FAVICON | `logo-favicon-32.*` → `/assets/favicon.png` + `.svg` | Onglet navigateur |
| Mono noir / blanc / grayscale / couleur inversée | `logo-mono-*`, `logo-grayscale-*`, `logo-couleur-inversee.*` | Print, fonds spéciaux (archivés) |

Ne plus utiliser les anciens `logo-primary-*` (interim).
