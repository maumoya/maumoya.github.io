"""Site translations: every visible English string has a translation in each language file.

The browser (options.js) and this tool cut a page into the same keys:
  - an element whose own text has a letter is one key; child elements and the numbers between
    <!--fact:...--> markers become {0}, {1}, ... so a translation can move them around;
  - aria-label, alt, title and placeholder attributes are keys of their own;
  - script, style, svg and anything with translate="no" is left alone.
Extra strings that options.js draws itself (menus, labels) live in i18n/ui.json.

  python3 tools/i18n.py keys    print every English key (one JSON list)
  python3 tools/i18n.py check   exit 1 when a language misses a key or breaks a {n} placeholder (CI)
"""
import html.parser
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("zh", "hi", "es", "ar", "fr", "pt", "de", "it", "ja", "he", "sjn", "ru", "eo", "qu")
ATTRS = ("aria-label", "alt", "title", "placeholder")
SKIP = {"script", "style", "svg", "noscript", "template", "source", "head"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
LETTER = re.compile(r"[^\W\d_]")
PLACE = re.compile(r"\{(\d+)\}")


class El:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids = tag, dict(attrs), parent, []


class Tree(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = El("#root", [], None)
        self.cur = self.root
        self.title = None

    def handle_starttag(self, tag, attrs):
        el = El(tag, attrs, self.cur)
        self.cur.kids.append(el)
        if tag not in VOID:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(El(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.kids.append(("text", data))
        if self.cur.tag == "title":
            self.title = (self.title or "") + data

    def handle_comment(self, data):
        self.cur.kids.append(("comment", data))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def has_letter(key):
    return bool(LETTER.search(PLACE.sub("", key)))


def element_key(el):
    """Key for an element's own content, or None when its own text has no letter."""
    parts, n, own, in_fact = [], 0, "", False
    for k in el.kids:
        if isinstance(k, El):
            parts.append("{%d}" % n)
            n += 1
        elif k[0] == "comment":
            if k[1].startswith("fact:"):
                in_fact = True
                parts.append("{%d}" % n)
                n += 1
            elif k[1].startswith("/fact"):
                in_fact = False
        elif not in_fact:
            parts.append(k[1])
            own += k[1]
    if not LETTER.search(own):
        return None
    return norm("".join(parts))


def walk(el, keys):
    if isinstance(el, El):
        if el.tag in SKIP or el.attrs.get("translate") == "no":
            if el.tag == "head":
                return
            for a in ATTRS:  # a skipped <video> still has an aria-label worth translating
                v = norm(el.attrs.get(a) or "")
                if v and has_letter(v) and el.attrs.get("translate") != "no":
                    keys.append(v)
            return
        for a in ATTRS:
            v = norm(el.attrs.get(a) or "")
            if v and has_letter(v):
                keys.append(v)
        if el.tag != "#root":
            k = element_key(el)
            if k:
                keys.append(k)
        for kid in el.kids:
            walk(kid, keys)


def pages():
    # brand/ holds internal logo review pages, not site pages, so they are not translated
    skip = {".claude", "brand"}
    return [p for p in sorted(ROOT.glob("**/index.html")) if not skip & set(p.relative_to(ROOT).parts)]


def all_keys():
    keys = []
    for page in pages():
        t = Tree()
        t.feed(page.read_text())
        if t.title:
            keys.append(norm(t.title))
        walk(t.root, keys)
    ui = ROOT / "i18n" / "ui.json"
    keys += json.loads(ui.read_text()) if ui.exists() else []
    seen, out = set(), []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def check():
    keys = all_keys()
    bad = []
    for lang in LANGS:
        f = ROOT / "i18n" / f"{lang}.json"
        if not f.exists():
            bad.append(f"{lang}: missing file")
            continue
        tr = json.loads(f.read_text())
        for k in keys:
            if k not in tr:
                bad.append(f"{lang}: no translation for {k!r}")
            elif sorted(PLACE.findall(tr[k])) != sorted(PLACE.findall(k)):
                bad.append(f"{lang}: placeholders differ for {k!r}")
    for b in bad:
        print(b)
    print(f"{len(keys)} keys x {len(LANGS)} languages: " + ("OK" if not bad else f"{len(bad)} problems"))
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1:] or ["check"]
    if cmd == ["keys"]:
        print(json.dumps(all_keys(), ensure_ascii=False, indent=1))
        sys.exit(0)
    sys.exit(check())
