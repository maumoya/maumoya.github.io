#!/usr/bin/env python3
"""Builds the logo option SVGs and the comparison page (index.html).

Run: python3 brand/logo-options/build.py
Every mark is pure geometry (no font needed). Lockups set the name in the
system UI font stack (SF Pro on Apple devices, free fallbacks elsewhere);
the chosen one gets outlined before production use.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

# One colour per area. Apple system palette values, readable on light and dark.
FIN, TEC, CMP, EDU = "#30b158", "#0a84ff", "#5e5ce6", "#ff9500"
AREAS = [("Finance", FIN), ("Technology", TEC), ("Compliance", CMP), ("Education", EDU)]

FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue',Inter,Arial,sans-serif"

# Classes swap with the theme: standalone files use prefers-color-scheme,
# the comparison page sets them per panel.
STANDALONE_STYLE = (
    "<style>.ink{fill:#1d1d1f}.paper{fill:#fff}.ink-s{stroke:#1d1d1f}.paper-s{stroke:#fff}"
    ".muted{fill:#6e6e73}"
    "@media(prefers-color-scheme:dark){.ink{fill:#f5f5f7}.paper{fill:#000}"
    ".ink-s{stroke:#f5f5f7}.paper-s{stroke:#000}.muted{fill:#a1a1a6}}</style>"
)

M_PATH = "M17 45V20L32 35L47 20V45"  # the shared M skeleton, 64-unit grid


def seg(x1, y1, x2, y2, color, w=6):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


# ---------- marks (64 x 64) ----------

def mark_strokes():
    """A. Four Strokes: an M drawn as four strokes, one per area, on a squircle."""
    pts = [(17, 45), (17, 20), (32, 35), (47, 20), (47, 45)]
    lines = "".join(seg(*pts[i], *pts[i + 1], c) for i, (_, c) in enumerate(AREAS))
    return f'<rect class="ink" width="64" height="64" rx="15"/>{lines}'


def mark_twin():
    """B. Twin: MM sharing one leg; the four diagonals read as a rising chart line."""
    legs = (f'<path class="ink-s" d="M8 47V17M32 17V47M56 47V17" fill="none" '
            f'stroke-width="6" stroke-linecap="round"/>')
    pts = [(8, 17), (20, 33), (32, 17), (44, 33), (56, 17)]
    diag = "".join(seg(*pts[i], *pts[i + 1], c) for i, (_, c) in enumerate(AREAS))
    return legs + diag


def mark_quad():
    """C. Quad: four area tiles, one white M across all of them."""
    tiles = "".join(
        f'<rect x="{x}" y="{y}" width="31" height="31" fill="{c}"/>'
        for (x, y), (_, c) in zip([(0, 0), (33, 0), (0, 33), (33, 33)], AREAS)
    )
    return (f'<clipPath id="qclip"><rect width="64" height="64" rx="15"/></clipPath>'
            f'<g clip-path="url(#qclip)">{tiles}</g>'
            f'<path d="{M_PATH}" fill="none" stroke="#fff" stroke-width="6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def mark_folio():
    """D. Folio: an open book whose page edges draw the M."""
    return (
        '<rect class="ink" width="64" height="64" rx="15"/>'
        '<path class="paper-s" d="M13 44V22Q22.5 15 32 23Q41.5 15 51 22V44" fill="none" '
        'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path class="paper-s" d="M32 23V47" fill="none" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M13 44Q22.5 39 32 47Q41.5 39 51 44" fill="none" stroke="{EDU}" '
        'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def mark_seal():
    """E. Seal: a shield (compliance) holding the M, with a ledger rule beneath."""
    return (
        '<path class="ink" d="M32 4L55 11.5V30C55 45 45 55 32 60C19 55 9 45 9 30V11.5Z"/>'
        '<path class="paper-s" d="M20 38V19L32 31L44 19V38" fill="none" stroke-width="5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        + "".join(
            f'<rect x="{19 + i * 7}" y="44" width="5" height="3" rx="1.5" fill="{c}"/>'
            for i, (_, c) in enumerate(AREAS)
        )
    )


MARKS = [
    ("a-four-strokes", "Four Strokes", mark_strokes,
     "One M, four strokes: each stroke is one area. Reads at 16 px as a solid tile."),
    ("b-twin", "Twin", mark_twin,
     "MM monogram sharing one leg. The four coloured diagonals double as a rising chart line."),
    ("c-quad", "Quad", mark_quad,
     "Four tiles, one per area, held together by a single M. Strongest favicon."),
    ("d-folio", "Folio", mark_folio,
     "The M drawn as an open book; spine and pages for education, ledger base line in warm accent."),
    ("e-seal", "Seal", mark_seal,
     "Shield for compliance and trust, M inside, four-area rule beneath. Most formal."),
]


# ---------- wordmarks / lockups ----------

def name_text(x, y, size, moya_fill='class="ink"'):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="600" '
            f'letter-spacing="-0.6"><tspan class="ink">Mauricio </tspan>'
            f'<tspan {moya_fill}>Moya</tspan></text>')


def tagline(x, y, size=10.5):
    return (f'<text class="muted" x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="500" letter-spacing="0.4">Finance · Technology · Compliance · Education</text>')


def lockup(mark_fn):
    return f'<g>{mark_fn()}</g>{name_text(80, 36, 28)}{tagline(81, 55)}'


def wordmark_gradient():
    """F. Wordmark: the name alone, 'Moya' carrying the four-area gradient."""
    grad = ('<linearGradient id="wg" x1="0" x2="1"><stop offset="0" stop-color="' + FIN +
            '"/><stop offset=".35" stop-color="' + TEC + '"/><stop offset=".68" stop-color="' + CMP +
            '"/><stop offset="1" stop-color="' + EDU + '"/></linearGradient>')
    name = name_text(0, 36, 34, moya_fill='fill="url(#wg)"')
    return f'<defs>{grad}</defs>{name}{tagline(1, 56, 11)}'


def svg(body, w, h, standalone=True, label=""):
    style = STANDALONE_STYLE if standalone else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label}">{style}{body}</svg>')


def main():
    files = []
    for slug, name, fn, _ in MARKS:
        (OUT / f"{slug}-mark.svg").write_text(svg(fn(), 64, 64, label=f"Mauricio Moya, {name} mark") + "\n")
        (OUT / f"{slug}-lockup.svg").write_text(svg(lockup(fn), 350, 64, label="Mauricio Moya") + "\n")
        files += [f"{slug}-mark.svg", f"{slug}-lockup.svg"]
    (OUT / "f-wordmark.svg").write_text(svg(wordmark_gradient(), 290, 64, label="Mauricio Moya") + "\n")
    files.append("f-wordmark.svg")
    (OUT / "index.html").write_text(page())
    print("\n".join(files + ["index.html"]))


# ---------- comparison page ----------

def row(slug, name, desc, mark_body, lockup_body, lockup_w):
    def panel(theme):
        return f'''<div class="panel {theme}">
  <div class="sizes">
    <figure><div class="hero">{svg(mark_body, 64, 64, False)}</div><figcaption>App icon · 120</figcaption></figure>
    <figure><div class="fav32">{svg(mark_body, 64, 64, False)}</div><figcaption>32</figcaption></figure>
    <figure><div class="fav16">{svg(mark_body, 64, 64, False)}</div><figcaption>16</figcaption></figure>
  </div>
  <div class="tab"><span class="tabicon">{svg(mark_body, 64, 64, False)}</span>Mauricio Moya</div>
  <nav class="nav"><span class="navmark">{svg(mark_body, 64, 64, False)}</span>
    <span>Finance</span><span>Development</span><span>Compliance</span><span>Education</span></nav>
  <div class="lock">{svg(lockup_body, lockup_w, 64, False)}</div>
</div>'''
    return f'''<section class="opt" id="{slug}">
<header><h2>{slug[0].upper()}. {name}</h2><p>{desc}</p></header>
<div class="panels">{panel("light")}{panel("dark")}</div>
</section>'''


def page():
    rows = "".join(row(s, n, d, fn(), lockup(fn), 350) for s, n, fn, d in MARKS)
    wm = svg(wordmark_gradient(), 290, 64, False)
    legend = "".join(f'<li><i style="background:{c}"></i>{a}</li>' for a, c in AREAS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Logo Options · Mauricio Moya</title>
<style>
:root{{--bg:#f5f5f7;--fg:#1d1d1f;--muted:#6e6e73}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 {FONT};padding:40px 20px 80px}}
main{{max-width:1100px;margin:0 auto}}
h1{{font-size:40px;letter-spacing:-.03em;margin:0 0 6px}}
.lead{{color:var(--muted);margin:0 0 14px;max-width:62ch}}
.legend{{display:flex;flex-wrap:wrap;gap:16px;list-style:none;padding:0;margin:0 0 40px;color:var(--muted);font-size:13px}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}}
.opt{{margin:0 0 56px}}
.opt header h2{{font-size:24px;letter-spacing:-.02em;margin:0}}
.opt header p{{color:var(--muted);margin:2px 0 14px}}
.panels{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:760px){{.panels{{grid-template-columns:1fr}}}}
.panel{{border-radius:20px;padding:24px;display:grid;gap:20px;overflow:hidden}}
.light{{background:#fff;color:#1d1d1f}}
.dark{{background:#000;color:#f5f5f7}}
.light .ink{{fill:#1d1d1f}}.light .paper{{fill:#fff}}.light .ink-s{{stroke:#1d1d1f}}.light .paper-s{{stroke:#fff}}.light .muted{{fill:#6e6e73}}
.dark .ink{{fill:#f5f5f7}}.dark .paper{{fill:#000}}.dark .ink-s{{stroke:#f5f5f7}}.dark .paper-s{{stroke:#000}}.dark .muted{{fill:#a1a1a6}}
.sizes{{display:flex;align-items:flex-end;gap:28px}}
figure{{margin:0;display:grid;justify-items:center;gap:8px}}
figcaption{{font-size:11px;opacity:.55}}
svg{{display:block}}
.hero svg{{width:120px;height:120px}}
.fav32 svg{{width:32px;height:32px}}
.fav16 svg{{width:16px;height:16px}}
.tab{{display:flex;align-items:center;gap:8px;font-size:12px;padding:8px 12px;border-radius:10px 10px 0 0;width:max-content;max-width:100%}}
.light .tab{{background:#e8e8ed}}.dark .tab{{background:#1d1d1f}}
.tabicon svg{{width:16px;height:16px}}
.nav{{display:flex;align-items:center;gap:22px;height:44px;padding:0 16px;font-size:12px;border-radius:12px;overflow-x:auto;white-space:nowrap}}
.light .nav{{background:rgba(0,0,0,.04)}}.dark .nav{{background:#161617}}
.navmark svg{{width:22px;height:22px}}
.lock{{overflow-x:auto}}
.lock svg{{width:350px;max-width:100%;height:auto}}
.wm{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
@media(max-width:760px){{.wm{{grid-template-columns:1fr}}}}
.wm .panel svg{{width:100%;max-width:420px;height:auto}}
.wm .nav svg{{width:auto;height:22px}}
footer{{color:var(--muted);font-size:13px;margin-top:40px}}
</style></head>
<body><main>
<h1>Logo options</h1>
<p class="lead">Six directions for the Mauricio Moya mark. Each is shown on light and dark, at app-icon,
favicon (32 and 16 px), browser tab and 44 px header size, plus the full lockup.
The four colours stand for the four areas:</p>
<ul class="legend">{legend}</ul>
{rows}
<section class="opt" id="f-wordmark">
<header><h2>F. Wordmark</h2><p>No symbol. The name alone, with “Moya” carrying the four-area gradient, like a product name. Pairs with any mark above for the favicon.</p></header>
<div class="wm">
<div class="panel light">{wm}<nav class="nav">{wm}<span>Finance</span><span>Development</span></nav></div>
<div class="panel dark">{wm}<nav class="nav">{wm}<span>Finance</span><span>Development</span></nav></div>
</div></section>
<footer>Marks are pure geometry. Lockups use the system font (SF Pro on Apple devices) and will be outlined to paths once one is chosen. Regenerate with <code>python3 brand/logo-options/build.py</code>.</footer>
</main></body></html>
'''


if __name__ == "__main__":
    main()
