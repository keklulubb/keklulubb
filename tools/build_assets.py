"""Build the images used by the profile README.

Makes, inside ../assets:
  name.svg              the animated name window at the top
  buttons/*.svg         the social buttons (same style as aniyah.dev)
  pixel/*.svg           small animated pixel-art icons
  kisa.gif              the sleeping cat from aniyah.dev, cropped and framed

Text is drawn as outlines in Hachi Maru Pop (the font aniyah.dev uses), so it
looks the same everywhere without needing the font installed.

Needs: pip install fonttools brotli pillow
Run:   python tools/build_assets.py [--font hachi-maru-pop.woff2] [--kisa kisa.gif]
With no arguments both files are downloaded from the aniyah.dev repo.
"""

import argparse
import io
import pathlib
import urllib.request

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageSequence

SITE_RAW = "https://raw.githubusercontent.com/keklulubb/aniyah.dev/main/public"
FONT_URL = f"{SITE_RAW}/fonts/hachi-maru-pop.woff2"
KISA_URL = f"{SITE_RAW}/figma/wireframe8/kisa.gif"

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# aniyah.dev colours, plus a few deeper tones so things read on white
INK = "#111111"
PAPER = "#ffffff"
SITE_PINK = "#f7dbe1"
SITE_BLUE = "#daf4ff"
SITE_GREEN = "#e6f7d9"
PINK = "#f49ab4"
BLUE = "#7cc4ea"
GREEN = "#9ad486"
YELLOW = "#ffd86b"


def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read()


def num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Font:
    def __init__(self, data):
        self.font = TTFont(io.BytesIO(data))
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm

    def width(self, text, size, spacing=0.0):
        s = size / self.upm
        return sum(self.glyphs[self.cmap[ord(c)]].width * s + spacing for c in text) - spacing

    def path(self, text, size, x, baseline, spacing=0.0):
        """SVG path data for text whose left edge is x."""
        s = size / self.upm
        out = []
        for c in text:
            g = self.glyphs[self.cmap[ord(c)]]
            pen = SVGPathPen(self.glyphs, ntos=num)
            g.draw(TransformPen(pen, (s, 0, 0, -s, x, baseline)))
            out.append(pen.getCommands())
            x += g.width * s + spacing
        return " ".join(p for p in out if p)

    def centered(self, text, size, cx, baseline, spacing=0.0):
        return self.path(text, size, cx - self.width(text, size, spacing) / 2, baseline, spacing)


# ---------------------------------------------------------------- name window

def sparkle(x, y, r, fill, delay, dur=2.4):
    d = (f"M0 {-r} C{r*.12} {-r*.25} {r*.25} {-r*.12} {r} 0 "
         f"C{r*.25} {r*.12} {r*.12} {r*.25} 0 {r} "
         f"C{-r*.12} {r*.25} {-r*.25} {r*.12} {-r} 0 "
         f"C{-r*.25} {-r*.12} {-r*.12} {-r*.25} 0 {-r}Z")
    return f'''
  <g transform="translate({x} {y})">
    <path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round">
      <animateTransform attributeName="transform" type="scale" values="0.35;1;0.35"
        keyTimes="0;0.5;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.4;1;0.4" keyTimes="0;0.5;1"
        dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>
    </path>
  </g>'''


def pixel_rects(rows, palette, px, ox=0, oy=0):
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                out.append(f'<rect x="{num(ox + x*px)}" y="{num(oy + y*px)}" '
                           f'width="{num(px)}" height="{num(px)}" fill="{palette[ch]}"/>')
    return "".join(out)


HEART = [
    ".kk...kk.",
    "kPPk.kPPk",
    "kPwPkPPPk",
    "kPPPPPPPk",
    ".kPPPPPk.",
    "..kPPPk..",
    "...kPk...",
    "....k....",
]


def build_name(font):
    W, H = 900, 284
    bar = 50
    x0, y0, w, h, r = 4, 4, W - 14, H - 14, 16

    name = "Aniyah Bohnen"
    size = 80                 # Hachi is wide: 80px is ~730px, leaving room for the sparkles
    base = 170
    name_w = font.width(name, size)
    name_d = font.centered(name, size, W / 2, base)

    sub = "cs + math @ sfu  ·  ai/ml research  ·  3x hackathon winner"
    sub_d = font.centered(sub, 19, W / 2, 226)

    title_d = font.path("hello_world.txt", 22, x0 + 22, y0 + 33)

    dots = "".join(
        f'<circle cx="{x0 + w - 30 - i*30}" cy="{y0 + bar/2}" r="9" fill="{c}" '
        f'stroke="{INK}" stroke-width="2"/>'
        for i, c in enumerate([PINK, BLUE, GREEN]))

    left = W / 2 - name_w / 2
    right = W / 2 + name_w / 2
    sparkles = "".join([
        sparkle(left - 36, 108, 15, YELLOW, 0),
        sparkle(left - 14, 186, 9, BLUE, 0.9),
        sparkle(right + 34, 186, 14, GREEN, 1.4),
        sparkle(W / 2 + 30, 78, 8, BLUE, 1.9),
        sparkle(right - 70, 76, 10, PINK, 0.4),
    ])

    heart_px = 3.2
    heart = pixel_rects(HEART, {"k": INK, "P": PINK, "w": PAPER}, heart_px)
    hx, hy = right + 12, 116

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Aniyah Bohnen">
  <title>Aniyah Bohnen</title>
  <defs>
    <linearGradient id="grad" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="repeat">
      <stop offset="0" stop-color="{PINK}"/>
      <stop offset="0.33" stop-color="{BLUE}"/>
      <stop offset="0.66" stop-color="{GREEN}"/>
      <stop offset="1" stop-color="{PINK}"/>
      <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 0"
        dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <clipPath id="top"><rect x="{x0}" y="{y0}" width="{w}" height="{bar}"/></clipPath>
  </defs>

  <rect x="{x0 + 6}" y="{y0 + 6}" width="{w}" height="{h}" rx="{r}" fill="{INK}"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}" fill="{PAPER}"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}" fill="{SITE_GREEN}" clip-path="url(#top)"/>
  <line x1="{x0}" y1="{y0 + bar}" x2="{x0 + w}" y2="{y0 + bar}" stroke="{INK}" stroke-width="2"/>
  <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{INK}" stroke-width="2.5"/>
  <path d="{title_d}" fill="{INK}"/>
  {dots}

  <path d="{name_d}" fill="url(#grad)" stroke="{INK}" stroke-width="3" stroke-linejoin="round" paint-order="stroke"/>
  <path d="{sub_d}" fill="#48664a"/>
{sparkles}

  <g transform="translate({num(hx)} {hy})">
    <g>
      {heart}
      <animateTransform attributeName="transform" type="translate" values="0 18;0 -34" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.2;0.7;1" dur="3.2s" repeatCount="indefinite"/>
    </g>
  </g>
</svg>
'''


# ---------------------------------------------------------------- buttons

def build_button(font, label, fill):
    size = 26
    pad = 24
    h = 50
    tw = font.width(label, size)
    w = round(tw + pad * 2)
    d = font.centered(label, size, w / 2 + 1, 34)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w + 4}" height="{h + 4}" viewBox="0 0 {w + 4} {h + 4}" role="img" aria-label="{label}">
  <title>{label}</title>
  <rect x="4" y="4" width="{w - 2}" height="{h - 2}" rx="10" fill="{INK}"/>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="10" fill="{fill}" stroke="{INK}" stroke-width="2"/>
  <path d="{d}" fill="{INK}"/>
</svg>
'''


# ---------------------------------------------------------------- pixel art
# Each icon is a list of frames; each frame is a 16x16 grid. "." is empty.

PAL = {
    "k": INK, "w": PAPER,
    "p": "#f9d3dd", "P": PINK, "R": "#e0668c",
    "b": "#cfeefb", "B": BLUE, "D": "#3f8fc0",
    "g": "#d6f2c8", "G": GREEN, "E": "#4e9a43",
    "y": "#ffe9a6", "Y": YELLOW, "O": "#f0a830",
    "s": "#e3e5e8", "S": "#a7adb5", "N": "#8a5a3c",
}

BUNNY_BODY = [
    "................",
    "...kk....kk.....",
    "..kwwk..kwwk....",
    "..kwpk..kpwk....",
    "..kwpk..kpwk....",
    "..kwpk..kpwk....",
    "..kwwkkkkwwk....",
    ".kwwwwwwwwwwk...",
    "kwwkwwwwwwkwwk..",
    "kwwkwwwwwwkwwk..",
    "kpwwwkwwkwwwpk..",
    "kwwwwwkkwwwwwk..",
    "kwwwwwwwwwwwwk..",
    ".kwwwwwwwwwwk...",
    "..kkkkkkkkkk....",
    "................",
]


def with_pixels(grid, pixels):
    rows = [list(r) for r in grid]
    for x, y, c in pixels:
        rows[y][x] = c
    return ["".join(r) for r in rows]


# paw resting by the cheek, then raised and waving (with little motion marks)
BUNNY = [
    with_pixels(BUNNY_BODY, [(14, 10, "k"), (14, 11, "w"), (15, 11, "k"), (14, 12, "k")]),
    with_pixels(BUNNY_BODY, [(14, 5, "k"), (13, 6, "k"), (14, 6, "w"), (15, 6, "k"), (14, 7, "k"),
                             (15, 3, "S"), (12, 3, "S"), (13, 2, "S")]),
]

LAPTOP_BASE = [
    "................",
    "................",
    "..kkkkkkkkkkkk..",
    "..kbbbbbbbbbbk..",
    "..kbPPPbbbbbbk..",
    "..kbbbGGGGbbbk..",
    "..kbBBBBBbbbbk..",
    "..kbbbYYbbbbbk..",
    "..kbbbbbbbbbbk..",
    "..kbbbbbbbbbbk..",
    "..kkkkkkkkkkkk..",
    ".kssssssssssssk.",
    "kssSsSsSsSsSsssk",
    "kkkkkkkkkkkkkkkk",
    "................",
    "................",
]
LAPTOP = [with_pixels(LAPTOP_BASE, [(9, 7, "k")]), LAPTOP_BASE]

MAGNIFIER_BASE = [
    "................",
    "....kkkkk.......",
    "...kbbbbbk......",
    "..kbwwbbbbk.....",
    "..kbwbbbbbk.....",
    "..kbbbbbbbk.....",
    "..kbbbbbbbk.....",
    "..kbbbbbbbk.....",
    "...kbbbbbk......",
    "....kkkkkNk.....",
    ".........kNk....",
    "..........kNk...",
    "...........kNk..",
    "............kNk.",
    ".............kk.",
    "................",
]
MAGNIFIER = [
    with_pixels(MAGNIFIER_BASE, [(13, 1, "Y"), (12, 2, "Y"), (13, 2, "O"), (14, 2, "Y"), (13, 3, "Y")]),
    MAGNIFIER_BASE,
]

CAP_BASE = [
    "................",
    "................",
    "................",
    ".......kk.......",
    ".....kkBBkk.....",
    "...kkBBBBBBkk...",
    ".kkBBBBBBBBBBkk.",
    "kBBBBBBYYYYYYBBk",
    ".kkBBBBBBBBBBYk.",
    "...kkBBBBBBkk...",
    "...kDDDDDDDDk...",
    "...kDDDDDDDDk...",
    "...kDDDDDDDDk...",
    "....kkkkkkkk....",
    "................",
    "................",
]
# tassel swings from the front corner
CAP = [
    with_pixels(CAP_BASE, [(13, 9, "Y"), (13, 10, "Y"), (13, 11, "O"), (13, 12, "O")]),
    with_pixels(CAP_BASE, [(14, 9, "Y"), (14, 10, "Y"), (15, 11, "O"), (15, 12, "O")]),
]

TROPHY_BASE = [
    "................",
    "..kkkkkkkkkkkk..",
    "kkkYYYYYYYYOOkkk",
    "k.kYYYYYYYYOOk.k",
    "k.kYYYYYYYYOOk.k",
    ".kkYYYYYYYYOOkk.",
    "...kYYYYYYOOk...",
    "....kYYYYOOk....",
    ".....kkYOkk.....",
    "......kYOk......",
    "......kYOk......",
    ".....kYYOOk.....",
    "....kkkkkkkk....",
    "....kNNNNNNk....",
    "....kkkkkkkk....",
    "................",
]
TROPHY = [
    with_pixels(TROPHY_BASE, [(4, 3, "w"), (4, 4, "w"), (5, 4, "w"), (4, 5, "w")]),
    with_pixels(TROPHY_BASE, [(7, 3, "w"), (7, 4, "w"), (8, 4, "w"), (7, 5, "w")]),
    with_pixels(TROPHY_BASE, [(10, 3, "w"), (10, 4, "w"), (9, 5, "w")]),
    TROPHY_BASE,
]

HEART_BIG = [
    "................",
    "................",
    "..kkk.....kkk...",
    ".kPPPk...kPPPk..",
    "kPwwPPk.kPPPPPk.",
    "kPwPPPPkPPPPPPk.",
    "kPPPPPPPPPPPPPk.",
    "kPPPPPPPPPPPPRk.",
    ".kPPPPPPPPPPRk..",
    "..kPPPPPPPPRk...",
    "...kPPPPPPRk....",
    "....kPPPPRk.....",
    ".....kPPRk......",
    "......kRk.......",
    ".......k........",
    "................",
]

SPARKLE = [
    [
        "................",
        "................",
        "................",
        "................",
        "................",
        ".......k........",
        "......kYk.......",
        ".....kYwYk......",
        "......kYk.......",
        ".......k........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    [
        "................",
        "................",
        ".......k........",
        ".......k........",
        "......kYk.......",
        "......kYk.......",
        "..kkkkYYYkkkk...",
        ".kYYYYYwYYYYYk..",
        "..kkkkYYYkkkk...",
        "......kYk.......",
        "......kYk.......",
        ".......k........",
        ".......k........",
        "................",
        "................",
        "................",
    ],
]


def sticker(grid):
    """Pad the grid by one cell and ring the drawing with white.

    Invisible on GitHub's light theme; on the dark theme it keeps the black
    outlines from disappearing into the background.
    """
    size = len(grid[0]) + 2
    rows = ["." * size] + ["." + r + "." for r in grid] + ["." * size]
    out = []
    for y in range(size):
        line = []
        for x in range(size):
            ch = rows[y][x]
            if ch == "." and any(
                    0 <= y + dy < size and 0 <= x + dx < size and rows[y + dy][x + dx] != "."
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                ch = "w"
            line.append(ch)
        out.append("".join(line))
    return out


def build_pixel(frames, frame_ms=450, pulse=False):
    n = len(frames)
    dur = frame_ms * n / 1000
    groups = []
    for i, grid in enumerate(frames):
        rects = pixel_rects(sticker(grid), PAL, 1, -1, -1)
        if n == 1:
            groups.append(f"<g>{rects}</g>")
            continue
        values = ";".join("visible" if j == i else "hidden" for j in range(n))
        keytimes = ";".join(num(j / n) if j else "0" for j in range(n))
        start = "visible" if i == 0 else "hidden"
        groups.append(
            f'<g visibility="{start}">{rects}'
            f'<animate attributeName="visibility" values="{values}" keyTimes="{keytimes}" '
            f'dur="{num(dur)}s" calcMode="discrete" repeatCount="indefinite"/></g>')
    body = "".join(groups)
    if pulse:
        # heartbeat: scale around the centre of the 16x16 grid
        body = (f'<g transform="translate(8 8)"><g>'
                f'<g transform="translate(-8 -8)">{body}</g>'
                f'<animateTransform attributeName="transform" type="scale" values="0.88;1;0.88;0.96;0.88" '
                f'keyTimes="0;0.15;0.3;0.45;1" dur="1.2s" repeatCount="indefinite"/></g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="-1 -1 18 18" '
            f'shape-rendering="crispEdges">{body}</svg>\n')


PIXEL_ICONS = {
    "bunny": (BUNNY, 500, False),
    "laptop": (LAPTOP, 530, False),
    "magnifier": (MAGNIFIER, 600, False),
    "cap": (CAP, 450, False),
    "trophy": (TROPHY, 180, False),
    "heart": ([HEART_BIG], 0, True),
    "sparkle": (SPARKLE, 400, False),
}


# ---------------------------------------------------------------- kisa.gif

def build_kisa(data, out):
    src = Image.open(io.BytesIO(data))
    crop = (541, 48, 941, 448)          # the cat lives around x 625-858 in the 1500x500 banner
    bar, border, radius, shadow = 34, 3, 16, 6
    cw, ch = crop[2] - crop[0], crop[3] - crop[1]
    W = cw + border * 2 + shadow
    H = ch + bar + border * 2 + shadow

    key = (255, 0, 255)
    ink = (17, 17, 17)
    green = (230, 247, 217)

    frame_bg = Image.new("RGB", (W, H), key)
    d = ImageDraw.Draw(frame_bg)
    box = (0, 0, W - shadow - 1, H - shadow - 1)
    d.rounded_rectangle((shadow, shadow, W - 1, H - 1), radius, fill=ink)
    d.rounded_rectangle(box, radius, fill=(255, 255, 255), outline=ink, width=border)
    top = Image.new("L", (W, H), 0)
    ImageDraw.Draw(top).rounded_rectangle((border, border, box[2] - border, box[3] - border),
                                          radius - border, fill=255)
    bar_img = Image.new("RGB", (W, H), green)
    bar_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(bar_mask).rectangle((0, 0, W, border + bar - 1), fill=255)
    frame_bg.paste(bar_img, (0, 0), Image.composite(top, Image.new("L", (W, H), 0), bar_mask))
    d.line((border, border + bar, box[2] - border, border + bar), fill=ink, width=2)
    for i, c in enumerate([(244, 154, 180), (124, 196, 234), (154, 212, 134)]):
        cx = box[2] - 26 - i * 24
        cy = border + bar // 2
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=c, outline=ink, width=2)

    frames, durations = [], []
    for f in ImageSequence.Iterator(src):
        cat = f.convert("RGB").crop(crop)
        cat = cat.point(lambda v: 255 if v > 228 else v)
        frame = frame_bg.copy()
        frame.paste(cat, (border, border + bar + 1))
        frames.append(frame)
        durations.append(f.info.get("duration", 60))

    # one shared palette for every frame, built from two sample frames
    pal_src = Image.new("RGB", (W, H * 2))
    pal_src.paste(frames[0], (0, 0))
    pal_src.paste(frames[len(frames) // 2], (0, H))
    palette = pal_src.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    p_frames = [fr.quantize(palette=palette, dither=Image.Dither.NONE) for fr in frames]
    pal = palette.getpalette()[:96]
    key_idx = min(range(32), key=lambda i: sum(abs(pal[i*3+j] - key[j]) for j in range(3)))
    p_frames[0].save(out, save_all=True, append_images=p_frames[1:], duration=durations,
                     loop=0, transparency=key_idx, disposal=1, optimize=True)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", type=pathlib.Path)
    ap.add_argument("--kisa", type=pathlib.Path)
    args = ap.parse_args()

    font = Font(args.font.read_bytes() if args.font else fetch(FONT_URL))
    kisa = args.kisa.read_bytes() if args.kisa else fetch(KISA_URL)

    (ASSETS / "buttons").mkdir(parents=True, exist_ok=True)
    (ASSETS / "pixel").mkdir(parents=True, exist_ok=True)

    (ASSETS / "name.svg").write_text(build_name(font), encoding="utf-8")

    for slug, label, fill in [
        ("site", "aniyah.dev", SITE_GREEN),
        ("linkedin", "LinkedIn", SITE_BLUE),
        ("devpost", "Devpost", SITE_PINK),
        ("email", "email", "#fff3c4"),
    ]:
        (ASSETS / "buttons" / f"{slug}.svg").write_text(build_button(font, label, fill), encoding="utf-8")

    for slug, (frames, ms, pulse) in PIXEL_ICONS.items():
        (ASSETS / "pixel" / f"{slug}.svg").write_text(build_pixel(frames, ms, pulse), encoding="utf-8")

    build_kisa(kisa, ASSETS / "kisa.gif")
    print("assets written to", ASSETS)


if __name__ == "__main__":
    main()
