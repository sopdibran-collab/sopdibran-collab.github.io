#!/usr/bin/env python3
"""Crop réalisations → heroes JPG 2000×1125 + variantes WebP 1024/1600 (ffmpeg)."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "realisations"
DST = ROOT / "assets" / "heroes"
TARGET_W, TARGET_H = 2000, 1125
WEBP_WIDTHS = (1024, 1600)

HERO_SOURCES = {
    "chauffage.jpg": "tuyauterie-fabrication-atelier.jpg",
    "ventilation.jpg": "ventilation-conduit-galvanise-chantier.jpg",
    "sanitaire.jpg": "sanitaire-local-technique-collecteurs.jpg",
    "depannage-sav.jpg": "sanitaire-local-technique-tuyauterie.jpg",
    "sprinkler-protection-incendie.jpg": "sprinkler-collecteur-rouges.jpg",
}

VF = (
    f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
    f"crop={TARGET_W}:{TARGET_H}"
)


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    DST.mkdir(parents=True, exist_ok=True)
    for hero_name, src_name in HERO_SOURCES.items():
        src = SRC / src_name
        dst = DST / hero_name
        if not src.is_file():
            raise SystemExit(f"Missing source: {src}")
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(src),
                "-vf",
                VF,
                "-q:v",
                "3",
                str(dst),
            ]
        )
        for w in WEBP_WIDTHS:
            old = DST / f"{dst.stem}-{w}.webp"
            if old.is_file():
                old.unlink()
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(dst),
                    "-vf",
                    f"scale={w}:-2",
                    "-c:v",
                    "libwebp",
                    "-quality",
                    "84",
                    str(DST / f"{dst.stem}-{w}.webp"),
                ]
            )
        print(f"OK {hero_name} ← {src_name}")


if __name__ == "__main__":
    main()
