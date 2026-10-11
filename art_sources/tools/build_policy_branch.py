"""Build a policy branch picture (192x292, DXT1, one mip) from a source image.
Usage: python art_sources/tools/build_policy_branch.py <source image> <game texture name>
Example: python art_sources/tools/build_policy_branch.py art_sources/policy_branches/commerce/commerce_merchant_ledger_v2.png SocialPoliciesCommerce.dds
The source is scaled to cover 192x292 and centre-cropped; the result goes to LEKMOD/Art/Lekmod (v 1)/Art/PolicyBranches/<name>.
The game finds the texture by file name, so <name> must be the base game's (see art_sources/README.md)."""
import os
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT_DIR = os.path.join(ROOT, 'LEKMOD', 'Art', 'Lekmod (v 1)', 'Art', 'PolicyBranches')
TEXCONV = os.path.join(ROOT, '..', 'texconv.exe')
W, H = 192, 292

src, name = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
s = max(W / im.width, H / im.height)
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
left, top = (im.width - W) // 2, (im.height - H) // 2
tmp = tempfile.mkdtemp()
png = os.path.join(tmp, os.path.splitext(name)[0] + '.png')
im.crop((left, top, left + W, top + H)).save(png)
subprocess.check_call([TEXCONV, '-nologo', '-y', '-f', 'BC1_UNORM', '-m', '1', '-o', OUT_DIR, png])
print('wrote', os.path.join(OUT_DIR, name))
