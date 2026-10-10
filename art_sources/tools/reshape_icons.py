"""Reshape AI-made Civ V promotion icons (gold glyph on dark square) into game-style icons.

Usage:  python reshape_icons.py <src_dir> <out_dir> name1 [name2 ...]
  Reads  <src_dir>/<name>_256.dds, writes <out_dir>/<name>_{256,64,45,32}.dds (DXT5).

Only background connected to the image border becomes transparent, so dark details
inside the glyph are kept. Colours are not changed. The glyph is centred and scaled to 72%.
Requires Pillow and texconv.exe next to this script.
"""
import os, subprocess, sys, tempfile
from collections import deque
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEXCONV = os.path.join(HERE, 'texconv.exe')


def reshape(src):
    im = src.convert('RGBA'); w, h = im.size; px = im.load()
    glyph = lambda x, y: max(px[x, y][0], px[x, y][1]) > 90
    ext = [[False] * w for _ in range(h)]
    q = deque([(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)])
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or ext[y][x] or glyph(x, y):
            continue
        ext[y][x] = True
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    out = Image.new('RGBA', (w, h)); o = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            o[x, y] = (r, g, b, max(0, min(255, (max(r, g) - 60) * 255 // 30)) if ext[y][x] else 255)
    bbox = out.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    gl = out.crop(bbox); s = int(256 * 0.72); gl.thumbnail((s, s), Image.LANCZOS)
    fin = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    fin.alpha_composite(gl, ((256 - gl.width) // 2, (256 - gl.height) // 2))
    return fin


def main(src_dir, out_dir, names):
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for n in names:
        fin = reshape(Image.open(os.path.join(src_dir, n + '_256.dds')))
        for sz in (256, 64, 45, 32):
            p = os.path.join(tmp, '%s_%d.png' % (n, sz))
            (fin if sz == 256 else fin.resize((sz, sz), Image.LANCZOS)).save(p)
            mips = '1' if sz == 45 else '0'   # 45px originals have a single mip level
            subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', mips, '-o', out_dir, p],
                                  stdout=subprocess.DEVNULL)
        print('reshaped', n)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
