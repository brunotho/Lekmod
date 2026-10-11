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


def build(name):
    folder = os.path.join(SRC, name)
    have = {}
    for f in os.listdir(folder):
        if f.startswith(name + '_') and f.endswith('.dds'):
            have[int(f[len(name) + 1:-4])] = os.path.join(folder, f)
    src = Image.open(have[max(have)]).convert('RGBA')
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
