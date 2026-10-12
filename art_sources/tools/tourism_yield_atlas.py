"""Rebuild the map's Tourism tile-yield atlas with a suitcase instead of the camera in the 5+ cell.
Usage: python art_sources/tools/tourism_yield_atlas.py
Source: art_sources/yield_icons/tourism_yield_atlas_upstream.dds (upstream Lekmod, 2026-08-08: cells 1-4 suitcases, 5+ camera).
The 5+ cell (y 512-639, the game writes the number on top) is drawn like the base game's big icons
(art_sources/yield_icons/extracted/yieldatlas.dds, Production 5+: an 87 px disc with a ~3 px dark rim):
the inner brown disc of the single-suitcase icon (radius 16.5 px, without its thick dark ring) scaled to radius 40.5,
plus a thin dark rim out to radius 43.5.
Output: LEKMOD/Art/Lekmod (v 1)/Art/YieldAtlas_128_Tourism.dds (DXT5, one mip, like the original)."""
import os
import subprocess
import tempfile
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'art_sources', 'yield_icons', 'tourism_yield_atlas_upstream.dds')
OUT_DIR = os.path.join(ROOT, 'LEKMOD', 'Art', 'Lekmod (v 1)', 'Art')
TEXCONV = os.path.join(ROOT, '..', 'texconv.exe')
SS = 4                      # supersampling for smooth circle edges
SRC_CX, SRC_CY, SRC_R = 64.5, 65.5, 16.5
DST_CX, DST_CY, DST_R, RIM = 65.5, 64.5, 40.5, 3.0

atlas = Image.open(SRC).convert('RGBA')
one = atlas.crop((0, 0, 128, 128))

# the inner disc, scaled up
box = (SRC_CX - SRC_R, SRC_CY - SRC_R, SRC_CX + SRC_R, SRC_CY + SRC_R)
d = int(round(2 * DST_R * SS))
disc = one.resize((d, d), Image.LANCZOS, box=box)
mask = Image.new('L', (d, d), 0)
ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
disc.putalpha(mask)

big = Image.new('RGBA', (128 * SS, 128 * SS), (0, 0, 0, 0))
draw = ImageDraw.Draw(big)
ro = (DST_R + RIM) * SS
draw.ellipse((DST_CX * SS - ro, DST_CY * SS - ro, DST_CX * SS + ro, DST_CY * SS + ro), fill=(10, 6, 4, 235))
big.alpha_composite(disc, (int(round((DST_CX - DST_R) * SS)), int(round((DST_CY - DST_R) * SS))))
cell = big.resize((128, 128), Image.LANCZOS)

atlas.paste(Image.new('RGBA', (128, 128), (0, 0, 0, 0)), (0, 512))
atlas.alpha_composite(cell, (0, 512))
tmp = tempfile.mkdtemp()
png = os.path.join(tmp, 'YieldAtlas_128_Tourism.png')
atlas.save(png)
subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '1', '-o', OUT_DIR, png])
print('wrote', os.path.join(OUT_DIR, 'YieldAtlas_128_Tourism.dds'))
