"""Rebuild the map's Tourism tile-yield atlas with a suitcase instead of the camera in the 5+ cell.
Usage: python art_sources/tools/tourism_yield_atlas.py
Source: art_sources/yield_icons/tourism_yield_atlas_upstream.dds (upstream Lekmod, 2026-08-08: cells 1-4 suitcases, 5+ camera).
The 5+ cell (y 512-639, the game writes the number on top) gets the single-suitcase cell scaled x2 around the same centre.
Output: LEKMOD/Art/Lekmod (v 1)/Art/YieldAtlas_128_Tourism.dds (DXT5, one mip, like the original)."""
import os
import subprocess
import tempfile
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'art_sources', 'yield_icons', 'tourism_yield_atlas_upstream.dds')
OUT_DIR = os.path.join(ROOT, 'LEKMOD', 'Art', 'Lekmod (v 1)', 'Art')
TEXCONV = os.path.join(ROOT, '..', 'texconv.exe')

atlas = Image.open(SRC).convert('RGBA')
single = atlas.crop((0, 0, 128, 128)).crop((40, 41, 89, 90))        # the one-suitcase circle, with a little margin
big = single.resize((single.width * 2, single.height * 2), Image.LANCZOS)
cell = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
cell.alpha_composite(big, ((128 - big.width) // 2 + 1, (128 - big.height) // 2 + 1))
atlas.paste(Image.new('RGBA', (128, 128), (0, 0, 0, 0)), (0, 512))
atlas.alpha_composite(cell, (0, 512))
tmp = tempfile.mkdtemp()
png = os.path.join(tmp, 'YieldAtlas_128_Tourism.png')
atlas.save(png)
subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '1', '-o', OUT_DIR, png])
print('wrote', os.path.join(OUT_DIR, 'YieldAtlas_128_Tourism.dds'))
