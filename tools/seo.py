"""Search engines and AI models see every language: static, pre-translated pages per language.

The browser translates English pages from i18n/<id>.json (options.js). Crawlers do not run that, so this
tool writes the same translation into static pages, one folder per language:
  /es/, /es/finance/, /zh/development/, ...   localized <title>, description, <html lang/dir>, canonical,
                                              Open Graph + Twitter, JSON-LD (inLanguage, localized text)
  every page (English too)                    hreflang alternates for all languages + x-default (English)
  sitemap.xml                                 every page in every language, with xhtml:link alternates
  llms.txt (Languages section), <id>/llms.txt one AI-readable summary per language

The body is cut into the same keys as tools/i18n.py and options.js and filled the way options.js fills it,
so a static page shows exactly what the browser would show after picking that language.

  python3 tools/seo.py        rewrite the language pages, hreflang blocks, sitemap.xml and llms files
  python3 tools/seo.py check  exit 1 when any of them is stale (CI)
"""
import html
import html.parser
import json
import pathlib
import posixpath
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import i18n  # noqa: E402

ROOT = i18n.ROOT
SITE = "https://maumoya.github.io/"
# (path, sitemap priority). Site pages only: tour/ and brand/ are noindex side pages.
PAGES = (("", "1.0"), ("finance/", "0.8"), ("development/", "0.8"), ("compliance/", "0.8"), ("education/", "0.8"))
# English-only pages: one sitemap entry each, no language copies (the resume is read in English).
ENGLISH_ONLY = (("resume/", "0.7"),)
# id: (html lang / hreflang tag, og:locale, right-to-left, native name, English name). Same ids as i18n.LANGS.
LANG = {
    "en": ("en", "en_US", False, "English", "English"),
    "zh": ("zh-Hans", "zh_CN", False, "中文", "Chinese"),
    "hi": ("hi", "hi_IN", False, "हिन्दी", "Hindi"),
    "es": ("es", "es_ES", False, "Español", "Spanish"),
    "ar": ("ar", "ar_AR", True, "العربية", "Arabic"),
    "fr": ("fr", "fr_FR", False, "Français", "French"),
    "pt": ("pt-BR", "pt_BR", False, "Português", "Portuguese"),
    "de": ("de", "de_DE", False, "Deutsch", "German"),
    "it": ("it", "it_IT", False, "Italiano", "Italian"),
    "ja": ("ja", "ja_JP", False, "日本語", "Japanese"),
    "he": ("he", "he_IL", True, "עברית", "Hebrew"),
    "sjn": ("sjn", None, False, "Edhellen", "Elvish (Sindarin)"),
    "ru": ("ru", "ru_RU", False, "Русский", "Russian"),
    "eo": ("eo", "eo_EO", False, "Esperanto", "Esperanto"),
    "qu": ("qu", "qu_PE", False, "Runasimi", "Quechua"),
    "bn": ("bn", "bn_BD", False, "বাংলা", "Bengali"),
    "ur": ("ur", "ur_PK", True, "اردو", "Urdu"),
    "id": ("id", "id_ID", False, "Bahasa Indonesia", "Indonesian"),
    "tr": ("tr", "tr_TR", False, "Türkçe", "Turkish"),
    "vi": ("vi", "vi_VN", False, "Tiếng Việt", "Vietnamese"),
    "ko": ("ko", "ko_KR", False, "한국어", "Korean"),
    "fa": ("fa", "fa_IR", True, "فارسی", "Persian"),
    "th": ("th", "th_TH", False, "ไทย", "Thai"),
    "sw": ("sw", "sw_TZ", False, "Kiswahili", "Swahili"),
    "tl": ("tl", "tl_PH", False, "Tagalog", "Tagalog"),
}
ORDER = ("en",) + i18n.LANGS
VOID = i18n.VOID
SKIP = {"script", "style", "svg", "noscript", "template", "source"}
PLACE = re.compile(r"\{(\d+)\}")


# ---------- A lossless HTML tree: unchanged parts are written back byte for byte ----------
class El:
    def __init__(self, tag, attrs, raw, parent):
        self.tag, self.attrs, self.raw, self.parent = tag, list(attrs), raw, parent
        self.kids, self.closed, self.dirty = [], False, False

    def get(self, name):
        for k, v in self.attrs:
            if k == name:
                return v
        return None

    def set(self, name, value):
        for i, (k, v) in enumerate(self.attrs):
            if k == name:
                if v != value:
                    self.attrs[i] = (k, value)
                    self.dirty = True
                return
        self.attrs.append((name, value))
        self.dirty = True


class Text:
    def __init__(self, raw):
        self.raw = raw

    @property
    def text(self):
        return html.unescape(self.raw)


class Raw:
    def __init__(self, raw, comment=None):
        self.raw, self.comment = raw, comment


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = El("#root", [], "", None)
        self.cur = self.root

    def _text(self, raw):
        if self.cur.kids and isinstance(self.cur.kids[-1], Text):
            self.cur.kids[-1].raw += raw
        else:
            self.cur.kids.append(Text(raw))

    def handle_starttag(self, tag, attrs):
        el = El(tag, attrs, self.get_starttag_text(), self.cur)
        self.cur.kids.append(el)
        if tag not in VOID:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(El(tag, attrs, self.get_starttag_text(), self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not None and node.tag != tag:
            node = node.parent
        if node is None or node.parent is None:
            self.cur.kids.append(Raw(f"</{tag}>"))
            return
        node.closed = True
        self.cur = node.parent

    def handle_data(self, data):
        self._text(data)

    def handle_entityref(self, name):
        self._text(f"&{name};")

    def handle_charref(self, name):
        self._text(f"&#{name};")

    def handle_comment(self, data):
        self.cur.kids.append(Raw(f"<!--{data}-->", data))

    def handle_decl(self, decl):
        self.cur.kids.append(Raw(f"<!{decl}>"))

    def handle_pi(self, data):
        self.cur.kids.append(Raw(f"<?{data}>"))

    def unknown_decl(self, data):
        self.cur.kids.append(Raw(f"<![{data}]>"))


def start_tag(el):
    if not el.dirty:
        return el.raw
    attrs = "".join(f" {k}" if v is None else f' {k}="{html.escape(v, quote=True)}"' for k, v in el.attrs)
    return f"<{el.tag}{attrs}{' /' if el.raw.endswith('/>') else ''}>"


def serialize(node, out):
    if isinstance(node, El):
        if node.tag != "#root":
            out.append(start_tag(node))
        for k in node.kids:
            serialize(k, out)
        if node.closed:
            out.append(f"</{node.tag}>")
    else:
        out.append(node.raw)
    return out


def find(el, tag):
    for k in el.kids:
        if isinstance(k, El):
            if k.tag == tag:
                return k
            hit = find(k, tag)
            if hit:
                return hit
    return None


# ---------- Translation: the same cut and fill as options.js ----------
def cut(el):
    """(key, groups) for an element's own content, like unit() in options.js; key is None without a letter."""
    parts, groups, own, in_fact = [], [], "", False
    for k in el.kids:
        if isinstance(k, El):
            parts.append("{%d}" % len(groups))
            groups.append([k])
        elif isinstance(k, Raw):
            c = k.comment or ""
            if k.comment is not None and c.startswith("fact:"):
                in_fact = True
                parts.append("{%d}" % len(groups))
                groups.append([k])
            elif k.comment is not None and c.startswith("/fact") and groups:
                in_fact = False
                groups[-1].append(k)
        elif in_fact:
            groups[-1].append(k)
        else:
            parts.append(k.text)
            own += k.text
    if not i18n.LETTER.search(own):
        return None, groups
    return i18n.norm("".join(parts)), groups


def fill(el, tr, groups):
    out, last = [], 0
    for m in PLACE.finditer(tr):
        if m.start() > last:
            out.append(Text(html.escape(tr[last:m.start()], quote=False)))
        out.extend(groups[int(m.group(1))] if int(m.group(1)) < len(groups) else [])
        last = m.end()
    if last < len(tr):
        out.append(Text(html.escape(tr[last:], quote=False)))
    el.kids = out


def attrs(el, d):
    if "vbtn" in (el.get("class") or "").split():  # app.js labels these itself
        return
    for a in i18n.ATTRS:
        v = el.get(a)
        if v and i18n.has_letter(i18n.norm(v)) and d.get(i18n.norm(v)):
            el.set(a, d[i18n.norm(v)])


def translate(el, d):
    if el.tag in SKIP or el.get("translate") == "no":
        if el.get("translate") != "no":
            attrs(el, d)
        return
    attrs(el, d)
    kids = [k for k in el.kids if isinstance(k, El)]
    key, groups = cut(el)
    if key and d.get(key):
        fill(el, d[key], groups)
    for k in kids:
        translate(k, d)


# ---------- Links: pages stay inside the language folder, files point one level up ----------
URL_ATTRS = ("href", "src", "poster")
PAGE_PATHS = {p for p, _ in PAGES}


def relink(el, page):
    for a in URL_ATTRS:
        v = el.get(a)
        if not v or re.match(r"^([a-z][a-z0-9+.-]*:|/|#)", v, re.I):
            continue
        path = urllib.parse.urlsplit(v).path
        if not path:
            continue
        target = posixpath.normpath(posixpath.join(page, path))
        target = "" if target == "." else target
        if target and (path.endswith("/") or path.split("/")[-1] in (".", "..")):
            target += "/"
        if target.startswith(".."):
            continue
        if target not in PAGE_PATHS:
            el.set(a, "../" + v)
    for k in el.kids:
        if isinstance(k, El):
            relink(k, page)


# ---------- Head: localized metadata, hreflang, JSON-LD ----------
def url(lang, page):
    return SITE + ("" if lang == "en" else lang + "/") + page


def esc(s):
    return html.escape(s, quote=True)


def meta(head, attr, key, value):
    pat = re.compile(r'(<meta %s="%s" content=")[^"]*(">)' % (attr, re.escape(key)))
    if not pat.search(head):
        sys.exit(f"seo.py: no <meta {attr}={key!r}> to localize")
    return pat.sub(lambda m: m.group(1) + esc(value) + m.group(2), head, count=1)


def alternates(page, lang):
    lines = ["<!-- i18n-alt (generated by tools/seo.py, do not edit) -->"]
    lines += [f'<meta property="og:locale:alternate" content="{LANG[x][1]}">' for x in ORDER if x != lang and LANG[x][1]]
    lines += [f'<link rel="alternate" hreflang="{LANG[x][0]}" href="{url(x, page)}">' for x in ORDER]
    lines += [f'<link rel="alternate" hreflang="x-default" href="{url("en", page)}">', "<!-- /i18n-alt -->"]
    return "\n".join(lines)


ALT = re.compile(r"\n?<!-- i18n-alt .*?<!-- /i18n-alt -->", re.S)
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def english(page):
    text = (ROOT / page / "index.html").read_text()
    head = text[:text.index("</head>")]
    title = i18n.norm(html.unescape(re.search(r"<title>(.*?)</title>", head, re.S).group(1)))
    desc = i18n.norm(html.unescape(re.search(r'<meta name="description" content="([^"]*)"', head).group(1)))
    return text, title, desc


def localize_head(head, page, lang, d, title, desc):
    tr = lambda s: d.get(s) or s  # noqa: E731
    t, ds = tr(title), tr(desc)
    tag, locale, rtl = LANG[lang][:3]
    head = ALT.sub("", head)
    if lang != "en":
        head = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(t, quote=False)}</title>", head, count=1, flags=re.S)
        for attr, key, value in (("name", "description", ds), ("property", "og:title", t), ("property", "og:description", ds),
                                 ("property", "og:image:alt", t), ("name", "twitter:title", t),
                                 ("name", "twitter:description", ds), ("name", "twitter:image:alt", t),
                                 ("property", "og:locale", locale), ("property", "og:url", url(lang, page))):
            if value is None:
                head = re.sub(r'\n?[ \t]*<meta %s="%s" content="[^"]*">' % (attr, re.escape(key)), "", head, count=1)
                continue
            head = meta(head, attr, key, value)
        head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url(lang, page)}">', head, count=1)
        head = re.sub(r'<html lang="en">', f'<html lang="{tag}" dir="{"rtl" if rtl else "ltr"}" data-page-lang="{lang}">', head, count=1)
        # the static page is already in its language: the saved choice must not hide it or flip its direction
        head, n = re.subn(r'l=localStorage\.getItem\("mm-lang"\)', "l=null", head)
        if n != 1:
            sys.exit(f"seo.py: early theme script not found in {page or 'index.html'}")

    def ld(m):
        data = json.loads(m.group(2))
        for node in data.get("@graph", []):
            if node.get("@type") == "WebSite":
                node["inLanguage"] = [LANG[x][0] for x in ORDER]
            if str(node.get("@id", "")).endswith("#page"):
                node.update({"@id": url(lang, page) + "#page", "url": url(lang, page), "name": t, "description": ds, "inLanguage": tag})
                for item in node.get("breadcrumb", {}).get("itemListElement", []):
                    p = item["item"][len(SITE):]
                    item.update({"name": tr(item["name"]), "item": url(lang, p)})
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return m.group(1) + body + m.group(3)
    head = LD.sub(ld, head, count=1)
    canon = re.search(r'<link rel="canonical" href="[^"]*">', head)
    if not canon:
        sys.exit(f"seo.py: no canonical link in {page or 'index.html'}")
    return head[:canon.end()] + "\n" + alternates(page, lang) + head[canon.end():]


# ---------- Everything this tool writes ----------
def dictionary(lang):
    return {} if lang == "en" else json.loads((ROOT / "i18n" / f"{lang}.json").read_text())


def build():
    out, meta_of = {}, {}
    dicts = {x: dictionary(x) for x in ORDER}
    for page, _ in PAGES:
        text, title, desc = english(page)
        cut_at = text.index("</head>")
        for lang in ORDER:
            d = dicts[lang]
            head = localize_head(text[:cut_at], page, lang, d, title, desc)
            meta_of[(lang, page)] = (d.get(title) or title, d.get(desc) or desc)
            if lang == "en":
                out[page + "index.html"] = head + text[cut_at:]
                continue
            p = Parser()
            p.feed(head + text[cut_at:])
            p.close()
            body = find(p.root, "body")
            translate(body, d)
            relink(p.root, page)
            out[f"{lang}/{page}index.html"] = "".join(serialize(p.root, []))
    out["sitemap.xml"] = sitemap()
    out["llms.txt"] = llms_root(meta_of)
    for lang in i18n.LANGS:
        out[f"{lang}/llms.txt"] = llms_lang(lang, meta_of, dicts[lang])
    return out


def sitemap():
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page, prio in PAGES:
        src = (ROOT / page / "index.html").read_text()
        date = re.search(r'"dateModified":"([0-9-]+)"', src).group(1)
        alts = [f'    <xhtml:link rel="alternate" hreflang="{LANG[x][0]}" href="{url(x, page)}"/>' for x in ORDER]
        alts.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en", page)}"/>')
        for lang in ORDER:
            lines += ["  <url>", f"    <loc>{url(lang, page)}</loc>", f"    <lastmod>{date}</lastmod>",
                      f"    <priority>{prio}</priority>"] + alts + ["  </url>"]
    for page, prio in ENGLISH_ONLY:
        src = (ROOT / page / "index.html").read_text()
        date = re.search(r'"dateModified":"([0-9-]+)"', src).group(1)
        lines += ["  <url>", f"    <loc>{SITE}{page}</loc>", f"    <lastmod>{date}</lastmod>",
                  f"    <priority>{prio}</priority>", "  </url>"]
    return "\n".join(lines + ["</urlset>", ""])


LLMS = re.compile(r"\n*<!-- languages .*?<!-- /languages -->\n?", re.S)


def llms_root(meta_of):
    base = LLMS.sub("\n", (ROOT / "llms.txt").read_text()).rstrip("\n")
    lines = ["", "", "<!-- languages (generated by tools/seo.py, do not edit) -->", "## Languages", "",
             "Every page is also published, fully translated, in these languages. Each has its own summary for AI models.", ""]
    for lang in i18n.LANGS:
        native, eng = LANG[lang][3], LANG[lang][4]
        lines.append(f"- [{native} ({eng})]({url(lang, '')}): {meta_of[(lang, '')][1]} Summary: {url(lang, 'llms.txt')}")
    lines.append("<!-- /languages -->")
    return base + "\n".join(lines) + "\n"


def llms_lang(lang, meta_of, d):
    tr = lambda s: d.get(s) or s  # noqa: E731
    lines = [f"# {tr('Mauricio Moya')}", "", f"> {meta_of[(lang, '')][1]}", "",
             f"{LANG[lang][3]} ({LANG[lang][4]}). English: {SITE}llms.txt", "", f"## {tr('Pages')}", ""]
    for page, _ in PAGES:
        t, ds = meta_of[(lang, page)]
        lines.append(f"- [{t}]({url(lang, page)}): {ds}")
    lines += ["", "## Links", "", "- Email: mmoyatapia@student.hult.edu", "- LinkedIn: https://www.linkedin.com/in/mba-mmoyat/", "- GitHub: https://github.com/maumoya",
              "- X: https://x.com/mau_amt", "- YouTube: https://www.youtube.com/@maumoya85", ""]
    return "\n".join(lines)


def main():
    check = sys.argv[1:] == ["check"]
    if set(LANG) != set(ORDER):
        sys.exit("seo.py: LANG and i18n.LANGS differ")
    want = build()
    stale = [p for p, body in want.items() if not (ROOT / p).exists() or (ROOT / p).read_text() != body]
    if check:
        for p in stale:
            print(f"STALE  {p}")
        print(f"{len(want)} files: " + ("seo current" if not stale else f"{len(stale)} stale, run python3 tools/seo.py"))
        return 1 if stale else 0
    for p in stale:
        (ROOT / p).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / p).write_text(want[p])
    print(f"updated {len(stale)} of {len(want)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
