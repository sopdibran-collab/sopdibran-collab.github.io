#!/usr/bin/env python3
"""Generate a business card (carte de visite) matching the OG visual.

Same navy field, brand mark, cyan rule and taglines as og-default.jpg,
plus phone and email. Print size: Swiss 85×55 mm at 300 DPI.

Typography is scaled for physical print (all text large enough to read
at arm's length), not for screen OG proportions.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
# 85 × 55 mm @ 300 DPI
WIDTH, HEIGHT = 1004, 650
OUT_JPG = ROOT / "assets" / "carte-visite.jpg"
OUT_PNG = ROOT / "assets" / "carte-visite.png"
BRAND = ROOT / "assets" / "brand"

SUBMARK = BRAND / "logo-submark-512.png"
SUBMARK_FALLBACK = BRAND / "logo-submark.png"

NAVY = (11, 37, 69)       # #0B2545
NAVY_DEEP = (6, 22, 42)
CYAN = (96, 192, 236)     # #60C0EC
WHITE = (248, 250, 252)
MUTED = (186, 198, 212)
SAGE = (168, 196, 184)

PHONE = "+41 79 932 68 62"
EMAIL = "info@sopjanitech.ch"
URL = "sopjanitech.ch"

SANS_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
SANS_REG = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(candidates: list[str], size: int) -> ImageFont.ImageFont:
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_background() -> Image.Image:
    yy = np.linspace(0, 1, HEIGHT)[:, None]
    xx = np.linspace(0, 1, WIDTH)[None, :]
    top = np.array(NAVY, dtype=np.float64)
    bottom = np.array(NAVY_DEEP, dtype=np.float64)
    gradient = top * (1 - yy) + bottom * yy
    base = np.repeat(gradient[:, None, :], WIDTH, axis=1)

    glow_strength = (xx * (1 - yy * 0.35))[:, :, None]
    glow = np.concatenate(
        [18 * glow_strength, 50 * glow_strength, 68 * glow_strength],
        axis=2,
    )
    base = base + glow * 0.4

    rng = np.random.default_rng(11)
    grain = rng.normal(0, 2.4, size=(HEIGHT, WIDTH, 1))
    arr = np.clip(base + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def fit_height(im: Image.Image, height: int) -> Image.Image:
    im = im.convert("RGBA")
    ratio = height / im.height
    return im.resize((max(1, int(im.width * ratio)), height), Image.Resampling.LANCZOS)


def paste_rgba(base: Image.Image, overlay: Image.Image, position: tuple[int, int]) -> None:
    base.paste(overlay, position, overlay)


def main() -> None:
    """Uniform print scale @ 300 DPI (~4.17 px/pt).

    brand ~15 pt · body (prestations + contact + URL) ~10 pt
    Logo beside the name; long tagline wraps so all body type matches.
    """
    submark_path = SUBMARK if SUBMARK.exists() else SUBMARK_FALLBACK
    if not submark_path.exists():
        raise FileNotFoundError(f"Missing submark: {submark_path}")

    img = build_background()
    draw = ImageDraw.Draw(img)

    # One body size for prestations, phone, email, URL — card must read as a whole
    BODY = 40
    font_brand = load_font(SANS_BOLD, 64)
    font_brand_sub = load_font(SANS_BOLD, 34)
    font_body = load_font(SANS_BOLD, BODY)
    margin = 34

    mark_h = 120
    mark = fit_height(Image.open(submark_path), mark_h)
    mark_x, mark_y = margin, 30
    paste_rgba(img, mark, (mark_x, mark_y))

    text_x = mark_x + mark.width + 20
    brand_y = mark_y + 16
    draw.text((text_x, brand_y), "SOPJANI TECH", font=font_brand, fill=WHITE)
    brand_bbox = draw.textbbox((text_x, brand_y), "SOPJANI TECH", font=font_brand)
    draw.text(
        (brand_bbox[2] + 14, brand_y + 20),
        "SÀRL",
        font=font_brand_sub,
        fill=CYAN,
    )

    rule_y = max(mark_y + mark_h, brand_bbox[3]) + 16
    rule_w = WIDTH - margin * 2 - 8
    draw.line([(margin, rule_y), (margin + rule_w, rule_y)], fill=CYAN, width=3)

    # Prestations — wrapped so type can match contact size (same font + size)
    line_gap = 48
    tag_y = rule_y + 20
    draw.text((margin, tag_y), "Chauffage · Ventilation · Climatisation", font=font_body, fill=WHITE)
    draw.text((margin, tag_y + line_gap), "Sanitaire · Dépannage SAV · Sprinkler", font=font_body, fill=WHITE)
    draw.text((margin, tag_y + line_gap * 2), "Suisse romande", font=font_body, fill=MUTED)

    contact_y = tag_y + line_gap * 3 + 18
    draw.text((margin, contact_y), PHONE, font=font_body, fill=WHITE)
    draw.text((margin, contact_y + line_gap), EMAIL, font=font_body, fill=CYAN)

    bbox = draw.textbbox((0, 0), URL, font=font_body)
    draw.text(
        (WIDTH - margin - (bbox[2] - bbox[0]), HEIGHT - 58),
        URL,
        font=font_body,
        fill=SAGE,
    )

    draw.rectangle([0, 0, 7, HEIGHT], fill=CYAN)

    OUT_JPG.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_JPG, format="JPEG", quality=92, optimize=True, progressive=True)
    img.save(OUT_PNG, format="PNG", optimize=True)
    print(f"Wrote {OUT_JPG} ({OUT_JPG.stat().st_size // 1024} Ko) {WIDTH}×{HEIGHT}")
    print(f"Wrote {OUT_PNG} ({OUT_PNG.stat().st_size // 1024} Ko) {WIDTH}×{HEIGHT}")


if __name__ == "__main__":
    main()
