"""Share images (1200x630) for link previews on LinkedIn, X, Slack, WhatsApp and search results.

  python3 tools/og.py    writes og.png and <section>/og.png

Needs Pillow and a sans-serif TrueType font (FONT env var, else Arial Unicode on macOS).
The images are committed, so the site itself needs nothing at run time.
"""
import os
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = os.environ.get("FONT", "/Library/Fonts/Arial Unicode.ttf")
W, H = 1200, 630
BG, FG, MUTED, ACCENT = (22, 22, 23), (245, 245, 247), (161, 161, 170), (41, 151, 255)
ROLES = "Finance leader · AI agent engineer · FP&A · Automation · Compliance"

PAGES = {
    ".": ("Building systems,\ndriving profits.", "Automation, dashboards and AI agents that cut cost\nand remove manual work. Open to roles and consulting."),
    "development": ("AI agents that ship.\nNumbers that prove it.", "Agent skills and workflows, measured with evals,\nhardened and shipped end to end."),
    "finance": ("Cash you can see.\nBudgets that hold.", "FP&A, cash flow, receivables and funding strategy,\nrun on clean data and automation."),
    "compliance": ("Controls that hold up\nwhen the auditor calls.", "Internal controls, grant compliance, audit readiness\nand security built into the systems."),
    "education": ("I teach the system so\nit outlives the project.", "University teaching, data tutoring and AI workshops\nthat leave teams able to run what was built."),
}


def font(size):
    return ImageFont.truetype(FONT, size)


def card(title, sub, section):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    x = 80
    d.rectangle([0, 0, W, 6], fill=ACCENT)
    # Monogram: an original rounded square with initials.
    d.rounded_rectangle([x, 70, x + 64, 134], 16, fill=ACCENT)
    d.text((x + 32, 102), "MM", font=font(28), fill=FG, anchor="mm", stroke_width=1, stroke_fill=FG)
    d.text((x + 88, 82), "Mauricio Moya", font=font(30), fill=FG, stroke_width=1, stroke_fill=FG)
    d.text((x + 88, 120), section, font=font(20), fill=MUTED)
    d.multiline_text((x, 172), title, font=font(70), fill=FG, spacing=12, stroke_width=2, stroke_fill=FG)
    d.multiline_text((x, 392), sub, font=font(28), fill=MUTED, spacing=10)
    d.line([x, 520, W - x, 520], fill=(58, 58, 60), width=2)
    d.text((x, 545), ROLES, font=font(22), fill=MUTED)
    d.text((W - x, 545), "maumoya.github.io", font=font(22), fill=ACCENT, anchor="ra")
    return im


def main():
    names = {".": "Portfolio", "development": "Development", "finance": "Finance",
             "compliance": "Compliance", "education": "Education"}
    for path, (title, sub) in PAGES.items():
        out = ROOT / path / "og.png"
        card(title, sub, names[path]).save(out, optimize=True)
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
