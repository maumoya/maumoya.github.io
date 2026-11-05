#!/usr/bin/env python3
"""Builds the luxury round (N1-N7) logo SVGs and luxe.html.

Run: python3 brand/logo-options/luxe/build.py
Gold on navy, circle-based, heavy letterforms. Lettering uses Cinzel
(SIL Open Font License, free); it gets outlined to paths once one is chosen.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

NAVY, IVORY = "#0b1a2e", "#f6f1e7"
GOLD_STOPS = (("0", "#f6dc8f"), (".45", "#c9962f"), (".7", "#e8c260"), ("1", "#a8761d"))
SERIF = "Cinzel,'Trajan Pro',Optima,'Times New Roman',serif"
AREAS = "FINANCE · TECHNOLOGY · COMPLIANCE · EDUCATION"


def defs():
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GOLD_STOPS)
    return (f'<defs><linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">{stops}</linearGradient>'
            '<path id="rim" d="M50 89.5A39.5 39.5 0 1 1 50 10.5A39.5 39.5 0 1 1 50 89.5"/></defs>')


G = 'stroke="url(#gold)" fill="none"'
GF = 'fill="url(#gold)"'


def heavy(d, w=8):
    return f'<path d="{d}" {G} stroke-width="{w}" stroke-linejoin="miter" stroke-miterlimit="6"/>'


def ring(r, w):
    return f'<circle cx="50" cy="50" r="{r}" {G} stroke-width="{w}"/>'


def disc():
    return '<circle class="disc" cx="50" cy="50" r="49"/>'


def diamond(x, y, s=2.6):
    return f'<path d="M{x} {y - s}L{x + s} {y}L{x} {y + s}L{x - s} {y}Z" {GF}/>'


# ---------- marks (100 x 100) ----------

def n1_crest():
    return (disc() + ring(45, 2.2) + ring(40.5, .8)
            + "".join(diamond(x, y) for x, y in ((50, 7.3), (92.7, 50), (50, 92.7), (7.3, 50)))
            + heavy("M31 68V34L50 54L69 34V68", 9))


def n2_signet():
    return disc() + ring(41, 6) + heavy("M29 71V30L50 52L71 30V71M50 52V91", 7.5)


def n3_quadrant():
    letters = "".join(
        f'<text x="{x}" y="{y}" {GF} font-family="{SERIF}" font-weight="700" font-size="21" '
        f'text-anchor="middle">{c}</text>'
        for c, x, y in (("M", 34, 44), ("O", 66, 44), ("Y", 34, 74), ("A", 66, 74)))
    return (disc() + ring(45, 2.4)
            + f'<path d="M50 17V83M17 50H83" {G} stroke-width="1.4"/>' + letters)


def n4_twin_ring():
    return disc() + ring(44, 3) + heavy("M20 68V34L35 54L50 34V68M50 34L65 54L80 34V68", 7.5)


def n5_pillar():
    cols = (f'<rect x="27" y="35" width="10" height="33" {GF}/><rect x="63" y="35" width="10" height="33" {GF}/>'
            f'<rect x="24" y="31" width="16" height="4" {GF}/><rect x="60" y="31" width="16" height="4" {GF}/>'
            f'<rect x="22" y="70" width="56" height="5" {GF}/>')
    return disc() + ring(44, 3) + cols + heavy("M37 37L50 55L63 37", 7)


def n7_coin():
    rim_text = (f'<text {GF} font-family="{SERIF}" font-weight="700" font-size="5.6">'
                f'<textPath href="#rim" textLength="244" lengthAdjust="spacing">'
                f'MAURICIO MOYA · {AREAS} ·</textPath></text>')
    return (disc() + ring(47, 1.6) + ring(33, 1.2) + rim_text
            + heavy("M36 63V38L50 53L64 38V63", 7))


def n6_wordmark():
    """M + gold ring O with a four-point star + YA. 260 x 100."""
    star = '<path d="M130 40L132.2 47.8L140 50L132.2 52.2L130 60L127.8 52.2L120 50L127.8 47.8Z" fill="url(#gold)"/>'
    txt = f'font-family="{SERIF}" font-weight="900" font-size="58" {GF}'
    return (f'<text x="104" y="71" text-anchor="end" {txt}>M</text>'
            f'<circle cx="130" cy="50" r="20" {G} stroke-width="7"/>{star}'
            f'<text x="156" y="71" {txt}>YA</text>'
            f'<text x="130" y="92" text-anchor="middle" class="sub" font-family="{SERIF}" '
            f'font-weight="700" font-size="5.8" letter-spacing="1.5">{AREAS}</text>')


MARKS = [
    ("n1-crest", "Crest", n1_crest, "Your Seal, made round: heavy M, double gold ring, four diamonds = four areas."),
    ("n2-signet", "Signet", n2_signet, "The ring is the O; the M drops into a Y stem. M, O and Y in one mark."),
    ("n3-quadrant", "Quadrant", n3_quadrant, "M O / Y A in four quarters, one per area. Business-card luxury; blurs at 16 px."),
    ("n4-twin-ring", "Twin Ring", n4_twin_ring, "MM sharing one leg inside a gold ring; the zig-zag doubles as a rising chart."),
    ("n5-pillar", "Pillar", n5_pillar, "M as two classical columns: bank, academy, institution."),
    ("n7-coin", "Coin", n7_coin, "Coin seal: heavy M, name and four areas on the rim. For large sizes only."),
]


def lockup(mark_fn, stacked=False):
    name = (f'<text class="name" x="118" y="52" font-family="{SERIF}" font-weight="900" font-size="30" '
            f'letter-spacing="3">MAURICIO MOYA</text>'
            f'<text class="sub" x="119" y="72" font-family="{SERIF}" font-weight="700" font-size="9.2" '
            f'letter-spacing="2.2">{AREAS}</text>')
    return f'<g>{mark_fn()}</g>{name}'


STYLE = (f"<style>.disc{{fill:{NAVY}}}.name{{fill:{NAVY}}}.sub{{fill:#8a6a2a}}"
         f"@media(prefers-color-scheme:dark){{.name{{fill:#f3e3b5}}.sub{{fill:#c9a35a}}}}</style>")


def svg(body, w, h, standalone=True):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="Mauricio Moya">{STYLE if standalone else ""}{defs()}{body}</svg>')


LOCK_W = 500


def main():
    for slug, _, fn, _ in MARKS:
        (OUT / f"{slug}-mark.svg").write_text(svg(fn(), 100, 100) + "\n")
        (OUT / f"{slug}-lockup.svg").write_text(svg(lockup(fn), LOCK_W, 100) + "\n")
    (OUT / "n6-wordmark.svg").write_text(svg(n6_wordmark(), 260, 100) + "\n")
    (OUT / "index.html").write_text(page())


# ---------- page ----------

def panel(theme, mark, lock):
    return f'''<div class="panel {theme}">
<div class="sizes"><figure><div class="hero">{mark}</div><figcaption>120</figcaption></figure>
<figure><div class="f32">{mark}</div><figcaption>32</figcaption></figure>
<figure><div class="f16">{mark}</div><figcaption>16</figcaption></figure></div>
<nav class="nav"><span class="nm">{mark}</span><span>Finance</span><span>Development</span><span>Compliance</span><span>Education</span></nav>
<div class="lock">{lock}</div></div>'''


def section(slug, name, desc, mark, lock):
    return (f'<section id="{slug}"><h2>{slug.split("-")[0].upper()} · {name}</h2><p>{desc}</p>'
            f'<div class="panels">{panel("dark", mark, lock)}{panel("light", mark, lock)}</div></section>')


def page():
    secs = "".join(section(s, n, d, svg(fn(), 100, 100, False), svg(lockup(fn), LOCK_W, 100, False))
                   for s, n, fn, d in MARKS)
    wm = svg(n6_wordmark(), 260, 100, False)
    wm_sec = (f'<section id="n6-wordmark"><h2>N6 · Wordmark</h2><p>MOYA in heavy Roman capitals; the O is a gold '
              f'ring with a four-point star (four areas). Fashion-house feel; pair with N1 as favicon.</p>'
              f'<div class="panels"><div class="panel dark"><div class="wm">{wm}</div></div>'
              f'<div class="panel light"><div class="wm">{wm}</div></div></div></section>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Luxe Logo Options · Mauricio Moya</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#07111f;color:#efe6d2;font:15px/1.5 -apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;padding:40px 20px 80px}}
main{{max-width:1120px;margin:0 auto}}
h1{{font:900 40px/1.1 {SERIF};letter-spacing:.06em;margin:0 0 8px;color:#e8c260}}
.lead{{color:#b9ad95;max-width:64ch;margin:0 0 36px}}
section{{margin:0 0 56px}}
h2{{font:700 22px {SERIF};letter-spacing:.08em;margin:0;color:#f3e3b5}}
section>p{{color:#b9ad95;margin:2px 0 14px}}
.panels{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:780px){{.panels{{grid-template-columns:1fr}}}}
.panel{{border-radius:20px;padding:24px;display:grid;gap:20px;overflow:hidden}}
.dark{{background:{NAVY};color:#f3e3b5;border:1px solid #1d3150}}
.light{{background:{IVORY};color:{NAVY}}}
.dark .name{{fill:#f3e3b5}}.dark .sub{{fill:#c9a35a}}.light .name{{fill:{NAVY}}}.light .sub{{fill:#8a6a2a}}
.disc{{fill:{NAVY}}}
.light .disc{{fill:{NAVY}}}
.sizes{{display:flex;align-items:flex-end;gap:28px}}
figure{{margin:0;display:grid;justify-items:center;gap:8px}}figcaption{{font-size:11px;opacity:.55}}
svg{{display:block}}
.hero svg{{width:120px;height:120px}}.f32 svg{{width:32px;height:32px}}.f16 svg{{width:16px;height:16px}}
.nav{{display:flex;align-items:center;gap:22px;height:44px;padding:0 16px;font-size:12px;border-radius:12px;overflow-x:auto;white-space:nowrap}}
.dark .nav{{background:#06101d}}.light .nav{{background:rgba(11,26,46,.06)}}
.nm svg{{width:26px;height:26px}}
.lock svg{{width:100%;max-width:440px;height:auto}}
.wm svg{{width:100%;max-width:460px;height:auto}}
#rank table{{width:100%;border-collapse:collapse;font-size:14px}}
#rank th,#rank td{{text-align:left;padding:8px 10px;border-bottom:1px solid #1d3150;vertical-align:top}}
#rank th{{color:#e8c260;font-weight:600}}
.tw{{overflow-x:auto}}
footer{{color:#8d826d;font-size:13px}}
</style></head><body><main>
<h1>MAURICIO MOYA</h1>
<p class="lead">Round two: luxury, circle-based, heavy letters. Gold on navy and on ivory, at 120, 32 and 16 px,
in a 44 px header and as a full lockup. Lettering is Cinzel (free, Open Font License).</p>
<section id="rank"><h2>Ranking · MiroFish swarm</h2>
<p>22 candidates (this round, round one and the owner's references) described in text to a MiroFish swarm,
3 rounds on a simulated Reddit and Twitter, 2026-11-05. Confidence 0.35: simulated opinion, not evidence.</p>
<div class="tw"><table><tr><th>#</th><th>Logo</th><th>Why (swarm)</th></tr>
<tr><td>1</td><td><a href="#n1-crest">N1 Crest</a></td><td>Luxury restraint; four diamonds tie to the four areas; only one to pass the 16 px test.</td></tr>
<tr><td>2</td><td><a href="#n7-coin">N7 Coin</a></td><td>Formal seal; rim text only works large.</td></tr>
<tr><td>3</td><td>R4 Outline MOA (reference)</td><td>Architectural, but fails at 16 px.</td></tr>
<tr><td>4</td><td>R1 Lion (reference)</td><td>Powerful, but fails at 16 px.</td></tr>
<tr><td>5</td><td>A6 Gradient wordmark (round one)</td><td>Reads like a software product, not luxury.</td></tr>
</table></div></section>
{secs}{wm_sec}
<footer>Regenerate with <code>python3 brand/logo-options/luxe/build.py</code>. Round one (colour, Apple-style) is in <code>brand/logo-options/index.html</code>.</footer>
</main></body></html>
'''


if __name__ == "__main__":
    main()
