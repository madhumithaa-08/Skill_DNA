"""
SKILL DNA — 18-second cinematic intro animation.

Renders 1920×1080 @ 30fps frames using Pillow + numpy, then encodes to MP4
with ffmpeg. Matches the brand palette (deep indigo, amber, craft crimson).

Sections (18 seconds = 540 frames @ 30fps):
  0–4s   [f000–119]  The craft — artisan hero full bleed, slow Ken Burns, voiceover cue
  4–9s   [f120–269]  The problem — fragmentation, "what gets recorded / what gets lost"
  9–14s  [f270–419]  The loss — hands fading, emotional punch line
  14–18s [f420–539]  SKILL DNA emerges — pipeline diagram, title card, cut frame

Output:
    kit/results/intro.mp4
"""
from __future__ import annotations

import math
import os
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "kit" / "results"
FRAMES  = RESULTS / "intro_frames"

W, H   = 1920, 1080
FPS    = 30
TOTAL  = 18  # seconds
N      = TOTAL * FPS  # 540 frames

# ── Brand colours (RGB tuples)
BG          = (7,   6,  15)   # #07060f
INDIGO_DARK = (12,  8,  46)   # ~#0c082e
AMBER       = (251,191, 36)   # #fbbf24
AMBER_DIM   = (180,130, 20)
CRIMSON     = (180, 30, 60)
WHITE       = (255,255,255)
STONE       = (168,162,158)   # stone-400
EMERALD     = ( 52,211,153)


# ── lazy PIL import
def _pil():
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    return Image, ImageDraw, ImageFilter, ImageFont


def _font(path: str, size: int):
    from PIL import ImageFont
    return ImageFont.truetype(path, size)


GEORGIA  = "/System/Library/Fonts/Supplemental/Georgia.ttf"
HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"


# ──────────────────────────────────────────────────────────────────────────────
# Easing helpers
# ──────────────────────────────────────────────────────────────────────────────
def ease_in_out(t: float) -> float:
    """Cubic ease-in-out, t in [0,1]."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * t


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * max(0.0, min(1.0, t))


def alpha_lerp(t: float) -> int:
    return int(lerp(0, 255, t))


# ──────────────────────────────────────────────────────────────────────────────
# Drawing primitives
# ──────────────────────────────────────────────────────────────────────────────
def draw_text_centered(draw, text: str, y: int, font, color, shadow: bool = True):
    """Draw text horizontally centered with optional drop shadow."""
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 120))
    draw.text((x, y), text, font=font, fill=color)


def draw_text_left(draw, text: str, x: int, y: int, font, color):
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 100))
    draw.text((x, y), text, font=font, fill=color)


def draw_amber_line(draw, x1: int, y: int, x2: int, alpha: int = 200):
    """Thin amber horizontal rule."""
    draw.line([(x1, y), (x2, y)], fill=(*AMBER, alpha), width=2)


def vignette_overlay(img):
    """Darken the edges for cinematic look."""
    from PIL import Image, ImageFilter
    import numpy as np
    arr = np.array(img).astype(float)
    cx, cy = W / 2, H / 2
    ys, xs = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xs - cx) / cx) ** 2 + ((ys - cy) / cy) ** 2)
    vign = np.clip(1 - dist * 0.55, 0, 1)
    for c in range(3):
        arr[:, :, c] *= vign
    return Image.fromarray(arr.astype("uint8"), mode=img.mode)


# ──────────────────────────────────────────────────────────────────────────────
# Load & prepare hero image
# ──────────────────────────────────────────────────────────────────────────────
def load_hero() -> "Image":
    from PIL import Image
    p = ROOT / "frontend" / "dist" / "artisan_hero.jpg"
    img = Image.open(p).convert("RGB")
    # Scale to cover 1920×1080 with some extra for Ken Burns pan
    scale = max((W + 200) / img.width, (H + 200) / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    return img.resize((nw, nh), Image.LANCZOS)


# ──────────────────────────────────────────────────────────────────────────────
# Ken Burns: slow zoom + pan on the hero image
# ──────────────────────────────────────────────────────────────────────────────
def ken_burns_crop(hero, t: float) -> "Image":
    """
    t in [0,1]. Starts slightly zoomed in top-left, drifts toward center.
    """
    from PIL import Image
    iw, ih = hero.size
    # zoom factor: 1.08 → 1.02 over the clip
    zoom = lerp(1.10, 1.02, ease_in_out(t))
    cw = int(W / zoom)
    ch = int(H / zoom)
    # pan from (0.1, 0.1) to (0.5, 0.5) of excess space
    ex = iw - cw
    ey = ih - ch
    ox = int(lerp(ex * 0.08, ex * 0.45, ease_in_out(t)))
    oy = int(lerp(ey * 0.05, ey * 0.40, ease_in_out(t)))
    cropped = hero.crop((ox, oy, ox + cw, oy + ch))
    return cropped.resize((W, H), Image.LANCZOS)


# ──────────────────────────────────────────────────────────────────────────────
# Gradient overlay helpers
# ──────────────────────────────────────────────────────────────────────────────
def dark_gradient(draw, strength: float = 0.75):
    """Bottom-to-top dark gradient over the frame."""
    import numpy as np
    from PIL import Image
    grad = np.zeros((H, W, 4), dtype=np.uint8)
    for y in range(H):
        t = y / H
        # heavier at bottom, lighter at top
        alpha = int(strength * 255 * (0.3 + 0.7 * t))
        grad[y, :, 3] = alpha
    overlay = Image.fromarray(grad, mode="RGBA")
    return overlay


def solid_color_frame(color: tuple, alpha: float = 1.0) -> "Image":
    from PIL import Image
    img = Image.new("RGBA", (W, H), (*color, int(255 * alpha)))
    return img


# ──────────────────────────────────────────────────────────────────────────────
# Individual scene renderers
# ──────────────────────────────────────────────────────────────────────────────

def render_scene1(f: int, hero) -> "Image":
    """
    0–119 (0–4s): The craft — full-bleed artisan image, slow Ken Burns.
    f: absolute frame index 0..119
    """
    from PIL import Image, ImageDraw
    t  = f / 119
    ft = f / FPS  # time in seconds within this scene

    frame = ken_burns_crop(hero, t * 0.4).convert("RGBA")

    # Dark gradient overlay
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        frac = y / H
        a = int(200 * (0.15 + 0.85 * frac))
        gd.rectangle([(0, y), (W, y)], fill=(7, 6, 15, a))
    frame = Image.alpha_composite(frame, grad)

    draw = ImageDraw.Draw(frame)

    # ── Fade-in from black (first 0.7s)
    fade_in = ease_out(min(ft / 0.7, 1.0))

    # ── Top label: "PRESERVING INTANGIBLE CULTURAL HERITAGE"
    label_a = alpha_lerp(ease_out(min((ft - 0.3) / 0.8, 1.0)) if ft > 0.3 else 0.0)
    if label_a > 0:
        fl = _font(HELVETICA, 22)
        label = "PRESERVING INTANGIBLE CULTURAL HERITAGE"
        bbox = fl.getbbox(label)
        lw = bbox[2] - bbox[0]
        lx = (W - lw) // 2
        # amber dot + text
        draw.ellipse([(lx - 20, 68), (lx - 8, 80)], fill=(*AMBER, label_a))
        draw.text((lx, 64), label, font=fl, fill=(*AMBER, label_a))

    # ── Main headline fades in at 0.8s in two lines
    h1_a = alpha_lerp(ease_out(min((ft - 0.8) / 1.0, 1.0)) if ft > 0.8 else 0.0)
    if h1_a > 0:
        fg = _font(GEORGIA, 92)
        line1 = "The knowledge that"
        line2 = "lives in hands"
        y1 = H // 2 - 30
        draw_text_centered(draw, line1, y1 - 100, fg, (*WHITE, h1_a))
        # amber gradient on line2 — simulate by drawing in amber
        draw_text_centered(draw, line2, y1 + 10, fg, (*AMBER, h1_a))

    # ── Sub-line fades in at 2.2s
    sub_a = alpha_lerp(ease_out(min((ft - 2.2) / 0.9, 1.0)) if ft > 2.2 else 0.0)
    if sub_a > 0:
        fs = _font(HELVETICA, 34)
        sub = "deserves to live forever."
        draw_text_centered(draw, sub, H // 2 + 130, fs, (*STONE, sub_a))

    # ── Floating badge (top right) fades in at 1.5s
    badge_a = alpha_lerp(ease_out(min((ft - 1.5) / 0.8, 1.0)) if ft > 1.5 else 0.0)
    if badge_a > 0:
        bx, by = W - 460, 130
        # badge background
        badge_img = Image.new("RGBA", (400, 80), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge_img)
        bd.rounded_rectangle([(0, 0), (399, 79)], radius=12,
                              fill=(255, 255, 255, int(0.10 * badge_a)),
                              outline=(255, 255, 255, int(0.15 * badge_a)), width=1)
        fb = _font(HELVETICA, 18)
        fb2 = _font(HELVETICA, 24)
        bd.text((18, 14), "TACIT JUDGMENT CAPTURED", font=fb, fill=(*AMBER, badge_a))
        bd.text((18, 40), '"3 wraps · 4mm pinch · tactile snap"', font=fb2, fill=(*WHITE, badge_a))
        frame.alpha_composite(badge_img, (bx, by))

    # Black fade-in veil
    if fade_in < 1.0:
        veil = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - fade_in))))
        frame = Image.alpha_composite(frame, veil)

    return frame.convert("RGB")


def render_scene2(f: int, hero) -> "Image":
    """
    120–269 (4–9s): The problem — fragmentation.
    f: absolute frame 120..269 → local 0..149
    """
    from PIL import Image, ImageDraw, ImageFilter
    lf = f - 120
    ft = lf / FPS  # 0..4.97s

    # Base: slightly desaturated hero, darker
    base = ken_burns_crop(hero, 0.4 + lf / 149 * 0.2).convert("RGBA")
    # desaturate progressively
    desat = lf / 149
    if desat > 0:
        from PIL import ImageEnhance
        base_rgb = base.convert("RGB")
        base_rgb = ImageEnhance.Color(base_rgb).enhance(1.0 - desat * 0.6)
        base = base_rgb.convert("RGBA")

    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        frac = y / H
        a = int(220 * (0.25 + 0.75 * frac))
        gd.rectangle([(0, y), (W, y)], fill=(7, 6, 15, a))
    frame = Image.alpha_composite(base, grad)
    draw = ImageDraw.Draw(frame)

    # ── "What gets recorded?" block  (appears at 0.4s)
    r_a = alpha_lerp(ease_out(min((ft - 0.4) / 0.6, 1.0)) if ft > 0.4 else 0.0)
    if r_a > 0:
        fl = _font(HELVETICA, 28)
        fm = _font(HELVETICA, 22)
        fg = _font(GEORGIA, 50)
        # Left column
        draw.text((160, 280), "What gets recorded?", font=fl, fill=(*STONE, r_a))
        draw_amber_line(draw, 160, 320, 560, r_a)
        for i, item in enumerate(["Steps.", "Instructions.", "Videos."]):
            ia = alpha_lerp(ease_out(min((ft - 0.4 - i * 0.2) / 0.5, 1.0)))
            if ia > 0:
                draw.text((175, 340 + i * 44), item, font=fm, fill=(*WHITE, ia))

    # ── "What gets LOST?" block (appears at 2.0s) — amber, larger
    lost_a = alpha_lerp(ease_out(min((ft - 2.0) / 0.7, 1.0)) if ft > 2.0 else 0.0)
    if lost_a > 0:
        fl2 = _font(HELVETICA, 28)
        fm2 = _font(HELVETICA, 22)
        draw.text((W - 620, 280), "What gets LOST?", font=fl2, fill=(*AMBER, lost_a))
        draw_amber_line(draw, W - 620, 320, W - 160, lost_a)
        lost_items = ["Experience.", "Judgment.", "Tacit knowledge."]
        for i, item in enumerate(lost_items):
            ia = alpha_lerp(ease_out(min((ft - 2.0 - i * 0.25) / 0.5, 1.0)))
            if ia > 0:
                draw.text((W - 605, 340 + i * 44), item, font=fm2,
                          fill=(*AMBER, ia))

    # ── Centre divider line (appears at 1.5s)
    div_a = alpha_lerp(ease_out(min((ft - 1.5) / 0.5, 1.0)) if ft > 1.5 else 0.0)
    if div_a > 0:
        cx = W // 2
        h_line = int(lerp(0, 220, ease_out(min((ft - 1.5) / 0.4, 1.0))))
        draw.line([(cx, H // 2 - h_line // 2), (cx, H // 2 + h_line // 2)],
                  fill=(*STONE, div_a // 2), width=1)

    # ── Bottom quote fades in at 3.5s
    q_a = alpha_lerp(ease_out(min((ft - 3.5) / 0.8, 1.0)) if ft > 3.5 else 0.0)
    if q_a > 0:
        fq = _font(GEORGIA, 36)
        quote = "The touch. The pressure. The timing. The judgment."
        draw_text_centered(draw, quote, H - 160, fq, (*WHITE, q_a))
        fq2 = _font(HELVETICA, 24)
        draw_text_centered(draw, "An artisan makes these decisions instinctively.", H - 110, fq2, (*STONE, q_a))

    return frame.convert("RGB")


def render_scene3(f: int, hero) -> "Image":
    """
    270–419 (9–14s): The loss — emotional punch.
    f: absolute 270..419 → local 0..149
    """
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    lf = f - 270
    ft = lf / FPS  # 0..4.97s

    # Artisan image fades out — goes very dark
    fade_out = ease_in(min(ft / 3.5, 1.0))
    base = ken_burns_crop(hero, 0.6 + lf / 149 * 0.15).convert("RGBA")
    base_rgb = base.convert("RGB")
    # progressively desaturate and darken
    base_rgb = ImageEnhance.Color(base_rgb).enhance(max(0.0, 1.0 - fade_out * 0.85))
    base_rgb = ImageEnhance.Brightness(base_rgb).enhance(max(0.08, 1.0 - fade_out * 0.85))
    base = base_rgb.convert("RGBA")

    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        frac = y / H
        a = int(230 * (0.3 + 0.7 * frac))
        gd.rectangle([(0, y), (W, y)], fill=(7, 6, 15, a))
    frame = Image.alpha_composite(base, grad)
    draw = ImageDraw.Draw(frame)

    # ── "When a master retires..." (0.5s)
    a1 = alpha_lerp(ease_out(min((ft - 0.5) / 0.8, 1.0)) if ft > 0.5 else 0.0)
    # fade it out after 3s
    if ft > 3.0:
        a1 = alpha_lerp(ease_in(max(0, 1 - (ft - 3.0) / 0.6)))
    if a1 > 0:
        fg = _font(GEORGIA, 56)
        draw_text_centered(draw, "When a master artisan retires…", H // 2 - 120, fg, (*WHITE, a1))

    # ── "a piece of the craft retires with them." (1.5s)
    a2 = alpha_lerp(ease_out(min((ft - 1.5) / 0.8, 1.0)) if ft > 1.5 else 0.0)
    if ft > 3.0:
        a2 = alpha_lerp(ease_in(max(0, 1 - (ft - 3.0) / 0.6)))
    if a2 > 0:
        fg2 = _font(GEORGIA, 56)
        draw_text_centered(draw, "a piece of the craft retires with them.", H // 2 - 40, fg2, (*WHITE, a2))

    # ── "Permanently." in amber — the emotional punch (2.5s)
    a3 = alpha_lerp(ease_out(min((ft - 2.5) / 0.5, 1.0)) if ft > 2.5 else 0.0)
    if ft > 3.8:
        a3 = alpha_lerp(ease_in(max(0, 1 - (ft - 3.8) / 0.5)))
    if a3 > 0:
        fg3 = _font(GEORGIA, 80)
        draw_text_centered(draw, "Permanently.", H // 2 + 80, fg3, (*AMBER, a3))

    # ── Transition: stat line fades in at 3.5s
    stat_a = alpha_lerp(ease_out(min((ft - 3.5) / 0.8, 1.0)) if ft > 3.5 else 0.0)
    if stat_a > 0:
        fs = _font(HELVETICA, 26)
        stat = "India alone: 6.46 million artisans · 318 GI-protected crafts · fewer than 20 Sungudi knot-tiers remaining"
        draw_text_centered(draw, stat, H - 100, fs, (*STONE, stat_a))

    return frame.convert("RGB")


def render_scene4(f: int) -> "Image":
    """
    420–539 (14–18s): SKILL DNA solution emerges on dark canvas.
    Full vertical centering: headline at top-third, pipeline in middle, tagline at bottom-third.
    """
    from PIL import Image, ImageDraw
    lf = f - 420
    ft = lf / FPS   # 0..3.97s

    frame = Image.new("RGBA", (W, H), (*BG, 255))
    draw  = ImageDraw.Draw(frame)

    # ── 1. Radial amber glow dead-center
    glow_r = int(lerp(0, 620, ease_out(min(ft / 1.8, 1.0))))
    if glow_r > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd   = ImageDraw.Draw(glow)
        for r in range(glow_r, 0, -4):
            a = int(18 * (1 - r / glow_r) ** 2)
            gd.ellipse([(W//2 - r, H//2 - r), (W//2 + r, H//2 + r)],
                       fill=(*AMBER_DIM, a))
        frame = Image.alpha_composite(frame, glow)
        draw  = ImageDraw.Draw(frame)

    # ── Fixed anchor rows — vertically centered block on 1920×1080
    # Total block height: headline(88) + gap(14) + subtitle(38) + gap(14) + rule(2) + gap(52) + boxes(76) + gap(36) + sdk(28) + gap(18) + tag(26) = ~392px
    # To center: top of block at (1080 - 392) / 2 = 344px
    Y_HEADLINE = 344
    Y_SUBTITLE = Y_HEADLINE + 100
    Y_RULE     = Y_SUBTITLE + 54
    Y_BOXES    = Y_RULE + 90          # centre of pipeline boxes
    Y_SDK      = Y_BOXES + 76
    Y_TAG      = Y_SDK + 46

    BH = 76                   # box height
    total_w = 1380
    sx0 = (W - total_w) // 2

    # ── 2. Large "SKILL DNA" headline (fades in at 0.3s)
    h_a = alpha_lerp(ease_out(min((ft - 0.3) / 0.7, 1.0)) if ft > 0.3 else 0.0)
    if h_a > 0:
        fh = _font(HELVETICA, 88)
        # draw letter-spaced manually isn't needed — just draw centered
        bb = fh.getbbox("SKILL DNA")
        tw = bb[2] - bb[0]
        tx = (W - tw) // 2
        # shadow
        draw.text((tx + 4, Y_HEADLINE + 4), "SKILL DNA", font=fh, fill=(0, 0, 0, h_a // 3))
        draw.text((tx, Y_HEADLINE), "SKILL DNA", font=fh, fill=(*AMBER, h_a))

    # ── 3. Subtitle (0.8s)
    sub_a = alpha_lerp(ease_out(min((ft - 0.8) / 0.6, 1.0)) if ft > 0.8 else 0.0)
    if sub_a > 0:
        fs = _font(HELVETICA, 34)
        draw_text_centered(draw, "Preserving the knowledge behind the craft.",
                           Y_SUBTITLE, fs, (*WHITE, sub_a))

    # ── 4. Amber rule (1.2s) — full width across diagram
    rule_a = alpha_lerp(ease_out(min((ft - 1.2) / 0.5, 1.0)) if ft > 1.2 else 0.0)
    if rule_a > 0:
        draw_amber_line(draw, sx0, Y_RULE, sx0 + total_w, rule_a)

    # ── 5. Pipeline boxes (staggered from 1.4s)
    steps = [
        ("ARTISAN\nKNOWLEDGE", STONE, 230),
        ("OBSERVE",             STONE, 200),
        ("INTERVIEW",           STONE, 220),
        ("STRUCTURE",           STONE, 220),
        ("SKILL DNA",           AMBER, 260),
    ]
    gap   = (total_w - sum(s[2] for s in steps)) // (len(steps) - 1)
    xs    = []
    x_cur = sx0
    for s in steps:
        xs.append(x_cur)
        x_cur += s[2] + gap

    f_step = _font(HELVETICA, 28)
    f_last = _font(HELVETICA, 42)

    for i, ((label, col, bw), sx) in enumerate(zip(steps, xs)):
        delay = 1.4 + i * 0.22
        sa = alpha_lerp(ease_out(min((ft - delay) / 0.35, 1.0)) if ft > delay else 0.0)
        if sa <= 0:
            continue

        is_last = i == len(steps) - 1
        by = Y_BOXES - BH // 2

        box = Image.new("RGBA", (bw, BH), (0, 0, 0, 0))
        bd  = ImageDraw.Draw(box)
        if is_last:
            bd.rounded_rectangle([(0, 0), (bw-1, BH-1)], radius=14,
                                  fill=(*AMBER, int(0.22 * sa)),
                                  outline=(*AMBER, sa), width=2)
        else:
            bd.rounded_rectangle([(0, 0), (bw-1, BH-1)], radius=10,
                                  fill=(255,255,255,int(0.07*sa)),
                                  outline=(255,255,255,int(0.20*sa)), width=1)
        frame.alpha_composite(box, (sx, by))
        draw = ImageDraw.Draw(frame)

        font  = f_last if is_last else f_step
        lines = label.split("\n")
        lh    = BH // len(lines)
        for li, line in enumerate(lines):
            bb  = font.getbbox(line)
            tw  = bb[2] - bb[0]
            th  = bb[3] - bb[1]
            tx  = sx + (bw - tw) // 2
            ty  = by + lh * li + (lh - th) // 2
            draw.text((tx, ty), line, font=font, fill=(*col, sa))

        # Arrow (filled triangle, not text)
        if not is_last:
            aa = alpha_lerp(ease_out(min((ft - delay - 0.05) / 0.25, 1.0)) if ft > delay + 0.05 else 0.0)
            if aa > 0:
                ax = sx + bw + gap // 2 - 8
                ay = Y_BOXES
                draw.polygon([(ax, ay-10), (ax+16, ay), (ax, ay+10)],
                              fill=(*STONE, aa // 2))

    # ── 6. SDK line (2.8s)
    sdk_a = alpha_lerp(ease_out(min((ft - 2.8) / 0.5, 1.0)) if ft > 2.8 else 0.0)
    if sdk_a > 0:
        fs2 = _font(HELVETICA, 24)
        draw_text_centered(draw, "Built with Strands Agents SDK  |  Amazon Bedrock Nova Pro",
                           Y_SDK, fs2, (*STONE, sdk_a))

    # ── 7. Tagline (3.3s)
    tag_a = alpha_lerp(ease_out(min((ft - 3.3) / 0.4, 1.0)) if ft > 3.3 else 0.0)
    if tag_a > 0:
        ft2 = _font(HELVETICA, 22)
        draw_text_centered(draw, "Starting in Madurai   |   Built for the world",
                           Y_TAG, ft2, (*AMBER_DIM, tag_a))

    # ── Hard-cut fade to black (last 5 frames)
    if lf >= 115:
        veil = Image.new("RGBA", (W, H), (*BG, int(255 * ease_in((lf - 115) / 4))))
        frame = Image.alpha_composite(frame, veil)

    return frame.convert("RGB")


# ──────────────────────────────────────────────────────────────────────────────
# Main render loop
# ──────────────────────────────────────────────────────────────────────────────
def render(output: Path | None = None, preview_every: int = 0) -> Path:
    from PIL import Image

    if output is None:
        output = RESULTS / "intro.mp4"
    FRAMES.mkdir(parents=True, exist_ok=True)

    # Clean old frames
    for p in FRAMES.glob("*.png"):
        p.unlink()

    hero = load_hero()
    print(f"  Hero image: {hero.size}")
    print(f"  Rendering {N} frames @ {FPS}fps ({TOTAL}s)...")

    for f in range(N):
        if f % 30 == 0:
            print(f"    frame {f:4d}/{N}  ({f/FPS:.1f}s)", flush=True)

        if   f < 120:  frame = render_scene1(f, hero)
        elif f < 270:  frame = render_scene2(f, hero)
        elif f < 420:  frame = render_scene3(f, hero)
        else:          frame = render_scene4(f)

        frame.save(FRAMES / f"f{f:04d}.png")

    print(f"\n  Encoding to {output} ...")
    result = subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS),
        "-i", str(FRAMES / "f%04d.png"),
        "-c:v", "libx264",
        "-preset", "slow",        # better quality
        "-crf", "16",             # near-lossless quality
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("ffmpeg error:", result.stderr)
        return None

    # Clean frames
    shutil.rmtree(FRAMES, ignore_errors=True)

    size_mb = output.stat().st_size / 1_000_000
    print(f"\n✅  {output}  ({size_mb:.1f} MB, {TOTAL}s @ {FPS}fps, 1920×1080)")
    return output


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="python kit/make_intro.py")
    ap.add_argument("--output", default=str(RESULTS / "intro.mp4"))
    args = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = render(Path(args.output))
    return 0 if out else 1


if __name__ == "__main__":
    sys.exit(main())
