#!/usr/bin/env python3
"""Builds the ranking page (index.html) and the live-poll page from results.json.

Run: python3 brand/logo-options/ranking/build_page.py <scratch-dir-with-16px-pngs> [poll-out.html]
"""
from __future__ import annotations

import base64
import json
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPTIONS = HERE.parent
TOP_N = 20
POLL_URL = "https://claude.ai/code/artifact/cfba5155-7d0b-4877-89d2-753203542d74"

LABEL = {"fid16": "16 px fidelity", "contrast": "Contrast", "mono": "One colour", "simple": "Simplicity",
         "circle": "Circle form", "lux": "Luxury", "str": "Letter strength", "pro": "Professional",
         "per": "Personality fit", "mean": "Meaning", "dis": "Distinctive", "time": "Timeless"}


def inline_svg(cid: str, path: Path) -> str:
    """SVG ready to inline: ids namespaced per candidate so gradients never collide."""
    body = re.sub(r"<\?xml[^>]*>", "", path.read_text()).strip()
    ids = set(re.findall(r'id="([^"]+)"', body))
    for i in ids:
        body = body.replace(f'id="{i}"', f'id="{cid}-{i}"').replace(f"url(#{i})", f"url(#{cid}-{i})")
        body = body.replace(f'href="#{i}"', f'href="#{cid}-{i}"')
    return re.sub(r"<svg ", '<svg width="100%" height="100%" ', body, count=1)


def png_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def is_raster(r: dict) -> bool:
    return r["file"].endswith(".png")


def mark(r: dict, work: Path | None) -> str:
    """The mark as shown: inline SVG, or the owner's crop (linked on the site, embedded in the poll)."""
    if not is_raster(r):
        return inline_svg(r["id"], OPTIONS / r["file"])
    src = png_uri(work / f"{r['id']}-128.png") if work else f"../{r['file']}"
    return f"<img src='{src}' alt='{escape(r['name'])}' loading='lazy' style='width:100%;height:100%;object-fit:contain'>"


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')

BASE_CSS = """
/* Layout: one centred column, a vault-like navy header band, data tables below. */
:root{--ink:#0b1a2e;--paper:#f7f4ee;--panel:#ffffff;--line:#e2dccf;--muted:#5d6675;--gold:#a8761d;
--gold-hi:#c9962f;--band:#0b1a2e;--band-ink:#f3e3b5;--bar:#c9962f;--good:#2f7a4f;--up:#1f7a45;--down:#b3261e;
--display:"Cinzel",Optima,"Palatino Linotype",serif;--body:"IBM Plex Sans",-apple-system,"Segoe UI",sans-serif;
--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#efe7d6;--paper:#081220;--panel:#18293f;
--line:#22324a;--muted:#9aa5b5;--gold:#e1b866;--gold-hi:#e8c260;--band:#040a14;--bar:#d6aa4c;--good:#6cc493;--up:#5fd08f;--down:#ff8a80;color-scheme:dark}}
:root[data-theme="dark"]{--ink:#efe7d6;--paper:#081220;--panel:#18293f;--line:#22324a;--muted:#9aa5b5;--gold:#e1b866;
--gold-hi:#e8c260;--band:#040a14;--bar:#d6aa4c;--good:#6cc493;--up:#5fd08f;--down:#ff8a80;color-scheme:dark}
body{background:var(--paper);color:var(--ink);font:15px/1.55 var(--body)}
.wrap{max-width:1180px;margin:0 auto;padding-block:0 64px;padding-left:max(16px,env(safe-area-inset-left,0px));
padding-right:max(16px,env(safe-area-inset-right,0px))}
.band{background:var(--band);color:var(--band-ink)}
.band .wrap{padding-block:48px 40px}
h1,h2{font-family:var(--display);font-weight:900;letter-spacing:.04em;text-wrap:balance;margin:0}
h1{font-size:clamp(28px,5vw,46px)}
h2{font-size:22px;margin-block:44px 14px}
.eyebrow{font:500 12px/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--gold-hi)}
.lede{max-width:66ch;color:inherit;opacity:.86}
p{max-width:68ch}
.mv{font:600 12px var(--mono);white-space:nowrap}.mv.up{color:var(--up)}.mv.dn{color:var(--down)}
.mv.new{color:var(--gold)}.mv.eq{color:var(--muted)}
.num{font-variant-numeric:tabular-nums;font-family:var(--mono)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th{font:600 11px/1.2 var(--body);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);vertical-align:bottom}
td.l,th.l{text-align:left}
tr:last-child td{border-bottom:0}
.mk{width:44px;height:44px;display:block}
.px16{width:16px;height:16px;image-rendering:pixelated;vertical-align:middle}
.px16x{width:48px;height:48px;image-rendering:pixelated;vertical-align:middle;margin-left:6px}
.vote{display:inline-block;font:600 14px var(--body);padding:10px 18px;border-radius:6px;background:var(--gold);color:var(--band);text-decoration:none}
.bar{display:inline-block;height:6px;background:var(--bar);border-radius:3px;vertical-align:middle;margin-left:8px}
.top td{background:color-mix(in srgb,var(--gold-hi) 9%,transparent)}
.cut td{border-bottom:2px solid var(--gold)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-block:12px}
.chip{font:500 13px var(--body);padding:6px 12px;border-radius:16px;border:1px solid var(--line);
background:var(--panel);color:var(--ink);cursor:pointer}
.chip[aria-pressed="true"]{border-color:var(--gold);box-shadow:0 0 0 1px var(--gold) inset}
.src{font:500 10px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.src.owner{color:var(--gold)}
"""


def move(now: int, before: int | None) -> str:
    """Rank change badge: green up, red down, gold NEW, grey dash."""
    if before is None:
        return "<span class='mv new' title='not in the previous ranking'>NEW</span>"
    d = before - now
    if d > 0:
        return f"<span class='mv up' title='was #{before}'>&#9650;{d}</span>"
    if d < 0:
        return f"<span class='mv dn' title='was #{before}'>&#9660;{-d}</span>"
    return f"<span class='mv eq' title='was #{before}'>&ndash;</span>"


def previous_ranks() -> dict[str, int]:
    f = HERE / "previous.json"
    return {r["id"]: r["rank"] for r in json.loads(f.read_text())["results"]} if f.exists() else {}


def ranking_page(data: dict, work: Path) -> str:
    prev = previous_ranks()
    rows = data["results"]
    mw, jw, pw = data["weights"]["measured"], data["weights"]["judge"], data["weights"]["panel"]
    head = ("<tr><th>#</th><th>Move</th><th class='l'>Mark</th><th class='l'>Name</th><th>16 px</th>"
            + "".join(f"<th>{LABEL[k]}<br><span class='num'>{w}</span></th>" for k, w in mw.items())
            + "".join(f"<th>{LABEL[k]}<br><span class='num'>{w}</span></th>" for k, w in jw.items())
            + "<th>Measured<br>/35</th><th>Rubric<br>/60</th><th>Panel<br>/5</th><th>Total<br>/100</th></tr>")
    body = []
    for r in rows:
        m = r["metrics"]
        cls = "top" if r["rank"] <= TOP_N else ""
        cls += " cut" if r["rank"] == TOP_N else ""
        px = png_uri(work / f"{r['id']}-16.png")
        src = "owner" if is_raster(r) else "designed"
        cells = [f"<td class='num'>{r['rank']}</td>", f"<td>{move(r['rank'], prev.get(r['id']))}</td>",
                 f"<td class='l'><span class='mk'>{mark(r, work)}</span></td>",
                 f"<td class='l'><b>{r['id']}</b> {escape(r['name'])}<br><small class='src {src}'>"
                 f"{'your sheet' if src == 'owner' else 'designed'}</small></td>",
                 f"<td><img class='px16' src='{px}' alt=''><img class='px16x' src='{px}' alt='{r['id']} at 16 px, enlarged'></td>"]
        detail = {"fid16": f"r={m['r16']:.3f}", "contrast": f"{m['contrast_ratio']}:1",
                  "mono": f"{m['hue_families']} hue", "simple": f"cx {m['complexity']}", "circle": r["shape"]}
        cells += [f"<td class='num' title='{detail[k]}'>{m[k] * w:.1f}<br><small>{detail[k]}</small></td>"
                  for k, w in mw.items()]
        cells += [f"<td class='num'>{r['judge'][k]}</td>" for k in jw]
        cells += [f"<td class='num'>{r['measured']}</td>", f"<td class='num'>{r['judged']}</td>",
                  f"<td class='num'>{r['panel']}</td>",
                  f"<td class='num'><b>{r['total']}</b><span class='bar' style='width:{r['total'] * .6:.0f}px'></span></td>"]
        body.append(f"<tr class='{cls.strip()}' data-src='{src}'>" + "".join(cells) + "</tr>")
    n_owner = sum(1 for r in rows if is_raster(r))
    owner_top = [r for r in rows if is_raster(r)][:5]
    weights = "".join(f"<tr><td class='l'>{LABEL[k]}</td><td class='l'>{src}</td><td class='num'>{w}</td></tr>"
                      for src, d in (("measured", mw), ("rubric", jw)) for k, w in d.items())
    return f"""<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Moya Mark Ranking</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}<style>{BASE_CSS}</style>
<div class="band"><div class="wrap">
<div class="eyebrow">Mauricio Moya · brand identity · all options</div>
<h1>All {len(rows)} logo options, scored</h1>
<p class="lede">{len(rows) - n_owner} designed options plus all {n_owner} logos from your own reference sheets,
scored by one algorithm out of 100: 35 points measured from real renders, 60 points from a designer rubric
tuned to the brand personality, and 5 points reserved for audience opinion. The top {TOP_N} go to the live poll.</p>
<p><a class="vote" href="{POLL_URL}">Vote in the live poll &rarr;</a></p>
</div></div>
<div class="wrap">
<h2>Ranking and analysis</h2>
<p>Gold rows are the top {TOP_N}. Move compares each mark with the previous ranking of {len(prev)} options:
<span class='mv up'>&#9650; up</span>, <span class='mv dn'>&#9660; down</span>, <span class='mv new'>NEW</span> first time ranked. Measured columns show points earned, with the raw reading under them.
The 16 px column is the actual favicon-size render, shown at true size and enlarged.</p>
<p><b>Best of your sheets:</b> {', '.join(f"#{r['rank']} {r['id']} {escape(r['name'])} ({r['total']})" for r in owner_top)}.</p>
<div class="filters" role="group" aria-label="Show">
<button class="chip" aria-pressed="true" data-f="all">All {len(rows)}</button>
<button class="chip" aria-pressed="false" data-f="owner">Your sheets {n_owner}</button>
<button class="chip" aria-pressed="false" data-f="designed">Designed {len(rows) - n_owner}</button></div>
<div class="scroll"><table><thead>{head}</thead><tbody id="rows">{''.join(body)}</tbody></table></div>
<script>
document.querySelector('.filters').addEventListener('click', e => {{
  const b = e.target.closest('.chip'); if (!b) return;
  document.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', c === b ? 'true' : 'false'));
  document.querySelectorAll('#rows tr').forEach(tr => {{ tr.hidden = b.dataset.f !== 'all' && tr.dataset.src !== b.dataset.f; }});
}});
</script>

<h2>How your sheets were measured</h2>
<p>Your {n_owner} logos came as photos of logo sheets, not vector files, so each was cropped from its sheet
(U01 to U{n_owner:02d}, left to right, top to bottom; a laptop advert in the same upload held no logo and was skipped).
Each crop gets the same tests as the vector marks, with three adjustments so the photo is not judged instead of the design:
a 5 px median filter removes paper and foil grain, the crop is trimmed to the ink with a 6 % margin,
and the background colour is not counted as a brand colour. Simplicity uses edge density at 128 px,
scaled so the vector marks' median edge density equals their median complexity.
Lockups (U55 to U64) are scored with their words, as sent. U05 and U06 are the same design from two sheets.
Most fine-line designs lose all 15 points of 16 px fidelity: their hairlines vanish at favicon size.
That is a real finding for an app icon or favicon, not a photo artefact; a bolder stroke would recover most of it.</p>

<h2>The algorithm</h2>
<p><b>Total = measured (35) + rubric (60) + panel (5).</b> Every rubric score s from 1 to 10 counts as
(s − 1) / 9 of its weight. Measured scores come from headless Chrome renders at 128 px and 16 px on ivory.</p>
<div class="scroll"><table><thead><tr><th class="l">Criterion</th><th class="l">Source</th><th>Weight</th></tr></thead>
<tbody>{weights}<tr><td class="l">Audience panel</td><td class="l">persona simulation / live poll</td><td class="num">{pw}</td></tr></tbody></table></div>
<p><b>16 px fidelity</b>: Pearson correlation between the 16 px render (upscaled) and the 128 px render; full points at r ≥ 0.98, zero at 0.80.
<b>Contrast</b>: WCAG ratio between the 2nd and 98th luminance percentile of the mark's centre; full points at 7:1.
<b>One colour</b>: number of hue families a mark needs (a gold gradient counts as one).
<b>Simplicity</b>: SVG elements + path commands / 2 + letters; fewer means easier to engrave, stitch or emboss.
<b>Circle form</b>: the owner's rule that circles work better.</p>

<h2>Personality target</h2>
<p>From the 12-archetype brand model: <b>Ruler</b> (authority, trust: finance and compliance) +
<b>Sage</b> (wisdom: education) + a touch of <b>Creator</b> (technology). The rubric's Personality fit,
Professional and Luxury columns score against this target: private bank, Swiss watch, university seal.
Playful, startup-coloured marks (A1 to A3) score low here by design.</p>

<h2>Sources and tests</h2>
<p>Criteria were taken from published agent skills for brand and logo work, read only, nothing installed:
a brand-identity skill (16 px legibility, one-colour use, silhouette, application stress test),
a logo-design skill (SVG audit, complexity, detail size, the 96 to 16 px size ladder, squint and reversed tests, 3:1 minimum contrast)
and a brand-identity skill with the 12 archetypes. The persona simulation (MiroFish swarm, six audience personas)
ran twice and failed both times without a ranking, so the panel scores 0 for every option and the
live poll replaces it with real votes.</p>
</div>
"""


def poll_page(data: dict, work: Path | None = None) -> str:
    top = [r for r in data["results"] if r["rank"] <= TOP_N]
    cards = "".join(
        f"<button class='card' id='c-{r['id']}' data-id='{r['id']}' aria-pressed='false'>"
        f"<span class='mk'>{mark(r, work)}</span>"
        f"<span class='nm'><b>{r['id']}</b> {escape(r['name'])}</span>"
        f"<span class='sc num'>score {r['total']}</span><span class='pick' aria-hidden='true'></span></button>"
        for r in top)
    meta = json.dumps({r["id"]: {"name": r["name"], "score": r["total"], "rank": r["rank"]} for r in top})
    return f"""<title>Moya Mark Poll</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}<style>{BASE_CSS}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
.card{{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;padding:14px 10px 12px;
background:var(--panel);border:1px solid var(--line);border-radius:8px;color:var(--ink);font:inherit;cursor:pointer}}
.card .mk{{width:96px;height:96px}}
.card:hover{{border-color:var(--gold)}}
.card:focus-visible{{outline:2px solid var(--gold);outline-offset:2px}}
.card[aria-pressed="true"]{{border-color:var(--gold);box-shadow:0 0 0 2px var(--gold) inset}}
.pick{{position:absolute;top:8px;left:8px;font:600 12px/1 var(--mono);color:var(--paper);background:var(--gold);
border-radius:10px;padding:4px 7px}}
.pick:empty{{display:none}}
.nm{{font-size:13px}}.sc{{font-size:11px;color:var(--muted)}}
.bar-row{{display:grid;grid-template-columns:22px 36px minmax(0,1fr) 50px;font-size:13px;gap:10px;align-items:center;padding:6px 0;
border-bottom:1px solid var(--line)}}
.track{{display:block;margin-top:4px;height:6px;background:var(--line);border-radius:5px;overflow:hidden}}
.fill{{height:100%;background:var(--bar)}}
.bar-row.flash{{background:color-mix(in srgb,var(--gold) 14%,transparent)}}
.legend{{font-size:12px;color:var(--muted);margin:4px 0 8px}}
.actions{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-block:16px}}
.btn{{font:600 14px var(--body);padding:10px 18px;border-radius:6px;border:1px solid var(--gold);
background:var(--gold);color:var(--paper);cursor:pointer}}
.btn.ghost{{background:transparent;color:var(--ink)}}
.btn:disabled{{opacity:.45;cursor:default}}
.note{{color:var(--muted);font-size:13px}}
.cols{{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:28px}}
@media (max-width:820px){{.cols{{grid-template-columns:1fr}}}}
@media (prefers-reduced-motion:no-preference){{.fill{{transition:width .4s ease}}}}
</style>
<div class="band"><div class="wrap">
<div class="eyebrow">Mauricio Moya · logo vote</div>
<h1>Pick the mark</h1>
<p class="lede">Twenty finalists for a personal brand in finance, technology, compliance and education.
Choose your top three in order: first pick gets 3 points, second 2, third 1. You can change your vote any time.</p>
</div></div>
<div class="wrap"><div class="cols">
<section><h2>Finalists</h2>
<div class="actions"><button class="btn" id="submit" disabled>Save my top 3</button>
<button class="btn ghost" id="clear">Clear picks</button><span class="note" id="status">Loading votes…</span></div>
<div class="grid" id="grid">{cards}</div></section>
<section><h2>Live results</h2><p class="note" id="voters">No votes yet. Be the first: pick three marks and save.</p>
<p class="legend">Arrows compare the vote rank with the algorithm rank: <span class="mv up">&#9650; voters like it more</span>, <span class="mv dn">&#9660; less</span>. Rows flash when they move.</p>
<div id="tally"></div></section>
</div></div>
<script>
const META = {meta};
const picks = [];
let db = null, me = null, votes = [];
const $ = s => document.querySelector(s);
function paint() {{
  document.querySelectorAll('.card').forEach(c => {{
    const i = picks.indexOf(c.dataset.id);
    c.setAttribute('aria-pressed', i >= 0 ? 'true' : 'false');
    c.querySelector('.pick').textContent = i >= 0 ? ['1st','2nd','3rd'][i] : '';
  }});
  $('#submit').disabled = !(db && me && picks.length === 3);
}}
let lastPos = null;
function tally() {{
  const pts = {{}};
  for (const id in META) pts[id] = 0;
  for (const v of votes) (v.picks || []).slice(0, 3).forEach((id, i) => {{ if (META[id]) pts[id] += 3 - i; }});
  const ranked = Object.entries(pts).sort((a, b) => b[1] - a[1] || META[a[0]].rank - META[b[0]].rank);
  const max = Math.max(1, ranked[0][1]);
  $('#voters').textContent = votes.length ? votes.length + (votes.length === 1 ? ' person has' : ' people have') + ' voted.' :
    'No votes yet. Be the first: pick three marks and save.';
  const box = $('#tally'); box.replaceChildren();
  const pos = {{}};
  ranked.forEach(([id, p], i) => {{
    pos[id] = i + 1;
    const row = document.createElement('div'); row.className = 'bar-row';
    if (lastPos && lastPos[id] !== i + 1) row.classList.add('flash');
    const no = document.createElement('span'); no.className = 'num'; no.textContent = i + 1;
    const d = META[id].rank - (i + 1);
    const mv = document.createElement('span');
    mv.className = 'mv ' + (!votes.length || d === 0 ? 'eq' : d > 0 ? 'up' : 'dn');
    mv.textContent = !votes.length || d === 0 ? '\u2013' : (d > 0 ? '\u25B2' : '\u25BC') + Math.abs(d);
    mv.title = 'algorithm rank #' + META[id].rank;
    const name = document.createElement('span'); name.textContent = id + ' ' + META[id].name;
    const track = document.createElement('span'); track.className = 'track';
    const fill = document.createElement('span'); fill.className = 'fill'; fill.style.width = (100 * p / max) + '%';
    fill.style.display = 'block'; track.append(fill);
    const n = document.createElement('span'); n.className = 'num'; n.style.textAlign = 'right'; n.textContent = p + ' pts';
    name.append(track); row.append(no, mv, name, n); box.append(row);
  }});
  lastPos = pos;
}}
document.getElementById('grid').addEventListener('click', e => {{
  const c = e.target.closest('.card'); if (!c) return;
  const id = c.dataset.id, i = picks.indexOf(id);
  if (i >= 0) picks.splice(i, 1); else if (picks.length < 3) picks.push(id);
  paint();
}});
$('#clear').addEventListener('click', () => {{ picks.length = 0; paint(); }});
$('#submit').addEventListener('click', async () => {{
  $('#submit').disabled = true; $('#status').textContent = 'Saving…';
  try {{
    await db.doc('votes/' + me).set({{ picks: picks.slice(), at: Date.now() }});
    $('#status').textContent = 'Saved. Your vote counts in the live results.';
  }} catch (err) {{
    $('#status').textContent = 'Could not save your vote (' + (err && err.code || 'error') + '). Check you are signed in and try again.';
  }}
  paint();
}});
(async () => {{
  const timer = setTimeout(() => {{ $('#status').textContent = 'Votes did not load. Reopen the page to try again.'; }}, 10000);
  db = await claude.use('db');
  const user = await claude.use('user');
  if (!db) {{ clearTimeout(timer); $('#status').textContent = 'Voting needs you to be signed in to Claude.'; return; }}
  me = user ? await user.id() : null;
  if (!me) $('#status').textContent = 'Sign in to vote. Results are visible below.';
  db.collection('votes').onSnapshot(snap => {{
    clearTimeout(timer);
    votes = snap.docs.map(d => d.data() || {{}});
    const mine = me && snap.docs.find(d => d.id === me);
    if (mine && !picks.length) {{ picks.push(...((mine.data() || {{}}).picks || []).filter(id => META[id])); }}
    if (me) $('#status').textContent = mine ? 'You have voted. Change picks and save again to update.' : 'Pick three, then save.';
    tally(); paint();
  }}, err => {{ clearTimeout(timer); $('#status').textContent = 'Votes could not load (' + (err && err.code || 'error') + ').'; }});
}})();
</script>
"""


def main(work: Path, poll_out: str | None) -> None:
    data = json.loads((HERE / "results.json").read_text())
    (HERE / "index.html").write_text(ranking_page(data, work))
    print("wrote ranking/index.html")
    if poll_out:
        Path(poll_out).write_text(poll_page(data, work))
        print("wrote", poll_out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
