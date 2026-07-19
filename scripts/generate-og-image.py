#!/usr/bin/env python3
"""Generate the default Open Graph image (1200×630 JPG) for sopjanitech.ch.

Layout aligned with Markaj Renting / Gzimmo OG cards:
navy field, brand mark, cyan rule, tagline, domain.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 630
OUT = ROOT / "assets" / "og-default.jpg"
BRAND = ROOT / "assets" / "brand"

SUBMARK = BRAND / "logo-submark-512.png"
SUBMARK_FALLBACK = BRAND / "logo-submark.png"

NAVY = (11, 37, 69)       # #0B2545
NAVY_DEEP = (6, 22, 42)
CYAN = (96, 192, 236)     # #60C0EC
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)   # slate-ish on navy
SAGE = (143, 168, 155)    # #8FA89B

SANS_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def load_font(candidates: list[str], size: int) -> ImageFont.ImageFont:
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_background() -> Image.Image:
    """Vertical navy gradient + light grain (WhatsApp-friendly, not noisy)."""
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
    submark_path = SUBMARK if SUBMARK.exists() else SUBMARK_FALLBACK
    if not submark_path.exists():
        raise FileNotFoundError(f"Missing submark: {submark_path}")

    img = build_background()
    draw = ImageDraw.Draw(img)
    font_brand = load_font(SANS_CANDIDATES, 54)
    font_brand_sub = load_font(SANS_CANDIDATES, 26)
    font_tag = load_font(SANS_CANDIDATES, 28)
    font_sub = load_font(SANS_CANDIDATES, 24)
    font_url = load_font(SANS_CANDIDATES, 22)
    margin = 88

    mark = fit_height(Image.open(submark_path), 200)
    paste_rgba(img, mark, (margin, 78))

    brand_y = 300
    draw.text((margin, brand_y), "SOPJANI TECH", font=font_brand, fill=WHITE)
    brand_bbox = draw.textbbox((margin, brand_y), "SOPJANI TECH", font=font_brand)
    draw.text(
        (brand_bbox[2] + 14, brand_y + 22),
        "SÀRL",
        font=font_brand_sub,
        fill=CYAN,
    )

    rule_y = brand_bbox[3] + 18
    rule_w = max(420, brand_bbox[2] - brand_bbox[0] + 80)
    draw.line([(margin, rule_y), (margin + rule_w, rule_y)], fill=CYAN, width=3)

    tag_y = rule_y + 22
    draw.text(
        (margin, tag_y),
        "Chauffage · Ventilation · Climatisation · Sanitaire",
        font=font_tag,
        fill=WHITE,
    )
    draw.text(
        (margin, tag_y + 42),
        "Dépannage SAV · Sprinkler · Suisse romande",
        font=font_sub,
        fill=MUTED,
    )

    url = "sopjanitech.ch"
    bbox = draw.textbbox((0, 0), url, font=font_url)
    draw.text(
        (WIDTH - margin - (bbox[2] - bbox[0]), HEIGHT - 72),
        url,
        font=font_url,
        fill=SAGE,
    )

    draw.rectangle([0, 0, 8, HEIGHT], fill=CYAN)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="JPEG", quality=90, optimize=True, progressive=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} Ko) {WIDTH}×{HEIGHT}")


if __name__ == "__main__":
    main()
