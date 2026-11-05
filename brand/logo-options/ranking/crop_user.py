#!/usr/bin/env python3
"""Crops every logo out of the owner's reference sheets into brand/logo-options/user/uNN.png.

Run: python3 brand/logo-options/ranking/crop_user.py <dir-with-sheets>
Sheet 1 (a laptop advert) holds no logo and is skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "user"


def grid(cols: int, xs: list[float], ys: list[tuple[int, int]], inset: int = 10) -> list[tuple]:
    return [(round(xs[c]) + inset, y0, round(xs[c + 1]) - inset, y1) for (y0, y1) in ys for c in range(cols)]


W5 = [i * 1408 / 5 for i in range(6)]
SHEETS: list[tuple[str, list[tuple]]] = [
    ("2.webp", [(220, 120, 1330, 900)]),
    ("3.webp", [(180, 60, 1080, 960)]),
    ("4.png", [(0, 0, 74, 58)]),
    ("5.png", [(0, 0, 428, 381)]),
    ("6.png", [(0, 0, 428, 381)]),
    ("7.webp", grid(5, W5, [(50, 268), (430, 645)])),
    ("8.webp", grid(5, W5, [(55, 262), (440, 640)])),
    ("9.webp", grid(5, [40, 275, 513, 750, 988, 1226], [(55, 287), (307, 542), (562, 796)])),
    ("10.webp", grid(5, W5, [(90, 292), (470, 675)], inset=30)),
    ("11.webp", [(490, 100, 920, 530)]),
    ("12.webp", [(480, 165, 935, 495)]),
    ("13.png", [(240, 195, 790, 715)]),
    ("14.png", [(355, 175, 905, 675)]),
    ("15.webp", [(x0, y0, x0 + 235, y0 + h) for (y0, h) in ((127, 270), (462, 240))
                 for x0 in (78, 332, 587, 842, 1097)]),
]


def main(src: Path) -> None:
    OUT.mkdir(exist_ok=True)
    n = 0
    for name, boxes in SHEETS:
        sheet = Image.open(src / name).convert("RGB")
        for box in boxes:
            n += 1
            sheet.crop(box).save(OUT / f"u{n:02d}.png", optimize=True)
    print(f"cropped {n} logos into {OUT}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
