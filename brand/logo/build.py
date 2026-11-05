"""Builds the final N1 Crest asset set for the Mauricio Moya brand.

Run: python3 brand/logo/build.py  (writes SVGs next to this file).
PNG and ICO files come from render.sh, which uses headless Chrome.

The mark itself is pure geometry (no font), so it needs no outlining.
The lockup name uses Cinzel (Open Font License) as live text.
"""
from pathlib import Path

OUT = Path(__file__).parent
NAVY = "#0b1a2e"
IVORY = "#f6f1e7"
GOLD_SOLID = "#c9962f"
GOLD_STOPS = (("0", "#f6dc8f"), (".45", "#c9962f"), (".7", "#e8c260"), ("1", "#a8761d"))
SERIF = "Cinzel,'Trajan Pro',Optima,'Times New Roman',serif"
M_PATH = "M31 68V34L50 54L69 34V68"


def gold_defs() -> str:
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GOLD_STOPS)
    return (f'<defs><linearGradient id="gold" x1="0" y1="0" x2="1" y2="1" '
            f'gradientUnits="objectBoundingBox">{stops}</linearGradient></defs>')


def diamond(x: float, y: float, s: float = 2.6) -> str:
    return f'M{x:g} {y - s:g}L{x + s:g} {y:g}L{x:g} {y + s:g}L{x - s:g} {y:g}Z'


def crest(disc: str, ink: str, detail: bool = True) -> str:
    """The N1 Crest on a 100 x 100 grid. detail=False is the small-size cut."""
    parts = [f'<circle cx="50" cy="50" r="49" fill="{disc}"/>'] if disc != "none" else []
    if detail:
        diamonds = "".join(diamond(x, y) for x, y in ((50, 7.3), (92.7, 50), (50, 92.7), (7.3, 50)))
        parts += [
            f'<circle cx="50" cy="50" r="45" fill="none" stroke="{ink}" stroke-width="2.2"/>',
            f'<circle cx="50" cy="50" r="40.5" fill="none" stroke="{ink}" stroke-width="0.8"/>',
            f'<path d="{diamonds}" fill="{ink}"/>',
            f'<path d="{M_PATH}" fill="none" stroke="{ink}" stroke-width="9" stroke-miterlimit="6"/>',
        ]
    else:
        # Favicon cut: one bold ring, heavier and larger M, no hairlines or diamonds.
        parts += [
            f'<circle cx="50" cy="50" r="43" fill="none" stroke="{ink}" stroke-width="6"/>',
            '<path d="M27 71V31L50 55L73 31V71" fill="none" '
            f'stroke="{ink}" stroke-width="12" stroke-miterlimit="6"/>',
        ]
    return "".join(parts)


def svg(body: str, w: int, h: int, defs: str = "", label: str = "Mauricio Moya") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label}">{defs}{body}</svg>\n')


def lockup(name_fill: str, sub_fill: str) -> str:
    return (crest(NAVY, "url(#gold)")
            + f'<text x="122" y="52" font-family="{SERIF}" font-weight="900" font-size="30" '
              f'letter-spacing="3" fill="{name_fill}">MAURICIO MOYA</text>'
            + f'<text x="123" y="74" font-family="{SERIF}" font-weight="700" font-size="9.5" '
              f'letter-spacing="2.4" fill="{sub_fill}">FINANCE · TECHNOLOGY · COMPLIANCE · EDUCATION</text>')


ASSETS = {
    "crest.svg": (crest(NAVY, "url(#gold)"), 100, 100, True),
    "crest-gold.svg": (crest("none", GOLD_SOLID), 100, 100, False),
    "crest-mono-black.svg": (crest("none", "#000"), 100, 100, False),
    "crest-mono-white.svg": (crest("none", "#fff"), 100, 100, False),
    "favicon.svg": (crest(NAVY, GOLD_SOLID, detail=False), 100, 100, False),
    "lockup-light.svg": (lockup(NAVY, "#8a6a2a"), 520, 100, True),
    "lockup-dark.svg": (f'<rect width="520" height="100" fill="{NAVY}"/>' + lockup("#f3e3b5", "#c9a35a"),
                        520, 100, True),
}


def main() -> None:
    for name, (body, w, h, needs_gold) in ASSETS.items():
        (OUT / name).write_text(svg(body, w, h, gold_defs() if needs_gold else ""))
        print("wrote", name)


if __name__ == "__main__":
    main()
