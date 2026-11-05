#!/usr/bin/env python3
"""Round 3: fifteen more circle + gold marks (N8-N22) for the Mauricio Moya brand.

Run: python3 brand/logo-options/round3/build.py
Reuses the helpers of the luxury round so colours and gold match exactly.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "luxe"))
from build import G, GF, NAVY, SERIF, diamond, disc, heavy, ring, svg  # noqa: E402

# Gold gradient in canvas units, for straight lines (a bounding-box gradient on a
# perfectly horizontal or vertical line has zero area and draws nothing).
LINE_DEFS = ('<defs><linearGradient id="goldU" gradientUnits="userSpaceOnUse" x1="0" y1="0" '
             'x2="100" y2="100"><stop offset="0" stop-color="#f6dc8f"/><stop offset=".45" '
             'stop-color="#c9962f"/><stop offset=".7" stop-color="#e8c260"/><stop offset="1" '
             'stop-color="#a8761d"/></linearGradient></defs>')
GL = 'stroke="url(#goldU)" fill="none"'


def n8_deco() -> str:
    """Art-deco M: one heavy stroke split into three gold lines."""
    m = "M30 70V33L50 55L70 33V70"
    inner = (f'<path d="{m}" stroke="{NAVY}" fill="none" stroke-width="7.6" stroke-miterlimit="6"/>'
             f'<path d="{m}" {G} stroke-width="2.4" stroke-miterlimit="6"/>')
    return disc() + ring(45, 2) + ring(41, .8) + heavy(m, 12.5) + inner


def n9_my_ring() -> str:
    """A ring broken at the bottom; the M's middle drops through it as a Y stem."""
    arc = f'<path d="M38 90.25A42 42 0 1 1 62 90.25" {G} stroke-width="5.5"/>'
    return disc() + arc + heavy("M30 72V30L50 52L70 30V72M50 52V97", 8)


def n10_outline() -> str:
    """Engraved look: an M drawn as a double outline inside a double ring."""
    m = "M30 70V32L50 54L70 32V70"
    return (disc() + ring(45, 2.4) + ring(40, 1)
            + heavy(m, 11) + f'<path d="{m}" stroke="{NAVY}" fill="none" stroke-width="5" '
            'stroke-linejoin="miter" stroke-miterlimit="6"/>')


def n11_laurel() -> str:
    """Heavy M framed by two laurel branches: academy, excellence."""
    leaves = []
    for i in range(6):
        y = 74 - i * 8
        leaves.append(f'<ellipse cx="{22 + i * 1.2}" cy="{y}" rx="2.6" ry="5.5" transform="rotate(-30 {22 + i * 1.2} {y})" {GF}/>')
        leaves.append(f'<ellipse cx="{78 - i * 1.2}" cy="{y}" rx="2.6" ry="5.5" transform="rotate(30 {78 - i * 1.2} {y})" {GF}/>')
    return disc() + ring(46, 1.6) + "".join(leaves) + heavy("M35 66V36L50 53L65 36V66", 8)


def n12_keystone() -> str:
    """M under a keystone arch: bank facade, stability."""
    arch = f'<path d="M26 72V44A24 24 0 0 1 74 44V72" {G} stroke-width="3"/>'
    key = f'<path d="M45 17H55L53 26H47Z" {GF}/>'
    return disc() + ring(45, 2.4) + arch + key + heavy("M35 70V42L50 57L65 42V70", 8)


def n13_compass() -> str:
    """Four-point compass star behind a heavy M: four areas, one direction."""
    star = f'<path d="M50 8L56 44L92 50L56 56L50 92L44 56L8 50L44 44Z" {GF} opacity=".28"/>'
    return disc() + ring(45, 2) + star + heavy("M32 67V35L50 54L68 35V67", 9)


def n14_shield() -> str:
    """Round seal with a shield silhouette holding the M: compliance, trust."""
    shield = f'<path d="M50 18L76 27V50C76 66 64 77 50 83C36 77 24 66 24 50V27Z" {G} stroke-width="3"/>'
    return disc() + ring(45, 2) + shield + heavy("M37 64V38L50 52L63 38V64", 7.5)


def n15_facet() -> str:
    """M cut like a gem: four facets in two gold tones."""
    f1 = f'<path d="M28 70V30L50 53V65L38 52V70Z" {GF}/>'
    f2 = '<path d="M72 70V30L50 53V65L62 52V70Z" fill="#a8761d"/>'
    return disc() + ring(45, 2.2) + f1 + f2


def n16_rays() -> str:
    """Heavy M with four groups of three rays on the ring: four areas radiating."""
    rays = []
    for cx, cy, dx, dy in ((50, 4, 0, 1), (96, 50, -1, 0), (50, 96, 0, -1), (4, 50, 1, 0)):
        for k in (-4, 0, 4):
            x1, y1 = cx + k * dy, cy + k * dx
            rays.append(f'<path d="M{x1} {y1}l{dx * 7} {dy * 7}" {GL} stroke-width="2.2"/>')
    return disc() + ring(38, 2) + "".join(rays) + heavy("M33 66V36L50 54L67 36V66", 8.5)


def n17_mw_diamond() -> str:
    """M above, mirrored M below: a diamond of two Ms (Mauricio Moya, MM)."""
    return (disc() + ring(45, 2)
            + heavy("M28 48V24L50 42L72 24V48", 6.5) + heavy("M28 52V76L50 58L72 76V52", 6.5))


def n18_didone() -> str:
    """High-contrast classic serif M built from thick and thin strokes."""
    # Thin left stem, thick left diagonal, thin right diagonal, thick right stem, bracket serifs.
    # Filled shapes, not strokes: a gradient stroke on a perfectly vertical line renders nothing.
    body = (f'<rect x="31.7" y="31" width="2.6" height="39" {GF}/>'
            f'<rect x="61" y="31" width="8" height="39" {GF}/>'
            f'<path d="M31.7 31H39.5L54 62L50 70Z" {GF}/>'
            f'<path d="M61 31H63.2L51.4 70H50Z" {GF}/>'
            f'<rect x="26" y="29" width="12" height="2.4" {GF}/><rect x="60" y="29" width="14" height="2.4" {GF}/>'
            f'<rect x="26" y="69" width="13" height="2.4" {GF}/><rect x="57" y="69" width="17" height="2.4" {GF}/>')
    return disc() + ring(45, 1.6) + ring(42, .6) + body


def n19_moya_ring() -> str:
    """Bold MOYA around the rim, heavy M centre; a coin you can still read."""
    txt = (f'<text {GF} font-family="{SERIF}" font-weight="900" font-size="12" letter-spacing="3">'
           '<textPath href="#rim" startOffset="50%" text-anchor="middle">MOYA</textPath></text>')
    return disc() + ring(30, 1.6) + txt + heavy("M38 61V40L50 52L62 40V61", 6.5)


def n20_reverse() -> str:
    """Solid gold coin with the M cut out in navy: negative space."""
    return (f'<circle cx="50" cy="50" r="48" {GF}/><circle cx="50" cy="50" r="42" fill="none" '
            f'stroke="{NAVY}" stroke-width="1.2"/>'
            f'<path d="M31 68V34L50 54L69 34V68" stroke="{NAVY}" fill="none" stroke-width="9.5" '
            'stroke-miterlimit="6"/>')


def n21_ledger() -> str:
    """M over three ledger lines: finance, records, compliance."""
    lines = "".join(f'<path d="M24 {y}H76" {GL} stroke-width="2"/>' for y in (66, 72, 78))
    return disc() + ring(45, 2.2) + lines + heavy("M31 58V26L50 45L69 26V58", 8.5)


def n22_circuit() -> str:
    """Heavy M whose feet end in circuit nodes: technology, precision."""
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="4" {GF}/>' for x, y in ((31, 74), (69, 74), (50, 26)))
    trace = f'<path d="M50 54V26" {GL} stroke-width="2.4"/>'
    return disc() + ring(45, 2) + trace + nodes + heavy("M31 74V34L50 54L69 34V74", 8)


MARKS = [
    ("n8-deco", "Deco", n8_deco, "Art-deco M split into three gold lines. Hotel and jewellery feel."),
    ("n9-my-ring", "MY Ring", n9_my_ring, "Ring broken at the bottom; the M drops into a Y stem. Modern monogram."),
    ("n10-engraved", "Engraved", n10_outline, "M drawn as a double outline, like engraved metal."),
    ("n11-laurel", "Laurel", n11_laurel, "M framed by laurel branches: academy, excellence."),
    ("n12-keystone", "Keystone", n12_keystone, "M under a keystone arch: bank facade, stability."),
    ("n13-compass", "Compass", n13_compass, "Four-point compass star behind the M: four areas, one direction."),
    ("n14-shield", "Shield Seal", n14_shield, "Shield inside a round seal: compliance, trust."),
    ("n15-facet", "Facet", n15_facet, "M cut like a gem in two gold tones."),
    ("n16-rays", "Rays", n16_rays, "Four groups of rays: four areas radiating from one M."),
    ("n17-mm-diamond", "MM Diamond", n17_mw_diamond, "M and mirrored M form a diamond: Mauricio Moya."),
    ("n18-didone", "Didone", n18_didone, "High-contrast classic serif M, fashion-house luxury."),
    ("n19-moya-ring", "MOYA Ring", n19_moya_ring, "MOYA in bold caps on the rim, M in the centre."),
    ("n20-reverse", "Gold Coin", n20_reverse, "Solid gold coin, navy M cut out. Strongest at small sizes."),
    ("n21-ledger", "Ledger", n21_ledger, "M over three ledger lines: finance and records."),
    ("n22-circuit", "Circuit", n22_circuit, "M feet end in circuit nodes: technology."),
]


def main() -> None:
    for slug, _name, fn, _desc in MARKS:
        (HERE / f"{slug}-mark.svg").write_text(svg(LINE_DEFS + fn(), 100, 100) + "\n")
        print("wrote", slug)


if __name__ == "__main__":
    main()
