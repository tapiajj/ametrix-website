"""Generate Ametrix logo lockups with Inter text converted to vector outlines.

Usage (from the repo root):
    pip install fonttools uharfbuzz
    Download Inter 4.x from https://github.com/rsms/inter/releases and unzip into tools/inter/
    python tools/gen_logo.py

Outputs assets/brand/logo-*.svg and tools/logo-symbol.html (the inline <symbol> used in index.html / 404.html).
"""
import os, re, json
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "brand")
FONT_BOLD = os.path.join(HERE, "inter/extras/ttf/Inter-ExtraBold.ttf")
FONT_MED = os.path.join(HERE, "inter/extras/ttf/Inter-Medium.ttf")

ICON_PATHS = [
    "M50 6 L85 16 L85 96 L50 106 L15 96 L15 16 Z",
    "M15 36 L50 46 L85 36",
    "M50 46 L50 106",
    "M15 56 L50 66 L85 56",
    "M15 76 L50 86 L85 76",
]
ICON_W, ICON_H = 100, 112
ICON_CX, ICON_CY = 50.0, 56.0   # geometric centre of the icon inside its 100x112 box
ICON_SCALE = 0.93               # icon reduced 7% (refinement brief: 5-8%), scaled about its centre
DESC_SCALE = 0.92               # "technologies" reduced 8% (brief: 5-10%) relative to the width-matched size


def scaled_icon_paths(scale=ICON_SCALE):
    """ICON_PATHS scaled about the icon centre; stroke width is left untouched so line weight is preserved."""
    def repl(m):
        x = ICON_CX + (float(m.group(1)) - ICON_CX) * scale
        y = ICON_CY + (float(m.group(2)) - ICON_CY) * scale
        return f"{x:g} {y:g}".replace("-0 ", "0 ")
    return [re.sub(r"(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)", repl, path) for path in ICON_PATHS]


def shape(path, text, size, tracking_em=0.0):
    """Return (list of (glyphname, x_offset_px), total_width_px, upem)."""
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    tt = TTFont(path)
    upem = tt["head"].unitsPerEm
    scale = size / upem
    x = 0.0
    glyphs = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = tt.getGlyphName(info.codepoint)
        glyphs.append((name, x + pos.x_offset * scale, pos.y_offset * scale))
        x += pos.x_advance * scale + tracking_em * size
    total = x - tracking_em * size  # no tracking after the last glyph
    return tt, glyphs, total, scale


def word_paths(tt, glyphs, scale, ox, oy):
    """SVG path 'd' strings for each glyph placed at origin (ox, oy baseline), y flipped."""
    gs = tt.getGlyphSet()
    ds = []
    bp = BoundsPen(gs)
    for name, gx, gy in glyphs:
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (scale, 0, 0, -scale, ox + gx, oy - gy))
        gs[name].draw(tp)
        d = pen.getCommands()
        if d:
            ds.append(d)
        bpen = TransformPen(bp, (scale, 0, 0, -scale, ox + gx, oy - gy))
        gs[name].draw(bpen)
    return " ".join(ds), bp.bounds  # bounds: (xmin, ymin, xmax, ymax) in svg coords


def build(word_size=60.0, tracking_word=-0.015, tracking_desc=0.0, gap_text=7.0, icon_gap=18.0):
    tt1, g1, w1, s1 = shape(FONT_BOLD, "ametrix", word_size, tracking_word)
    # size "technologies" so its width matches the wordmark width (per the logo idea)
    _, g2p, w2p, _ = shape(FONT_MED, "technologies", 100.0, tracking_desc)
    desc_size = 100.0 * w1 / w2p * DESC_SCALE   # slightly narrower than "ametrix" for clearer hierarchy
    tt2, g2, w2, s2 = shape(FONT_MED, "technologies", desc_size, tracking_desc)

    # First pass at baseline 0 to measure bounds
    _, b1 = word_paths(tt1, g1, s1, 0, 0)
    _, b2 = word_paths(tt2, g2, s2, 0, 0)
    h1_top = -b1[1]            # height above baseline of ametrix (i-dot / t)
    asc2 = -b2[1]              # ascender height of technologies (t,h,l)
    desc2 = b2[3]              # descender depth (g)

    # vertical layout: ametrix baseline y1, technologies baseline y2
    block_h = h1_top + gap_text + asc2 + desc2
    icon_center = ICON_H / 2
    top = icon_center - block_h / 2
    y1 = top + h1_top
    y2 = y1 + gap_text + asc2

    # Keep the optical gap between the icon's right edge and the wordmark unchanged after the icon shrinks.
    icon_shrink = (ICON_CX - 15.0) * (1.0 - ICON_SCALE)
    tx = ICON_W + icon_gap - icon_shrink - b1[0]  # align left edge of ink with text origin
    d1, bb1 = word_paths(tt1, g1, s1, tx, y1)
    d2, bb2 = word_paths(tt2, g2, s2, tx + (b1[0] - b2[0]), y2)  # align ink left edges
    right = max(bb1[2], bb2[2])
    return dict(d1=d1, d2=d2, right=right, bb1=bb1, bb2=bb2, word_size=word_size, desc_size=desc_size,
                text_left=min(bb1[0], bb2[0]))


def icon_group(stroke, tx=0, ty=0):
    g = f'<g transform="translate({tx} {ty})" fill="none" stroke="{stroke}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round">'
    g += "".join(f'<path d="{p}"/>' for p in scaled_icon_paths()) + "</g>"
    return g


def horizontal_svg(L, icon, word, desc, bg=None, pad=6):
    W = round(L["right"] + pad, 1)
    H = ICON_H
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Ametrix Technologies">']
    if bg:
        parts.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
    parts.append(icon_group(icon))
    parts.append(f'<path fill="{word}" d="{L["d1"]}"/>')
    parts.append(f'<path fill="{desc}" d="{L["d2"]}"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def stacked_svg(L, icon, word, desc, bg=None, gap=16, pad=10):
    text_w = L["right"] - L["text_left"]
    W = round(max(text_w, ICON_W) + pad * 2, 1)
    text_h = L["bb2"][3] - L["bb1"][1]
    H = round(pad + ICON_H + gap + text_h + pad, 1)
    icon_x = (W - ICON_W) / 2
    # move text: from its current left (text_left) and top (bb1 ymin) to centered below the icon
    tx = (W - text_w) / 2 - L["text_left"]
    ty = pad + ICON_H + gap - L["bb1"][1]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Ametrix Technologies">']
    if bg:
        parts.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
    parts.append(icon_group(icon, round(icon_x, 2), pad))
    parts.append(f'<g transform="translate({tx:.2f} {ty:.2f})"><path fill="{word}" d="{L["d1"]}"/><path fill="{desc}" d="{L["d2"]}"/></g>')
    parts.append("</svg>")
    return "\n".join(parts)


def symbol_snippet(L):
    """Inline <symbol> for the website: colors come from CSS variables."""
    W = round(L["right"] + 2, 1)
    s = f'<symbol id="ametrix-logo" viewBox="0 0 {W} {ICON_H}">'
    s += icon_group("var(--logo-icon)")
    s += f'<path fill="var(--logo-word)" d="{L["d1"]}"/>'
    s += f'<path fill="var(--logo-desc)" d="{L["d2"]}"/>'
    s += "</symbol>"
    return s, W


if __name__ == "__main__":
    L = build()
    os.makedirs(OUT, exist_ok=True)
    files = {
        "logo-light.svg": horizontal_svg(L, "#2497E8", "#0F2D5B", "#2497E8"),
        "logo-dark.svg": horizontal_svg(L, "#22B8E6", "#FFEEDB", "#FF8A52"),
        "logo-mono-black.svg": horizontal_svg(L, "#000000", "#000000", "#000000"),
        "logo-mono-white.svg": horizontal_svg(L, "#FFFFFF", "#FFFFFF", "#FFFFFF"),
        "logo-stacked-light.svg": stacked_svg(L, "#2497E8", "#0F2D5B", "#2497E8"),
        "logo-stacked-dark.svg": stacked_svg(L, "#22B8E6", "#FFEEDB", "#FF8A52"),
    }
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg + "\n")
    sym, W = symbol_snippet(L)
    with open(os.path.join(HERE, "logo-symbol.html"), "w", encoding="utf-8") as f:
        f.write(sym)
    print(json.dumps({"word_size": L["word_size"], "desc_size": round(L["desc_size"], 2), "ratio": round(L["desc_size"] / L["word_size"], 3),
                      "symbol_viewbox_w": W, "bb1": [round(v, 1) for v in L["bb1"]], "bb2": [round(v, 1) for v in L["bb2"]],
                      "symbol_bytes": len(sym)}))
