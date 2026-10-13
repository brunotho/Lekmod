"""Espionage screen: framed 45 px "level up" icon for the diplomat progress bar.

Drawn from scratch in the style of the base game's Esp_FramedIcons45_Expansion icons (packed in the game archives):
gold ring, glossy black-to-blue disc, pale cyan glyph. The glyph is a wide double chevron (up arrow).
Run from the repo root: python art_sources/tools/build_levelup_icon.py [--preview out.png]
Writes LEKMOD/Art/Lekmod (v 1)/UI/lekmod_esp_levelup45.dds (uncompressed B8G8R8A8, one mip).
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

S = 8                      # supersampling
N = 45
OUT = os.path.join('LEKMOD', 'Art', 'Lekmod (v 1)', 'UI', 'lekmod_esp_levelup45.dds')
TEXCONV = os.environ.get('TEXCONV', r'C:\Users\bbruno\civ-tools\texconv.exe')


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def build():
    W = N * S
    img = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    cx = cy = W / 2.0
    r_out = 20.5 * S       # outer edge of the gold ring
    r_in = 17.5 * S        # inner edge of the ring = disc

    # gold ring: lighter at the top, darker at the bottom
    ring = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    px = ring.load()
    for y in range(W):
        t = y / float(W)
        col = lerp((236, 206, 140), (150, 112, 52), t)
        for x in range(W):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if r_in - S <= d <= r_out:
                px[x, y] = col + (255,)
    img.alpha_composite(ring)

    # disc: black at the top left, deep blue at the bottom right
    disc = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    px = disc.load()
    for y in range(W):
        for x in range(W):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= r_in:
                t = max(0.0, min(1.0, ((x - cx) + (y - cy)) / (2 * r_in) + 0.5))
                px[x, y] = lerp((4, 6, 14), (10, 34, 120), t ** 1.4) + (255,)
    img.alpha_composite(disc)

    # gloss: soft white ellipse in the upper half
    gloss = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).ellipse((cx - 13 * S, cy - 16 * S, cx + 11 * S, cy - 2 * S), fill=(255, 255, 255, 46))
    gloss = gloss.filter(ImageFilter.GaussianBlur(2 * S))
    mask = Image.new('L', (W, W), 0)
    ImageDraw.Draw(mask).ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in), fill=255)
    img.paste(Image.alpha_composite(img, gloss), (0, 0), mask)

    # glyph: two wide chevrons with a dark outline
    glyph = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    g = ImageDraw.Draw(glyph)
    half = 11.0 * S        # half width of a chevron
    rise = 7.0 * S         # height of a chevron
    for top, col in ((cy - 8.5 * S, (196, 238, 244)), (cy + 0.5 * S, (150, 214, 226))):
        pts = [(cx - half, top + rise), (cx, top), (cx + half, top + rise)]
        g.line(pts, fill=(0, 10, 30, 255), width=int(5.6 * S), joint='curve')
        g.line(pts, fill=col + (255,), width=int(3.4 * S), joint='curve')
    img.alpha_composite(glyph)

    return img.resize((N, N), Image.LANCZOS)


def main():
    img = build()
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        img.resize((N * 6, N * 6), Image.NEAREST).save(out)
        print('preview', out)
        return
    tmp = os.path.join(tempfile.mkdtemp(), 'lekmod_esp_levelup45.png')
    img.save(tmp)
    subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'B8G8R8A8_UNORM', '-m', '1', '-o', os.path.dirname(OUT), tmp])
    print('wrote', OUT)


if __name__ == '__main__':
    main()
