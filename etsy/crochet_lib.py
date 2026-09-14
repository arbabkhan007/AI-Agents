"""
crochet_lib - draw pixel-perfect "screenshots" of the Crochet Craft Fair
Tracker using the REAL demo data (crochet_tracker.demo.Demo), for the
Etsy listing images and the user-guide PDF.

Everything is drawn with PIL: fonts are Poppins / Gelasio (Georgia-metric)
/ Playfair Display / Caveat / JetBrains Mono, plus NotoColorEmoji for the
emoji the real workbook uses.  The palette mirrors the workbook's Berry
theme (cream / deep berry plum / rose / honey gold).

This module is a sibling of etsy/catering_lib.py and deliberately leaves
that file (and the Christmas engine) untouched.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from crochet_tracker import config as C
from crochet_tracker.demo import Demo

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# ---------------------------------------------------------------------------
# palette (classic theme of the workbook)
# ---------------------------------------------------------------------------
PRIMARY = "#5C3A50"          # deep berry plum  (the "espresso" role)
MAUVE = "#8A5F79"            # dusty mauve      (the "latte" role)
ROSE = "#C05268"             # rose accent      (the "copper" role)
GOLD = "#B98A2E"             # honey gold       (the "brass" role)
INK = "#33222C"
MUTED = "#97818D"
CREAM = "#FAF6F1"
CANVAS = "#FAF6F1"
CARD = "#FFFFFF"
ALT = "#FBF7F3"
BORDER = "#E6D9D2"
WHITE = "#FFFFFF"
OK = "#4C7A4C"
WARN = "#B4761A"
BAD = "#AC2F2F"
INFO = "#5E6FA3"
PLUM = "#7A5273"
SOFT = {
    "primary": "#EDE2E8", "mauve": "#EFE2EA", "rose": "#F8E3E7",
    "gold": "#F6EDD8", "ok": "#E2EEE0", "warn": "#FBF0D9", "bad":
    "#F7E2E0", "info": "#E5E9F4", "plum": "#F0E6EE", "muted": "#F2EBEE",
}
COLORS = {
    "primary": PRIMARY, "mauve": MAUVE, "rose": ROSE, "gold": GOLD,
    "ok": OK, "warn": WARN, "bad": BAD, "info": INFO, "plum": PLUM,
    "muted": MUTED, "ink": INK,
}

EMOJI_STRIKE = 109


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# fonts
# ---------------------------------------------------------------------------
_FILES = {
    "sans": "Poppins-Regular.ttf", "sans_md": "Poppins-Medium.ttf",
    "sans_sb": "Poppins-SemiBold.ttf", "sans_b": "Poppins-Bold.ttf",
    "sans_xb": "Poppins-ExtraBold.ttf",
    "serif": "Gelasio[wght].ttf", "display": "PlayfairDisplay[wght].ttf",
    "hand": "Caveat[wght].ttf", "mono": "JetBrainsMono[wght].ttf",
}
_VAR_WEIGHT = {"serif": "Regular", "serif_b": "Bold", "serif_sb": "SemiBold",
               "display": "Regular", "display_b": "Bold",
               "display_xb": "ExtraBold", "display_blk": "Black",
               "hand": "Bold", "mono": "Medium"}
_font_cache = {}
_emoji_font = None


def F(name, size):
    """Get a cached font.  name in _FILES keys + weight variants."""
    key = (name, size)
    if key in _font_cache:
        return _font_cache[key]
    base = name.split("_")[0] if name.split("_")[0] in ("serif", "display",
                                                        "hand", "mono") \
        else name
    path = os.path.join(FONTS, _FILES[base])
    f = ImageFont.truetype(path, size)
    if base != name:                       # variable weight variant
        try:
            f.set_variation_by_name(_VAR_WEIGHT[name])
        except Exception:
            pass
    _font_cache[key] = f
    return f


def emoji_font():
    global _emoji_font
    if _emoji_font is None:
        _emoji_font = ImageFont.truetype(
            os.path.join(FONTS, "NotoColorEmoji.ttf"), EMOJI_STRIKE)
    return _emoji_font


# ---------------------------------------------------------------------------
# emoji-aware text engine
# ---------------------------------------------------------------------------
_EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2B00, 0x2BFF), (0x2300, 0x23FF),
                 (0x2190, 0x21FF), (0x2600, 0x27BF))
_SPECIAL = {"\u2713": "check"}             # drawn as a vector check mark


def _is_emoji(ch):
    o = ord(ch)
    if o == 0x2713:
        return False
    return any(a <= o <= b for a, b in _EMOJI_RANGES)


def tokenize(s):
    """Split into [('text'|'emoji'|'check', run)] runs."""
    runs = []

    def push(kind, chunk):
        if chunk:
            if runs and runs[-1][0] == kind and kind == "text":
                runs[-1] = (kind, runs[-1][1] + chunk)
            else:
                runs.append((kind, chunk))

    for ch in str(s):
        if ord(ch) in (0xFE0F, 0x200D):
            continue
        if ch in _SPECIAL:
            push("check", ch)
        elif _is_emoji(ch):
            push("emoji", ch)
        else:
            push("text", ch)
    return runs


_emoji_bitmap_cache = {}


def emoji_bitmap(ch, height):
    key = (ch, height)
    if key in _emoji_bitmap_cache:
        return _emoji_bitmap_cache[key]
    scratch = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(scratch)
    d.text((30, 30), ch, font=emoji_font(), embedded_color=True)
    box = scratch.getbbox()
    if box is None:                        # fallback: empty
        bmp = Image.new("RGBA", (height, height), (0, 0, 0, 0))
    else:
        bmp = scratch.crop(box)
        scale = height / float(bmp.height)
        bmp = bmp.resize((max(1, int(bmp.width * scale)), height),
                         Image.LANCZOS)
    _emoji_bitmap_cache[key] = bmp
    return bmp


_scratch_draw = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def text_width(s, font):
    total = 0
    size = font.size
    ascent, _ = font.getmetrics()
    for kind, chunk in tokenize(s):
        if kind == "text":
            total += _scratch_draw.textlength(chunk, font=font)
        elif kind == "emoji":
            for ch in chunk:
                total += emoji_bitmap(ch, int(ascent * 1.02)).width + \
                    int(size * 0.06)
        else:                              # check mark
            total += int(ascent * 0.9)
    return total


def draw_text(img, xy, s, font, fill=INK, anchor="la"):
    """Emoji-aware text.  anchor: la | ma | ra (y is always the top)."""
    x, y = xy
    w = text_width(s, font)
    if anchor == "ma":
        x -= w / 2.0
    elif anchor == "ra":
        x -= w
    d = ImageDraw.Draw(img)
    ascent, descent = font.getmetrics()
    for kind, chunk in tokenize(s):
        if kind == "text":
            d.text((x, y), chunk, font=font, fill=fill)
            x += _scratch_draw.textlength(chunk, font=font)
        elif kind == "emoji":
            h = int(ascent * 1.02)
            for ch in chunk:
                bmp = emoji_bitmap(ch, h)
                img.paste(bmp, (int(x), int(y + (ascent - h) * 0.45)), bmp)
                x += bmp.width + int(font.size * 0.06)
        else:                              # vector check mark
            size = ascent * 0.72
            cx, cy = x + size * 0.1, y + ascent * 0.72
            check_poly(d, cx, cy, size, fill, max(2, int(ascent * 0.11)))
            x += int(ascent * 0.9)
    return w


def check_poly(d, cx, cy, size, color, width):
    """A crisp vector check mark centred on (cx, cy)."""
    s = size / 2.0
    pts = [(cx - s * 0.95, cy + s * 0.05), (cx - s * 0.3, cy + s * 0.7),
           (cx + s * 1.0, cy - s * 0.75)]
    d.line(pts, fill=color, width=width, joint="curve")


def fit_size(s, spec, size, max_w, min_size=10):
    """Shrink font size until the string fits max_w. Returns (font, size)."""
    while size > min_size:
        f = F(spec, size)
        if text_width(s, f) <= max_w:
            return f, size
        size -= 2
    return F(spec, min_size), min_size


def wrap(s, font, max_w):
    lines, line = [], ""
    for word in str(s).split():
        trial = word if not line else line + " " + word
        if text_width(trial, font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or [""]


# ---------------------------------------------------------------------------
# small drawing primitives
# ---------------------------------------------------------------------------
def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def chip(img, xy, s, bg, fg, size=20, spec="sans_sb", pad=(16, 9),
         bold=True, radius=None):
    """Draw a rounded pill of text.  Returns its width."""
    x, y = xy
    f = F(spec, size)
    w = text_width(s, f)
    h = int(size * 1.9)
    d = ImageDraw.Draw(img)
    r = radius if radius is not None else h // 2
    rrect(d, [x, y, x + w + pad[0] * 2, y + h], r, fill=hexrgb(bg) if
          isinstance(bg, str) and bg.startswith("#") else
          (bg if isinstance(bg, tuple) else hexrgb(SOFT[bg])))
    draw_text(img, (x + pad[0], y + (h - size) / 2.0 - size * 0.14), s, f,
              COLORS.get(fg, fg) if not str(fg).startswith("#") else fg)
    return w + pad[0] * 2


def shadow_paste(canvas, img, xy, blur=24, alpha=70, offset=(0, 14)):
    x, y = int(xy[0]), int(xy[1])
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                   fill=255)
    sh.paste(Image.new("RGBA", img.size, (20, 15, 10, alpha)),
             (x + offset[0], y + offset[1]), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh)
    canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)


def blocks_bar(img, box, pct, n=40, fg=MAUVE, bg=CARD, gap=4,
               border=BORDER):
    """The workbook's signature text progress bar, drawn as blocks."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=hexrgb(bg), outline=hexrgb(border))
    inner = [x0 + 5, y0 + 5, x1 - 5, y1 - 5]
    total = int(n * pct + 0.5)
    slot = (inner[2] - inner[0] - gap * (n - 1)) / float(n)
    for i in range(n):
        bx = inner[0] + i * (slot + gap)
        d.rectangle([bx, inner[1], bx + slot, inner[3]],
                    fill=hexrgb(fg if i < total else "#F0E5E9"))


# ---------------------------------------------------------------------------
# sheet chrome shared by every screen
# ---------------------------------------------------------------------------
def screen_canvas(width, height, bg=CANVAS):
    img = Image.new("RGBA", (width, height), hexrgb(bg))
    return img


def sheet_header(img, title, subtitle, y=0, width=1320, pill_home=True):
    """The 3-row title band every tracker tab uses."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, width, y + 92], fill=hexrgb(CANVAS))
    draw_text(img, (44, y + 10), title, F("serif_b", 40), PRIMARY)
    if pill_home:
        f = F("sans_sb", 17)
        s = "\U0001F3E0  Back to Dashboard"
        w = text_width(s, f)
        rrect(d, [width - 44 - w - 36, y + 24, width - 44, y + 66], 8,
              fill=hexrgb(ROSE))
        draw_text(img, (width - 44 - w - 18, y + 30), s, f, WHITE)
    draw_text(img, (44, y + 64), subtitle, F("sans", 18), MUTED)
    return y + 104


def pill_row(img, y, pills, width=1320, x=44, gap=12, size=17):
    """The quick-stat strip. pills = [(text, color_key)]."""
    for text, color in pills:
        f = F("sans_sb", size)
        w = text_width(text, f) + 30
        d = ImageDraw.Draw(img)
        rrect(d, [x, y, x + w, y + 40], 20, fill=hexrgb(SOFT[color]))
        draw_text(img, (x + 15, y + 8), text, f, COLORS[color])
        x += w + gap
    return y + 40


def section_bar(img, y, text, color=PRIMARY, width=1320, h=52, size=24,
                x=44, w_pad=36):
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + width - 88, y + h], 6, fill=hexrgb(color))
    draw_text(img, (x + 20, y + (h - size) / 2.0 - 2), text,
              F("serif_b", size), WHITE)
    return y + h


STATUS_COLORS = {
    C.ST_OUT: ("bad", "bad"), C.ST_LOW: ("warn", "warn"),
    C.ST_OK: ("ok", "ok"),
}
REORDER_COLORS = {
    C.RE_YES: ("warn", "warn"), C.RE_NO: ("ok", "ok"),
}
PRIORITY_COLORS = {
    C.PR_URGENT: ("bad", "bad"), C.PR_HIGH: ("warn", "warn"),
    C.PR_NORMAL: ("gold", "gold"),
}
PAYMENT_COLORS = {
    "Cash": ("ok", "ok"), "Card": ("info", "info"),
    "Bank transfer": ("plum", "plum"), "Mobile wallet": ("gold", "gold"),
    "Online order": ("rose", "rose"), "Other": ("muted", "muted"),
}


def draw_table(img, x, y, widths, headers, rows, row_h=42, hdr_h=48,
               hdr_bg=PRIMARY, size=17, hdr_size=15, pad=12):
    """rows: list of lists; each cell = str or dict:
       {"t": text, "align": "l/c/r", "color": key, "pill": (bgkey, fgkey),
        "tick": bool, "mono": bool, "bold": bool}"""
    d = ImageDraw.Draw(img)
    total_w = sum(widths)
    rrect(d, [x, y, x + total_w, y + hdr_h], 8, fill=hexrgb(hdr_bg))
    cx = x
    for w, htxt in zip(widths, headers):
        f, _ = fit_size(htxt, "sans_sb", hdr_size, w - 10, 10)
        draw_text(img, (cx + w / 2.0, y + (hdr_h - f.size) / 2.0 - 1), htxt,
                  f, WHITE, anchor="ma")
        cx += w
    yy = y + hdr_h
    for ri, row in enumerate(rows):
        bg = ALT if ri % 2 else CARD
        d.rectangle([x, yy, x + total_w, yy + row_h], fill=hexrgb(bg))
        cx = x
        for w, cell in zip(widths, row):
            cell = cell if isinstance(cell, dict) else {"t": cell}
            txt = str(cell.get("t", ""))
            align = cell.get("align", "l")
            color = COLORS.get(cell.get("color", "ink"), INK)
            if cell.get("pill"):
                bgk, fgk = cell["pill"]
                pf = F("sans_sb", size - 1)
                pw = text_width(txt, pf) + 22
                rrect(d, [cx + (w - pw) / 2.0, yy + 6,
                          cx + (w + pw) / 2.0, yy + row_h - 6],
                      (row_h - 12) / 2.0, fill=hexrgb(SOFT[bgk]))
                draw_text(img, (cx + w / 2.0, yy + (row_h - pf.size) / 2.0
                                - 1), txt, pf, COLORS[fgk], anchor="ma")
            elif cell.get("tick"):
                check_poly(d, cx + w / 2.0, yy + row_h / 2.0, size * 1.1,
                           OK, 4)
            else:
                f, _ = fit_size(txt, "sans_b" if cell.get("bold") else
                                ("mono" if cell.get("mono") else "sans_md"),
                                size, w - 2 * pad - 4, 9)
                ty = yy + (row_h - f.size) / 2.0 - 1
                if align == "c":
                    draw_text(img, (cx + w / 2.0, ty), txt, f, color,
                              anchor="ma")
                elif align == "r":
                    draw_text(img, (cx + w - pad, ty), txt, f, color,
                              anchor="ra")
                else:
                    draw_text(img, (cx + pad, ty), txt, f, color)
            cx += w
        cx = x
        for w in widths[:-1]:
            cx += w
            d.line([cx, yy, cx, yy + row_h], fill=hexrgb(BORDER), width=1)
        yy += row_h
    d.rectangle([x, y, x + total_w, yy], outline=hexrgb(BORDER), width=1)
    return yy


# ---------------------------------------------------------------------------
# charts (real data)
# ---------------------------------------------------------------------------
def _axis_title(img, box, title, size=1.0):
    draw_text(img, ((box[0] + box[2]) / 2.0, box[1] - int(34 * size)), title,
              F("serif_sb", int(23 * size)), PRIMARY, anchor="ma")


def hbar_chart(img, box, title, items, color=ROSE, fmt="${:,.0f}",
               size=1.0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    fs = lambda n: F("sans_sb", int(n * size))
    n = len(items)
    row_h = (y1 - y0) / float(n)
    label_w = max(text_width(lbl, fs(16)) for lbl, _ in items) + 18 * size
    val_w = max(text_width(fmt.format(v), fs(16))
                for _, v in items) + 10 * size
    gx0, gx1 = x0 + label_w, x1 - val_w
    vmax = max(v for _, v in items) or 1
    for i in range(5):                     # gridlines
        gx = gx0 + (gx1 - gx0) * i / 4.0
        d.line([gx, y0, gx, y1], fill=hexrgb(BORDER), width=1)
    for i, (lbl, v) in enumerate(items):
        cy = y0 + row_h * (i + 0.5)
        draw_text(img, (x0, cy - 12 * size), lbl, fs(16), INK)
        bw = (gx1 - gx0) * v / float(vmax)
        rrect(d, [gx0, cy - 12 * size, gx0 + max(bw, 6 * size),
                  cy + 12 * size], int(6 * size), fill=hexrgb(color))
        draw_text(img, (x1, cy - 11 * size), fmt.format(v), fs(16),
                  PRIMARY, anchor="ra")


def grouped_columns(img, box, title, cats, series, fmt="{:,.0f}", size=1.0):
    """series = [(name, values, color)]"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    all_v = [v for _, vals, _ in series for v in vals]
    vmax = max(all_v) or 1
    ncat = len(cats)
    slot = (x1 - x0) / float(ncat)
    bw = min(34 * size, slot * 0.32)
    for i in range(5):
        gy = y1 - (y1 - y0 - 30 * size) * i / 4.0
        d.line([x0, gy, x1, gy], fill=hexrgb(BORDER), width=1)
        draw_text(img, (x0 - 8 * size, gy - 9 * size),
                  fmt.format(vmax * i / 4.0), F("sans", int(13 * size)),
                  MUTED, anchor="ra")
    for ci, cat in enumerate(cats):
        cx = x0 + slot * (ci + 0.5)
        f, _ = fit_size(cat, "sans_md", int(13 * size), slot - 6 * size,
                        int(8 * size))
        draw_text(img, (cx, y1 - 26 * size), cat, f, MUTED, anchor="ma")
        for si, (name, vals, color) in enumerate(series):
            v = vals[ci]
            h = (y1 - 30 * size - y0) * v / float(vmax)
            bx = cx - bw - 3 * size + si * (bw + 6 * size)
            d.rectangle([bx, y1 - 30 * size - h, bx + bw, y1 - 30 * size],
                        fill=hexrgb(color))
    lx = x0
    for name, _, color in series:
        d.rectangle([lx, y0 - 22 * size, lx + 16 * size, y0 - 6 * size],
                    fill=hexrgb(color))
        draw_text(img, (lx + 22 * size, y0 - 24 * size), name,
                  F("sans_sb", int(15 * size)), INK)
        lx += 22 * size + text_width(name, F("sans_sb", int(15 * size))) \
            + 26 * size


def line_series(img, box, title, cats, values, color=PRIMARY, fmt="{:,.0f}",
                size=1.0, width=None):
    """A single line with markers (the 'net' line of the combo charts)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    vmax = max(max(values), 1)
    vmin = min(min(values), 0)
    ncat = len(cats)
    slot = (x1 - x0) / float(ncat)
    pts = []
    for ci, v in enumerate(values):
        cx = x0 + slot * (ci + 0.5)
        cy = y1 - 30 * size - (y1 - 30 * size - y0) * (v - vmin) / \
            float(vmax - vmin or 1)
        pts.append((cx, cy))
    if width is None:
        width = max(3, int(4 * size))
    d.line(pts, fill=hexrgb(color), width=width, joint="curve")
    for (cx, cy) in pts:
        d.ellipse([cx - 6 * size, cy - 6 * size, cx + 6 * size,
                   cy + 6 * size], fill=hexrgb(color))


def doughnut_chart(img, box, title, items, size=1.0, center_word="events",
                   center_value=None):
    """items = [(label, value, color)]"""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    total = sum(v for _, v, _ in items) or 1
    cx, cy = x0 + (y1 - y0) / 2.0 + 10, (y0 + y1) / 2.0
    r = (y1 - y0) / 2.0 - 6
    start = -90
    for lbl, v, color in items:
        sweep = 360.0 * v / total
        if v:
            d.pieslice([cx - r, cy - r, cx + r, cy + r], start,
                       start + sweep, fill=hexrgb(color),
                       outline=hexrgb(CREAM))
        start += sweep
    hr = r * 0.58
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=hexrgb(CARD),
              outline=hexrgb(BORDER))
    big = center_value if center_value is not None else total
    draw_text(img, (cx, cy - 26 * size), str(big),
              F("display_b", int(44 * size)), PRIMARY, anchor="ma")
    draw_text(img, (cx, cy + 24 * size), center_word,
              F("sans_sb", int(16 * size)), MUTED, anchor="ma")
    lx = cx + r + 40 * size
    ly = y0 + 24 * size
    import re as _re
    for lbl, v, color in items:
        lbl = _re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF"
                      r"\u2300-\u23FF\u2190-\u21FF]\uFE0F?\s*", "", lbl).strip()
        d.rectangle([lx, ly + 4, lx + 16, ly + 20], fill=hexrgb(color))
        f, _ = fit_size(lbl, "sans_md", 15, x1 - lx - 90, 9)
        draw_text(img, (lx + 24, ly), lbl, f, INK)
        draw_text(img, (x1, ly - 1), str(v), F("sans_sb", 16), PRIMARY,
                  anchor="ra")
        ly += 34


def stacked_columns(img, box, title, cats, series, fmt="{:,.0f}", size=1.0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    _axis_title(img, box, title, size=size)
    totals = [sum(vals[i] for _, vals, _ in series) for i in range(len(cats))]
    vmax = max(totals) or 1
    slot = (x1 - x0) / float(len(cats))
    bw = min(44 * size, slot * 0.44)
    for i in range(5):
        gy = y1 - (y1 - y0 - 30 * size) * i / 4.0
        d.line([x0, gy, x1, gy], fill=hexrgb(BORDER), width=1)
        draw_text(img, (x0 - 8 * size, gy - 9 * size),
                  fmt.format(vmax * i / 4.0), F("sans", int(13 * size)),
                  MUTED, anchor="ra")
    for ci, cat in enumerate(cats):
        cx = x0 + slot * (ci + 0.5)
        f, _ = fit_size(cat, "sans_md", int(13 * size), slot - 4 * size,
                        int(8 * size))
        draw_text(img, (cx, y1 - 26 * size), cat, f, MUTED, anchor="ma")
        base = y1 - 30 * size
        for name, vals, color in series:
            v = vals[ci]
            h = (y1 - 30 * size - y0) * v / float(vmax)
            if h > 0:
                d.rectangle([cx - bw / 2.0, base - h, cx + bw / 2.0, base],
                            fill=hexrgb(color))
                base -= h
    lx = x0
    for name, _, color in series:
        d.rectangle([lx, y0 - 22 * size, lx + 16 * size, y0 - 6 * size],
                    fill=hexrgb(color))
        draw_text(img, (lx + 22 * size, y0 - 24 * size), name,
                  F("sans_sb", int(15 * size)), INK)
        lx += 22 * size + text_width(name, F("sans_sb", int(15 * size))) \
            + 26 * size


# ---------------------------------------------------------------------------
# the real data
# ---------------------------------------------------------------------------
def get_model():
    """The demo business, with every aggregate the screens need."""
    return Demo()


def kpi_card(img, x, y, w, label, value, color, value_size=40,
             label_size=15, h_label=34, h_value=76, pct=False):
    d = ImageDraw.Draw(img)
    rrect(d, [x, y, x + w, y + h_label], 6, fill=hexrgb(COLORS[color]))
    f, _ = fit_size(label, "sans_sb", label_size, w - 16, 9)
    draw_text(img, (x + w / 2.0, y + (h_label - f.size) / 2.0 - 1), label, f,
              WHITE, anchor="ma")
    rrect(d, [x, y + h_label, x + w, y + h_label + h_value], 6,
          fill=hexrgb(CARD), outline=hexrgb(BORDER))
    f, _ = fit_size(value, "display_b", value_size, w - 30, 14)
    draw_text(img, (x + w / 2.0, y + h_label + (h_value - f.size) / 2.0 - 4),
              value, f, COLORS[color], anchor="ma")
    return y + h_label + h_value
