"""Make building icons round, like the base game's (the production list and city screen show them as circles).

Usage (from the repo root):
    python art_sources/tools/round_building_icon.py <name> [<name> ...]
Reads art_sources/buildings/<name>/<name>_<size>.dds (any of 32/45/64/80/128/214/256 that exist; missing sizes are
scaled from the largest), masks each to a circle (anti-aliased edge, drawn at 4x and scaled down) and writes
LEKMOD/Art/Lekmod (v 1)/Art/Buildings/<name>_<size>.dds for 32/45/64/80/128/256 (BC3, one mip).
The sources stay untouched, so this can be rerun.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, 'art_sources', 'buildings')
OUT = os.path.join(REPO, 'LEKMOD', 'Art', 'Lekmod (v 1)', 'Art', 'Buildings')
TEXCONV = os.environ.get('TEXCONV', os.path.join(os.path.dirname(REPO), 'texconv.exe'))
SIZES = (32, 45, 64, 80, 128, 256)


def circle_mask(size, inset=0.02):
    s = 4
    m = Image.new('L', (size * s, size * s), 0)
    pad = size * s * inset
    ImageDraw.Draw(m).ellipse((pad, pad, size * s - 1 - pad, size * s - 1 - pad), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def build(name):
    folder = os.path.join(SRC, name)
    have = {}
    for f in os.listdir(folder):
        if f.startswith(name + '_') and f.endswith('.dds'):
            have[int(f[len(name) + 1:-4])] = os.path.join(folder, f)
    largest = Image.open(have[max(have)]).convert('RGBA')
    tmp = tempfile.mkdtemp()
    for sz in SIZES:
        im = Image.open(have[sz]).convert('RGBA') if sz in have else largest.resize((sz, sz), Image.LANCZOS)
        alpha = Image.composite(im.getchannel('A'), Image.new('L', im.size, 0), circle_mask(sz))
        im.putalpha(alpha)
        p = os.path.join(tmp, '%s_%d.png' % (name, sz))
        im.save(p)
        subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '1', '-o', OUT, p], stdout=subprocess.DEVNULL)
    print('built', name)


if __name__ == '__main__':
    for n in sys.argv[1:]:
        build(n)
