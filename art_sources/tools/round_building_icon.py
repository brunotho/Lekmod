"""Make building icons match the base game's: a circle 171 px wide at (43,42) inside a 256 px cell (two thirds of the
cell, same layout as unit portraits), transparent around it. Measured on BuildingPortraits3_*_Exp2Patch.dds
(256: 43..214, 128: 22..107, 64: 11..54, 45: 8..38). The city screen draws its bronze ring (IconFrame64.dds)
around that circle, so no frame is baked in.

Usage (from the repo root):
    python art_sources/tools/round_building_icon.py <name> [<name> ...]
Reads the largest art_sources/buildings/<name>/<name>_<size>.dds, scales it into the circle, masks it (anti-aliased
edge, drawn at 4x) and writes LEKMOD/Art/Lekmod (v 1)/Art/Buildings/<name>_<size>.dds for 32/45/64/80/128/214/256
(BC3, one mip). The sources stay untouched, so this can be rerun.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, 'art_sources', 'buildings')
OUT = os.path.join(REPO, 'LEKMOD', 'Art', 'Lekmod (v 1)', 'Art', 'Buildings')
TEXCONV = os.environ.get('TEXCONV', os.path.join(os.path.dirname(REPO), 'texconv.exe'))
SIZES = (32, 45, 64, 80, 128, 214, 256)
DIAMETER, OFF_X, OFF_Y = 171 / 256.0, 43 / 256.0, 42 / 256.0
CROP = 0.05  # fraction trimmed from each edge of the source before scaling
# sources delivered as a cut-out on white: the white connected to the edges becomes this background colour
WHITE_BACKGROUND = {'ministry_of_truth': (22, 22, 24)}


def icon(src, size):
    s = 4
    big = size * s
    d = int(round(DIAMETER * big))
    x, y = int(round(OFF_X * big)), int(round(OFF_Y * big))
    art = src.resize((d, d), Image.LANCZOS)
    mask = Image.new('L', (d, d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
    art.putalpha(Image.composite(art.getchannel('A'), Image.new('L', (d, d), 0), mask))
    canvas = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    canvas.alpha_composite(art, (x, y))
    return canvas.resize((size, size), Image.LANCZOS)


def replace_white_background(src, colour):
    rgb = src.convert('RGB')
    w, h = rgb.size
    seeds = [(x, 0) for x in range(0, w, 8)] + [(x, h - 1) for x in range(0, w, 8)] +             [(0, y) for y in range(0, h, 8)] + [(w - 1, y) for y in range(0, h, 8)]
    marker = (255, 0, 255)
    for seed in seeds:
        if min(rgb.getpixel(seed)) >= 225:
            ImageDraw.floodfill(rgb, seed, marker, thresh=40)
    out = Image.new('RGBA', (w, h))
    px_in, px_out = rgb.load(), out.load()
    for yy in range(h):
        for xx in range(w):
            px_out[xx, yy] = colour + (255,) if px_in[xx, yy] == marker else px_in[xx, yy] + (255,)
    return out


def build(name):
    folder = os.path.join(SRC, name)
    have = {}
    for f in os.listdir(folder):
        if f.startswith(name + '_') and f.endswith('.dds'):
            have[int(f[len(name) + 1:-4])] = os.path.join(folder, f)
    src = Image.open(have[max(have)]).convert('RGBA')
    if name in WHITE_BACKGROUND:
        src = replace_white_background(src, WHITE_BACKGROUND[name])
    # the delivered art has a dark border/vignette: trim it so the circle shows the picture, not a black ring
    c = int(round(src.size[0] * CROP))
    src = src.crop((c, c, src.size[0] - c, src.size[1] - c))
    tmp = tempfile.mkdtemp()
    for sz in SIZES:
        p = os.path.join(tmp, '%s_%d.png' % (name, sz))
        icon(src, sz).save(p)
        subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '1', '-o', OUT, p], stdout=subprocess.DEVNULL)
    print('built', name)


if __name__ == '__main__':
    for n in sys.argv[1:]:
        build(n)
