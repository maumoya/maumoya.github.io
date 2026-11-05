#!/usr/bin/env python3
"""Scores all logo options with one transparent algorithm and writes results.json.

Run: python3 brand/logo-options/ranking/score.py <scratch-dir> [panel.json]

Score (0-100) = 35 measured + 60 designer rubric + 5 persona panel.

Measured (from real renders in headless Chrome, plus the SVG source):
  fid16   15  16 px fidelity: Pearson r between the 16 px render (upscaled) and the
              128 px render. Fine detail that dies at favicon size lowers r.
  contrast 5  WCAG ratio between the 2nd and 98th luminance percentile of the mark's centre.
  mono     5  one-colour readiness: how many hue families the mark needs (gold = 1).
  simple   5  fewer SVG elements and path commands = easier to reproduce.
  circle   5  owner's rule "circles work better": circle 1, shield .5, squircle .3, wordmark 0.
Rubric (judgment, 1-10 in candidates.json): lux 12, str 10, pro 10, per 10, mean 5, dis 7, time 6.
Panel (MiroFish persona swarm, opinion not evidence): Borda points from its top-10.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OPTIONS = HERE.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&display=swap" rel="stylesheet">'
BIG, SMALL = 128, 16

MEASURED_W = {"fid16": 15, "contrast": 5, "mono": 5, "simple": 5, "circle": 5}
JUDGE_W = {"lux": 12, "str": 10, "pro": 10, "per": 10, "mean": 5, "dis": 7, "time": 6}
PANEL_W = 5
SHAPE = {"circle": 1.0, "shield": 0.5, "squircle": 0.3, "wordmark": 0.0}


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def render(svg_path: Path, work: Path) -> tuple[Image.Image, Image.Image]:
    """One page holding the mark at 128 px and at 16 px, on ivory, inline so Cinzel applies."""
    body = svg_path.read_text()
    cell = '<div style="position:absolute;left:{x}px;top:0;width:{s}px;height:{s}px">{svg}</div>'
    sized = re.sub(r"<svg ", '<svg width="100%" height="100%" preserveAspectRatio="xMidYMid meet" ', body, count=1)
    page = (f'<html><head>{FONT}<style>body{{margin:0;background:#f6f1e7}}</style></head><body>'
            + cell.format(x=0, s=BIG, svg=sized) + cell.format(x=BIG + 8, s=SMALL, svg=sized)
            + "</body></html>")
    html, png = work / "score.html", work / "score.png"
    html.write_text(page)
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={BIG + 8 + SMALL},{BIG}", "--virtual-time-budget=2500",
                    f"--screenshot={png}", f"file://{html}"], check=True, capture_output=True)
    img = Image.open(png).convert("RGB")
    return img.crop((0, 0, BIG, BIG)), img.crop((BIG + 8, 0, BIG + 8 + SMALL, SMALL))


def pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** .5
    vb = sum((y - mb) ** 2 for y in b) ** .5
    return cov / (va * vb) if va and vb else 0.0


def rel_lum(v: float) -> float:
    c = v / 255
    return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4


def measure(big: Image.Image, small: Image.Image, svg_text: str, shape: str) -> dict:
    lum_big = list(big.convert("L").getdata())
    up = small.resize((BIG, BIG), Image.BICUBIC).convert("L")
    r = pearson(lum_big, list(up.getdata()))

    # Ink against its own ground: the centre of the mark, so a navy disc is not
    # compared with the page around it.
    centre = big.crop((BIG // 5, BIG // 5, BIG * 4 // 5, BIG * 4 // 5)).convert("L")
    lums = sorted(rel_lum(p) for p in centre.getdata())
    lo, hi = lums[len(lums) // 50], lums[-len(lums) // 50]
    ratio = (hi + .05) / (lo + .05)

    hues = {}
    for h, s, v in big.convert("HSV").getdata():
        if s > 90 and v > 60:
            hues[h // 21] = hues.get(h // 21, 0) + 1   # 12 hue families
    total = sum(hues.values()) or 1
    families = sum(1 for n in hues.values() if n / total > .03)
    families = families - 1 if families >= 2 and _adjacent_gold(hues, total) else families

    elements = len(re.findall(r"<(path|circle|rect|ellipse|text|line|polygon)\b", svg_text))
    commands = len(re.findall(r"[MLHVCSQTAZ]", " ".join(re.findall(r' d="([^"]+)"', svg_text))))
    glyphs = sum(len(t) for t in re.findall(r">([^<>]+)</(?:text|textPath)>", svg_text))
    complexity = elements + commands / 2 + glyphs

    return {
        "r16": round(r, 4), "contrast_ratio": round(ratio, 2), "hue_families": families,
        "complexity": round(complexity, 1),
        "fid16": clamp((r - .80) / .18),
        "contrast": clamp((ratio - 1) / 6),
        "mono": {0: 1.0, 1: 1.0, 2: .6}.get(families, .2),
        "simple": clamp(1 - (complexity - 8) / 60),
        "circle": SHAPE[shape],
    }


def _adjacent_gold(hues: dict, total: int) -> bool:
    """Gold gradients span two neighbouring hue bins; count them as one family."""
    big_bins = sorted(b for b, n in hues.items() if n / total > .03)
    return len(big_bins) == 2 and big_bins[1] - big_bins[0] == 1


def borda(panel: list[str], cid: str) -> float:
    return (len(panel) - panel.index(cid)) / len(panel) if cid in panel else 0.0


def main(work: Path, panel_file: str | None) -> None:
    data = json.loads((HERE / "candidates.json").read_text())
    panel = json.loads(Path(panel_file).read_text())["top"] if panel_file else []
    rows = []
    for c in data["candidates"]:
        path = OPTIONS / c["file"]
        big, small = render(path, work)
        small.save(work / f"{c['id']}-16.png")
        big.save(work / f"{c['id']}-128.png")
        m = measure(big, small, path.read_text(), c["shape"])
        measured = sum(m[k] * w for k, w in MEASURED_W.items())
        judged = sum((c["judge"][k] - 1) / 9 * w for k, w in JUDGE_W.items())
        pan = borda(panel, c["id"]) * PANEL_W
        rows.append({**c, "metrics": m, "measured": round(measured, 1), "judged": round(judged, 1),
                     "panel": round(pan, 1), "total": round(measured + judged + pan, 1)})
        print(f"{c['id']:>4} r16={m['r16']:.3f} cr={m['contrast_ratio']:>5} hues={m['hue_families']} "
              f"cx={m['complexity']:>5} total={rows[-1]['total']}")
    rows.sort(key=lambda x: -x["total"])
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    out = {"weights": {"measured": MEASURED_W, "judge": JUDGE_W, "panel": PANEL_W}, "panel_top": panel,
           "results": rows}
    (HERE / "results.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print("wrote results.json")


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
